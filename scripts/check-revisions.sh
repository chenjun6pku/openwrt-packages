#!/bin/sh
set -eu

# Warn when package content changed since the last release tag but PKG_RELEASE
# was not bumped. This is a guardrail, not a hard failure: README-only changes
# are ignored.

base="${1:-}"
if [ -z "$base" ]; then
	base="$(git describe --tags --abbrev=0 2>/dev/null || true)"
fi

if [ -z "$base" ]; then
	echo "No base tag found; skipping revision check."
	exit 0
fi

changed="$(git diff --name-only "$base"...HEAD -- packages luci themes |
	awk -F/ 'NF >= 2 { print $1 "/" $2 }' | sort -u)"

[ -n "$changed" ] || {
	echo "No package changes since $base."
	exit 0
}

status=0
for pkg in $changed; do
	[ -f "$pkg/Makefile" ] || continue

	# Ignore changes that cannot affect the built package.
	if ! git diff --name-only "$base"...HEAD -- "$pkg" |
		grep -qE "^$pkg/(src|patches|files|htdocs|root|po|ucode|Makefile)(/|$)"; then
		continue
	fi

	old="$(git show "$base:$pkg/Makefile" 2>/dev/null |
		sed -n 's/^PKG_RELEASE:=//p' | head -n 1)"
	new="$(sed -n 's/^PKG_RELEASE:=//p' "$pkg/Makefile" | head -n 1)"

	if [ "$old" = "$new" ]; then
		echo "WARNING: $pkg changed but PKG_RELEASE is still $new" >&2
		status=1
	fi
done

exit "$status"
