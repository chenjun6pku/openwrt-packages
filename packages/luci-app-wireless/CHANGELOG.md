# Changelog

## v0.7.12（2026-11-13）

### 变更

- 按官方源码方式在 `crypto_modes.sort()` 前增加：
  ```js
  if (!is_6ghz)
      crypto_modes.push(['none',       _('No Encryption'),   0]);
  ```
- 2.4/5GHz 的 Encryption 选项增加 `none`，显示为“无加密 (开放网络)”。
- 6GHz 不添加该选项。
- 未添加 Key 清理、特殊标签分支或其他修改。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1），中文界面：
  - Encryption 下拉包含 `无加密 (开放网络)`
  - 选项值为 `none`
  - 选择 `none` 后 Key 字段自动隐藏
  - 其他两个选项仍为 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 字段绑定和标题不变
  - 浏览器控制台无 JS 异常
- “无加密 (开放网络)”使用 LuCI 基础中文目录中的 `No Encryption`、`open network` 翻译，没有新增 po 条目。
- 修改后文件：668 行，20372 字节，SHA-256 `ea59c104196fde5945800065dcc2b19ba066818dbd937ddf41009e59eeaedbe6`。
- 中文测试 lmo 仍为 124 字节，未变化。
- 本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署，不是本次测试写入的。

### 说明

- 未按“仅显示无加密”做特殊文案处理，保留官方源码生成的“无加密 (开放网络)”。
- 未在切换到 `none` 时清除旧 `key`；开放网络不会使用旧 key，功能不受影响。

## v0.7.11（2026-11-13）

### 变更

- 将 Edit 弹窗的 Encryption 字段标签从通用 `_('Encryption')` 改为唯一 msgid `_('Encryption method')`。
- 在 `po/zh_Hans/wireless.po` 和 `po/templates/wireless.pot` 增加：
  - `msgid`: `Encryption method`
  - `msgstr`: `加密方式`
- 概览行和 `render_modal_status()` 中的简短状态标签仍使用 `_('Encryption')`，本次未改动。
- 未修改字段 ID、UCI 选项、加密候选、保存逻辑或其他功能。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1），`luci.main.lang=auto`，浏览器中文界面：
  - 菜单显示 `Wi-Fi 快速设置`
  - Edit 弹窗标题为 `编辑 "CUCC_2.4G"`
  - 字段标签为 `Wi-Fi 名称`、`加密方式`、`WIFI 密码`
  - 字段仍绑定到 `wireless.default_radio0.ssid`、`.encryption`、`._wpa_key`
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 概览行仍显示简短的“加密”状态
  - 浏览器控制台无 JS 异常
- 修改后文件：665 行，20288 字节，SHA-256 `525c654aa4fef8f7a68203c0296c9214422c7dac71c82a1ee69733bc6c0c9b68`。
- 中文测试 lmo 更新为 124 字节，包含菜单、Wi-Fi 名称、加密方式、WIFI 密码四个翻译条目。
- 本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署，不是本次测试写入的。

### 说明

- 使用唯一 msgid 后，`Encryption` 的全局翻译不会影响其他 LuCI 页面。
- 本次只改 Edit 弹窗字段标签；概览状态仍保留较短的“加密”。

## v0.7.10（2026-11-13）

### 变更

- 将 `_wpa_key` 字段的标签从通用 `_('Key')` 改为唯一 msgid `_('Wi-Fi password')`。
- 在 `po/zh_Hans/wireless.po` 和 `po/templates/wireless.pot` 增加：
  - `msgid`: `Wi-Fi password`
  - `msgstr`: `WIFI 密码`
- 未修改字段 ID、UCI 选项、加密候选、保存逻辑或其他功能。
- 本次未添加“无加密”选项。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1），`luci.main.lang=auto`，浏览器中文界面：
  - 菜单显示 `Wi-Fi 快速设置`
  - Edit 弹窗标题为 `编辑 "CUCC_2.4G"`
  - 字段标签为 `Wi-Fi 名称`、`加密`、`WIFI 密码`
  - 字段仍绑定到 `wireless.default_radio0.ssid`、`.encryption`、`._wpa_key`
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 没有“无加密”选项
  - 浏览器控制台无 JS 异常
