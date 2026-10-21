#!/bin/sh
set -eu

found=""
for dir in packages/*; do
	[ -f "$dir/Makefile" ] || continue

	names="$(sed -n 's/^PKG_NAME:=//p' "$dir/Makefile")"
	[ -n "$names" ] || {
		echo "No PKG_NAME in $dir/Makefile" >&2
		exit 1
	}

	echo "$names"
	found=1
done

[ -n "$found" ] || {
	echo "No package Makefiles found" >&2
	exit 1
}
