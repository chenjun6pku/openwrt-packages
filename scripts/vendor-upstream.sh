#!/bin/sh
set -eu

usage() {
	cat <<'EOF'
Usage: vendor-upstream.sh <git-url> <ref> <dest-dir> [subdir]

Snapshot an upstream git repository into dest-dir, remove VCS metadata,
and record the origin in UPSTREAM.md.

  git-url   https://github.com/owner/project.git
  ref       branch, tag, or commit
  dest-dir  destination directory (must be empty or absent)
  subdir    optional subdirectory to snapshot instead of the whole repo

Nested OpenWrt Makefiles (containing "call BuildPackage") are renamed to
Makefile.upstream so the OpenWrt feed scanner does not index them twice.
The top-level Makefile in dest-dir is left untouched: when vendoring a LuCI
app or theme, that Makefile is intentionally the package recipe.
EOF
}

[ $# -ge 3 ] || {
	usage
	exit 1
}

url="$1"
ref="$2"
dest="$3"
subdir="${4:-}"

if [ -e "$dest" ] && [ -n "$(ls -A "$dest" 2>/dev/null)" ]; then
	echo "Destination is not empty: $dest" >&2
	exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git init -q "$tmp/repo"
git -C "$tmp/repo" remote add origin "$url"
git -C "$tmp/repo" fetch --depth 1 origin "$ref"
git -C "$tmp/repo" checkout -q --detach FETCH_HEAD

commit="$(git -C "$tmp/repo" rev-parse HEAD)"
src="$tmp/repo"
if [ -n "$subdir" ]; then
	src="$tmp/repo/$subdir"
	[ -d "$src" ] || {
		echo "No such subdirectory: $subdir" >&2
		exit 1
	}
fi

mkdir -p "$dest"
tar -C "$src" --exclude=.git --exclude=.github -cf - . | tar -C "$dest" -xf -

find "$dest" -type f -name Makefile ! -path "$dest/Makefile" \
	-exec grep -l 'call BuildPackage' {} \; |
while IFS= read -r f; do
	mv "$f" "$f.upstream"
	echo "Renamed nested OpenWrt Makefile: ${f#"$dest"/} -> ${f#"$dest"/}.upstream"
done

if [ -f "$dest/Makefile" ] && grep -q 'call BuildPackage' "$dest/Makefile"; then
	echo "NOTE: $dest/Makefile is an OpenWrt package Makefile and was kept." >&2
	echo "      When vendoring into src/, rename it to Makefile.upstream to avoid" >&2
	echo "      the feed scanner indexing it as a second package." >&2
fi

{
	echo "Upstream: $url"
	echo "Ref: $ref"
	echo "Commit: $commit"
	echo "Snapshot: $(date -u +%Y-%m-%d)"
	[ -n "$subdir" ] && echo "Subdirectory: $subdir"
	echo "License: TODO"
	echo "Local changes: TODO"
} > "$dest/UPSTREAM.md"

echo "Vendored $url @ $commit into $dest"
