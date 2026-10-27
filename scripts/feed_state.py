#!/usr/bin/env python3
"""Incremental release state for the OpenWrt package feed.

The state file records the source tree hash, package hashes and index hash of
the last successful release.  It is signed with the feed signing key and is
used by the next release to decide which packages can be reused safely.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import feed_meta

STATE_SCHEMA = 1
STATE_GENERATOR = 1
HEX = re.compile(r"^[0-9a-f]{40,64}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_DIR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SAFE_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+~-]*\.apk$")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise feed_meta.FeedError("state file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise feed_meta.FeedError("invalid JSON in %s: %s" % (path, exc)) from exc
    if not isinstance(data, dict):
        raise feed_meta.FeedError("state file must be a JSON object")
    return data


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def state_validate(state: dict) -> None:
    errors: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    need(state.get("schema") == STATE_SCHEMA, "state.schema must be %d" % STATE_SCHEMA)
    need(state.get("generator") == STATE_GENERATOR, "state.generator must be %d" % STATE_GENERATOR)
    need(isinstance(state.get("build_version"), str) and state["build_version"], "state.build_version is missing")
    need(isinstance(state.get("source_commit"), str) and HEX.match(state["source_commit"]), "state.source_commit is invalid")
    need(isinstance(state.get("generated_at"), str) and state["generated_at"], "state.generated_at is missing")
    vendor_tree = state.get("vendor_tree")
    need(vendor_tree is None or (isinstance(vendor_tree, str) and HEX.match(vendor_tree)), "state.vendor_tree is invalid")
    need(isinstance(state.get("build_config"), str) and HEX64.match(state["build_config"]), "state.build_config is invalid")
    sources = state.get("sources")
    need(isinstance(sources, dict) and sources, "state.sources must be a non-empty object")
    if isinstance(sources, dict):
        for source, value in sources.items():
            need(isinstance(source, str) and SAFE_DIR.match(source), "invalid state source: %r" % (source,))
            need(isinstance(value, dict) and isinstance(value.get("tree"), str) and HEX.match(value["tree"]), "invalid tree for source %s" % source)
    arches = state.get("arches")
    need(isinstance(arches, dict) and arches, "state.arches must be a non-empty object")
    if isinstance(arches, dict):
        for arch, value in arches.items():
            need(isinstance(arch, str) and feed_meta.SAFE_ARCH.match(arch), "invalid state arch: %r" % (arch,))
            need(isinstance(value, dict), "state.arches[%s] must be an object" % arch)
            if not isinstance(value, dict):
                continue
            index = value.get("index")
            need(isinstance(index, dict), "state.arches[%s].index is missing" % arch)
            if isinstance(index, dict):
                need(index.get("file") == "packages.adb", "invalid index file for %s" % arch)
                need(isinstance(index.get("sha256"), str) and HEX64.match(index["sha256"]), "invalid index sha256 for %s" % arch)
                need(isinstance(index.get("size"), int) and index["size"] >= 0, "invalid index size for %s" % arch)
            packages = value.get("packages")
            need(isinstance(packages, list), "state.arches[%s].packages must be a list" % arch)
            if not isinstance(packages, list):
                continue
            names: set[str] = set()
            files: set[str] = set()
            for package in packages:
                need(isinstance(package, dict), "invalid package entry in %s" % arch)
                if not isinstance(package, dict):
                    continue
                name = package.get("name")
                version = package.get("version")
                source = package.get("source")
                origin = package.get("origin")
                file_name = package.get("file")
                digest = package.get("sha256")
                size = package.get("size")
                need(isinstance(name, str) and name and " " not in name, "invalid package name in %s" % arch)
                need(isinstance(version, str) and version and " " not in version, "invalid version for %s/%s" % (arch, name))
                need(isinstance(source, str) and SAFE_DIR.match(source), "invalid source for %s/%s" % (arch, name))
                need(isinstance(origin, str) and origin, "invalid origin for %s/%s" % (arch, name))
                need(isinstance(file_name, str) and SAFE_FILE.match(file_name), "invalid file for %s/%s" % (arch, name))
                need(isinstance(digest, str) and HEX64.match(digest), "invalid sha256 for %s/%s" % (arch, name))
                need(isinstance(size, int) and size >= 0, "invalid size for %s/%s" % (arch, name))
                if isinstance(name, str):
                    need(name not in names, "duplicate package name %s in %s" % (name, arch))
                    names.add(name)
                if isinstance(file_name, str):
                    need(file_name not in files, "duplicate package file %s in %s" % (file_name, arch))
                    files.add(file_name)
                if isinstance(source, str) and isinstance(sources, dict):
                    need(source in sources, "package %s references unknown source %s" % (name, source))
    if errors:
        raise feed_meta.FeedError("\n".join(errors))


def verify_state(state_path: Path, sig_path: Path, feed_path: Path, repo: Path) -> None:
    feed = feed_meta.load_feed(feed_path)
    feed_meta.validate_feed(feed, repo)
    keys = feed_meta.active_keys(feed, repo, include_trusted=True)
    if not keys:
        raise feed_meta.FeedError("no active/trusted signing keys in feed.json")
    last_error = ""
    for key, key_path in keys:
        proc = subprocess.run(
            [
                "openssl",
                "dgst",
                "-sha256",
                "-verify",
                str(key_path),
                "-signature",
                str(sig_path),
                str(state_path),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return
        last_error = proc.stderr.strip()
    raise feed_meta.FeedError("state signature verification failed: %s" % (last_error or "unknown error"))


def current_sources(repo: Path) -> tuple[dict[str, str], dict[str, feed_meta.Package]]:
    packages = feed_meta.discover_packages(repo)
    by_dir = {package.directory: package for package in packages}
    trees: dict[str, str] = {}
    for directory in by_dir:
        proc = feed_meta.git(repo, "rev-parse", "HEAD:packages/%s" % directory)
        trees[directory] = proc.stdout.strip()
    return trees, by_dir


def current_vendor_tree(repo: Path) -> str | None:
    proc = feed_meta.git(repo, "rev-parse", "HEAD:vendor", check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def control_files_changed(repo: Path, source_commit: str) -> bool:
    proc = feed_meta.git(
        repo,
        "diff",
        "--name-only",
        source_commit,
        "HEAD",
        "--",
        "scripts/feed_meta.py",
        "scripts/feed_state.py",
        ".github/workflows/release.yml",
        check=False,
    )
    return proc.returncode != 0 or bool(proc.stdout.strip())


def version_string(package: feed_meta.Package) -> str:
    if package.release:
        return "%s-r%s" % (package.version, package.release)
    return package.version


def gh_write(path: Path | None, key: str, value: str) -> None:
    if path is None:
        print("%s=%s" % (key, value))
        return
    with path.open("a", encoding="utf-8") as handle:
        if "\n" in value:
            handle.write("%s<<__FEED_OUTPUT_EOF__\n%s\n__FEED_OUTPUT_EOF__\n" % (key, value))
        else:
            handle.write("%s=%s\n" % (key, value))


def command_plan(args: argparse.Namespace, repo: Path) -> int:
    feed = feed_meta.load_feed((repo / args.feed).resolve())
    feed_meta.validate_feed(feed, repo)
    trees, by_dir = current_sources(repo)
    all_packages = " ".join(package.name for package in by_dir.values())
    state_path = Path(args.state).resolve() if args.state else None
    state: dict | None = None
    has_state = "0"
    reasons: list[str] = []

    if state_path is not None and state_path.is_file() and state_path.stat().st_size:
        state = load_json(state_path)
        try:
            state_validate(state)
        except feed_meta.FeedError:
            if not args.full_build:
                raise
            state = None
        else:
            has_state = "1"

    if args.full_build:
        reasons.append("full_build input")
    if state is None:
        reasons.append("no previous state")
    else:
        if state["build_version"] != feed["build_version"]:
            reasons.append("build_version changed")
        if set(state["arches"]) != set(feed["arches"]):
            reasons.append("arch list changed")
        if feed_meta.git(repo, "merge-base", "--is-ancestor", state["source_commit"], "HEAD", check=False).returncode != 0:
            reasons.append("previous state is not an ancestor of HEAD")
        if state.get("vendor_tree") != current_vendor_tree(repo):
            reasons.append("vendor tree changed")
        if state.get("build_config") != feed_meta.build_config_hash(repo, feed):
            reasons.append("build config changed")
        if control_files_changed(repo, state["source_commit"]):
            reasons.append("release control files changed")
    local_dep = feed_meta.local_build_dependency(list(by_dir.values()))
    if local_dep:
        reasons.append("local build dependency: %s" % local_dep)

    full = bool(reasons)
    build_dirs: list[str] = []
    removed_dirs: list[str] = []
    build_packages: list[str] = []
    if full:
        matrix = [
            {
                "arch": arch,
                "packages": all_packages,
                "all_packages": all_packages,
                "full": "1",
                "build_dirs": "",
                "removed_dirs": "",
            }
            for arch in feed["arches"]
        ]
    else:
        assert state is not None
        state_sources = state["sources"]
        build_dirs = [
            directory
            for directory, tree in trees.items()
            if state_sources.get(directory, {}).get("tree") != tree
        ]
        removed_dirs = sorted(directory for directory in state_sources if directory not in trees)
        build_packages = [by_dir[directory].name for directory in build_dirs]
        matrix = []
        for arch in feed["arches"]:
            arch_state = state["arches"].get(arch)
            arch_full = arch_state is None
            if arch_state is not None:
                state_sources_for_arch = {package["source"] for package in arch_state["packages"]}
                expected_kept = set(trees) - set(build_dirs) - set(removed_dirs)
                if not expected_kept.issubset(state_sources_for_arch):
                    arch_full = True
                if any(package["source"] not in state_sources for package in arch_state["packages"]):
                    arch_full = True
            if arch_full:
                matrix.append(
                    {
                        "arch": arch,
                        "packages": all_packages,
                        "all_packages": all_packages,
                        "full": "1",
                        "build_dirs": "",
                        "removed_dirs": "",
                    }
                )
            else:
                matrix.append(
                    {
                        "arch": arch,
                        "packages": " ".join(build_packages),
                        "all_packages": all_packages,
                        "full": "0",
                        "build_dirs": " ".join(build_dirs),
                        "removed_dirs": " ".join(removed_dirs),
                    }
                )
        for directory in build_dirs:
            package = by_dir[directory]
            previous_versions = {
                item["version"]
                for arch_state in state["arches"].values()
                for item in arch_state["packages"]
                if item["source"] == directory and item["name"] == package.name
            }
            if previous_versions == {version_string(package)}:
                print(
                    "WARNING: %s changed but version is still %s; bump PKG_RELEASE or "
                    "set allow_same_version=true on workflow_dispatch"
                    % (directory, version_string(package)),
                    file=sys.stderr,
                )

    matrix_json = json.dumps({"include": matrix}, separators=(",", ":"))
    gh_write(Path(args.github_output) if args.github_output else None, "matrix", matrix_json)
    gh_write(Path(args.github_output) if args.github_output else None, "build_packages", " ".join(build_packages))
    gh_write(Path(args.github_output) if args.github_output else None, "build_dirs", " ".join(build_dirs))
    gh_write(Path(args.github_output) if args.github_output else None, "removed_dirs", " ".join(removed_dirs))
    gh_write(Path(args.github_output) if args.github_output else None, "all_packages", all_packages)
    gh_write(Path(args.github_output) if args.github_output else None, "full_build", "1" if full else "0")
    gh_write(Path(args.github_output) if args.github_output else None, "has_state", has_state)
    gh_write(Path(args.github_output) if args.github_output else None, "build_version", feed["build_version"])
    print(
        json.dumps(
            {
                "full_build": bool(full),
                "reasons": reasons,
                "build_dirs": build_dirs,
                "removed_dirs": removed_dirs,
                "matrix": matrix,
            },
            indent=2,
        )
    )
    return 0


def command_verify(args: argparse.Namespace, repo: Path) -> int:
    verify_state(
        Path(args.state).resolve(),
        Path(args.sig).resolve(),
        (repo / args.feed).resolve(),
        repo,
    )
    print("state signature OK")
    return 0


def command_restore(args: argparse.Namespace, repo: Path) -> int:
    state = load_json(Path(args.state).resolve())
    state_validate(state)
    arch_state = state["arches"].get(args.arch)
    if arch_state is None:
        raise feed_meta.FeedError("state has no arch %s" % args.arch)
    base_url = args.base_url.rstrip("/")
    build_version = state["build_version"]
    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    skip = set(args.skip_dirs.split())
    cache = "?v=%s" % state["source_commit"]
    for package in arch_state["packages"]:
        if package["source"] in skip:
            continue
        relative = "%s/%s/custom/%s" % (build_version, args.arch, package["file"])
        url = "%s/%s%s" % (base_url, urllib.parse.quote(relative), cache)
        target = dest / package["file"]
        temp = dest / (package["file"] + ".part")
        try:
            with urllib.request.urlopen(url, timeout=60) as response, temp.open("wb") as handle:
                shutil.copyfileobj(response, handle)
        except Exception as exc:
            temp.unlink(missing_ok=True)
            raise feed_meta.FeedError("unable to download %s: %s" % (url, exc)) from exc
        if temp.stat().st_size != package["size"]:
            temp.unlink(missing_ok=True)
            raise feed_meta.FeedError("size mismatch for %s" % package["file"])
        if feed_meta.sha256_file(temp) != package["sha256"]:
            temp.unlink(missing_ok=True)
            raise feed_meta.FeedError("sha256 mismatch for %s" % package["file"])
        temp.replace(target)
    print("restored %d packages for %s" % (len(list(dest.glob("*.apk"))), args.arch))
    return 0


def command_merge(args: argparse.Namespace, repo: Path) -> int:
    out = Path(args.out).resolve()
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    built = Path(args.built).resolve()
    built_files = sorted(built.glob("*.apk")) if built.is_dir() else []
    if args.full:
        if not built_files:
            raise feed_meta.FeedError("full build produced no .apk files")
        for path in built_files:
            shutil.copy2(path, out / path.name)
        print("merged %d packages (full build)" % len(built_files))
        return 0
    state = load_json(Path(args.state).resolve())
    state_validate(state)
    arch_state = state["arches"].get(args.arch)
    if arch_state is None:
        raise feed_meta.FeedError("state has no arch %s" % args.arch)
    build_dirs = set(args.build_dirs.split())
    removed_dirs = set(args.removed_dirs.split())
    previous = Path(args.previous).resolve()
    kept = 0
    for package in arch_state["packages"]:
        if package["source"] in build_dirs or package["source"] in removed_dirs:
            continue
        source = previous / package["file"]
        if not source.is_file():
            raise feed_meta.FeedError("restored file missing: %s" % source)
        if source.stat().st_size != package["size"] or feed_meta.sha256_file(source) != package["sha256"]:
            raise feed_meta.FeedError("restored file hash mismatch: %s" % source)
        shutil.copy2(source, out / package["file"])
        kept += 1
    for path in built_files:
        shutil.copy2(path, out / path.name)
    if not list(out.glob("*.apk")):
        raise feed_meta.FeedError("merge produced an empty feed")
    print("merged %d kept + %d built packages" % (kept, len(built_files)))
    return 0


def normalize_source(origin: str, known: set[str]) -> str:
    value = origin.lstrip("/")
    for pattern in (
        r"^feeds/[^/]+/packages/(.+)$",
        r"^feed/packages/(.+)$",
        r"^packages/(.+)$",
        r"^([^/]+)$",
    ):
        match = re.match(pattern, value)
        if not match:
            continue
        source = match.group(1)
        if source in known:
            return source
    raise feed_meta.FeedError("unknown package origin: %s" % origin)


def previous_state_by_arch(state: dict | None, arch: str) -> dict[str, dict]:
    if not state:
        return {}
    return {package["name"]: package for package in state["arches"].get(arch, {}).get("packages", [])}


def command_generate(args: argparse.Namespace, repo: Path) -> int:
    feed = feed_meta.load_feed((repo / args.feed).resolve())
    feed_meta.validate_feed(feed, repo)
    packages = feed_meta.discover_packages(repo)
    by_dir = {package.directory: package for package in packages}
    known = set(by_dir)
    previous = None
    if args.previous_state and Path(args.previous_state).is_file():
        previous = load_json(Path(args.previous_state).resolve())
        state_validate(previous)

    signed = Path(args.signed).resolve()
    metadata_dir = Path(args.metadata).resolve()
    trees: dict[str, str] = {}
    arches: dict[str, dict] = {}
    seen_sources: set[str] = set()
    for arch_dir in sorted(path for path in signed.iterdir() if path.is_dir()):
        arch = arch_dir.name
        files = sorted(path.name for path in arch_dir.glob("*.apk"))
        if not files:
            raise feed_meta.FeedError("no .apk files for arch %s" % arch)
        metadata_path = metadata_dir / (arch + ".json")
        metadata = load_json(metadata_path)
        entries = metadata.get("packages")
        if not isinstance(entries, list):
            raise feed_meta.FeedError("metadata for %s has no packages list" % arch)
        previous_by_name = previous_state_by_arch(previous, arch)
        packages_out: list[dict] = []
        used_files: set[str] = set()
        arch_sources: set[str] = set()
        for info in entries:
            if not isinstance(info, dict):
                raise feed_meta.FeedError("invalid package metadata entry for %s" % arch)
            name = info.get("name")
            version = info.get("version")
            origin = info.get("origin")
            if not isinstance(name, str) or not name or not isinstance(version, str) or not version:
                raise feed_meta.FeedError("package metadata missing name/version for %s" % arch)
            if not isinstance(origin, str) or not origin:
                raise feed_meta.FeedError("package %s has no origin" % name)
            source = normalize_source(origin, known)
            candidate = "%s-%s.apk" % (name, version)
            if candidate not in files:
                matches = [item for item in files if item.startswith(name + "-") and item.endswith(".apk")]
                if len(matches) != 1:
                    raise feed_meta.FeedError("cannot map package %s-%s to an .apk file" % (name, version))
                candidate = matches[0]
            if candidate in used_files:
                raise feed_meta.FeedError("duplicate .apk mapping for %s in %s" % (candidate, arch))
            used_files.add(candidate)
            path = arch_dir / candidate
            digest = feed_meta.sha256_file(path)
            size = path.stat().st_size
            previous_package = previous_by_name.get(name)
            if (
                previous_package
                and previous_package.get("version") == version
                and previous_package.get("sha256") != digest
                and not args.allow_same_version
            ):
                raise feed_meta.FeedError(
                    "package %s %s changed bytes without a version bump; bump PKG_RELEASE "
                    "or use allow_same_version=true" % (name, version)
                )
            packages_out.append(
                {
                    "name": name,
                    "version": version,
                    "arch": info.get("arch") or "",
                    "source": source,
                    "origin": origin,
                    "file": candidate,
                    "sha256": digest,
                    "size": size,
                }
            )
            arch_sources.add(source)
        if used_files != set(files):
            missing = sorted(set(files) - used_files)
            raise feed_meta.FeedError("unreferenced .apk files for %s: %s" % (arch, ", ".join(missing)))
        missing_dirs = sorted(known - arch_sources)
        if missing_dirs:
            raise feed_meta.FeedError(
                "no package output for %s in arch %s (changed dir produced nothing or state is incomplete)"
                % (", ".join(missing_dirs), arch)
            )
        seen_sources |= arch_sources
        index = arch_dir / "packages.adb"
        if not index.is_file():
            raise feed_meta.FeedError("missing index for arch %s" % arch)
        arches[arch] = {
            "index": {
                "file": index.name,
                "sha256": feed_meta.sha256_file(index),
                "size": index.stat().st_size,
            },
            "packages": packages_out,
        }

    missing_arches = sorted(set(feed["arches"]) - set(arches))
    if missing_arches:
        raise feed_meta.FeedError("missing build output for arches: %s" % ", ".join(missing_arches))
    extra_arches = sorted(set(arches) - set(feed["arches"]))
    if extra_arches:
        raise feed_meta.FeedError("unexpected build output for arches: %s" % ", ".join(extra_arches))
    missing_sources = sorted(known - seen_sources)
    if missing_sources:
        raise feed_meta.FeedError("no package output for source directories: %s" % ", ".join(missing_sources))
    for source in sorted(known):
        trees[source] = feed_meta.git(repo, "rev-parse", "HEAD:packages/%s" % source).stdout.strip()
    state = {
        "schema": STATE_SCHEMA,
        "generator": STATE_GENERATOR,
        "build_version": feed["build_version"],
        "source_commit": args.source_commit,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vendor_tree": current_vendor_tree(repo),
        "build_config": feed_meta.build_config_hash(repo, feed),
        "sources": {source: {"tree": tree} for source, tree in sorted(trees.items())},
        "arches": arches,
    }
    state_validate(state)
    save_json(Path(args.out).resolve(), state)
    print("wrote %s (%d arches, %d packages per arch)" % (args.out, len(arches), len(next(iter(arches.values()))["packages"])))
    return 0


def command_sign(args: argparse.Namespace, repo: Path) -> int:
    state = Path(args.state).resolve()
    out = Path(args.out).resolve()
    key = Path(args.key).resolve()
    if not state.is_file() or not key.is_file():
        raise feed_meta.FeedError("state or private key not found")
    subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(key), "-out", str(out), str(state)],
        check=True,
    )
    print("signed state: %s" % out)
    return 0


def command_verify_publish(args: argparse.Namespace, repo: Path) -> int:
    feed = feed_meta.load_feed((repo / args.feed).resolve())
    feed_meta.validate_feed(feed, repo)
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    state_validate(state)
    if args.sig:
        verify_state(state_path, Path(args.sig).resolve(), (repo / args.feed).resolve(), repo)
    public = Path(args.public).resolve()
    for arch, arch_state in state["arches"].items():
        custom = public / state["build_version"] / arch / "custom"
        index = custom / arch_state["index"]["file"]
        if not index.is_file():
            raise feed_meta.FeedError("published index missing: %s" % index)
        if index.stat().st_size != arch_state["index"]["size"] or feed_meta.sha256_file(index) != arch_state["index"]["sha256"]:
            raise feed_meta.FeedError("published index does not match state: %s" % index)
        files = {path.name for path in custom.glob("*.apk")}
        expected = {package["file"] for package in arch_state["packages"]}
        if files != expected:
            raise feed_meta.FeedError(
                "published package set mismatch for %s (missing=%s extra=%s)"
                % (arch, sorted(expected - files), sorted(files - expected))
            )
        for package in arch_state["packages"]:
            path = custom / package["file"]
            if path.stat().st_size != package["size"] or feed_meta.sha256_file(path) != package["sha256"]:
                raise feed_meta.FeedError("published package hash mismatch: %s" % path)
    print("published feed matches state")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--repo", default=argparse.SUPPRESS)
    verify.add_argument("--state", required=True)
    verify.add_argument("--sig", required=True)
    verify.add_argument("--feed", default="feed.json")

    plan = subparsers.add_parser("plan")
    plan.add_argument("--repo", default=argparse.SUPPRESS)
    plan.add_argument("--state", default="")
    plan.add_argument("--feed", default="feed.json")
    plan.add_argument("--full-build", action="store_true")
    plan.add_argument("--github-output", default="")

    restore = subparsers.add_parser("restore")
    restore.add_argument("--repo", default=argparse.SUPPRESS)
    restore.add_argument("--state", required=True)
    restore.add_argument("--arch", required=True)
    restore.add_argument("--base-url", required=True)
    restore.add_argument("--dest", required=True)
    restore.add_argument("--skip-dirs", default="")

    merge = subparsers.add_parser("merge")
    merge.add_argument("--repo", default=argparse.SUPPRESS)
    merge.add_argument("--state", default="")
    merge.add_argument("--arch", required=True)
    merge.add_argument("--previous", required=True)
    merge.add_argument("--built", required=True)
    merge.add_argument("--build-dirs", default="")
    merge.add_argument("--removed-dirs", default="")
    merge.add_argument("--full", action="store_true")
    merge.add_argument("--out", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--repo", default=argparse.SUPPRESS)
    generate.add_argument("--feed", default="feed.json")
    generate.add_argument("--signed", required=True)
    generate.add_argument("--metadata", required=True)
    generate.add_argument("--previous-state", default="")
    generate.add_argument("--source-commit", required=True)
    generate.add_argument("--allow-same-version", action="store_true")
    generate.add_argument("--out", required=True)

    sign = subparsers.add_parser("sign")
    sign.add_argument("--repo", default=argparse.SUPPRESS)
    sign.add_argument("--state", required=True)
    sign.add_argument("--key", required=True)
    sign.add_argument("--out", required=True)

    verify_publish = subparsers.add_parser("verify-publish")
    verify_publish.add_argument("--repo", default=argparse.SUPPRESS)
    verify_publish.add_argument("--feed", default="feed.json")
    verify_publish.add_argument("--state", required=True)
    verify_publish.add_argument("--sig", default="")
    verify_publish.add_argument("--public", required=True)

    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        if args.command == "verify":
            return command_verify(args, repo)
        if args.command == "plan":
            return command_plan(args, repo)
        if args.command == "restore":
            return command_restore(args, repo)
        if args.command == "merge":
            return command_merge(args, repo)
        if args.command == "generate":
            return command_generate(args, repo)
        if args.command == "sign":
            return command_sign(args, repo)
        if args.command == "verify-publish":
            return command_verify_publish(args, repo)
    except feed_meta.FeedError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print("error: command failed: %s" % exc, file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
