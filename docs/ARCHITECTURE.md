# 架构设计

## 目标

- 在一个公开 GitHub 仓库中保存收集的 OpenWrt 插件、LuCI app、LuCI 主题及自研插件源码；
- 源码随仓库保存，避免上游删库后无法构建，并允许本地改造；
- 使用 GitHub Actions 和官方 OpenWrt SDK 自动构建 `.apk`；
- 生成签名的 apk 仓库索引，发布到 GitHub Pages；
- 设备端通过 `customfeeds.list` 直接添加为源并用 `apk` 安装。

## 非目标

- 不支持 OpenWrt 24.10 及更早的 opkg/ipk；
- 不支持 SNAPSHOT；
- 不发布内核模块（kmod）；
- 不替代官方 feed，不保证与官方包同名时的行为。

## 为什么用 SDK，而不是完整 buildroot

完整 OpenWrt buildroot 会编译工具链和固件，耗时和磁盘占用都高。第三方用户态包只需
要目标架构对应的 SDK：它包含交叉工具链、目标 libc、官方包索引和 `scripts/feeds`，
足以编译插件、LuCI app 和主题。只有 kmod 或需要改内核配置的包才需要按 target/subtarget
使用完整 buildroot。

## 两个“源”

1. **源码 feed**：本 Git 仓库。开发者可以把它加入 `feeds.conf`：

   ```text
   src-git custom https://github.com/chenjun6pku/openwrt-packages.git
   ```

2. **二进制 feed**：CI 发布的静态目录，设备通过 HTTPS 访问：

   ```text
   https://chenjun6pku.github.io/openwrt-packages/25.12/<arch>/custom/packages.adb
   ```

设备不需要 Git，也不需要构建工具。

## 目录布局

```text
packages/<name>/          所有包（普通插件、luci-app-*、luci-theme-*）
vendor/<project>/         可选：多个包共享的上游源码
```

OpenWrt 的 `scripts/feeds` 以 `SCAN_DEPTH=5` 扫描 feed，并只把包含
`call BuildPackage` 的 `Makefile` 当作包。因此包目录可以直接放在 `packages/` 下，
不需要类型分类目录。当前仓库采用单层扁平结构，类型由 `luci-app-*`、`luci-theme-*`
等包名表达；以后包数量增长时再引入功能分类即可，包名和 feed URL 不变。

### vendored 源码的扫描冲突

如果把一个“本身是 OpenWrt 包”的上游目录整体放进另一个包的 `src/`，其 `Makefile`
含有 `call BuildPackage`，会被扫描成第二个包。处理方式：

- LuCI app/主题：上游包目录本身就是我们的包目录，放在 `packages/luci-app-*` 或
  `packages/luci-theme-*` 下；
- 通用项目：源码放 `src/`，包根目录放我们的 Makefile；`src/` 内若出现 OpenWrt
  Makefile，重命名为 `Makefile.upstream`；
- 一个上游仓库含多个包：在 `vendor/<project>/` 放一份源码，各包 Makefile 引用它；
  同样要重命名内部 OpenWrt Makefile。

`scripts/vendor-upstream.sh` 会自动做最后一步重命名。

## 构建流水线

```text
PR:
  build (x86_64) ──> 只编译变更包，不生成索引，不接触密钥
                      修改 CI/自动发现脚本时全量验证

push main / tag:
  build (x86_64, aarch64_cortex-a53, mipsel_24kc)
    └─ 每个架构编译全部 .apk，上传 artifact
  sign (单个 job)
    └─ 下载全部 .apk
    └─ 用官方 SDK 的 apk mkndx 为每个架构生成并签名 packages.adb
  publish
    └─ 组装 public/25.12/<arch>/custom/
    └─ 部署 GitHub Pages
```

### 为什么把构建和签名拆开

构建过程会执行第三方包中的 `Build/Prepare`、`install` 等脚本。如果签名私钥在构建
容器中，恶意源码可以直接读取并外传。因此：

