#!/bin/sh
set -eu

base="${1:-}"
head="${2:-HEAD}"

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

fallback_all() {
	exec ./scripts/list-packages.sh
}

if [ -z "$base" ]; then
	echo "No base commit supplied; listing all packages" >&2
	fallback_all
fi

if ! git cat-file -e "$base^{commit}" 2>/dev/null; then
	echo "Base commit not found: $base; listing all packages" >&2
	fallback_all
fi

dirs="$(git diff --name-only "$base...$head" -- packages |
	awk -F/ 'NF >= 3 { print $2 }' | sort -u)"

names=""
for dir in $dirs; do
	[ -f "packages/$dir/Makefile" ] || continue

	dir_names="$(sed -n 's/^PKG_NAME:=//p' "packages/$dir/Makefile")"
	[ -n "$dir_names" ] || {
		echo "No PKG_NAME in packages/$dir/Makefile" >&2
		exit 1
	}

	names="$(printf '%s\n%s' "$names" "$dir_names")"
done

printf '%s\n' "$names" | sed '/^$/d' | sort -u
