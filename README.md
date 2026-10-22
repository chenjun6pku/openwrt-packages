# OpenWrt Packages Feed

面向 **OpenWrt 25.x** 的第三方 apk 软件源。使用官方 **OpenWrt 25.12.6 SDK**
构建、签名，并发布到 GitHub Pages。

## 支持范围

| 项目 | 范围 |
| --- | --- |
| OpenWrt | 25.x（已在 25.12.0、25.12.6 验证） |
| 包管理 | apk v3（不支持 24.10/opkg、SNAPSHOT） |
| 架构 | `x86_64`、`aarch64_cortex-a53`、`mipsel_24kc` |
| 包类型 | 用户态插件、LuCI app、LuCI 主题 |
| 内核模块 | 不支持（kmod 与 target/内核版本绑定） |

Feed 路径中的 `25.12.6` 是**构建版本**；安装脚本接受所有 OpenWrt 25.x 设备。

## 快速开始

### 1. 添加 feed（一次性）

```sh
uclient-fetch -O /tmp/install-feed.sh \
  https://chenjun6pku.github.io/openwrt-packages/install-feed.sh
sh /tmp/install-feed.sh
```

脚本会检查系统版本和架构、安装公钥、写入 feed，并执行 `apk update`。

### 2. 安装软件包

以 EDUNET 校园网认证为例：

```sh
apk add luci-app-edunet
apk add luci-i18n-edunet-zh-cn   # 可选：中文界面
```

`luci-app-edunet` 依赖 `luci-base` 和 `minieap`，缺失时会自动安装。

安装其他包只需替换包名，例如：

```sh
apk add minieap
apk add feed-selftest
```

### 3. 配置 EDUNET

在 LuCI 中进入 `Services → EDUNET`，或直接编辑：

```sh
vi /etc/config/edunet
```

至少填写 `username`、`password`、`nic`，并将 `enabled` 设为 `1`。然后：

```sh
/etc/init.d/edunet enable
/etc/init.d/edunet start
logread -f
```

初始化脚本默认不会自动启用。首次启动如果只创建了 `/tmp/edunet.active`
而没有拉起进程，再执行一次 `/etc/init.d/edunet start`，或在 LuCI 中重新保存并应用。

### 手动添加 feed

<details>
<summary>不使用安装脚本时</summary>

```sh
BASE="https://chenjun6pku.github.io/openwrt-packages"
ARCH="$(. /etc/openwrt_release; echo "$DISTRIB_ARCH")"

mkdir -p /etc/apk/keys /etc/apk/repositories.d
uclient-fetch -O /etc/apk/keys/openwrt-packages.pem "$BASE/public-key.pem"
touch /etc/apk/repositories.d/customfeeds.list
grep -vF "$BASE" /etc/apk/repositories.d/customfeeds.list > /tmp/feeds.tmp || true
echo "$BASE/25.12.6/$ARCH/custom/packages.adb" >> /tmp/feeds.tmp
mv /tmp/feeds.tmp /etc/apk/repositories.d/customfeeds.list
apk update
```

</details>

`/etc/apk/repositories.d/customfeeds.list` 和 `/etc/apk/keys/` 位于 `/etc`，
sysupgrade 时通常会保留；如果没有保留，重新运行安装脚本即可。

## 包列表

| 包名 | 说明 | 来源 |
| --- | --- | --- |
| `luci-app-edunet` | EDUNET/minieap 的 LuCI 配置页面 | 本仓库 `packages/luci-app-edunet` |
| `luci-i18n-edunet-zh-cn` | EDUNET 中文翻译 | 由 `po/zh_Hans` 生成 |
| `minieap` | 802.1X 客户端，支持锐捷 RJv3 插件 | [chenjun6pku/minieap](https://github.com/chenjun6pku/minieap) fork |
| `feed-selftest` | 诊断包：验证源、签名和安装 | 本仓库 |

当前 feed 的版本和架构信息以索引为准：

```text
https://chenjun6pku.github.io/openwrt-packages/25.12.6/<arch>/custom/packages.adb
```

## 仓库结构

```text
packages/               每个目录一个 OpenWrt 包（luci-app-*、luci-theme-*、普通插件）
scripts/                设备安装脚本、源码快照和版本检查脚本
keys/                   只存放签名公钥
site/                   GitHub Pages 首页
docs/                   架构和新增包说明
vendor/                 可选：多个包共享的上游源码
.github/workflows/      PR CI 和 release 流水线
.github/scripts/        PR 变更包检测
```

每个包目录包含 `Makefile`、可选的 `patches/`、`files/`，以及源码或 LuCI 包文件；
来源、commit、许可证和本地改动记录在 `UPSTREAM.md`。

## 源码策略

| 类型 | 做法 |
| --- | --- |
| LuCI app / 主题 / 自研包 | 完整源码放在 `packages/<pkg>/` |
| 非原生上游项目 | 公开 fork 固定 commit；`packages/<pkg>/` 只放 OpenWrt 适配层 |
| 多包共享上游源码 | 放在 `vendor/<project>/`，避免被 feed 扫描器重复识别 |

版本规则：

- `PKG_VERSION` 跟随上游；
- 修改源码、补丁、init、配置或依赖时递增 `PKG_RELEASE`；
- 非原生项目更新 fork commit 时，同时更新 `PKG_SOURCE_VERSION` 和 `PKG_RELEASE`；
- 同版本重建不会触发设备升级，用户升级建议：

```sh
apk update
apk add --upgrade <package>
```

## 开发与发布

新增包请阅读 [docs/adding-a-package.md](docs/adding-a-package.md)。本地编译是可选的：

```sh
cd /path/to/openwrt-sdk-25.12.6-x86-64
# 首次使用：把本仓库加入 SDK 的 feeds.conf
echo "src-link custom /path/to/openwrt-packages" >> feeds.conf
./scripts/feeds update custom
./scripts/feeds install -p custom -f <pkg>
make package/<pkg>/compile V=s
```

CI 规则：

- **PR**：只在 `x86_64-25.12.6` 上编译变更包及依赖；
- **push 到 `main` / `v*` tag**：三个架构全量构建 → 独立签名 job → 部署 Pages；
- Release 固定使用 **25.12.6** SDK 镜像；
- 构建和签名拆开：build job 不接触私钥，sign job 只运行 `apk mkndx`。

详细架构见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 签名与安全

- feed 使用 EC P-256 私钥签名索引；
- 私钥只保存在 GitHub Actions secret `APK_PRIVATE_KEY` 中；
- 公钥为 [keys/public-key.pem](keys/public-key.pem)，安装脚本会自动放到
  `/etc/apk/keys/openwrt-packages.pem`；
- 密钥生成、配置和轮换见 [keys/README.md](keys/README.md)。

## 故障排查

| 现象 | 处理 |
| --- | --- |
| `UNTRUSTED signature` | 公钥缺失或损坏；重新运行安装脚本 |
| 访问旧 `/25.12/...` 返回 404 | 旧路径已下线；重新运行安装脚本切换到 `/25.12.6/` |
| `Unsupported OpenWrt release` | feed 只支持 OpenWrt 25.x |
| 找不到包 | 先 `apk update`，并确认设备 `DISTRIB_ARCH` 在支持列表中 |
| EDUNET 不启动 | 检查 `/etc/config/edunet`，然后 `/etc/init.d/edunet enable && start` |

## 许可

构建脚本、CI 配置、文档和 `feed-selftest` 使用 MIT 许可证。`packages/` 下的第三方包
保留其上游许可证；详见各包的 `UPSTREAM.md` 和许可证文件。