- 修改后文件：665 行，20281 字节，SHA-256 `566fd4943b10f9c303ae1b3135f1acb3716a4756b4eb28783d8035b1d9e0c90f`。
- 中文测试 lmo 更新为 96 字节，包含菜单、Wi-Fi 名称、WIFI 密码三个翻译条目。
- 本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署，不是本次测试写入的。

### 说明

- 使用唯一 msgid 后，`Key` 的全局翻译不会影响其他 LuCI 页面。
- 中文按需求使用大写 `WIFI 密码`；未改为 `Wi-Fi 密码` 以保持与本次指定文案一致。

## v0.7.9（2026-11-13）

### 变更

- 将服务菜单标题从 `Wireless` 改为 `Wi-Fi Quick Setup`。
- 在 `po/zh_Hans/wireless.po` 和 `po/templates/wireless.pot` 增加菜单翻译：
  - `msgid`: `Wi-Fi Quick Setup`
  - `msgstr`: `Wi-Fi 快速设置`
- 菜单路径 `/luci/admin/services/wireless`、包名 `luci-app-wireless` 和 `wireless.js` 均未变化。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1），当前英文界面：
  - 服务菜单显示 `Wi-Fi Quick Setup`
  - 菜单链接仍为 `/cgi-bin/luci/admin/services/wireless`
  - 通过 `/admin/translations/zh-cn` 验证 `Wi-Fi Quick Setup` 对应 `Wi-Fi 快速设置`
  - 概览行仍不显示 `Mode`/`Master`
  - Edit 弹窗标题、字段和绑定保持 v0.7.8 的状态
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 菜单 JSON：13 行，206 字节，SHA-256 `6c797cb770a60601314b520a288b420cf4f0f785c1ceb42ab5be85b92871c263`。
- `wireless.js` 未变化：665 行，20270 字节，SHA-256 `1e71ecdc12e9c2fc01da9ec9116c39866afaf9c5a639e1c1c65ed3f2b0732201`。
- 中文测试 lmo 更新为 68 字节，包含菜单和字段两个翻译条目。
- 本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署，不是本次测试写入的。

### 说明

- 英文界面使用 `Wi-Fi Quick Setup`，中文界面使用 `Wi-Fi 快速设置`。
- 该名称比“无线”更直观，也不会和系统原生的“网络 → 无线”同名。

## v0.7.8（2026-11-13）

### 变更

- 从 `render_network_status()` 的概览网络行删除 `_('Mode'), mode`，不再显示 `Mode: Master`。
- `mode` 变量仍用于 `is_assoc` 判断，未删除相关逻辑。
- `render_modal_status()` 中的 Mode 信息未改动；本次只影响概览行。
- 未改动表单字段、UCI 绑定、加密选项、保存逻辑或其他功能。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1），当前英文界面：
  - 两个概览网络行均不显示 `Mode`/`Master`
  - `default_radio0` 当前禁用，显示 SSID 和 `Wireless is disabled`
  - `default_radio1` 显示 SSID 和 Encryption
  - Edit 弹窗标题为 `Edit "CUCC_2.4G"`
  - 字段标签为 `Wi-Fi name`、`Encryption`、`Key`
  - 没有标题分组、没有标签页
  - 字段仍绑定到 `wireless.default_radio0.ssid`、`.encryption`、`._wpa_key`
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 修改后文件：665 行，20270 字节，SHA-256 `1e71ecdc12e9c2fc01da9ec9116c39866afaf9c5a639e1c1c65ed3f2b0732201`。
- 相对 v0.7.7：1 行删除。
- 本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署，不是本次测试写入的。

### 说明

- 概览行现在只保留 SSID、加密状态和接口状态，减少 `Master` 这类术语对新手造成的困惑。
- 如果需要，后续也可以按同样方式处理弹窗状态中的 Mode；本次未改动。

## v0.7.7（2026-11-13）

### 变更

- 将 ESSID 标签从 `_('<abbr title="Extended Service Set Identifier">ESSID</abbr>')` 改为 `_('Wi-Fi name')`。
- 删除 `<abbr>` 悬浮提示和 `ESSID` 缩写；英文界面显示 `Wi-Fi name`，中文界面显示 `Wi-Fi 名称`。
- 同步更新 `po/zh_Hans/wireless.po` 和 `po/templates/wireless.pot`：
  - `msgid`: `Wi-Fi name`
  - `msgstr`: `Wi-Fi 名称`
