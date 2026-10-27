# 增量发布

`release.yml` 不再每次都构建整个 feed。它读取上一版已签名的 `feed-state.json`，对比
每个 `packages/<dir>` 的 git tree hash，只重新编译变化、新增或删除的包；未变包直接从
上一版 Pages feed 复用。

## 状态文件

`public/feed-state.json` 由 sign job 生成，并附带 `feed-state.json.sig`（EC P-256 /
`openssl dgst -sha256 -sign`，与 `packages.adb` 使用同一把 key）。

```json
{
  "schema": 1,
  "generator": 1,
  "build_version": "25.12.6",
  "source_commit": "<git sha>",
  "generated_at": "2026-10-27T00:00:00Z",
  "vendor_tree": "<git tree sha or null>",
  "build_config": "<sha256>",
  "sources": {
    "luci-theme-argon": { "tree": "<git tree sha>" }
  },
  "arches": {
    "x86_64": {
      "index": { "file": "packages.adb", "sha256": "<sha256>", "size": 3861 },
      "packages": [
        {
          "name": "luci-theme-argon",
          "version": "3.1.0-r20261027",
          "arch": "noarch",
          "source": "luci-theme-argon",
          "origin": "/feed/packages/luci-theme-argon",
          "file": "luci-theme-argon-3.1.0-r20261027.apk",
          "sha256": "<sha256>",
          "size": 296000
        }
      ]
    }
  }
}
```

- `sources` 以包目录为键，tree hash 决定是否需要重建；README/tests 变化也会重建该包，但不会全量。
- `source` 是归一化目录名，用于恢复/删除；`origin` 保留 APK 原始值用于校验。
- `arch` 可能是 `noarch`、`all` 或目标架构；本 feed 目前每个包都按三个架构构建。
- `index` 绑定对应架构的 `packages.adb`，publish 前会校验。

## 决策规则

`prepare` 在以下情况强制全量：

- 没有 `feed-state.json`（首次发布）；
- `build_version` 或架构列表变化；
- `source_commit` 不是当前 HEAD 的祖先；
- `vendor_tree` 或 `build_config` 变化；
- `scripts/feed_meta.py`、`scripts/feed_state.py`、`release.yml` 自 state 以来有变化；
- `PKG_BUILD_DEPENDS` 指向本 feed 的包（当前没有）；
- `workflow_dispatch` 勾选 `full_build`。

state 存在但签名/结构无效时，流程**失败**；只有显式 `full_build=true` 才继续。
某个架构缺少 state 或恢复后缺少上一版存在的包时，该架构单独全量，其他架构仍可增量。

## 恢复与合并

1. prepare 把上一版 state 上传为 1 天有效的 `feed-state` artifact。
2. build job 验签 state，只下载本架构需要保留的 `.apk`，逐个校验 sha256/size。
3. 只编译 `build_dirs` 中的包。`gh-action-sdk` 的 `PACKAGES` 为空时**必须跳过 action**，
   否则 action 会构建整个 feed。
4. 新产物按 `apk adbdump --format json` 的 `origin` 过滤，只接受属于 `build_dirs` 的包；
   依赖副作用产物不会覆盖已恢复的旧包。
5. merge 按 `source` 删除重建/移除目录的全部旧输出，再复制新产物。
6. sign 重新生成完整索引；若同版本但字节变化，默认失败。

## 发布

- 只有 `main` 或 `v*` tag 的 run 会执行 sign；分支 `workflow_dispatch` 只能做无签名的
  build/dry-run。
- 非 dry-run 的 publish 也只允许 `main`/`v*`。
- `feed-state.json`、`.sig`、`feed.json`、keyring 一起发布到 Pages 根目录。
- `full_build=true` 可随时重建整个 feed；`dry_run=true` 只构建/签名，不部署。

## 操作建议

- 修改包内容后递增 `PKG_RELEASE`，否则 sign 会因同版本不同字节而失败。
- 升级 SDK 时修改 `feed.json.build_version`；首次会自动全量，之后恢复增量。
- 修改 `vendor/` 或发布控制脚本时会自动全量一次，这是有意的保守策略。
- 需要回滚时优先 revert 相关提交后重新发布；上一版 `signed` artifact 保留 90 天。
