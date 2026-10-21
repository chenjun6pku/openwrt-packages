# vendor/

可选的共享上游源码目录，供一个上游仓库包含多个包时复用。

`scripts/list-packages.sh` 只扫描 `packages/*`，不会把这里当成包；但 OpenWrt 的
`scripts/feeds` 会扫描 feed 根目录，因此这里的 OpenWrt Makefile 需要重命名为
`Makefile.upstream`，避免被识别为重复包。

单包项目的源码优先放在该包的 `packages/<pkg>/src/` 下。
