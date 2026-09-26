# Handoff: onn 4K Streaming Stick (2026, "wayne") root attempt

Paste this into the new session. Status as of 2026-09-26.

> **Local values (kept out of the repo):** `<stick-ip>` is shown on the stick under Developer options → Wireless debugging
> (it was the reserved AdGuard client address). `<router-ip>` is the GL.iNet Flint 2 / AdGuard Home address. Ask the user if unsure.

## Goal
Find out whether this stick's bootloader can still be unlocked, and if it can, root it with Magisk.
The next action is a **read-only** fastboot check. Nothing has been flashed or unlocked yet.

## Device
- onn 4K Streaming Stick 2026: codename `wayne`, Realtek RTD1325, Android TV 14, 32-bit (armeabi-v7a), Virtual A/B
- Fingerprint: `onn/wayne/wayne:14/UKRB.260113.027.A1/14997501:user/release-keys`
- Security patch 2026-01-01, active slot `_b`, `verifiedbootstate=green`, `ro.boot.flash.locked=1`
- **OEM unlocking = ON** (`sys.oem_unlock_allowed=1`); USB debugging and Wireless debugging are ON
- IP **<stick-ip>** (Wi-Fi, router GL.iNet Flint 2 at <router-ip> running AdGuard Home)
- Serial starts `WUSA…`. Private: never publish it.

## The key problem
Source: three XDA guides by almyz125:
- setup without OTA: https://xdaforums.com/t/guide-walmart-onn-4k-streaming-stick-2026-google-tv-wayne-rtd1325-setup-without-forced-ota-update.4794193/
- unlock: https://xdaforums.com/t/guide-walmart-onn-4k-streaming-stick-2026-google-tv-wayne-rtd1325-unlock-the-bootloader.4794202/
- root: https://xdaforums.com/t/root-guide-walmart-onn-4k-streaming-stick-2026-google-tv-wayne-rtd1325-root-with-magisk.4794208/

What the threads report:
- Factory build `UKRB.251217.001.A1` unlocks.
- The update `UKRB.260113.027.A1` replaces the `bootcode` partition (the Realtek bootloader) with one where every fastboot
  command fails with `FAILED (remote: 'unknown reason')`, including `fastboot reboot`. A stick that is locked and on that
  build has no known way back.
- **This unit shipped from the factory on 260113.027.A1.** No update was installed during our setup. Nobody on XDA has
  reported testing a unit like this, so the result is new information either way.

## What's done
1. The update was blocked in AdGuard Home (custom rules, network-wide, still ON):
   `gvt1.com, gvt2.com, update.googleapis.com, dl.google.com, android.googleapis.com, play.googleapis.com,
   gmscompliance-pa.googleapis.com, mtalk.google.com, digitalassetlinks.googleapis.com, androidtvsetupwraithfe-pa.googleapis.com`
   (each written as `||domain^`).
2. Setup sequence that worked: all domains blocked → "cannot reach internet" → unblock **only** `android.googleapis.com`
   → reconnect → update fails → sign in → re-block **after** sign-in succeeds.
   **Lesson:** blocking `android.googleapis.com` during sign-in makes sign-in fail.
3. The Google TV home screen shows "Unable to load Home" while the blocks are on. Expected. Settings opens with a long-press on Home.
4. ADB was paired over Wi-Fi from the **first PC**. That pairing key belongs to that PC only.
5. `adb reboot bootloader` works: the TV goes black, meaning the stick is in the bootloader. But the first PC never saw a USB
   device on any of 3 ports. Cause: its USB-A to USB-C cable is **charge-only**.
   To leave the bootloader, unplug and replug the stick; even `fastboot reboot` may fail on a locked bootcode.

## AdGuard rules scoped to the stick only (optional, to un-break the rest of the network)
The network-wide block breaks Play Store downloads and Google updates on every device. For steady state, scope the rules to the stick:

1. In the GL.iNet admin page (http://<router-ip>), create a DHCP address reservation so the stick always gets **<stick-ip>**.
2. In AGH → Filters → Custom filtering rules, replace the network-wide lines with:
   ```
   ! --- onn wayne stick OTA block (scoped to the stick) ---
   ||gvt1.com^$client=<stick-ip>
   ||gvt2.com^$client=<stick-ip>
   ||update.googleapis.com^$client=<stick-ip>
   ||dl.google.com^$client=<stick-ip>
   ||android.googleapis.com^$client=<stick-ip>
   ||play.googleapis.com^$client=<stick-ip>
   ||gmscompliance-pa.googleapis.com^$client=<stick-ip>
   ||mtalk.google.com^$client=<stick-ip>
   ||digitalassetlinks.googleapis.com^$client=<stick-ip>
   ||androidtvsetupwraithfe-pa.googleapis.com^$client=<stick-ip>
   ```
   To toggle the sign-in exception, put `! ` in front of the `android.googleapis.com` line, then remove it again after sign-in.
3. Verify from a PC with `nslookup dl.google.com <router-ip>`. It should now return a real IP for the PC (it isn't
   <stick-ip>), and the AGH Query Log should still show **Blocked** for the stick's queries.

⚠️ **During any setup wizard, including setup pass 2 after the unlock wipe, use the NETWORK-WIDE rules, not the scoped ones.** A factory
reset gives Android a new randomized Wi-Fi MAC. The reservation then won't match and the stick may get a different IP,
which would slip past the `$client=` rules and let the update through. Switch to the scoped rules only after
setup finishes and the stick is confirmed at <stick-ip>. On the stick you can also set
Wi-Fi → network → Privacy → **Use device MAC**, so the reservation stays stable.

## Next: run on the SECOND computer (USB-C to USB-C data cable)
Needs Android platform-tools (`adb`, `fastboot`) on that computer, and the computer must be on the same network (your LAN).
ADB is **Wi-Fi only** on this stick; fastboot is **USB only**.

1. Keep the stick's HDMI on the TV. Connect its USB-C to the computer with a USB-C cable that carries data, and let it boot to Android.
2. Pair ADB again, because this is a new computer. On the stick: Settings → System → Developer options → Wireless debugging →
   "Pair device with pairing code".
   ```
   adb pair <stick-ip>:<pairing_port>      # enter the 6-digit code
   adb connect <stick-ip>:<connect_port>   # port from the main Wireless debugging screen
   adb shell getprop ro.build.id              # expect UKRB.260113.027.A1
   ```
3. The read-only test:
   ```
   adb reboot bootloader
   fastboot devices
   fastboot getvar unlocked
   ```
   - If `fastboot devices` is empty on Windows: check Device Manager. If there's an unknown device, install the Google USB
     Driver or bind WinUSB with Zadig. If there's nothing at all, it's the cable or port.
   - **`unlocked: no`** → the bootloader's fastboot is alive. You can unlock (step 4).
   - **`FAILED (remote: 'unknown reason')`** → locked for good. Pull power to leave. Optional harmless check:
     `adb reboot fastboot` (userspace fastbootd), then `fastboot getvar unlocked`. Then plan to RETURN the stick
     (turn OEM unlocking back off first).

## If it unlocks (step 4 onward)
- `fastboot flashing unlock` **WIPES the stick**. Then set up again with the same block sequence (lesson in step 2 above).
- After setup: Developer options again, pair ADB again, then `adb shell getprop ro.boot.verifiedbootstate` should say `orange`.
- Root: Magisk **v30.7**, from GitHub releases only. A stock init_boot for **260113.027** is attached to the XDA root thread:
  `init_boot_onn-wayne-stock_49278be4ee8467becc7bf57bc6f799447c488812d1ec0db94044430464a98118_UKRB.260113.027.A1_14997501.img`
  (download needs an XDA login; check the SHA256 against the filename). Patch it on the device with Magisk's `boot_patch.sh`,
  using the armeabi-v7a libs from the APK. Flash via **fastbootd**: `adb reboot fastboot`, then `fastboot flash init_boot_<slot>`.
  Verify with `adb shell /debug_ramdisk/su -c id`.
- ⚠️ One XDA report: flashing images in fastbootd on 260113 plus a Magisk init_boot bricked a stick permanently. Read
  the root thread in full before flashing, and keep the stock init_boot.

## Rules for the session
- Never let the stick online without the AdGuard blocks. It could update to `UKRB.260113.075.A1`.
- Only read-only commands until the user approves the unlock (it wipes) or any flash.
- Guide the user one step at a time. They do the TV and remote steps; the agent runs adb and fastboot.
- Record results. Plan: a rooting guide in the user's `own-the-onn` repo (`guides/rooting`), only from verified steps,
  crediting almyz125, BigEmpty and moderndogs, linking to firmware images rather than rehosting them.