- 未改动表单字段、UCI 绑定、加密选项、保存逻辑或其他功能。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1），`luci.main.lang=zh_cn`：
  - 页面中文界面显示“禁用/编辑”
  - Edit 弹窗标题为 `编辑 "CUCC_2.4G"`
  - 字段标签为 `Wi-Fi 名称`、`加密`、`密钥`
  - 没有 `abbr` 元素，没有标签页
  - 字段仍绑定到 `wireless.default_radio0.ssid`、`.encryption`、`._wpa_key`
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 中文翻译使用由 po 生成的 32 字节测试 lmo 安装验证；正式打包时由 `luci.mk` 生成 `luci-i18n-wireless-zh-cn`，安装为 `/usr/lib/lua/luci/i18n/wireless.zh-cn.lmo`。
- 修改后文件：666 行，20295 字节，SHA-256 `b2ac5fa9db47c4d9819258702f31bae8ef84918586b4839d701275ce00db14ab`。
- 相对 v0.7.6：1 行新增、1 行删除（JS），另有 po/pot 文案更新。
- 本次未点击 Save；`/etc/config/wireless` 的 mtime 为 Nov 13 11:29，早于本次部署（11:40），不是本次测试写入的。

### 说明

- `abbr` 是 HTML 的缩写元素，不是 LuCI 配置；删除后不再有 ESSID 悬浮解释。
- 这次是面向新手的文案简化，英文标签也从 `ESSID` 改为更直白的 `Wi-Fi name`。

## v0.7.6（2026-11-13）

### 变更

- 新增标准 LuCI 国际化文件 `po/zh_Hans/wireless.po`。
- 将源码中的 ESSID 标签翻译为中文 `Wi-Fi 名称`：
  - `msgid`: `<abbr title="Extended Service Set Identifier">ESSID</abbr>`
  - `msgstr`: `Wi-Fi 名称`
- 新增 `po/templates/wireless.pot` 翻译模板。
- 未修改 `wireless.js`、表单字段、UCI 绑定、加密选项或保存逻辑。

### 说明

- 英文界面继续显示 `ESSID`，并保留下划线悬浮提示；中文界面显示 `Wi-Fi 名称`。
- 中文翻译没有保留 `<abbr>`，因为 `Wi-Fi 名称` 不是缩写。
- 按标准 LuCI 构建时，`luci.mk` 会根据 `po/zh_Hans/wireless.po` 生成 `luci-i18n-wireless-zh-cn`，安装为 `/usr/lib/lua/luci/i18n/wireless.zh-cn.lmo`。
- v0.7.6 验证时路由器 `luci.main.lang=en`，所以只在路由器上添加翻译文件不会让英文界面显示中文；需要把 LuCI 语言切换为“简体中文”。本次没有修改路由器的语言设置。

### 验证

- 在真机页面中临时把翻译键注入 `window.TR`，验证：
  - `_(<abbr title="Extended Service Set Identifier">ESSID</abbr>)` 返回 `Wi-Fi 名称`
  - Edit 弹窗字段标签显示为 `Wi-Fi 名称`、`Encryption`、`Key`
  - 标题仍为 `Edit "CUCC_2.4G"`
  - ESSID、Encryption、Key 字段绑定不变
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 修改后 `wireless.js` 未变化：666 行，20343 字节，SHA-256 `1f4498804843d68091b54023532c68bc023928e13d09ed6b8c5052714e74427a`。
- 新增文件：`po/zh_Hans/wireless.po`（12 行，385 字节）、`po/templates/wireless.pot`（12 行，366 字节）。
- 未点击 Save；`/etc/config/wireless` 未被修改。

## v0.7.5（2026-11-13）

### 安全修复

- 修复 Edit 弹窗标题中 SSID 的存储型 XSS 风险。
- LuCI 的 `titleFn()` 会先对标题调用 `stripTags()`，随后 `ui.showModal()` 通过 `innerHTML` 插入标题。若 SSID 中包含 HTML 实体（例如 `&lt;img src=x onerror=...&gt;`），单次转义会在两次解析后还原为真实标签。
- 现在对 SSID 连续执行两次 `%h` HTML 转义，使两次解析后仍只生成文本，不会生成元素或执行事件。

### 变更

