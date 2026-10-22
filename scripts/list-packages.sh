#!/bin/sh
set -eu

found=""
for dir in packages/*; do
	[ -f "$dir/Makefile" ] || continue

	names="$(sed -n 's/^PKG_NAME[[:space:]]*[?:]*=[[:space:]]*//p' "$dir/Makefile")"
	if [ -z "$names" ] && grep -q 'include.*luci\.mk' "$dir/Makefile"; then
		# Standard LuCI recipes omit PKG_NAME; luci.mk derives it from
		# LUCI_NAME, which itself defaults to the package directory name.
		names="$(sed -n 's/^LUCI_NAME[[:space:]]*[?:]*=[[:space:]]*//p' "$dir/Makefile")"
		[ -n "$names" ] || names="$(basename "$dir")"
	fi
	[ -n "$names" ] || {
		echo "No PKG_NAME or LuCI package name in $dir/Makefile" >&2
		exit 1
	}

	echo "$names"
	found=1
done

[ -n "$found" ] || {
	echo "No package Makefiles found" >&2
	exit 1
}
