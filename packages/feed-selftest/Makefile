include $(TOPDIR)/rules.mk

PKG_NAME:=feed-selftest
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=LICENSE
PKG_MAINTAINER:=chenjun6pku <chenjun6pku@users.noreply.github.com>

include $(INCLUDE_DIR)/package.mk

define Package/feed-selftest
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=OpenWrt custom feed self-test
  PKGARCH:=all
endef

define Package/feed-selftest/description
  A tiny diagnostic package for verifying that the custom apk feed is
  reachable, installable, and usable on the target device.
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/. $(PKG_BUILD_DIR)/
endef

define Build/Compile
	@:
endef

define Package/feed-selftest/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/feed-selftest $(1)/usr/bin/feed-selftest
endef

$(eval $(call BuildPackage,feed-selftest))