- 仅修改 `s.modaltitle` 中 SSID 的转义方式。
- 普通 SSID 的显示不变；含 `&`、`<`、`>`、单双引号等字符的 SSID 也会按原文显示。
- 未改动表单字段、UCI 绑定、加密选项、保存逻辑或其他代码。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - 未转义路径可生成 `<img>` 子元素并触发事件，确认风险存在
  - 使用 `%h` 二次转义后标题只生成文本，无子元素，事件未触发
  - 实际弹窗标题仍为 `Edit "CUCC_2.4G"`
  - ESSID、Encryption、Key 字段及绑定不变
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 修改后文件：666 行，20343 字节，SHA-256 `1f4498804843d68091b54023532c68bc023928e13d09ed6b8c5052714e74427a`。
- 相对 v0.7.4：6 行新增、1 行删除。
- 未点击 Save；`/etc/config/wireless` 未被修改。

### 说明

- 这次修复只影响标题中 SSID 的编码，不改变标题文字格式、字段显示和写入行为。
- `%h` 是 LuCI `String.prototype.format` 提供的 HTML 转义格式符，不需要新增依赖。

## v0.7.4（2026-11-13）

### 变更

- 仅修改 `s.modaltitle`，将 Edit 弹窗标题从完整的 `Wireless Network: <mode> "<SSID>" (<ifname>)` 简化为 `Edit "<SSID>"`。
- SSID 动态取自 `getActiveSSID() || getSSID()`；找不到对应网络或 SSID 时回退到原有 `Edit wireless network` 文案。
- 不再在标题中显示无线模式（Access Point）和接口名（radio0.network1）。
- 未改动表单字段、UCI 绑定、加密选项、保存逻辑或其他代码。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - `default_radio0` 的弹窗标题为 `Edit "CUCC_2.4G"`
  - `default_radio1` 的弹窗标题为 `Edit "CUCC_5G"`
  - 标题中不再出现 `Wireless Network`、`Access Point` 或 `radio0.network1`
  - 弹窗仍只有 ESSID、Encryption、Key，且没有标签页和分组标题
  - 字段仍绑定到各自 section 的 `ssid`、`encryption`、`._wpa_key`
  - Encryption 候选仍只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 修改后文件：661 行，20163 字节，SHA-256 `76392327d827f5345cdc35724f18e65888a04641ffcb6e29c473dbdaf9ab3ae9`。
- 相对 v0.7.3：6 行新增、1 行删除。
- 未点击 Save；`/etc/config/wireless` 的修改时间仍为 Nov 12 10:57，内置 `network/wireless.js` 的修改时间仍为 Oct 17 21:45。

### 说明

- 标题复用现有 `Edit` 翻译词条（`_('Edit')`），会跟随 LuCI 界面语言；v0.7.4 验证时路由器 `luci.main.lang=en`，因此实测显示英文 `Edit "..."`。
- 这次只影响弹窗标题，不改变字段显示、绑定和写入行为。

## v0.7.3（2026-11-13）

### 变更

- 将 `SectionValue` 的标题从 `Interface Configuration` 改为空，移除弹窗中的分组标题。
- 删除 `General Setup` 单标签声明。
- 将 ESSID、Encryption、Key 三个选项从 `ss.taboption('general', ...)` 改为 `ss.option(...)`。
- 字段仍绑定到对应的 `wifi-iface` section，UCI 配置和保存逻辑不变。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - 弹窗中没有 Interface Configuration 和 General Setup
  - 弹窗标签数组为空
  - 仅显示动态网络标题以及 ESSID、Encryption、Key
  - 字段仍绑定到 `wireless.default_radio0.ssid`、`.encryption`、`._wpa_key`
  - Encryption 仍只有 WPA2-PSK 与 WPA2-PSK/WPA3-SAE Mixed Mode
  - 浏览器控制台无 JS 异常
- 修改后文件：656 行，20030 字节，SHA-256 `0c336064cdaae975e2603356b9574d01707512f42901f86a368be33a08dd7483`。
- 相对 v0.7.2：4 行新增、5 行删除。

### 说明

- 这次只移除冗余的可见标题和单标签，`SectionValue`/`NamedSection` 的内部绑定仍保留，确保字段写入正确的 `wifi-iface`。
- 未点击 Save，`/etc/config/wireless` 未修改；系统内置无线页面未修改。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.7.2（2026-11-13）

