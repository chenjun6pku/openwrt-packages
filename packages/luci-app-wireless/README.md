# luci-app-wireless

基于 OpenWrt 25.12 的 LuCI 应用，目标是在「服务」菜单中提供一个面向新手的简化无线设置页面。

当前版本为 v0.7.12：按官方源码方式添加“无加密 (开放网络)”选项（仅 2.4/5GHz），选择后 Key 字段自动隐藏。

## 版本

- v0.7.12（2026-11-13）：按官方源码添加 `none` 加密选项，2.4/5GHz 显示“无加密 (开放网络)”。
- v0.7.11（2026-11-13）：Edit 弹窗的 Encryption 标签改为唯一 msgid `Encryption method`，中文翻译为“加密方式”。
- v0.7.10（2026-11-13）：Key 标签改为唯一 msgid `Wi-Fi password`，中文翻译为“WIFI 密码”；未添加“无加密”。
- v0.7.9（2026-11-13）：服务菜单名称改为 `Wi-Fi Quick Setup`，中文翻译为“Wi-Fi 快速设置”。
- v0.7.8（2026-11-13）：从概览网络行删除 `Mode` 字段；弹窗和功能不变。
- v0.7.7（2026-11-13）：将 ESSID 标签改为 `Wi-Fi name`，删除 `abbr` 悬浮提示，中文翻译为“Wi-Fi 名称”。
- v0.7.6（2026-11-13）：新增 `po/zh_Hans/wireless.po`，中文界面 ESSID 翻译为“Wi-Fi 名称”；JS 未改动。
- v0.7.5（2026-11-13）：修复 Edit 弹窗标题中 SSID 的存储型 XSS 风险，正常标题和表单不变。
- v0.7.4（2026-11-13）：Edit 弹窗标题改为动态的 `Edit "SSID"`，其余字段和绑定不变。
- v0.7.3（2026-11-13）：去掉 Interface Configuration 标题和 General Setup 单标签。
- v0.7.2（2026-11-13）：Encryption 收敛为 WPA2-PSK 与 WPA2-PSK/WPA3-SAE Mixed Mode。
- v0.7.1（2026-11-13）：将 ESSID、Encryption、Key 合并到 General Setup 单标签页。
- v0.7.0（2026-11-13）：删除 SAE-EXT-KEY、Transition Disable、WPS、WEP、OWE、No Encryption、纯 WPA-PSK。
- v0.6.0（2026-11-13）：删除 EAP/RADIUS/VLAN/DAE、gcmp256 及 EAP 加密选项。
- v0.5.0（2026-11-13）：删除 Cipher、QR Code、PPSK、802.11w、KRACK 相关代码。
- v0.4.1（2026-11-13）：删除 Mesh Id、BSSID、Hide ESSID 及依赖代码。
- v0.4.0（2026-11-13）：删除 General Setup 的 Mode、Network、WMM Mode 及相关 mode 依赖。
- v0.3.0（2026-11-13）：删除 Device Configuration、MAC-Filter、Advanced Settings、WLAN roaming。
- v0.2.1（2026-11-13）：移除网络行的 Remove 按钮及相关代码。
- v0.2.0（2026-11-13）：移除 radio 行及 Restart/Scan/Add 相关代码。
- v0.1.0（2026-11-13）：标准结构与官方 `wireless.js` 原样引入。

## 来源与校验

