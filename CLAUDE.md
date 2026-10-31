# 仓库操作规则

## 添加新插件：固定流程

### 1. 先检查 OpenWrt 官方源

读取 `feed.json` 中的 `build_version` 和 `arches`，然后检查 OpenWrt 官方对应版本的以下 feed：

```text
https://downloads.openwrt.org/releases/<build_version>/packages/<arch>/{base,luci,packages,routing,telephony}/packages.adb
```

对三个架构都要检查，并搜索：

- 包名（`PKG_NAME`）
- LuCI 包名
- 同名目录
- 对应翻译包

如果官方源已经提供同名包：

- 默认停止添加，向开发者报告官方包名、版本和 `origin`。
- 不得为了覆盖官方包而擅自抬高版本号、改包名或制造同名冲突。
- 只有在开发者明确要求覆盖或改名后，才继续。

### 2. 创建本地分支

从最新的 `main` 创建短生命周期的本地分支：

```sh
git switch main
git pull --ff-only
git switch -c add-<package>
```

功能分支不推送到远程。未经审核不得推送。

### 3. 原样导入上游快照

- 锁定要导入的上游仓库 commit。
- 使用 sparse checkout 获取目标目录：

```sh
git clone --depth 1 --filter=blob:none --sparse <upstream-url> /tmp/<name>
git -C /tmp/<name> sparse-checkout set <upstream-path>
```

- 使用 `git archive` 或 `cp -a` 导入完整目录，保留文件内容、权限和隐藏文件。
- 导入后逐字节校验：

```sh
diff -r --no-dereference <upstream-dir> packages/<package-dir>
```

- 严禁修改上游源代码、JS、菜单、ACL、配置文件或 init 脚本。
- 本地提交，提交信息必须记录上游 URL 和 commit：

```text
packages: add <name> from upstream
```

### 4. 分析并等待审核

导入提交完成后，先分析，不直接构建或推送：

- 包结构、版本、许可证。
- 直接依赖、传递依赖、构建依赖。
- 源码和前端资源的下载地址、commit/tag、哈希。
- 构建路径是否需要适配本 feed 布局。
- 与 OpenWrt 官方源的同名包、版本冲突。
- 运行时服务、端口、日志路径、权限和可选依赖。
- 自动化安全审查发现的问题。

必须报告需要修改的内容和理由。常见的必要适配：

- LuCI 包：

  ```make
  include $(TOPDIR)/feeds/luci/luci.mk
  ```

- Go 包：

  ```make
  include $(TOPDIR)/feeds/packages/lang/golang/golang-package.mk
  ```

- 显式固定 `PKG_VERSION`、`PKG_RELEASE` 和 `PKG_PO_VERSION`，避免浅克隆或文件时间戳导致版本漂移。
- 修改包内容后递增版本，避免同版本不同字节。

在开发者明确审核通过前，不修改上游文件、不构建、不推送。

### 5. 审核后的最小适配

只实施已批准的改动：

- 不改变上游功能逻辑。
- 路径、版本、依赖等适配应作为独立提交，便于审查。
- 安全修复如果会改变上游代码，必须先提出方案并等待审核。
- 再次确认 `python3 scripts/feed_meta.py names` 能发现新包。

### 6. 构建与发布

只有开发者明确要求发布后才执行：

- 将本地分支快进合并到 `main`。
- 推送 `main` 并等待 release workflow 完成。
- 验证：
  - `feed-state.json` 签名；
  - 新包名称、版本、依赖和架构；
  - 各架构 `packages.adb` 的 SHA-256 与 state 一致；
  - 页面和 APK 下载可用。
- 如果与官方同名包同时存在，必须先确认版本覆盖或改名策略。

### 7. 中止或移除

如果审核决定不收录，或官方源已经提供且无需覆盖：

- 未推送：直接删除本地添加分支。
- 已推送：删除 `packages/` 下对应目录及所有引用，创建移除提交并推送。
- 发布后移除：确认线上 state 不再包含相关包，并检查旧 APK URL 返回 `404`。

## 通用约束

- 不修改包布局和源码策略，除非开发者明确要求。
- 不提交构建产物、临时下载目录或私钥。
- 不推送未审核的功能分支。
- 安全审查未完成或存在未处理发现时，必须在最终报告中说明。
