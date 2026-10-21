include $(TOPDIR)/rules.mk

PKG_NAME:=luci-app-edunet
PKG_VERSION:=1.0
PKG_RELEASE:=2
PKG_LICENSE:=Apache-2.0

LUCI_TITLE:=LuCI Support for EDUNET
LUCI_DESCRIPTION:=This is a LuCI application for EDUNET client.
LUCI_DEPENDS:=+luci-base +minieap

define Package/luci-app-edunet/conffiles
/etc/config/edunet
endef

include $(TOPDIR)/feeds/luci/luci.mk

$(eval $(call BuildPackage,luci-app-edunet))