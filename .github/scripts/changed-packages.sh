#!/bin/sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
exec python3 "$repo_root/scripts/feed_meta.py" --repo "$repo_root" changed \
	--base "${1:-}" --head "${2:-HEAD}"
