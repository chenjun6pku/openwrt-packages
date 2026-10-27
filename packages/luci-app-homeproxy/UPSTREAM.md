# Upstream

- URL: https://github.com/immortalwrt/homeproxy
- Ref: `master`
- Commit: `fadaa676104f59ff6ace480a780a258d846d0aec`
- Snapshot: 2026-10-27
- License: GPL-2.0-only (see `LICENSE`)

## Local changes

- No source code changes.
- Added explicit package metadata to `Makefile`: `PKG_VERSION`,
  `PKG_RELEASE`, `PKG_PO_VERSION`, `PKG_LICENSE` and `PKG_LICENSE_FILES`.
  `PKG_RELEASE` is `2` because the package was removed from the feed and then
  re-added; this makes the re-introduction visible as an upgrade.
- Upstream `.github/` is excluded by `scripts/vendor-upstream.sh`.
- `UPSTREAM.md` is added by the vendor process.

## Packaging notes

- `LUCI_DEPENDS` is unchanged from upstream. No runtime dependency additions
  were made.
- `kmod-nft-tproxy` remains a runtime dependency. This feed does not build
  kernel modules; the dependency must be provided by the device's official
  target feed.
- No security hardening changes were applied.
- This snapshot is validated by the feed release CI after re-integration.