### 变更

- 2.4/5GHz 的 Encryption 收敛为两项：WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode。
- 删除 WPA3-SAE（2.4/5GHz）、WPA2-PSK/WPA3-SAE Compatibility Mode、WPA-PSK/WPA2-PSK Mixed Mode。
- 删除对应的 `psk-mixed`、`psk+psk2`、`sae-compat` 加密候选，以及 `_wpa_key` 中不再需要的依赖。
- 6GHz 射频仍保留 WPA3-SAE，因为 6GHz 不允许 WPA2。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - Edit 弹窗仍只有 General Setup 一个标签
  - Encryption 下拉只有 WPA2-PSK、WPA2-PSK/WPA3-SAE Mixed Mode
  - 不存在 WPA3-only、Compatibility Mode、WPA-PSK/WPA2-PSK 混合
  - 浏览器控制台无 JS 异常
- 修改后文件：657 行，20139 字节，SHA-256 `8dc0aebddfe0199de05ed2f1fbc05613280002d13d5e3953cc558e8900244362`。
- 相对 v0.7.1：4 行新增、10 行删除。

### 说明

- 保留 WPA2-PSK 是为了兼容老设备，并且当前路由器正在使用该加密方式。
- WPA2-PSK/WPA3-SAE Mixed Mode 适合大多数家庭：新设备使用 WPA3，老设备回退 WPA2。
- 系统内置 `admin/network/wireless` 页面仍保留完整加密选项，高级用户仍可在原页面配置 WPA3-only、WPA-Enterprise 等。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.7.1（2026-11-13）

### 变更

- 删除 `Wireless Security` 标签页。
- 将 `encryption` 与 `_wpa_key` 两个选项从 `encryption` 标签移到 `general` 标签。
- 现在 Edit 弹窗只有 General Setup 一个标签，包含 ESSID、Encryption、Key。
- 底层 UCI 配置不变，仍为 `/etc/config/wireless` 中同一 `wifi-iface` section 的 `ssid`、`encryption`、`key`。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - Edit 弹窗只有 1 个标签：General Setup
  - 同一标签内显示 ESSID、Encryption、Key
  - Encryption 候选仍为 WPA2-PSK、WPA3-SAE、SAE 混合/兼容、WPA-PSK/WPA2-PSK 混合
  - 浏览器控制台无 JS 异常
- 修改后文件：663 行，20554 字节，SHA-256 `966de3ef4bb635eefbdf935ff4542fc6a6a1d99b8967e9506a578547962d705f`。
- 相对 v0.7.0：2 行新增、3 行删除。

### 说明

- 这次只调整 UI 分组，不修改配置文件结构；内置 `admin/network/wireless` 页面仍读写同一份 `/etc/config/wireless`。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.7.0（2026-11-13）

### 变更

- 删除 SAE-EXT-KEY、Transition Disable、WPS pushbutton。
- 删除 WEP 加密选项、WEP 密钥槽（Used Key Slot、Key #1–#4）、WEP 特性探测、key1–key4 清理逻辑及 WEP 的 cfgvalue 分支。
- 删除 OWE 和 No Encryption 加密选项。
- 删除纯 WPA-PSK，保留 WPA-PSK/WPA2-PSK 混合模式用于老设备兼容。
- 删除不再使用的 `eht_compat_default`。
- Encryption 候选仅保留：WPA2-PSK、WPA3-SAE、WPA2-PSK/WPA3-SAE 混合、WPA2-PSK/WPA3-SAE 兼容、WPA-PSK/WPA2-PSK 混合。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - General Setup 仅显示 ESSID
  - Wireless Security 仅显示 Encryption 与 Key
  - Encryption 下拉不含纯 WPA-PSK、WEP、OWE、No Encryption、EAP
  - 页面不存在 SAE-EXT-KEY、Transition Disable、WPS
  - 浏览器控制台无 JS 异常
- 修改后文件：664 行，20610 字节，SHA-256 `b64e157b1f46326c03298a2174992ca098a8fe53a0d58156ed593ae98de06e7b`。
- 相对 v0.6.0：4 行新增（简化后的 cfgvalue/write）、119 行删除。

### 说明

