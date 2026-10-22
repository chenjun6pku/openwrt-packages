#!/bin/sh
set -eu

BASE_URL="${FEED_BASE_URL:-https://chenjun6pku.github.io/openwrt-packages}"
KEY_URL="$BASE_URL/public-key.pem"
KEY_PATH="/etc/apk/keys/openwrt-packages.pem"
FEEDS_FILE="/etc/apk/repositories.d/customfeeds.list"

[ "$(id -u)" = "0" ] || {
	echo "Please run this script as root." >&2
	exit 1
}

[ -r /etc/openwrt_release ] || {
	echo "This does not look like an OpenWrt system." >&2
	exit 1
}

. /etc/openwrt_release

case "${DISTRIB_RELEASE:-}" in
	25.*) ;;
	*)
		echo "Unsupported OpenWrt release: ${DISTRIB_RELEASE:-unknown}" >&2
		echo "This feed supports OpenWrt 25.x only." >&2
		exit 1
		;;
esac

case "${DISTRIB_ARCH:-}" in
	x86_64|aarch64_cortex-a53|mipsel_24kc)
		arch="$DISTRIB_ARCH"
		;;
	*)
		echo "Unsupported architecture: ${DISTRIB_ARCH:-unknown}" >&2
		echo "Supported: x86_64, aarch64_cortex-a53, mipsel_24kc" >&2
		exit 1
		;;
esac

FEED_URL="$BASE_URL/25.12.6/$arch/custom/packages.adb"
TMP_KEY="$(mktemp /tmp/openwrt-packages-key.XXXXXX)"
trap 'rm -f "$TMP_KEY"' EXIT

fetch() {
	if command -v uclient-fetch >/dev/null 2>&1; then
		uclient-fetch -O "$2" "$1"
	elif command -v wget >/dev/null 2>&1; then
		wget -O "$2" "$1"
	else
		echo "Neither uclient-fetch nor wget is available." >&2
		return 1
	fi
}

echo "Downloading feed signing key..."
fetch "$KEY_URL" "$TMP_KEY"

[ -s "$TMP_KEY" ] || {
	echo "Downloaded key is empty." >&2
	exit 1
}

head -n 1 "$TMP_KEY" | grep -q 'BEGIN PUBLIC KEY' || {
	echo "Downloaded key is not a PEM public key." >&2
	exit 1
}

mkdir -p /etc/apk/keys /etc/apk/repositories.d
cat "$TMP_KEY" > "$KEY_PATH"
chmod 644 "$KEY_PATH"

touch "$FEEDS_FILE"
grep -vF "$BASE_URL" "$FEEDS_FILE" > "$FEEDS_FILE.tmp" || true
echo "$FEED_URL" >> "$FEEDS_FILE.tmp"
mv "$FEEDS_FILE.tmp" "$FEEDS_FILE"

echo "Configured feed: $FEED_URL"
apk update

echo
echo "Done. Install a package with: apk add <package>"
