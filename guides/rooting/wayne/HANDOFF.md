# Handoff: onn 4K Streaming Stick (2026, "wayne") root attempt

Paste this into the new session. Status as of 2026-09-26.

> **Local values (kept out of the repo):** `<stick-ip>` is shown on the stick under Developer options → Wireless debugging
> (it was the reserved AdGuard client address). `<router-ip>` is the GL.iNet Flint 2 / AdGuard Home address. Ask the user if unsure.

## RESULT — 2026-09-26: bootloader cannot be unlocked; stick cannot be rooted

The read-only fastboot check was run on the second PC (Windows 11, USB-C data cable, WinUSB bound with Zadig). Outcome:

- Device booted normally on factory build `UKRB.260113.027.A1`; every property was unchanged from this handoff (`sys.oem_unlock_allowed=1`, `ro.boot.flash.locked=1`, `verifiedbootstate=green`, slot `_b`, abi `armeabi-v7a`). No OTA slipped through — the AdGuard blocks held.
- `adb reboot bootloader` worked. The stick entered the bootcode bootloader and enumerated over USB as a Google fastboot device (`USB\VID_18D1&PID_4E40`, serial `WUSA…`). Windows showed Code 28 (no driver) until WinUSB was bound with Zadig on that exact `18D1/4E40` device; after that `fastboot devices` listed it.
- With the driver bound, **every fastboot command failed identically** with `FAILED (remote: 'unknown reason')`: `getvar unlocked`, `getvar all`, `getvar product`, `getvar current-slot`, `getvar version`, `getvar partition-type:boot`, `getvar is-userspace`, and `fastboot reboot`.
- Leaving the bootloader required a power-cycle (unplug/replug), since `fastboot reboot` also fails.

**Conclusion:** this unit **shipped from the factory locked on `260113.027.A1`**, and its bootcode fastboot rejects all commands while locked — the same dead-fastboot behavior XDA reported for units that *updated* into `027`. Because the bootloader is locked and fastboot will not accept `flashing unlock`, **there is no way to unlock, and therefore no known way to root, this stick.** This appears to be the first recorded test of a factory-`027` unit, and the result matches the updated-unit reports: no known way back.

Userspace fastbootd (`adb reboot fastboot`) was not attempted and is not a workaround — flashing there still requires an unlocked bootloader, which is unreachable here.

### Cleanup / next
- **Returning the stick:** turn **OEM unlocking OFF** (Developer options) to restore the normal factory-locked state.
- **Keeping the stick:** leave the AdGuard OTA blocks on (or scope them to the stick, section below) so it can't update to `260113.075.A1`.
  *(Superseded by PIVOT below: the stick is kept and updated.)*

## PIVOT (2026-09-26): keep the stick as a second test device, and let it update

The stick stays as a **second Morphe test device**. It has a different chip from the main test unit (Realtek RTD1325 vs the
Amlogic S905X5M in the onn 4K Plus "coffey"); both are 32-bit armeabi-v7a. The AdGuard OTA blocks were **removed** and the stick
was allowed to update. Updating costs nothing unlock-wise (see the bootcode finding below).

### The 027 → .075 update package (captured and decoded)
- URL, taken from the stick's own log (`adb shell logcat -d -b all | grep system_update`; tags `system_update`,
  `SystemUpdate`, `update_engine` "initial url"):
  `https://android.googleapis.com/packages/ota-api/package/a071255680cfc22e0fdaaa81ff92e621ab865e9c.zip`
  (the earlier 251217 → 027 package posted on XDA by BigEmpty is `…/1c3424dc57b4b031859673c52caee97b806a154c.zip`)
- 85,362,772 bytes; `payload.bin` SHA256 (base64) `D7w0pbX/UXJg7z8UA/KXKODWVcQ4NSsmuC3pbQtvqXY=`, verified after download.
- `pre-build`: `UKRB.260113.027.A1/14997501` → `post-build`: **`UKRB.260113.075.A1/15646418`**, security patch
  2026-06-01, timestamp 1781542725 (2026-06-15). `ota-type=AB`, payload v2, **incremental** (29 partitions).
- The same URL was already logged on the stick's first setup attempt. That's the download the AdGuard block stopped.
- Tip: live `adb logcat` over Wi-Fi stalled on this stick. Use `logcat -d` dumps instead.

### What changes in .075
| Partition | Change | Note |
|---|---|---|
| `bootcode` | **SOURCE_COPY only**; result sha256 `4c0f826fcfe9e459…` | = XDA's "260113.027 OTA bootcode". **.075 keeps the same fastboot-dead bootloader**, so the unlock gate is unchanged |
| `init_boot` | BROTLI_BSDIFF against 027; result sha256 `96b387e8361153eb…` (full value in the payload manifest) | rebuildable, see below |
| `boot`, `vendor_boot`, `dtbo`, `vbmeta*` | diffs | new kernel/ramdisk and verified-boot metadata |
| `system`, `system_ext`, `product`, `vendor`, `vendor_dlkm` | BSDIFF + ZUCCHINI | normal OS update |
| `hifi`, `video` | full REPLACE; `audio` diff | Realtek audio and video processor firmware |
| `rescueRootFS`, `rescueDT`, `ta`, `pcpu` | copy or diff | Realtek rescue system, trusted apps, secure CPU. Worth a look for the privacy study |

### Why a rebuilt .075 init_boot matters (for OTHER people's sticks)
It's no use on this locked unit, but it fills a real gap:

- **Who needs it:** anyone whose stick was unlocked while on 251217 and then updated to .075. Unlocked sticks stay
  unlocked across updates, and fastbootd still works for them. XDA user **Broly** is exactly this case: unlocked, then
  updated to `UKRB.260113.075.A1/15646418`. They asked in the root thread for the latest build's link and init_boot, and
  couldn't root because **no stock .075 init_boot has been posted**.
- **Why they can't just dump it:** reading the `init_boot` partition off the device needs root, which is what they're
  trying to get. So the image has to come from the update package.
- **Why not flash the 027 image instead:** Magisk patches the init_boot ramdisk, which has to match the running kernel,
  vendor_boot and build. A mismatched image is a gamble on a bootloop. The root thread already reports one stick bricked
  by mixing images after 027, so a matching image is the safe path.
- **Why the update package alone isn't enough:** the package is incremental. It holds `init_boot` only as a patch against
  the 027 image, not as a full image.
- **How to rebuild it:** apply the payload's `init_boot` operations (SOURCE_COPY + BROTLI_BSDIFF + ZERO) to the stock 027
  init_boot from the XDA root thread (`49278be4…`). AOSP's `update_payload` / `ota_extractor`, or a payload dumper with
  incremental support, can do this.
- **Correctness is provable, not guessed:** the manifest carries the expected sha256 of **both** the 027 input and the .075
  output. If the rebuilt image hashes to `96b387e8…`, it's byte-for-byte what `update_engine` writes on a real stick.
- **How to share it without redistributing firmware:** publish the method, both hashes and a small script. Anyone can then
  rebuild the image from Google's public update URL plus XDA's 027 image. Post that recipe in the XDA root thread
  (crediting almyz125, BigEmpty and Broly).
- **Needed first:** the 027 init_boot image (the XDA attachment needs a login to download). Local copies of the update
  package and notes are kept off-repo.

---

## Goal
Find out whether this stick's bootloader can still be unlocked, and if it can, root it with Magisk.
~~The next action is a **read-only** fastboot check.~~ **Done — see RESULT above. The bootloader is locked with dead fastboot; it cannot be unlocked or rooted.** Nothing was flashed or unlocked.

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
