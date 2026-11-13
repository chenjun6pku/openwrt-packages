#
# Copyright (C) 2026 chenjun6pku
#
# This is free software, licensed under the Apache License, Version 2.0.
#

include $(TOPDIR)/rules.mk

LUCI_TITLE:=LuCI app for simplified wireless configuration
LUCI_DEPENDS:=+luci-base +rpcd-mod-iwinfo
LUCI_PKGARCH:=all

PKG_VERSION:=0.7.12
PKG_RELEASE:=1
PKG_PO_VERSION:=$(PKG_VERSION)-r$(PKG_RELEASE)
PKG_LICENSE:=Apache-2.0
PKG_LICENSE_FILES:=LICENSE
PKG_MAINTAINER:=chenjun6pku <chenjun6pku@gmail.com>

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
