#!/usr/bin/env bash
# Fetch CleanFrame's web UI at the pinned revision into the APK's assets.
#
# Upstream's app/ directory is ~16 MB of wallpapers, materials, licensed icon
# sets and fonts. THIRD_PARTY_NOTICES.md does not certify redistribution rights
# for those assets, and this repository's own rule is to keep vendor blobs out
# of git and pin them by hash instead. So they are fetched here, never committed.
#
# Usage:  tools/sync-upstream.sh [--force]
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest="$here/app/src/main/assets/web"
platform="$here/app/src/main/assets/platform"

# shellcheck source=/dev/null
source "$here/UPSTREAM"

if [[ -f "$dest/index.html" && "${1:-}" != "--force" ]]; then
  echo "Upstream assets already present at app/src/main/assets/web"
  echo "Re-run with --force to refetch."
  exit 0
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

echo "Fetching $CLEANFRAME_REPO at $CLEANFRAME_TAG ..."
git -c advice.detachedHead=false clone --quiet --depth 1 \
  --branch "$CLEANFRAME_TAG" "$CLEANFRAME_REPO" "$work/src"

actual="$(git -C "$work/src" rev-parse HEAD)"
if [[ "$actual" != "$CLEANFRAME_COMMIT" ]]; then
  echo "ERROR: $CLEANFRAME_TAG resolves to $actual," >&2
  echo "       but UPSTREAM pins $CLEANFRAME_COMMIT." >&2
  echo "       A pinned tag moved. Review upstream before bumping UPSTREAM." >&2
  exit 1
fi
echo "Verified pinned commit $actual"

rm -rf "$dest"
mkdir -p "$dest"
cp -R "$work/src/app/." "$dest/"

# config.xml is the Tizen widget manifest; AndroidManifest.xml replaces it.
rm -f "$dest/config.xml"

# Swap the Tizen platform layer for the Android one. This is the whole port:
# main.js, style.css and every asset are used exactly as upstream ships them.
cp "$platform/device.js" "$dest/device.js"

# The one edit to upstream's own code: lift the nine-app Home limit. Fails the
# sync if upstream's lines no longer match. See tools/patch-main.pl.
perl "$here/tools/patch-main.pl" "$dest/main.js"

cat > "$dest/UPSTREAM-PROVENANCE.txt" <<PROV
CleanFrame web assets fetched by tools/sync-upstream.sh
Repository: $CLEANFRAME_REPO
Tag:        $CLEANFRAME_TAG
Commit:     $actual

device.js has been replaced with the Android implementation from
app/src/main/assets/platform/device.js. config.xml (Tizen manifest) removed.
main.js has been patched by tools/patch-main.pl to lift the nine-app Home
limit. Everything else is upstream, unmodified. Upstream is MIT; bundled fonts,
photographs and icons keep their own terms -- see THIRD_PARTY_NOTICES.md.
PROV

echo
echo "Synced to app/src/main/assets/web (git-ignored)"
du -sh "$dest" 2>/dev/null || true
echo "device.js: $(head -1 "$dest/device.js")"
