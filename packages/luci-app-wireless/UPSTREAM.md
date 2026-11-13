# luci-app-wireless

- Source: `/home/ubuntu/workspace/openwrt/wireless/luci-app-wireless`
- Source commit: `983f7c46504fec71815a6ccf599fdd902ca38c7e`
- Project version: 0.7.12
- Upstream view: https://github.com/openwrt/luci (`openwrt-25.12`),
  `modules/luci-mod-network/htdocs/luci-static/resources/view/network/wireless.js`
- Upstream commit: `9602dd94f8c010cda442898361762d13de346c67`
- License: Apache-2.0 (see `LICENSE`)

## Feed adaptations

- Makefile: use `$(TOPDIR)/feeds/luci/luci.mk`, pin `PKG_VERSION:=0.7.12`,
  `PKG_RELEASE:=1` and `PKG_PO_VERSION`, and declare `PKG_LICENSE_FILES`.
- Menu: add the `wireless @wifi-device` UCI dependency.
- ACL: remove unused `cgi-io`, `/sbin/ifup`, `/sbin/ifdown`, `/sbin/wifi`,
  `iwinfo scan` and DHCP write grants.
- The view source is unchanged (SHA-256
  `ea59c104196fde5945800065dcc2b19ba066818dbd937ddf41009e59eeaedbe6`).
- Wi-Fi reload after Save & Apply is intentionally not handled yet; the
  package does not add an ucitrack file or depend on `luci-mod-network`.

## Packaging notes

- Pure LuCI app; no daemon, ports or log files.
- Runtime dependencies: `luci-base`, `rpcd-mod-iwinfo`.
- The view only writes `wireless` `ssid`, `encryption` and `key` through
  the LuCI form.

## Versioning note

- The previous feed package was `1.0.0-r3` and was removed. This package
  keeps the local project version `0.7.12`; devices that still have
  `1.0.0-r3` installed must remove it manually before installing this one.
