# 新增一个包

## 1. 选择分类

| 类型 | 目录 | 示例 |
| --- | --- | --- |
| 普通插件 | `packages/<name>/` | `packages/nikki/` |
| LuCI 应用 | `packages/luci-app-<name>/` | `packages/luci-app-nikki/` |
| LuCI 主题 | `packages/luci-theme-<name>/` | `packages/luci-theme-argon/` |

所有包都在 `packages/` 下平面存放，类型由包名表达，不再使用额外的分类目录。

包目录名通常与 `PKG_NAME` 一致。标准 LuCI 包可以省略 `PKG_NAME`：`luci.mk`
会从 `LUCI_NAME`（默认是目录名）推导。`scripts/list-packages.sh` 和 PR 变更
检测按同样规则识别，因此不需要为了本 feed 修改上游 Makefile。

## 2. 固化上游源码

推荐使用脚本，保证删除 `.git` 并记录 commit：

```sh
./scripts/vendor-upstream.sh \
  https://github.com/owner/project.git \
  <commit-or-tag> \
  packages/myplugin/src
```

如果是 LuCI app，通常整个上游包目录就是源码：

```sh
./scripts/vendor-upstream.sh \
  https://github.com/owner/luci-app-example.git \
  <commit-or-tag> \
  packages/luci-app-example
```

然后补全 `UPSTREAM.md` 中的 `License` 和 `Local changes`。

### 注意扫描冲突

`src/` 中如果含有 OpenWrt 包的 `Makefile`（包含 `call BuildPackage`），会被 feed
扫描器识别为第二个包。脚本会自动把它重命名为 `Makefile.upstream`；手动复制时也要
做同样处理。

## 3. 选择 Makefile 形态

### A. LuCI app / 主题

保留上游 `Makefile`，确认：

```make
include $(TOPDIR)/feeds/luci/luci.mk
LUCI_DEPENDS:=+luci-base
LUCI_PKGARCH:=all
```

Lua 应用还需要 `luci-compat`（以及运行时的 `luci-lua-runtime`），但 25.x 已弃用
Lua，能改 JS 的优先改 JS。

### B. 上游已经是 OpenWrt 包，但源码是下载的

把源码放到 `src/`，覆盖下载与 Prepare：

```make
PKG_NAME:=myplugin
PKG_VERSION:=1.2.3
PKG_RELEASE:=1

PKG_SOURCE:=
PKG_SOURCE_URL:=
PKG_HASH:=

include $(INCLUDE_DIR)/package.mk

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/. $(PKG_BUILD_DIR)/
	$(call PatchDir,$(PKG_BUILD_DIR),./patches)
endef
```

保留 `PKG_LICENSE`、`PKG_LICENSE_FILES`、`PKG_MAINTAINER`；`UPSTREAM.md` 记录上游
URL 和 commit。

### C. 通用项目，需要自己写 Makefile

参考 `packages/feed-selftest/Makefile`：

```make
include $(TOPDIR)/rules.mk

PKG_NAME:=myplugin
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=LICENSE
PKG_MAINTAINER:=Your Name <you@example.com>

include $(INCLUDE_DIR)/package.mk

define Package/myplugin
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=My plugin
  PKGARCH:=all
endef

define Package/myplugin/description
  ...
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/. $(PKG_BUILD_DIR)/
endef

define Package/myplugin/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/myplugin $(1)/usr/bin/myplugin
endef

$(eval $(call BuildPackage,myplugin))
```

## 4. 本地编译

需要先准备对应架构的 OpenWrt 25.12.6 SDK。以 x86_64 为例：

```sh
cd /path/to/openwrt-sdk-25.12.6-x86-64
echo "src-link custom /path/to/openwrt-packages" >> feeds.conf
./scripts/feeds update custom
./scripts/feeds install -p custom -f -a
make defconfig
make package/myplugin/compile V=s
```

产物在 `bin/packages/x86_64/custom/`。

## 5. 提交前检查

- `UPSTREAM.md` 已填写 URL、commit、许可证、本地改动；
- `PKG_RELEASE` 已递增（如果修改了现有包）；
- 没有引入 kmod；
- 没有与官方 feed 同名的包，或已确认覆盖行为；
- 许可证允许再分发；
- 没有把 `private-key.pem`、构建产物或 `.git` 提交进仓库。

`scripts/check-revisions.sh` 可以在本地做版本号提醒。

## 6. PR 与发布

- PR 只在 x86_64 上编译变更包（修改 CI/自动发现脚本时全量验证）；
- 合并到 `main` 或打 `v*` tag 后，release workflow 仍会在三个架构上全量构建、签名并发布；
- 发布后可用 `apk add <package>` 在设备上验证。