- 保留 WPA2-PSK、WPA3-SAE、SAE 混合/兼容、WPA-PSK/WPA2-PSK 混合与 Key。
- 系统内置 `/luci/admin/network/wireless` 页面仍保留，高级用户仍可在原页面配置 WEP、OWE、WPS、企业级加密等。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.6.0（2026-11-13）

### 变更

- 删除 EAP 字段：EAP-Method、证书、Identity、Anonymous Identity、Password。
- 删除 RADIUS/VLAN/DAE 区块：认证/计费服务器与端口、Secret、RADIUS 属性、动态 VLAN、Per-STA VLAN、VLAN Naming/Tagged/Bridge、DAE-Client/Port/Secret、RSN Preauth。
- 删除 `gcmp256` 选项。
- 删除 Encryption 下拉中的 WPA/WPA2/WPA3-EAP 选项，避免出现无配置项的空壳选项。
- 删除不再使用的 EAP 特性探测变量及 `tools.widgets` 引用。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - General Setup 仅显示 ESSID
  - Wireless Security 仅显示 Encryption 与 Key
  - Encryption 下拉不含 EAP 选项
  - 页面中不存在 EAP、RADIUS、gcmp256
  - 浏览器控制台无 JS 异常
- 修改后文件：779 行，26060 字节，SHA-256 `63ded84d4dc5fc83a5c2f5aa8edc6a46cb9003c6b388ea8881b76ab179f514f1`。
- 相对 v0.5.0：1 行新增（保留区块的外层 `hwtype` guard）、257 行删除。

### 说明

- ESSID、Encryption、Key 与被删除的 EAP/RADIUS/VLAN/DAE/gcmp256 没有反向依赖；删除后三者仍正常工作。
- Encryption 候选现在仅包含 PSK、SAE、WEP、OWE、No Encryption。
- SAE-EXT-KEY、Transition Disable、WPS pushbutton、WEP 密钥槽等仍保留，可后续继续精简。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.5.0（2026-11-13）

### 变更

- 删除 Cipher 下拉及其值、cfgvalue，以及 encryption write 中的 cipher 拼接逻辑。
- 删除 QR Code 区块、`createWiFiPassword`/`handleGenerateQR`、`buildSVGQRCode`、`uqr` 依赖及 `luci-lib-uqr` 包依赖。
- 删除 PPSK 选项及 9 处 PPSK 专用 PSK 依赖；共享的 RADIUS/VLAN/DAE 选项保留给 WPA-Enterprise。
- 删除 802.11w Management Frame Protection、max/retry timeout、OCV 及 KRACK countermeasures。
- Wireless Security 对 WPA2-PSK 仅显示 Encryption 与 Key。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - 概览无 BSSID，2 个网络行，按钮为 Enable/Edit 与 Disable/Edit
  - Wireless Security 仅显示 Encryption、Key
  - 不存在 Cipher、QR Code、PPSK、802.11w、KRACK、RADIUS Authentication Server
  - 浏览器控制台无 JS 异常
- 修改后文件：1035 行，41510 字节，SHA-256 `5a93e1e59f7a8a387240c8583fae9cdf994f113c642cfa3b161f13db714b06b3`。
- 相对 v0.4.1：0 行新增、311 行删除。

### 说明

- 共享的 EAP/RADIUS、VLAN、DAE 选项仍保留在代码中供 WPA-Enterprise 使用，但对 WPA-PSK 不显示。
- `gcmp256`（GCMP-256 pairwise cipher）作为独立选项保留，它不是已删除的 Cipher 下拉。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.4.1（2026-11-13）

### 变更

- 删除 General Setup 中的 Mesh Id、BSSID、Hide ESSID 表单字段。
- 删除二维码生成中的 `wifiHide` 变量及 H 字段输出。
- 删除概览状态和关联终端状态中的 BSSID 显示。
- General Setup 仅保留 ESSID；内部 `bssid` 变量仅用于 `is_assoc` 判断，不再显示。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - 概览不显示 BSSID
  - Edit 弹窗 General Setup 仅显示 ESSID，不存在 BSSID、Mesh Id、Hide ESSID
  - Wireless Security 标签可正常切换
  - 浏览器控制台无 JS 异常
- 修改后文件：1346 行，54809 字节，SHA-256 `8d3e894489e92d9e2cbe01a85750da408bab4fa44646a78dae36406a38b5c7cd`。
- 相对 v0.4.0：0 行新增、13 行删除。

