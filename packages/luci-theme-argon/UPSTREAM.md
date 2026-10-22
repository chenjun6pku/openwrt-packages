# Upstream

- URL: https://github.com/jerrykuku/luci-theme-argon
- Ref: `v3.1.0`
- Commit: `96734f4f52e98ac70f564ca4b92644b849e189ba`
- Snapshot: 2026-10-22
- License: Apache-2.0 (repository `LICENSE`); the package Makefile also
  declares MIT for bundled assets (`PKG_LICENSE:=Apache-2.0 MIT`).

## Local changes

- No source changes.
- `compat/luci-app-argon-config/Makefile` was renamed to
  `compat/luci-app-argon-config/Makefile.upstream` by
  `scripts/vendor-upstream.sh`, so the OpenWrt feed scanner does not index the
  nested recipe twice. The same recipe is published separately as
  `packages/luci-app-argon-config/`.
- The upstream `.github/` directory is excluded by the vendor script.

## Notes

The theme bundles the former standalone `luci-app-argon-config` settings app.
Fresh installations only need `luci-theme-argon`; the separate
`luci-app-argon-config` package is an empty migration package for installations
that still have the old standalone plugin.

Upstream publishes APK assets built with the 25.12.5 SDK. This feed builds the
same source with the 25.12.6 SDK and targets all OpenWrt 25.x devices.
