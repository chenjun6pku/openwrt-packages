# packages/

所有 feed 包都在这里平面存放，一个目录一个包：

```text
packages/
├── feed-selftest/
├── luci-app-example/
├── luci-theme-example/
└── myplugin/
```

命名约定：

- LuCI 应用：`luci-app-<name>`
- LuCI 主题：`luci-theme-<name>`
- 其它插件：使用包名

每个包目录包含 `Makefile`、可选的 `patches/`、`files/`、`src/`，以及 `UPSTREAM.md`。
类型由包名表达，不需要额外的分类目录。

需要多个包共享上游源码时，放到仓库根目录的 `vendor/<project>/`，不要放进
`packages/`，避免被自动发现脚本当成包。

新增包请阅读 [docs/adding-a-package.md](../docs/adding-a-package.md)。
