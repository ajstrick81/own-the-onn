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

Google TV has no launcher picker, and on coffey CleanFrame cannot win the HOME
intent (see "Why not just disable the stock launcher" below). Instead the APK
carries a small accessibility service, `HomeGuardService`, that:

- claims the HOME key and opens CleanFrame;
- brings CleanFrame forward whenever the stock home screen surfaces on its own
  (after boot, or when BACK exits the last app);
- maps **long-press HOME** to the Google TV home screen, so stock stays one
  gesture away. CleanFrame's own Home control does the same.

No system package is disabled. Enable it:

```bash
adb shell settings put secure enabled_accessibility_services com.cleanframe.onn/com.cleanframe.onn.HomeGuardService
```

```bash
adb shell settings put secure accessibility_enabled 1
```

If `settings get secure enabled_accessibility_services` already lists another
service, append with `:` rather than overwriting it. Sideloaded apps cannot be
enabled from the Accessibility settings screen on Android 13+ ("restricted
setting"), which is why this goes through adb.

### Undo

```bash
adb shell settings delete secure enabled_accessibility_services
```

Or switch "CleanFrame home button" off under Settings > System > Accessibility.
Stock HOME behaviour returns immediately. A force-stop of CleanFrame also
turns the service off until it is re-enabled.

### Verified 2026-11-11

- Service binds and survives `adb install -r` and a reboot.
- After a reboot the device settles on CleanFrame with no input.
- When the stock home screen is started, CleanFrame replaces it in about 100 ms.
- The HOME key on the real remote reaches the service (logged
  `HOME released after 202ms`) and opens CleanFrame. `input keyevent` cannot
  test this: it injects below the accessibility key filter.
- HOME inside CleanFrame returns to the home stage from any screen without the
  "Leave Home?" prompt (that prompt belongs to BACK at the top level).
- **Not verified:** long-press HOME opening the Google TV home screen.

### Why not just disable the stock launcher

Tested 2026-11-09 and reverted. HOME candidates rank by intent-filter priority,
and only system packages may declare one above 0:

```
com.google.android.apps.tv.launcherx        priority 2
com.google.android.tungsten.setupwraith     priority 1
com.cleanframe.onn                          priority 0
com.android.tv.settings (FallbackHome)      priority -1000
```

With `launcherx` disabled, HOME resolves to `setupwraith/.RecoveryActivity` (the
setup wizard's recovery screen), not CleanFrame. `cmd package
set-home-activity` returns `Success` but does not override it. Disabling
`setupwraith` too would remove part of the device's recovery path, and the
device dropped off network adb during the revert. If you ever tried this,
`adb shell pm enable com.google.android.apps.tv.launcherx` undoes it.

## More than nine apps on Home

Upstream caps Home at nine because its "Apps on Home" editor draws the Home
column as a fixed list. `tools/patch-main.pl` (run by `sync-upstream.sh`) raises
the cap to 24 and makes that column scroll. The same script exposes upstream's
`goScene()` for the HOME key and relabels "Samsung Home" as "Google TV Home".
Those are the only edits to upstream's `main.js`; the sync fails if upstream's
lines stop matching. Change
`$HOME_CAP` in that script for a different limit.

## Known limitations on this hardware

| Upstream feature | On the Onn |
|---|---|
| HDMI input switching (`sources`/`setSource`) | **Not available.** The Onn is an HDMI source with no inputs. The row reports empty and is hidden. |
| Samsung Art Mode (`art`) | **No equivalent.** Opens Google TV's Ambient mode settings (`com.google.android.tv.settings.ambient`); coffey has neither `DREAM_SETTINGS` nor `DISPLAY_SETTINGS`. Verified 2026-11-11. |
| Samsung Home (`home`) | Mapped to the Google TV launcher, kept as an escape hatch. |
| App discovery | `PackageManager` leanback + phone launcher entries, instead of `tizen.application.getAppsInfo`. |
| App artwork | Android TV banners (16:9), served from `/icon/<package>.png`. Upstream's `iconPath` has no Android analogue. |
| Brand icons | Upstream's nine Samsung Tizen app IDs are remapped to Google TV packages in `DeviceBridge.kt`. Apps not in that map still appear, just without a brand glyph. |

## Verified on the device (2026-11-09)

Checked on the owner's unit, build `URO4.260304.011.B1`, via network adb:

- Installs, launches, renders, and does not crash.
- App discovery returns the installed apps, with Android TV banner artwork
  served through `IconPathHandler`.
- D-pad navigation works: RIGHT moves along the dock, UP reaches the controls
  row, BACK returns to the apps zone without finishing the Activity.
- The 15 bundled wallpapers and the adaptive-ink treatment load correctly.

### The density trap, if you port this elsewhere

CleanFrame's stage is absolutely positioned at a fixed 1920x1080, and upstream's
meta is `width=device-width, initial-scale=1`. On Tizen that yields a 1920 CSS px
viewport because the TV reports density 1. **coffey reports density 2**, so
device-width is 960 CSS px: the layout viewport becomes 960x540 and only the
stage's top-left quadrant is on screen. The symptom is a wallpaper and a clock
with no dock at all — it looks like the app failed to populate, when in fact the
dock is laid out correctly just below the fold.

`device.js` pins the viewport to `width=1920, height=1080` before `main.js`
takes its first measurement. Any device with a different density needs that
pin, not a change to the UI.

## Still unverified

- **First-paint time.** Not measured. If cold start drags, trimming the
  wallpaper set is the first lever.
- **Brand icon mapping.** None of the apps installed on this unit matched the
  brand map in `DeviceBridge.kt`, so the branded-glyph path is untested on
  hardware. Apps outside the map appear correctly with their own banners.
