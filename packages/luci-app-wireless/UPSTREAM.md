# luci-app-wireless

- Upstream: https://github.com/openwrt/luci
- Ref: `9602dd94f8c010cda442898361762d13de346c67`
- Commit date: 2026-11-08
- Snapshot: 2026-11-12
- Source: `modules/luci-mod-network/htdocs/luci-static/resources/view/network/wireless.js`
- License: Apache-2.0 (see `LICENSE` and `NOTICE`)

## Local changes

- The upstream view was imported verbatim and then trimmed for the simplified
  UI. The original upstream file remains untouched in `luci-mod-network`.
- Kept:
  - SSID overview rows (radio rows removed)
  - ESSID / Encryption / Key editing
  - Enable/disable and edit row actions
  - Associated stations table
  - Anonymous `wifi-iface` migration
  - 5 second status polling
- Removed:
  - Radio rows and radio configuration (channel, band, width, txpower, country)
  - Scan/join and Add/Remove network actions
  - Network binding, mode, BSSID, hidden SSID, WMM
  - Cipher selection and WEP keys
  - MAC filter, advanced interface options
  - Roaming (802.11r/k/v)
  - Enterprise EAP, RADIUS, PPSK, dynamic VLAN
  - QR code
- Retained UCI section/option names and ubus calls are unchanged. The edit
  form only writes `ssid`, `encryption` and `key`; the enable/disable action
  writes `disabled`. Other existing options are left untouched.
- The ESSID, Encryption and Key fields are rendered directly in the edit
  modal. The nested Interface Configuration section and its heading are
  removed; the overview GridSection maps `wifi-iface` sections directly.
- The encryption list is limited to No Encryption, WPA2-PSK, WPA3-SAE and
  WPA2/WPA3 mixed mode. WPA1/WEP/enterprise EAP/OWE are not exposed; use the
  full wireless page for those.
- The Cipher field is removed. Saving an encryption mode writes the base mode
  (for example `psk2`), so an existing `psk2+ccmp` falls back to the hostapd
  default cipher.
- Interfaces in special modes (mesh/WDS/Ad-Hoc/Monitor) remain listed and can
  have their SSID/key edited; their `mode` is not changed. Complex settings
  belong to the full wireless page.
- Chinese translations are copied from the official LuCI `zh_Hans` base
  catalog. Only the menu label "Simple Wireless" is newly translated.

## Packaging notes

- The package depends on `luci-mod-network` and reuses its
  `luci-mod-network-config` ACL and `luci-mod-network-wireless` ucitrack.
- The original `admin/network/wireless` page is not modified. The simplified
  page is installed at `admin/services/wireless` and uses the view resource
  `view/wireless.js`, so it does not collide with the original
  `view/network/wireless.js`.
