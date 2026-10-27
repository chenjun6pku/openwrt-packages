# Feed signing keys

The binary apk feed is signed with an EC P-256 key. Only public keys belong in
this directory and in git.

- `public-key.pem` — committed; published at the root of the Pages site and
  installed on devices as `/etc/apk/keys/openwrt-packages.pem` for backward
  compatibility.
- Additional `*.pem` files — optional rotation keys. `feed.json` lists their
  install names, SHA-256 hashes and status.
- `private-key.pem` — **never committed**. Store it outside the repository and
  add it to GitHub Actions as the `APK_PRIVATE_KEY` secret.

## Configure `feed.json`

`feed.json.signing` is the source of truth:

```json
{
  "signing": {
    "active": "2026",
    "keys": [
      {
        "id": "2026",
        "file": "keys/public-key.pem",
        "install_name": "openwrt-packages.pem",
        "sha256": "<sha256 of the PEM file>",
        "status": "active"
      }
    ]
  }
}
```

Status values:

- `active` — the key used by the sign job; exactly one key must be active.
- `trusted` — published and installed by the device installer, but not used for
  signing. Use this for the grace period during rotation.
- `retired` — no longer published or used to verify `feed-state.json`.

The installer downloads `keys/keyring.sha256`, verifies every key's SHA-256 and
only then installs all active/trusted keys. It prunes only
`openwrt-packages*.pem` files that are no longer in the manifest.

## Generate a key pair

```sh
mkdir -p ~/.config/openwrt-packages
openssl ecparam -name prime256v1 -genkey -noout \
  -out ~/.config/openwrt-packages/private-key.pem
openssl ec -in ~/.config/openwrt-packages/private-key.pem -pubout \
  -out keys/public-key.pem
chmod 600 ~/.config/openwrt-packages/private-key.pem
sha256sum keys/public-key.pem
```

Put the printed SHA-256 into the matching `feed.json` key entry. `scripts/feed_meta.py check`
fails if the file or hash does not match, and the sign job also compares the
private key's DER public key with the active public key.

## Configure GitHub Actions

```sh
gh secret set APK_PRIVATE_KEY < ~/.config/openwrt-packages/private-key.pem
```

## Rotation

1. Add the new public key as a `trusted` entry in `feed.json` (keep the old
   `active` entry) and publish a release. Give the pending key a distinct
   `install_name` such as `openwrt-packages-2027.pem`; the active key must keep
   `openwrt-packages.pem`. The keyring now contains both keys.
2. Have devices re-run `install-feed.sh` during the grace period so they trust
   both keys. The old index is still signed by the old key.
3. Change `APK_PRIVATE_KEY`, make the new key `active` with
   `install_name: openwrt-packages.pem`, give the old key a distinct install
   name (for example `openwrt-packages-2026.pem`) and keep it `trusted`, then
   publish a release. Devices that already trusted the new key can verify the
   new index even if they have not re-run the installer again.
4. After devices have migrated, mark the old key `retired` and publish again.
   It is removed from the keyring and from state verification.

`apk mkndx` signs an index with one key. A device that only trusts the old key
cannot verify an index signed by the new key, so step 2 must happen before
step 3.

The keyring manifest prevents corruption, partial installs and stale keys. It
is fetched from the same HTTPS origin as the feed, so HTTPS and repository
review remain the first-install trust anchor.