### 说明

- 二维码规范注释中的 hidden 字样及 CSS 的 `.hidden` 类与已删除的表单字段无关。
- 内部 `bssid` 变量仍用于判断关联状态（`is_assoc`），不再显示。
- Wireless Security 中仍保留 EAP/RADIUS 等高级加密选项，尚未简化。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.4.0（2026-11-13）

### 变更

- 删除 General Setup 的 Mode 下拉及 AP/Client/Ad-Hoc/WDS/ahdemo/monitor/mesh 值、write/cfgvalue、mesh 安装链接和 `have_mesh`。
- 删除 Network 选择器及其 write 逻辑；现有 Wi-Fi 网络与 network 的关联保留，但页面不再修改。
- 删除 WMM Mode 复选框。
- 删除 16 处直接 `depends('mode', ...)` 及 56 处 `add_dependency_permutations` 中的 `mode` 键。
- 删除按 mode 校验加密的 `crypto_support`/`encr.validate` 及 OCV 的 mode 校验。
- General Setup 现在显示 Mesh Id、ESSID、BSSID、Hide ESSID；Wireless Security 保持可用。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - Edit 弹窗 General Setup 标签不存在 Mode、Network、WMM Mode
  - General Setup 仅显示 Mesh Id、ESSID、BSSID、Hide ESSID
  - Wireless Security 标签可正常切换，显示 Encryption、Cipher 等
  - 浏览器控制台无 JS 异常
- 修改后文件：1359 行，55531 字节，SHA-256 `dc4ea8660c499567699a19ceae3087bcc2d17559ad0a2adbd08acdc7b0f28871`。
- 相对 v0.3.0：56 行新增（均为移除 `mode` 键后的原 `add_dependency_permutations` 调用行）、261 行删除。

### 说明

- General Setup 中仍保留 Mesh Id、BSSID、Hide ESSID。
- Wireless Security 中仍保留 EAP/RADIUS 等高级加密选项，尚未简化。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.3.0（2026-11-13）

### 变更

- 删除 Edit 弹窗中的 Device Configuration 整个标签页：
  - 删除 radio 状态、启用/禁用按钮、频率、功率、国家、legacy rates、cell density、distance、frag、rts、noscan、beacon、LDPC 等全部选项。
  - 删除 `CBIWifiFrequencyValue`、`CBIWifiTxPowerValue`、`CBIWifiCountryValue` 三个专用类。
  - `eht_compat_default` 不再读取已删除的 `_freq` 选项，仅从 UCI 读取 htmode。
- 删除 Interface Configuration 的 MAC-Filter 标签及 `macfilter`/`maclist` 选项、加载逻辑。
- 删除 Interface Configuration 的 Advanced Settings 标签及全部 advanced 选项（`mesh_fwding`、`mesh_rssi_threshold`、`multicast_to_unicast_all`、`isolate`、`bridge_isolate`、`ifname`、`macaddr`、`short_preamble`、`dtim_period`、`wpa_group_rekey`、`skip_inactivity_poll`、`max_inactivity`、`max_listen_interval`、`disassoc_low_ack`）。
- 删除 WLAN roaming 标签及 802.11r/802.11k/802.11v 全部选项。
- Edit 弹窗仅保留 Interface Configuration 的 General Setup 与 Wireless Security 两个标签。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证：
  - Edit 弹窗打开正常，仅显示 General Setup、Wireless Security
  - 不存在 Device Configuration、MAC-Filter、Advanced Settings、WLAN roaming
  - 浏览器控制台无 JS 异常
- 修改后文件：1564 行，65102 字节，SHA-256 `96ef4b7a1100895b737349a253794f8f8096021db5422a45dd92996f1a211325`。
- 相对 v0.2.1：2 行新增、654 行删除。

### 说明

- Wireless Security 标签中仍保留 EAP/RADIUS 等高级加密选项，尚未简化。
- General Setup 中仍保留 Mode、Network、Hide ESSID、WMM Mode 等选项。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan、iwinfo freqlist/txpowerlist/countrylist 等已不再使用的权限暂未清理。

## v0.2.1（2026-11-13）

### 变更

