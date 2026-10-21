# Feed signing keys

The binary apk feed is signed with an EC P-256 key. Only the public key belongs
in this directory and in git.

- `public-key.pem` — committed; published at the root of the Pages site and
  installed on devices as `/etc/apk/keys/openwrt-packages.pem`.
- `private-key.pem` — **never committed**. Store it outside the repository and
  add it to GitHub Actions as the `APK_PRIVATE_KEY` secret.

## Generate a key pair

```sh
mkdir -p ~/.config/openwrt-packages
openssl ecparam -name prime256v1 -genkey -noout \
  -out ~/.config/openwrt-packages/private-key.pem
openssl ec -in ~/.config/openwrt-packages/private-key.pem -pubout \
  -out keys/public-key.pem
chmod 600 ~/.config/openwrt-packages/private-key.pem
```

## Configure GitHub Actions

```sh
gh secret set APK_PRIVATE_KEY < ~/.config/openwrt-packages/private-key.pem
```

## Rotation

1. Generate a new pair.
2. Add the new public key to devices while the old key is still trusted.
3. Publish a feed signed with the new key.
4. Remove the old public key after the old index is gone.

The private key is only used in the `sign` job, which does not execute package
build scripts. Do not pass it to the build job.
