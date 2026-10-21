# luci-app-edunet

- Upstream: https://github.com/chenjun6pku/luci-app-edunet
- Ref: 688cf9513fa170d377cda910d2dc7a8f7ceaca49
- Commit: 688cf9513fa170d377cda910d2dc7a8f7ceaca49
- Snapshot: 2026-10-21
- License: Apache-2.0 (declared in the upstream Makefile; the snapshot has no LICENSE file)
- Local changes:
  - added `+luci-base` to `LUCI_DEPENDS` in the package Makefile;
  - fixed the `--auth-round` option spelling in the init script;
  - added validation for cron hour/minute/weekday values and switched to
    `printf` when writing the crontab line (security hardening).

The LuCI JS view, UCI config, ACL, and menu files are otherwise unchanged
from the pinned commit.
