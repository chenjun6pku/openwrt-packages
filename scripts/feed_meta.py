#!/usr/bin/env python3
"""Feed configuration, package discovery and asset rendering.

This is the single source of truth for feed-level values (build version,
arches, base URL, signing keys) and for package-discovery rules used by CI
and the release workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SAFE_ARCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SAFE_PACKAGE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
SAFE_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+~-]*$")
SAFE_RELEASE_CASE = re.compile(r"^[A-Za-z0-9.*?_-]+$")
SAFE_KEY_NAME = re.compile(r"^openwrt-packages[A-Za-z0-9._-]*\.pem$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class FeedError(RuntimeError):
    pass


@dataclass
class Package:
    directory: str
    name: str
    version: str
    release: str
    license: str
    build_depends: list[str]
    makefile: Path


def repo_path(value: str | Path) -> Path:
    return Path(value).resolve()


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        raise FeedError(
            "git %s failed: %s" % (" ".join(args), proc.stderr.strip() or proc.stdout.strip())
        )
    return proc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_var(text: str, name: str) -> str | None:
    lines = text.splitlines()
    pattern = re.compile(r"^\s*" + re.escape(name) + r"\s*[:?]?=\s*(.*)$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        while value.endswith("\\"):
            value = value[:-1].rstrip()
            index += 1
            if index >= len(lines):
                break
            value += " " + lines[index].strip()
        return value.strip()
    return None


def dependency_name(token: str) -> str:
    token = token.strip().lstrip("+@!")
    if ":" in token:
        token = token.split(":", 1)[1]
    return re.split(r"[<>=~]", token, 1)[0]


def parse_package(directory: Path) -> Package:
    makefile = directory / "Makefile"
    text = makefile.read_text(encoding="utf-8", errors="replace")
    pkg_name = read_var(text, "PKG_NAME")
    luci_name = read_var(text, "LUCI_NAME")
    luci_recipe = re.search(r"include\s+.*luci\.mk", text) is not None
    if pkg_name:
        name = pkg_name.split()[0]
    elif luci_recipe:
        name = (luci_name or directory.name).split()[0]
    else:
        raise FeedError(
            "No PKG_NAME or LuCI package name in %s" % makefile.relative_to(makefile.parents[2])
        )
    if not SAFE_PACKAGE.match(name):
        raise FeedError("Unsafe package name in %s: %r" % (makefile, name))
    build_depends = []
    raw_deps = read_var(text, "PKG_BUILD_DEPENDS") or ""
    for token in raw_deps.split():
        dep = dependency_name(token)
        if dep:
            build_depends.append(dep)
    version = read_var(text, "PKG_VERSION") or ""
    release = read_var(text, "PKG_RELEASE") or ""
    return Package(
        directory=directory.name,
        name=name,
        version=version.split()[0] if version else "",
        release=release.split()[0] if release else "",
        license=read_var(text, "PKG_LICENSE") or "",
        build_depends=build_depends,
        makefile=makefile,
    )


def discover_packages(repo: Path) -> list[Package]:
    packages_dir = repo / "packages"
    if not packages_dir.is_dir():
        raise FeedError("packages/ directory not found in %s" % repo)
    packages: list[Package] = []
    seen: dict[str, str] = {}
    for directory in sorted(packages_dir.iterdir(), key=lambda item: item.name):
        if not directory.is_dir() or not (directory / "Makefile").is_file():
            continue
        if not SAFE_PACKAGE.match(directory.name):
            raise FeedError("Unsafe package directory name: %r" % directory.name)
        package = parse_package(directory)
        if package.name in seen:
            raise FeedError(
                "Duplicate package name %s in %s and %s"
                % (package.name, seen[package.name], directory.name)
            )
        seen[package.name] = directory.name
        packages.append(package)
    if not packages:
        raise FeedError("No package Makefiles found under packages/")
    return packages


def package_by_directory(repo: Path) -> dict[str, Package]:
    return {package.directory: package for package in discover_packages(repo)}


def load_feed(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FeedError("feed config not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise FeedError("invalid JSON in %s: %s" % (path, exc)) from exc
    if not isinstance(data, dict):
        raise FeedError("feed config must be a JSON object")
    return data


def validate_feed(feed: dict, repo: Path) -> None:
    errors: list[str] = []
    if feed.get("schema") != 1:
        errors.append("feed.schema must be 1")
    if not isinstance(feed.get("name"), str) or not feed["name"].strip():
        errors.append("feed.name must be a non-empty string")
    base_url = feed.get("base_url")
    if not isinstance(base_url, str) or not re.match(r"^https://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~-]+)*$", base_url):
        errors.append("feed.base_url must be an https URL without query/fragment")
    build_version = feed.get("build_version")
    if not isinstance(build_version, str) or not SAFE_VERSION.match(build_version):
        errors.append("feed.build_version must be a safe version string")
    arches = feed.get("arches")
    if not isinstance(arches, list) or not arches:
        errors.append("feed.arches must be a non-empty list")
    else:
        seen_arches = set()
        for arch in arches:
            if not isinstance(arch, str) or not SAFE_ARCH.match(arch):
                errors.append("invalid arch: %r" % (arch,))
            elif arch in seen_arches:
                errors.append("duplicate arch: %s" % arch)
            seen_arches.add(arch)
    supported = feed.get("supported_releases")
    if not isinstance(supported, list) or not supported:
        errors.append("feed.supported_releases must be a non-empty list")
    else:
        for pattern in supported:
            if not isinstance(pattern, str) or not SAFE_RELEASE_CASE.match(pattern):
                errors.append("invalid supported_releases pattern: %r" % (pattern,))
    signing = feed.get("signing")
    if not isinstance(signing, dict):
        errors.append("feed.signing must be an object")
        signing = {}
    keys = signing.get("keys")
    if not isinstance(keys, list) or not keys:
        errors.append("feed.signing.keys must be a non-empty list")
        keys = []
    active_id = signing.get("active")
    active_count = 0
    names: set[str] = set()
    ids: set[str] = set()
    for key in keys:
        if not isinstance(key, dict):
            errors.append("each signing key must be an object")
            continue
        key_id = key.get("id")
        status = key.get("status")
        if not isinstance(key_id, str) or not key_id:
            errors.append("signing key id must be a non-empty string")
            continue
        if key_id in ids:
            errors.append("duplicate signing key id: %s" % key_id)
        ids.add(key_id)
        if status not in {"active", "trusted", "retired"}:
            errors.append("signing key %s has invalid status: %r" % (key_id, status))
        if status == "active":
            active_count += 1
        install_name = key.get("install_name")
        if not isinstance(install_name, str) or not SAFE_KEY_NAME.match(install_name):
            errors.append("signing key %s has invalid install_name" % key_id)
        elif install_name in names:
            errors.append("duplicate signing key install_name: %s" % install_name)
        names.add(install_name)
        if status == "retired" and "file" not in key:
            continue
        key_file = key.get("file")
        digest = key.get("sha256")
        if not isinstance(key_file, str) or not key_file:
            errors.append("signing key %s has no file" % key_id)
            continue
        path = (repo / key_file).resolve()
        try:
            path.relative_to(repo.resolve())
        except ValueError:
            errors.append("signing key %s file escapes the repository: %s" % (key_id, key_file))
            continue
        if not path.is_file():
            errors.append("signing key %s file not found: %s" % (key_id, key_file))
            continue
        data = path.read_bytes()
        if not data or len(data) > 8192:
            errors.append("signing key %s has invalid size" % key_id)
            continue
        if b"PRIVATE KEY" in data:
            errors.append("signing key %s contains private key material" % key_id)
        lines = data.decode("utf-8", errors="replace").strip().splitlines()
        if not lines or "BEGIN PUBLIC KEY" not in lines[0] or "END PUBLIC KEY" not in lines[-1]:
            errors.append("signing key %s is not a PEM public key" % key_id)
        if not isinstance(digest, str) or not HEX64.match(digest):
            errors.append("signing key %s has invalid sha256" % key_id)
        elif sha256_bytes(data) != digest:
            errors.append("signing key %s sha256 does not match feed.json" % key_id)
    if active_count != 1:
        errors.append("exactly one signing key must have status active")
    published_count = sum(1 for key in keys if key.get("status") in {"active", "trusted"})
    if published_count > 8:
        errors.append("at most 8 active/trusted signing keys may be published")
    if active_id not in ids:
        errors.append("feed.signing.active does not name a listed key")
    else:
        active_key = next((key for key in keys if key.get("id") == active_id), None)
        if active_key and active_key.get("status") != "active":
            errors.append("feed.signing.active key must have status active")
        if active_key and active_key.get("install_name") != "openwrt-packages.pem":
            errors.append("the active key must use install_name openwrt-packages.pem")
    if errors:
        raise FeedError("\n".join(errors))


def active_keys(feed: dict, repo: Path, include_trusted: bool = True) -> list[tuple[dict, Path]]:
    keys = []
    for key in feed.get("signing", {}).get("keys", []):
        status = key.get("status")
        if status == "active" or (include_trusted and status == "trusted"):
            keys.append((key, (repo / key["file"]).resolve()))
    return keys


def active_key(feed: dict, repo: Path) -> tuple[dict, Path]:
    active_id = feed.get("signing", {}).get("active")
    for key in feed.get("signing", {}).get("keys", []):
        if key.get("id") == active_id:
            return key, (repo / key["file"]).resolve()
    raise FeedError("active signing key not found")


def build_config_hash(repo: Path, feed: dict) -> str:
    parts = [
        "build_version=%s" % feed.get("build_version", ""),
        "arches=%s" % ",".join(feed.get("arches", [])),
    ]
    for relative in (
        ".github/workflows/release.yml",
        "scripts/feed_meta.py",
        "scripts/feed_state.py",
    ):
        path = repo / relative
        parts.append("%s=%s" % (relative, sha256_file(path) if path.is_file() else "missing"))
    return sha256_bytes("\n".join(parts).encode("utf-8"))


def local_build_dependency(packages: list[Package]) -> str | None:
    names = {package.name for package in packages}
    for package in packages:
        for dep in package.build_depends:
            if dep in names:
                return "%s -> %s" % (package.directory, dep)
    return None


def key_path_for(feed: dict, key: dict, repo: Path) -> Path:
    return (repo / key["file"]).resolve()


def check_private_key_match(feed: dict, repo: Path, private_key: Path) -> None:
    _, active_path = active_key(feed, repo)
    try:
        private_der = subprocess.run(
            ["openssl", "pkey", "-in", str(private_key), "-pubout", "-outform", "DER"],
            capture_output=True,
            check=True,
        ).stdout
        public_der = subprocess.run(
            ["openssl", "pkey", "-pubin", "-in", str(active_path), "-outform", "DER"],
            capture_output=True,
            check=True,
        ).stdout
    except FileNotFoundError as exc:
        raise FeedError("openssl is required to validate the private key") from exc
    except subprocess.CalledProcessError as exc:
        raise FeedError("unable to derive public key: %s" % exc.stderr.decode(errors="replace").strip()) from exc
    if sha256_bytes(private_der) != sha256_bytes(public_der):
        raise FeedError("APK_PRIVATE_KEY does not match the active public key in feed.json")


def command_names(repo: Path) -> int:
    for package in discover_packages(repo):
        print(package.name)
    return 0


def command_changed(repo: Path, base: str, head: str) -> int:
    all_names = lambda: [package.name for package in discover_packages(repo)]
    if not base:
        for name in all_names():
            print(name)
        return 0
    if git(repo, "cat-file", "-e", base + "^{commit}", check=False).returncode != 0:
        for name in all_names():
            print(name)
        return 0
    proc = git(repo, "diff", "--name-only", "-z", "%s...%s" % (base, head), "--", "packages", "vendor", check=False)
    if proc.returncode != 0:
        for name in all_names():
            print(name)
        return 0
    paths = [path for path in proc.stdout.split("\0") if path]
    if any(path == "vendor" or path.startswith("vendor/") for path in paths):
        for name in all_names():
            print(name)
        return 0
    dirs: set[str] = set()
    for path in paths:
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "packages":
            dirs.add(parts[1])
    by_dir = package_by_directory(repo)
    names = []
    for directory in sorted(dirs):
        package = by_dir.get(directory)
        if package:
            names.append(package.name)
    for name in sorted(set(names)):
        print(name)
    return 0


def command_get(repo: Path, feed_path: Path, key: str) -> int:
    feed = load_feed(feed_path)
    validate_feed(feed, repo)
    if key == "base_url":
        print(feed["base_url"].rstrip("/"))
    elif key == "build_version":
        print(feed["build_version"])
    elif key == "arches":
        print(json.dumps(feed["arches"], separators=(",", ":")))
    elif key == "supported_releases":
        print(" ".join(feed["supported_releases"]))
    elif key == "active_key_id":
        print(feed["signing"]["active"])
    elif key == "active_key_file":
        print(active_key(feed, repo)[0]["file"])
    elif key == "active_key_install_name":
        print(active_key(feed, repo)[0]["install_name"])
    elif key == "active_key_sha256":
        print(active_key(feed, repo)[0]["sha256"])
    else:
        raise FeedError("unknown config key: %s" % key)
    return 0


def command_check(repo: Path, feed_path: Path, private_key: Path | None, github_output: Path | None) -> int:
    feed = load_feed(feed_path)
    validate_feed(feed, repo)
    packages = discover_packages(repo)
    local_dep = local_build_dependency(packages)
    if local_dep:
        print(
            "WARNING: local PKG_BUILD_DEPENDS detected (%s); incremental plan will force a full build"
            % local_dep,
            file=sys.stderr,
        )
    if private_key is not None:
        check_private_key_match(feed, repo, private_key)
    if github_output is not None:
        with github_output.open("a", encoding="utf-8") as handle:
            handle.write("force_full=%s\n" % ("1" if local_dep else "0"))
            if local_dep:
                handle.write("force_full_reason=local_build_dependency:%s\n" % local_dep)
    print("feed config OK (%d packages, %d arches)" % (len(packages), len(feed["arches"])))
    return 0


def command_render(repo: Path, feed_path: Path, output: Path) -> int:
    feed = load_feed(feed_path)
    validate_feed(feed, repo)
    base_url = feed["base_url"].rstrip("/")
    build_version = feed["build_version"]
    arch_case = "|".join(feed["arches"])
    release_case = "|".join(feed["supported_releases"])
    release_text = ", ".join(
        pattern.replace(".*", ".x") for pattern in feed["supported_releases"]
    )
    arch_rows = "\n".join(
        '    <tr><td>%s</td><td><code>/%s/%s/custom/packages.adb</code></td></tr>'
        % (html.escape(arch), html.escape(build_version), html.escape(arch))
        for arch in feed["arches"]
    )
    replacements = {
        "@BASE_URL@": base_url,
        "@BUILD_VERSION@": build_version,
        "@ARCH_CASE@": arch_case,
        "@SUPPORTED_RELEASES_CASE@": release_case,
        "@SUPPORTED_RELEASES_TEXT@": release_text,
        "@ARCH_ROWS@": arch_rows,
    }
    output.mkdir(parents=True, exist_ok=True)
    for template_name, target_name, mode in (
        ("scripts/install-feed.sh.in", "install-feed.sh", 0o755),
        ("site/index.html.in", "index.html", 0o644),
    ):
        template = repo / template_name
        if not template.is_file():
            raise FeedError("template not found: %s" % template)
        text = template.read_text(encoding="utf-8")
        for marker, value in replacements.items():
            text = text.replace(marker, value)
        target = output / target_name
        target.write_text(text, encoding="utf-8")
        target.chmod(mode)
    return 0


def command_publish_keys(repo: Path, feed_path: Path, output: Path, alias: Path | None) -> int:
    feed = load_feed(feed_path)
    validate_feed(feed, repo)
    output.mkdir(parents=True, exist_ok=True)
    active_key_data, active_path = active_key(feed, repo)
    published: list[tuple[str, str]] = []
    for key in feed["signing"]["keys"]:
        status = key.get("status")
        if status not in {"active", "trusted"}:
            continue
        path = key_path_for(feed, key, repo)
        data = path.read_bytes()
        digest = sha256_bytes(data)
        if digest != key["sha256"]:
            raise FeedError("signing key %s sha256 mismatch" % key["id"])
        install_name = key["install_name"]
        (output / install_name).write_bytes(data)
        (output / install_name).chmod(0o644)
        published.append((digest, install_name))
    if not published:
        raise FeedError("no active/trusted signing keys to publish")
    published.sort(key=lambda item: item[1])
    (output / "keyring.sha256").write_text(
        "".join("%s  %s\n" % (digest, name) for digest, name in published),
        encoding="utf-8",
    )
    (output / "keyring.sha256").chmod(0o644)
    for stale in output.glob("openwrt-packages*.pem"):
        if stale.name not in {name for _, name in published}:
            stale.unlink()
    if alias is not None:
        alias.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(active_path, alias)
        alias.chmod(0o644)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    names = subparsers.add_parser("names", help="list package names")
    names.add_argument("--repo", default=argparse.SUPPRESS)

    changed = subparsers.add_parser("changed", help="list changed package names")
    changed.add_argument("--repo", default=argparse.SUPPRESS)
    changed.add_argument("--base", default="")
    changed.add_argument("--head", default="HEAD")

    get = subparsers.add_parser("get", help="read a feed config value")
    get.add_argument("--repo", default=argparse.SUPPRESS)
    get.add_argument("--feed", default="feed.json")
    get.add_argument("key")

    check = subparsers.add_parser("check", help="validate feed config and keys")
    check.add_argument("--repo", default=argparse.SUPPRESS)
    check.add_argument("--feed", default="feed.json")
    check.add_argument("--check-private-key", default=None)
    check.add_argument("--github-output", default=None)

    render = subparsers.add_parser("render", help="render installer and site")
    render.add_argument("--repo", default=argparse.SUPPRESS)
    render.add_argument("--feed", default="feed.json")
    render.add_argument("--output", required=True)

    publish_keys = subparsers.add_parser("publish-keys", help="publish keyring files")
    publish_keys.add_argument("--repo", default=argparse.SUPPRESS)
    publish_keys.add_argument("--feed", default="feed.json")
    publish_keys.add_argument("--output", required=True)
    publish_keys.add_argument("--alias", default=None)

    args = parser.parse_args(argv)
    repo = repo_path(args.repo)
    try:
        if args.command == "names":
            return command_names(repo)
        if args.command == "changed":
            return command_changed(repo, args.base, args.head)
        if args.command == "get":
            return command_get(repo, (repo / args.feed).resolve(), args.key)
        if args.command == "check":
            return command_check(
                repo,
                (repo / args.feed).resolve(),
                Path(args.check_private_key).resolve() if args.check_private_key else None,
                Path(args.github_output) if args.github_output else None,
            )
        if args.command == "render":
            return command_render(repo, (repo / args.feed).resolve(), Path(args.output).resolve())
        if args.command == "publish-keys":
            return command_publish_keys(
                repo,
                (repo / args.feed).resolve(),
                Path(args.output).resolve(),
                Path(args.alias).resolve() if args.alias else None,
            )
    except FeedError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
