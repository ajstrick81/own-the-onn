# Installing CleanFrame on the onn 4K Plus (`coffey`)

Device this was written against: onn 4K Plus Streaming, `coffey`, Amlogic S905X5M,
build `onn/coffey/coffey:14/URO4.260304.011.B1/15051976` (Android 14).

**No root and no bootloader unlock are required.** Everything here is sideloading
plus `adb` on an owner's own device. That matters because `coffey`'s bootloader is
welded shut — see `research/root-study.md` in the parent repository. A replacement
home screen does not need and does not attempt to touch any of that.

## 1. Build the APK

```bash
tools/sync-upstream.sh
```

```bash
./gradlew :app:assembleDebug
```

The APK lands at `app/build/outputs/apk/debug/app-debug.apk`.

`sync-upstream.sh` must run first: the build deliberately fails with
"Upstream CleanFrame assets are missing" rather than producing an APK that boots
to a blank screen on the TV.

## 2. Enable ADB on the device

On the Onn: **Settings → System → About → Build** (click 7 times) to enable
Developer options, then **Settings → System → Developer options → USB debugging**
and **Network debugging**. Note the IP under Settings → Network.

```bash
adb connect <onn-ip>:5555
```

Accept the authorisation prompt on the TV. Confirm you are talking to the right
device before anything else:

```bash
adb shell getprop ro.build.fingerprint
```

That should print the `onn/coffey/coffey:14/...` fingerprint above.

## 3. Install

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

At this point CleanFrame appears in the Google TV apps row. **Open it from there
first.** Confirm the UI draws, the D-pad moves focus, OK launches an app and BACK
steps back inside the UI. Do not proceed to step 4 until that all works — step 4
is the part that can leave you without a usable home screen.

## 4. Promote it to the home screen

Google TV has no launcher picker, so the stock launcher has to be stood down.
This is reversible and does **not** require root.

Take the recovery path first:

```bash
adb shell pm list packages | grep -E 'launcherx|tvlauncher'
```

Then disable the stock launcher for the current user:

```bash
adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
```

Press HOME on the remote. CleanFrame should come up.

### Undo

```bash
adb shell pm enable com.google.android.apps.tv.launcherx
```

If you are locked out with no working home screen and ADB still connects, that
single command restores the stock launcher. **Keep a second device with `adb`
reachable before you run step 4.** If ADB is not reachable and HOME does nothing,
the remaining route is a factory reset from recovery.

## Known limitations on this hardware

| Upstream feature | On the Onn |
|---|---|
| HDMI input switching (`sources`/`setSource`) | **Not available.** The Onn is an HDMI source with no inputs. The row reports empty and is hidden. |
| Samsung Art Mode (`art`) | **No equivalent.** Mapped to the Google TV ambient/screensaver setting. |
| Samsung Home (`home`) | Mapped to the Google TV launcher, kept as an escape hatch. |
| App discovery | `PackageManager` leanback + phone launcher entries, instead of `tizen.application.getAppsInfo`. |
| App artwork | Android TV banners (16:9), served from `/icon/<package>.png`. Upstream's `iconPath` has no Android analogue. |
| Brand icons | Upstream's nine Samsung Tizen app IDs are remapped to Google TV packages in `DeviceBridge.kt`. Apps not in that map still appear, just without a brand glyph. |

## Things worth verifying on the device

These are untested predictions until someone runs them on real hardware:

- **D-pad feel in WebView.** CleanFrame drives focus itself and the key map
  already matches what WebView delivers, but WebView's own focus handling can
  still interfere. This is the most likely thing to need tuning.
- **First-paint time.** 16 MB of wallpapers from local assets on an S905X5M;
  if cold start is slow, trimming the wallpaper set is the first lever.
- **HOME re-press behaviour.** `__cleanframeHome()` currently steps back one
  level, which is an approximation rather than a verified-correct behaviour.
- **Ambient/screensaver intent.** `android.settings.DREAM_SETTINGS` is not
  guaranteed present on every Google TV build.
