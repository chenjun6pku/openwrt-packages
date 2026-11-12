# luci-app-wireless

- Upstream: https://github.com/openwrt/luci
- Ref: `9602dd94f8c010cda442898361762d13de346c67`
- Commit date: 2026-11-08
- Snapshot: 2026-11-12
- Source: `modules/luci-mod-network/htdocs/luci-static/resources/view/network/wireless.js`
- License: Apache-2.0 (see `LICENSE` and `NOTICE`)

## Local changes

- The upstream view is imported verbatim as
  `htdocs/luci-static/resources/view/wireless.js`. The destination path
  differs from upstream because the package uses its own menu entry under
  `admin/services/wireless`.
- No content changes in this snapshot commit. The simplified trim and
  package scaffolding follow in a separate commit.

## Packaging notes

- The package depends on `luci-mod-network` and reuses its
  `luci-mod-network-config` ACL and `luci-mod-network-wireless` ucitrack.
- The original `admin/network/wireless` page is not modified.
