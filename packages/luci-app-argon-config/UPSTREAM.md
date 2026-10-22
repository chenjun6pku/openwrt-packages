# Upstream

- URL: https://github.com/jerrykuku/luci-theme-argon
- Ref: `v3.1.0`
- Commit: `96734f4f52e98ac70f564ca4b92644b849e189ba`
- Snapshot: 2026-10-22
- License: Apache-2.0

## Source

The `Makefile` is copied verbatim from
`compat/luci-app-argon-config/Makefile` in the same upstream commit. The
vendored theme keeps the original file as
`packages/luci-theme-argon/compat/luci-app-argon-config/Makefile.upstream`.

## Purpose

This is an empty migration package that keeps the old
`luci-app-argon-config` package name. Its `preinst` saves an existing
`/etc/config/argon` before the package releases the legacy file, and the
integrated `luci-theme-argon` package restores that backup on first start.

Fresh installations only need `luci-theme-argon`; install this package first
only when migrating from the old standalone configuration plugin.

## Local changes

None. The recipe is copied verbatim.
