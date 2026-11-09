# cleanframe-onn

A port of [CleanFrame](https://github.com/nthnclrk/CleanFrame) — a quiet,
remote-first home screen — from Samsung Tizen to the **onn 4K Plus Streaming**
(`coffey`, Google TV / Android 14).

> **Status: running on hardware.** Installed and verified on the owner's onn
> 4K Plus (`coffey`, build `URO4.260304.011.B1`) on 2026-11-09: renders, lists
> installed apps with their banners, and D-pad/BACK navigation works. It has
> **not** been promoted to the system home screen: disabling the stock launcher
> does not work on coffey (`setupwraith` takes HOME instead) and was reverted. See
> [`docs/install.md`](docs/install.md) for what is verified and what is not.

No root. No bootloader unlock. This is a sideloaded APK plus `adb` on the
owner's own device, and it does not touch the boot chain studied in the parent
repository.

## Why this is a small port

Upstream is a Tizen web app, and the entire Tizen surface lives in one file.
`app/device.js` is 143 lines exposing nine methods on `window.FrameDevice`;
`app/main.js` is 1,922 lines of UI with **no** Tizen calls at all. Upstream's key
map is already `{37:left, 38:up, 39:right, 40:down, 13:ok, 27:back}`, which is
exactly what Android WebView delivers for a D-pad.

So the port reimplements that one file and leaves everything else alone:

```
upstream app/main.js  (1922 lines)  ->  used verbatim
upstream app/style.css (635 lines)  ->  used verbatim
upstream app/assets/   (16 MB)      ->  used verbatim, fetched not vendored
upstream app/device.js (143 lines)  ->  REPLACED  (assets/platform/device.js)
upstream app/config.xml (Tizen)     ->  REPLACED  (AndroidManifest.xml)
```

## How it fits together

| Piece | Role |
|---|---|
| `HomeActivity.kt` | Hosts the UI in a WebView, declares `CATEGORY_HOME`, routes the remote's BACK/HOME into the web layer |
| `DeviceBridge.kt` | `@JavascriptInterface` implementation of the nine capabilities: app discovery via `PackageManager`, launching via `Intent` |
| `IconPathHandler.kt` | Serves installed-app banners as `/icon/<package>.png` |
| `assets/platform/device.js` | ES5 shim re-exposing the bridge as `window.FrameDevice`, so `main.js` is untouched |
| `tools/sync-upstream.sh` | Fetches upstream `app/` at the pinned tag, swaps in the Android `device.js` |

Assets are served over the virtual origin `https://appassets.androidplatform.net`
rather than `file://`, because CleanFrame persists preferences in `localStorage`
and Web Storage on a `file://` document is unreliable on modern WebView.

## Build

```bash
tools/sync-upstream.sh && ./gradlew :app:assembleDebug
```

Full device steps, including how to promote it to the home screen and how to
undo that, are in [`docs/install.md`](docs/install.md).

## Upstream assets are fetched, never committed

`app/src/main/assets/web/` is git-ignored. Upstream's `app/` directory is ~16 MB
of wallpapers, materials, licensed icon sets and fonts whose
`THIRD_PARTY_NOTICES.md` does not certify redistribution rights, and this
repository's own rule is to keep vendor blobs out of git. `UPSTREAM` pins the
revision (`v0.7.0`, commit `845f332`) and `sync-upstream.sh` verifies the tag
still resolves to that commit before copying anything.

Upstream's paid Pangram fonts are not involved: `app/assets/private-fonts.css`
is an empty stub in the public tree, so nothing proprietary is fetched.

## Licence

Port code here is MIT, matching upstream. Upstream's fonts, photographs and
icons keep their own terms — see upstream `THIRD_PARTY_NOTICES.md`.

Credit for the design, and for the clean platform seam that made this port a
single file, goes to [nthnclrk/CleanFrame](https://github.com/nthnclrk/CleanFrame).
