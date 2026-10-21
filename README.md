# OpenWrt Packages Feed

一个面向 **OpenWrt 25.12.x / apk v3** 的第三方软件源，包含收集并固化在仓库中的
OpenWrt 插件、LuCI 应用和 LuCI 主题。CI 使用官方 OpenWrt SDK 为每个支持的架构
编译 `.apk`，签名索引后发布到 GitHub Pages。

## 支持范围

| 项目 | 范围 |
| --- | --- |
| OpenWrt | 25.12.x（不包含 24.10/opkg、SNAPSHOT） |
| 架构 | `x86_64`、`aarch64_cortex-a53`、`mipsel_24kc` |
| 包类型 | 用户态插件、LuCI app、LuCI 主题 |
| 内核模块 | 不支持（kmod 与 target/内核版本绑定） |

## 设备端安装

先下载并检查安装脚本，再执行：

```sh
uclient-fetch -O /tmp/install-feed.sh \
  https://chenjun6pku.github.io/openwrt-packages/install-feed.sh
sh /tmp/install-feed.sh
```

脚本会：

1. 检查发行版是否为 25.12.x；
2. 检查 `DISTRIB_ARCH` 是否受支持；
3. 把公钥安装到 `/etc/apk/keys/openwrt-packages.pem`；
4. 把 feed 写入 `/etc/apk/repositories.d/customfeeds.list`；
5. 执行 `apk update`。

之后安装包：

```sh
apk add feed-selftest
```

### 手动安装

```sh
BASE="https://chenjun6pku.github.io/openwrt-packages"
ARCH="$(. /etc/openwrt_release; echo "$DISTRIB_ARCH")"

uclient-fetch -O /etc/apk/keys/openwrt-packages.pem "$BASE/public-key.pem"
echo "$BASE/25.12/$ARCH/custom/packages.adb" \
  >> /etc/apk/repositories.d/customfeeds.list
apk update
```

`/etc/apk/repositories.d/customfeeds.list` 和 `/etc/apk/keys/` 位于 `/etc`，
sysupgrade 时通常会保留；如果设备没有保留，重新执行安装脚本即可。

## 包列表

| 包名 | 说明 |
| --- | --- |
| `feed-selftest` | 诊断包，用于验证源是否可访问、签名是否有效、安装是否成功 |
| `minieap` | 802.1X 客户端，支持锐捷 RJv3 插件；源码在 [chenjun6pku/minieap](https://github.com/chenjun6pku/minieap) |

## 仓库结构

```text
packages/       所有包，每个目录一个 OpenWrt 包（普通插件、luci-app-*、luci-theme-*）
vendor/         可选：多个包共享的上游源码
scripts/        设备安装脚本、源码固化脚本
keys/           只存放公钥
docs/           架构与新增包说明
.github/        CI/CD 流水线
```

每个包目录包含 `Makefile`、可选的 `patches/`、`files/`，以及完整的上游源码或
LuCI 包文件；来源、commit 和许可证记录在 `UPSTREAM.md` 中。

## 开发

新增包之前请阅读 [docs/adding-a-package.md](docs/adding-a-package.md)。基本流程：

```sh
# 1. 固化上游源码（示例）
./scripts/vendor-upstream.sh https://github.com/owner/project.git <commit> \
  packages/myplugin/src

# 2. 编写/调整 Makefile，补 UPSTREAM.md

# 3. 本地用 SDK 编译（需要已解压的 OpenWrt 25.12 SDK）
cd /path/to/sdk
echo "src-link custom $PWD/../openwrt-packages" >> feeds.conf
./scripts/feeds update custom
./scripts/feeds install -p custom -f -a
make defconfig
make package/myplugin/compile V=s
```

CI 规则：

- Pull Request：在 `x86_64` 上编译全部包，不使用签名密钥；
- push 到 `main` / 打 `v*` tag：三个架构构建 → 独立签名 job → 部署 Pages。

## 签名

feed 使用 EC P-256 私钥签名索引。私钥只保存在 GitHub Actions secret
`APK_PRIVATE_KEY` 中，构建 job 不接触它；签名 job 只运行 `apk mkndx`，不执行包内
构建脚本。公钥为 [keys/public-key.pem](keys/public-key.pem)。

密钥生成、配置和轮换步骤见 [keys/README.md](keys/README.md)。

## 版本与升级

- `PKG_VERSION` 跟随上游；
- 自己修改源码、补丁或依赖时递增 `PKG_RELEASE`；
- 同一版本重建不会触发设备升级，这是预期行为；
- 用户升级建议：`apk update && apk add --upgrade <package>`。

`scripts/check-revisions.sh` 会在源码发生变化但 `PKG_RELEASE` 未变时给出警告。

## 许可

构建脚本、CI 配置、文档和 `feed-selftest` 使用 MIT 许可证。`packages/` 下的第三方包
保留其上游许可证；详见各包的 `UPSTREAM.md` 和许可证文件。