- 源码仓库：<https://github.com/openwrt/luci>
- 分支：`openwrt-25.12`
- 文件：`modules/luci-mod-network/htdocs/luci-static/resources/view/network/wireless.js`
- v0.1.0：与官方源码逐字节一致，SHA-256 `6385cebb2b415257d05def51e890620d7e6b9f8b14071a374ed9dc2ed392c45f`。
- v0.2.0：在 v0.1.0 基础上删除 radio 行及 Restart/Scan/Add 相关代码，SHA-256 `ac2e4a1f7710cd5e278b9dbbe0b77cf621e4a63e767b0f50f552563803811410`。
- v0.2.1：在 v0.2.0 基础上删除网络行的 Remove 按钮及 `handleRemove` 等代码，SHA-256 `d544f6c65761f0c7eaad3d94a1c52c55cb90d0493c725b4ebcf36972fd507e47`。
- v0.3.0：删除 Device Configuration、MAC-Filter、Advanced Settings、WLAN roaming 相关代码，SHA-256 `96ef4b7a1100895b737349a253794f8f8096021db5422a45dd92996f1a211325`。
- v0.4.0：删除 General Setup 的 Mode、Network、WMM Mode 及相关 mode 依赖，SHA-256 `dc4ea8660c499567699a19ceae3087bcc2d17559ad0a2adbd08acdc7b0f28871`。
- v0.4.1：删除 Mesh Id、BSSID、Hide ESSID 及依赖代码，SHA-256 `8d3e894489e92d9e2cbe01a85750da408bab4fa44646a78dae36406a38b5c7cd`。
- v0.5.0：删除 Cipher、QR Code、PPSK、802.11w、KRACK 相关代码，SHA-256 `5a93e1e59f7a8a387240c8583fae9cdf994f113c642cfa3b161f13db714b06b3`。
- v0.6.0：删除 EAP/RADIUS/VLAN/DAE、gcmp256 及 EAP 加密选项，SHA-256 `63ded84d4dc5fc83a5c2f5aa8edc6a46cb9003c6b388ea8881b76ab179f514f1`。
- v0.7.0：删除 SAE-EXT-KEY、Transition Disable、WPS、WEP、OWE、No Encryption、纯 WPA-PSK，SHA-256 `b64e157b1f46326c03298a2174992ca098a8fe53a0d58156ed593ae98de06e7b`。
- v0.7.1：将 ESSID、Encryption、Key 合并到 General Setup 单标签页，SHA-256 `966de3ef4bb635eefbdf935ff4542fc6a6a1d99b8967e9506a578547962d705f`。
- v0.7.2：Encryption 收敛为 WPA2-PSK 与 WPA2-PSK/WPA3-SAE Mixed Mode，SHA-256 `8dc0aebddfe0199de05ed2f1fbc05613280002d13d5e3953cc558e8900244362`。
- v0.7.3：去掉 Interface Configuration 标题和 General Setup 单标签，SHA-256 `0c336064cdaae975e2603356b9574d01707512f42901f86a368be33a08dd7483`。
- v0.7.4：Edit 弹窗标题改为动态的 `Edit "SSID"`，SHA-256 `76392327d827f5345cdc35724f18e65888a04641ffcb6e29c473dbdaf9ab3ae9`。
- v0.7.5：修复标题 SSID 的存储型 XSS 风险，SHA-256 `1f4498804843d68091b54023532c68bc023928e13d09ed6b8c5052714e74427a`。
- v0.7.6：新增中文翻译，JS 未改动，SHA-256 `1f4498804843d68091b54023532c68bc023928e13d09ed6b8c5052714e74427a`。
- v0.7.7：ESSID 标签改为 `Wi-Fi name`，删除 `abbr`，SHA-256 `b2ac5fa9db47c4d9819258702f31bae8ef84918586b4839d701275ce00db14ab`。
- v0.7.8：概览行隐藏 `Mode`，SHA-256 `1e71ecdc12e9c2fc01da9ec9116c39866afaf9c5a639e1c1c65ed3f2b0732201`。
- v0.7.9：菜单名称改为 `Wi-Fi Quick Setup`，JS 未改动，SHA-256 `1e71ecdc12e9c2fc01da9ec9116c39866afaf9c5a639e1c1c65ed3f2b0732201`；菜单 JSON SHA-256 `6c797cb770a60601314b520a288b420cf4f0f785c1ceb42ab5be85b92871c263`。
- v0.7.10：Key 标签改为 `Wi-Fi password`，SHA-256 `566fd4943b10f9c303ae1b3135f1acb3716a4756b4eb28783d8035b1d9e0c90f`。
- v0.7.11：Encryption 字段标签改为 `Encryption method`，SHA-256 `525c654aa4fef8f7a68203c0296c9214422c7dac71c82a1ee69733bc6c0c9b68`。
- v0.7.12：添加“无加密 (开放网络)”选项，当前文件 SHA-256 `ea59c104196fde5945800065dcc2b19ba066818dbd937ddf41009e59eeaedbe6`。

## 页面

- 菜单路径：`/luci/admin/services/wireless`
- 安装后视图文件：`/www/luci-static/resources/view/wireless/wireless.js`

## 目录结构