- build job 没有任何 secret；
- sign job 只运行受信任的 `apk mkndx` 命令，不执行包内代码；
- 私钥只在 sign job 中通过 GitHub Environment secret 注入，使用后删除。

### 索引命令

与 OpenWrt 构建系统一致：

```sh
apk mkndx \
  --root "$SDK" --keys-dir "$SDK" --allow-untrusted \
  --sign private-key.pem \
  --output packages.adb \
  *.apk
```

`apk mkndx` 只读取 `.apk` 元数据，因此一个 x86_64 SDK 就可以为三个架构生成索引；
签名 job 只下载一次 SDK。

### 失败策略

- `fail-fast: false`：一个架构失败时其他架构继续构建；
- 任一 build job 失败，`sign` 不会运行，避免发布不完整索引；
- 包编译失败不会发布部分 feed；
- PR 的构建失败不会影响 Pages。

## 发布布局

```text
public/
├── 25.12/
│   ├── x86_64/custom/
│   │   ├── packages.adb
│   │   └── *.apk
│   ├── aarch64_cortex-a53/custom/
│   └── mipsel_24kc/custom/
├── public-key.pem
├── install-feed.sh
└── index.html
```

`packages.adb` 中的文件名是相对于索引目录的，因此 `.apk` 必须与索引放在同一目录。

## 设备端

```text
/etc/apk/keys/openwrt-packages.pem
/etc/apk/repositories.d/customfeeds.list
  -> https://.../25.12/<arch>/custom/packages.adb
```

`install-feed.sh` 是幂等的：它会先删除包含本 feed base URL 的旧行，再写入新行。
它还会校验发行版和架构，避免用户在不兼容设备上得到难以理解的依赖错误。

## 版本管理

- `PKG_VERSION` 跟随上游版本；
- `PKG_RELEASE` 在本地修改源码、补丁或依赖时手动递增；
- 发布 tag 只表示“这次构建发布”，不改变包版本；
- 同版本重建不会让 `apk` 认为需要升级；这是预期行为，避免每次 CI 都提示升级；
- `scripts/check-revisions.sh` 在源码变更但 `PKG_RELEASE` 未变时告警。

## 兼容性边界

- **仅 25.12.x**：SDK 使用 `openwrt-25.12` 分支镜像，包依赖该分支的 libc/ABI；
- **精确架构匹配**：`x86_64`、`aarch64_cortex-a53`、`mipsel_24kc`；
  `mipsel_24kc_24kf` 等变体不兼容；
- **无 kmod**：内核模块不能按 package arch 跨设备发布；
- **LuCI**：优先 JS/ucode；Lua 应用需要 `luci-compat`/`luci-lua-runtime`，且官方已弃用；
- **包名冲突**：与官方 feed 同名时，`apk` 可能选择官方版本；收录前必须审计；
- **许可证**：每个 vendored 包必须允许再分发；不满足的包不能进入公开 feed；
- **预编译二进制**：需要单独确认许可证和架构兼容性。

## 安全注意事项

- 所有上游源码固定到 commit，并在 `UPSTREAM.md` 记录；
- GitHub Actions 固定 action 版本（`gh-action-sdk@v11` 等）；
- 发布 job 使用 GitHub Environment（`release`、`github-pages`），可配置 required reviewers；
- 保护 `main` 分支，禁止直接 push（建议）；
- 私钥不外泄；如果怀疑泄露，立即轮换并重新发布索引；
- 公开仓库的 fork PR 不会获得 secret，CI 只在 PR 上做无签名编译。

## 未来扩展

- 增加更多架构：在 `release.yml` 的 matrix 和安装脚本中加入对应 arch；
- 增加安装冒烟测试：在 OpenWrt rootfs 容器中 `apk add` 本 feed 的包；
- 改用 Cloudflare Pages/R2：如果 Pages 的 1GB/100GB 限制成为瓶颈；
- 支持 SNAPSHOT：需要每日/每周重建并接受 ABI 漂移；
- 支持 24.10：需要同时维护 ipk 和 usign 签名，不推荐。