- 移除 Wireless Overview 中每个 wifi-iface 网络行的 Remove 按钮。
- 删除 `s.handleRemove` 方法及对 `form.TypedSection.prototype.handleRemove` 的调用。
- `poll_status` 的按钮轮询/禁用逻辑由三个按钮改为两个按钮，移除 `btns[2]` 引用。
- 保留 Enable/Disable、Edit、Associated Stations、Save & Apply。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证通过：
  - 仅 2 个网络行
  - 按钮为 Enable/Edit 与 Disable/Edit
  - 页面中不存在 Remove、Restart、Scan、Add
  - 浏览器控制台无 JS 异常
- 修改后文件：2216 行，92505 字节，SHA-256 `d544f6c65761f0c7eaad3d94a1c52c55cb90d0493c725b4ebcf36972fd507e47`。
- 相对 v0.2.0：2 行新增、13 行删除。

### 说明

- 网络 Edit 弹窗中的 Device Configuration（radio 信道、功率、国家等）仍保留。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan 等已不再使用的权限暂未清理。

## v0.2.0（2026-11-13）

### 变更

- 移除 Wireless Overview 中的 radio 硬件行（radio0/radio1），包括行内的 Restart、Scan、Add 按钮。
- 删除 radio 行专用代码：
  - `render_radio_badge`、`render_radio_status`、`radio_restart`
  - `handleScan`、`handleScanRefresh`、`handleScanStartStop`、`handleScanAbort`
  - `handleJoinConfirm`、`handleJoin`、`handleAdd`
- 删除 `poll_status` 的 radio 分支、`cfgsections` 的 radio 行生成、`lookupRadioOrNetwork` 的 radio 查找、`renderRowActions` 的 radio 分支、`_badge`/`_stat` 的 radio 分支。
- 删除 Restart 的轮询执行逻辑（`/sbin/wifi up`）及不再使用的 `fs` 依赖。
- 保留 wifi-iface 网络行、Enable/Disable、Edit、Remove、Associated Stations、Save & Apply。

### 验证

- 真机 OpenWrt 25.12.6（192.168.1.1）部署验证通过：
  - 仅 2 个网络行（default_radio0、default_radio1）
  - 按钮为 Enable/Edit/Remove 与 Disable/Edit/Remove
  - 页面中不存在 Restart、Scan、Add
  - 浏览器控制台无 JS 异常
- 修改后文件：2227 行，SHA-256 `ac2e4a1f7710cd5e278b9dbbe0b77cf621e4a63e767b0f50f552563803811410`。
- 相对 v0.1.0：27 行新增（网络行逻辑重排）、494 行删除。

### 说明

- 网络 Edit 弹窗中的 Device Configuration（radio 信道、功率、国家等）仍保留。
- `lookupRadioOrNetwork` 名称暂未重命名，当前仅查找网络行。
- 菜单仍未添加官方 `@wifi-device` 依赖；无无线配置的系统上页面会报 `uci/get` 错误，待后续处理。
- ACL 中 scan 等已不再使用的权限暂未清理。

## v0.1.0（2026-11-13）

### 新增

- 按 OpenWrt 25.12 LuCI app 标准创建项目结构。
- 从 `openwrt/luci` 的 `openwrt-25.12` 分支原样复制 `wireless.js`，未做任何源码修改。
  - 源文件：`modules/luci-mod-network/htdocs/luci-static/resources/view/network/wireless.js`
  - SHA-256：`6385cebb2b415257d05def51e890620d7e6b9f8b14071a374ed9dc2ed392c45f`
- 新增标准 LuCI `Makefile`、`menu.d` 菜单和 `rpcd` ACL。
- 页面入口：`/luci/admin/services/wireless`。

### 验证

- 本地安装包与官方 `wireless.js` 逐字节一致（`cmp` 通过）。
- 已部署到 OpenWrt 25.12.6 虚拟机，文件校验一致。
- `rpcd` 已加载 `luci-app-wireless` ACL 组。
- LuCI 菜单树中 `admin/services/wireless` 可见，页面返回 HTTP 200。

### 说明

- 当前测试虚拟机没有无线硬件（无 `/etc/config/wireless`、无 `/sys/class/ieee80211`），页面会显示空的无线概览。
- 官方页面菜单带有 `@wifi-device` UCI 依赖；为保证在测试虚拟机上可见，本版本菜单只依赖 ACL。后续是否恢复由开发者决定。
- 本版本尚未对 `wireless.js` 做任何精简。