```
luci-app-wireless/
├── Makefile
├── README.md
├── LICENSE
├── htdocs/luci-static/resources/view/wireless/wireless.js
├── po/
│   ├── templates/wireless.pot
│   └── zh_Hans/wireless.po
└── root/usr/share/
    ├── luci/menu.d/luci-app-wireless.json
    └── rpcd/acl.d/luci-app-wireless.json
```

## 依赖

- `luci-base`：view/ui/form/rpc/uci/network/firewall 等基础 JS 模块
- `rpcd-mod-iwinfo`：iwinfo ubus 接口

## 国际化

- v0.7.7 将页面字段标签简化为 `_('Wi-Fi name')`，不再使用 `<abbr>` 悬浮提示：
  - 英文界面：`Wi-Fi name`
  - 中文界面：`Wi-Fi 名称`
- v0.7.9 将服务菜单标题改为 `Wi-Fi Quick Setup`：
  - 英文界面：`Wi-Fi Quick Setup`
  - 中文界面：`Wi-Fi 快速设置`
- `po/zh_Hans/wireless.po` 中的翻译键与源码/菜单 JSON 完全一致：
  - `msgid`: `Wi-Fi name` → `msgstr`: `Wi-Fi 名称`
  - `msgid`: `Wi-Fi Quick Setup` → `msgstr`: `Wi-Fi 快速设置`
  - `msgid`: `Encryption method` → `msgstr`: `加密方式`
  - `msgid`: `Wi-Fi password` → `msgstr`: `WIFI 密码`
- `po/templates/wireless.pot` 是翻译模板，供后续增加其他语言使用。
- 按标准 LuCI 构建时，`luci.mk` 会把 `po/zh_Hans` 映射为 OpenWrt 的 `zh-cn`，生成 `luci-i18n-wireless-zh-cn` 包，安装为 `/usr/lib/lua/luci/i18n/wireless.zh-cn.lmo`。
- 当前 `luci.main.lang=auto`，浏览器中文环境显示中文；实测弹窗字段为 `Wi-Fi 名称`、`加密方式`、`WIFI 密码`，菜单为 `Wi-Fi 快速设置`。
- v0.7.12 的“无加密 (开放网络)”使用 LuCI 基础中文目录中的 `No Encryption`、`open network` 翻译，没有新增 po 条目。
- 为验证中文界面，已在真机上安装一个由该 po 生成的 124 字节测试 lmo（包含四个翻译条目），并保留在路由器中。正式打包时应由 `luci.mk` 生成并安装翻译包，仓库中不保存 `.lmo` 二进制。

## 说明

