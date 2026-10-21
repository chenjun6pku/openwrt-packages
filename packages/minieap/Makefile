include $(TOPDIR)/rules.mk

PKG_NAME:=minieap
PKG_VERSION:=0.93
PKG_RELEASE:=1

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/chenjun6pku/minieap.git
PKG_SOURCE_VERSION:=9e10f320a9fce46c8f4286324a0fc70e572f61dc
PKG_MIRROR_HASH:=9ed078ef98d67c96687c07d31d5ead0b63f87a04063e42404250be3b7d190641

PKG_LICENSE:=GPL-3.0-only
PKG_LICENSE_FILES:=LICENSE
PKG_MAINTAINER:=chenjun6pku <chenjun6pku@users.noreply.github.com>

include $(INCLUDE_DIR)/package.mk

define Package/minieap
  SECTION:=net
  CATEGORY:=Network
  TITLE:=MiniEAP 802.1X client
  URL:=https://github.com/updateing/minieap
endef

define Package/minieap/description
  A standard EAP-MD5-Challenge client with pluggable packet
  modifiers, including the RJv3 authentication algorithm.
endef

define Package/minieap/conffiles
/etc/minieap.conf
endef

define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(TARGET_CPPFLAGS)" \
		CPPFLAGS="$(TARGET_CPPFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS) -ldl" \
		ENABLE_ICONV=false \
		ENABLE_GBCONV=true
endef

define Package/minieap/install
	$(INSTALL_DIR) $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/minieap $(1)/usr/sbin/minieap
	$(INSTALL_DIR) $(1)/etc
	$(INSTALL_CONF) ./files/minieap.conf $(1)/etc/minieap.conf
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/minieap.init $(1)/etc/init.d/minieap
endef

$(eval $(call BuildPackage,minieap))