- v0.2.1 仅保留 wifi-iface 网络行，以及 Enable/Disable、Edit 操作；Remove 已删除。Associated Stations 与 Save & Apply 保留。
- 已删除每个网络行的 Remove 按钮、`handleRemove` 方法及 `form.TypedSection.prototype.handleRemove` 调用；`poll_status` 同步改为两个按钮。
- 已删除 radio 硬件行及其 Restart/Scan/Add 按钮，并删除 `render_radio_badge`、`render_radio_status`、`radio_restart`、`handleScan*`、`handleJoin*`、`handleAdd` 等 radio 行专用代码。
- v0.3.0 的 Edit 弹窗仅保留 Interface Configuration 的 General Setup 与 Wireless Security 两个标签。
- 已删除 Device Configuration 整个标签页（radio 状态/开关、频率、功率、国家、legacy rates、cell density、distance、frag、rts、noscan、beacon、LDPC 等），以及 `CBIWifiFrequencyValue`、`CBIWifiTxPowerValue`、`CBIWifiCountryValue` 三个专用类。
- 已删除 Interface Configuration 的 MAC-Filter 标签、Advanced Settings 标签、WLAN roaming 标签及全部相关选项（802.11r/11k/11v）。
- `eht_compat_default` 不再读取已删除的 `_freq` 选项，仅从 UCI 读取 htmode。
- v0.4.0 删除了 General Setup 中的 Mode、Network、WMM Mode，并移除了所有依赖 Mode 的可见性/校验逻辑。
- Mode 下拉、WDS/ahdemo/monitor/mesh 值、write/cfgvalue、mesh 安装链接和 `have_mesh` 已删除；Network 选择器及其 write 逻辑已删除；WMM Mode 复选框已删除。
- 删除 16 处直接 `depends('mode', ...)` 及 56 处 `add_dependency_permutations` 中的 `mode` 键；删除按 mode 校验加密的 `crypto_support`/`encr.validate` 及 OCV 的 mode 校验。
- v0.4.0 时 General Setup 显示 Mesh Id、ESSID、BSSID、Hide ESSID；v0.4.1 已删除 Mesh Id、BSSID、Hide ESSID，仅保留 ESSID。
- v0.4.1 删除了二维码生成中的 `wifiHide` 变量及 H 字段输出，并删除了概览状态和关联终端状态中的 BSSID 显示。
- 内部 `bssid` 变量仍用于 `is_assoc` 关联状态判断，不再显示；二维码规范注释中的 hidden 字样和 CSS 的 `.hidden` 类与已删除的表单字段无关。
- v0.5.0 删除了 Cipher 下拉及其 cipher 拼接逻辑、整个 QR Code 区块、PPSK 选项及 9 处 PPSK 专用 PSK 依赖、802.11w/OCV、KRACK countermeasures。
- 删除 QR Code 后不再使用 `uqr`，`luci-lib-uqr` 依赖也已从 Makefile 移除。
- v0.7.1 删除了 Wireless Security 标签，将 Encryption 与 Key 移到 General Setup，与 ESSID 显示在同一个标签页。
- ESSID、Encryption、Key 都是 `/etc/config/wireless` 中同一个 `wifi-iface` section 的选项（`ssid`、`encryption`、`key`）；合并标签页只是 UI 调整，不改变配置文件。
- v0.6.0 删除了 EAP-Method、证书、身份/密码等 EAP 字段，RADIUS 认证/计费/属性、动态 VLAN、Per-STA VLAN、VLAN Naming/Tagged/Bridge、DAE、RSN Preauth 全部代码。
- v0.6.0 删除了 `gcmp256`，并移除了 Encryption 下拉中的 WPA/WPA2/WPA3-EAP 选项，避免出现没有配置项的空壳加密选项。
- v0.6.0 还删除了不再使用的 EAP 特性探测变量及 `tools.widgets` 引用。ESSID、Encryption、Key 与这些被删代码没有反向依赖。
- v0.7.0 删除了 SAE-EXT-KEY、Transition Disable、WPS pushbutton。
- v0.7.0 删除了 WEP 加密选项、密钥槽、WEP 特性探测、key1–key4 清理逻辑及 WEP 的 cfgvalue 分支。
- v0.7.0 删除了 OWE、No Encryption 和纯 WPA-PSK，并删除了不再使用的 `eht_compat_default`。
- v0.7.2 删除了 WPA3-SAE（2.4/5GHz）、WPA2-PSK/WPA3-SAE Compatibility Mode、WPA-PSK/WPA2-PSK Mixed Mode，以及对应的 `psk-mixed`、`psk+psk2`、`sae-compat` 加密候选和 Key 依赖。
- 2.4/5GHz 的 Encryption 现在只有 WPA2-PSK 与 WPA2-PSK/WPA3-SAE Mixed Mode；6GHz 射频仍保留 WPA3-SAE 作为必要选项（6GHz 不允许 WPA2）。
- v0.7.3 将 SectionValue 标题设为空，移除 General Setup 单标签，并将三个选项从 `taboption('general', ...)` 改为 `option(...)`。
- v0.7.3 时弹窗只有动态网络标题和 ESSID、Encryption、Key 三个字段；字段仍绑定在 `wireless.default_radio0`/`default_radio1` 等 `wifi-iface` section，UCI 配置不变。v0.7.7 仅把 ESSID 标签改为 `Wi-Fi name`/`Wi-Fi 名称`。
- v0.7.4 仅修改 `s.modaltitle`：标题从完整的 `Wireless Network: <mode> "<SSID>" (<ifname>)` 改为 `Edit "<SSID>"`，不再显示模式和接口名。
- 标题中的 SSID 动态取自 `getActiveSSID() || getSSID()`；找不到对应网络或 SSID 时回退到原有的 `Edit wireless network` 文案。
- 标题复用现有的 `Edit` 翻译词条（`_('Edit')`），会跟随 LuCI 界面语言；v0.7.4 验证时 `luci.main.lang=en`，实测显示 `Edit "CUCC_2.4G"` 和 `Edit "CUCC_5G"`。
- 这次没有改动表单字段、UCI 绑定、加密选项或保存逻辑；浏览器实测两个网络仍绑定到各自的 `ssid`、`encryption`、`_wpa_key`，无标签页、无 JS 异常。
- v0.7.5 修复标题的存储型 XSS 风险：LuCI 的 `titleFn()` 会先调用 `stripTags()`，随后 `ui.showModal()` 通过 `innerHTML` 插入标题；如果 SSID 含 HTML 实体（例如 `&lt;img ...&gt;`），单次转义会在两次解析后还原成标签。
- 现在对 SSID 连续执行两次 `%h` HTML 转义，使两次解析后仍只生成文本；普通 SSID（如 `CUCC_2.4G`）显示完全不变，含 `&`、`<`、`>`、引号等字符的 SSID 也会按原文显示。
- 无头浏览器验证：未转义路径会生成 `<img>` 子元素并触发事件；使用 `%h` 二次转义后没有子元素，事件未触发；实际弹窗标题仍为 `Edit "CUCC_2.4G"`，字段和加密选项不变。
- v0.7.6 仅在无头浏览器中把翻译键临时注入 `window.TR` 验证渲染，弹窗字段标签变为 `Wi-Fi 名称`、`Encryption`、`Key`，标题仍为 `Edit "CUCC_2.4G"`，字段绑定和加密选项不变，无 JS 异常；当时没有在路由器上安装 `.lmo` 或修改语言设置。
- v0.7.7 将标签从 `ESSID`/`abbr` 改为 `Wi-Fi name`，并在中文环境 `luci.main.lang=zh_cn` 下安装了由 po 生成的测试 lmo；实测弹窗字段标签为 `Wi-Fi 名称`、`加密`、`密钥`，标题为 `编辑 "CUCC_2.4G"`，没有 `abbr`、没有标签页，字段绑定和加密候选不变，无 JS 异常。
- v0.7.8 仅从 `render_network_status()` 的概览行删除 `_('Mode'), mode`；`mode` 变量仍用于 `is_assoc` 判断，`render_modal_status()` 和其他功能未改动。
- v0.7.9 仅修改菜单标题 `menu.d` 和 po/pot，`wireless.js`、菜单路径 `/luci/admin/services/wireless`、包名 `luci-app-wireless` 均未变化。
- v0.7.10 仅将 `_wpa_key` 字段的标签从通用 `_('Key')` 改为唯一 `_('Wi-Fi password')`，避免影响其他页面的 `Key` 翻译；未修改字段名、UCI 选项、加密候选或保存逻辑，也未添加“无加密”选项。
- v0.7.11 仅将 Edit 弹窗的 Encryption 标签从通用 `_('Encryption')` 改为唯一 `_('Encryption method')`；概览行和 `render_modal_status()` 中的简短“加密”状态标签仍使用 `_('Encryption')`，未改动。
- v0.7.12 按官方源码在 `crypto_modes.sort()` 前增加 `if (!is_6ghz) crypto_modes.push(['none', _('No Encryption'), 0]);`；没有添加 Key 清理或特殊标签分支，选择 `none` 后 Key 字段由现有依赖自动隐藏。
- 官方 `admin/network/wireless` 页面带有 `@wifi-device` 的 UCI 菜单依赖；当前菜单只依赖 ACL，没有添加该 UCI 依赖。在无无线配置的系统上页面仍会报 `uci/get` 错误，属于已知问题。
- ACL 取自官方 `luci-mod-network-config` 组，并补充了官方 `luci-base-network-status` 组中的网络状态读取权限；scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。
- 已在 OpenWrt 25.12.6 真机（192.168.1.1）验证 v0.7.12（中文界面）：服务菜单显示 `Wi-Fi 快速设置`，链接仍为 `/cgi-bin/luci/admin/services/wireless`；两个概览网络行均不显示 `Mode`/`Master`，状态行仍显示简短的“加密”；`default_radio0` 当前禁用，显示 SSID 和“无线已禁用”，`default_radio1` 显示 SSID 和加密信息；Edit 弹窗标题为 `编辑 "CUCC_2.4G"`，字段为 `Wi-Fi 名称`、`加密方式`、`WIFI 密码`，没有标题分组和标签页；字段仍绑定到 `wireless.default_radio0.ssid`、`.encryption`、`._wpa_key`；Encryption 候选为 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode 和“无加密 (开放网络)”；选择 `none` 后 Key 字段自动隐藏；浏览器控制台无异常；本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署，不是本次测试写入的。
