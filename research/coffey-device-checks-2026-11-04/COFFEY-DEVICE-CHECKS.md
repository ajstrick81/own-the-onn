# coffey read-only device checks + OTA currency — 2026-11-04

Two quick checks that tie the offline analysis to the owner's actual unit and to the current public build.

## 1. Read-only `adb` properties from the owner's unit (grade **P**, device-reported)

Run by the maintainer from their own PC over network ADB (`adb connect <LAN IP>:5555`). Read-only property and
package queries; nothing was changed on the device.

| Query | Result | What it settles |
|---|---|---|
| `getprop ro.build.fingerprint` | `onn/coffey/coffey:14/URO4.260304.011.B1/15051976:user/release-keys` | The unit runs **exactly** the build analyzed in the OTA capture, R4, Phase B–F packets |
| `getprop ro.boot.verifiedbootstate` | `green` | Bootloader reports verified boot with the OEM key |
| `getprop ro.boot.flash.locked` | `1` | Bootloader reports **locked** (C5 moves from B to P, device-reported) |
| `pm list packages --apex-only --show-versioncode` | `com.android.adbd` **340090000**, `com.android.art` **340090000** (29 of 32 APEX modules at factory versions; only `extservices` 361153323, `permission` 361524000, `widevine.nonupdatable` 343700000 differ) | Play system updates have **not** replaced the `adbd` or ART modules: the unit runs the shipped modules analyzed in R4 |

Full module list as reported: `configinfrastructure`, `tzdata`, `mediaprovider`, `resolv`, `media`, `adservices`,
`ondevicepersonalization`, `scheduling`, `btservices`, `neuralnetworks`, `conscrypt`, `tethering`, `os.statsd`,
`adbd`, `uwb`, `appsearch`, `healthfitness`, `media.swcodec`, `wifi`, `art`, `ipsec`, `sdkext` all at
`340090000`; `rkpd`, `vndk.v34`, `virt` (2), `apex.cts.shim`, `runtime`, `i18n`, `devicelock` at `1`;
`extservices`, `permission`, `widevine.nonupdatable` as above.

## 2. Is there a newer coffey OTA? (grade **P**, bounded)

| Source | Search space | Result |
|---|---|---|
| OTAChecker #2594 | the entry itself | `URO4.260304.011.B1/15051976`, SPL 2026-03-01, built 2026-03-19, found 2026-09-23; source build `onn/coffey/coffey:13/URO1.250103.020.A2/13277964`; links no other coffey entries |
| OTAChecker `/list` | pages 1–8 (entry IDs 2502–2900, i.e. everything found since #2594), raw HTML grepped for `coffey` and `onn/` fingerprints | **No newer coffey entry.** The only coffey string is #2594's own Android 13 source fingerprint. Other onn devices present (`jarvis`, `wayne`, tablets) |
| Field report | [cleanyourtv-app issue #6489](https://github.com/udhaykumarbala/cleanyourtv-app/issues/6489), dated 2026-11-04 | Another unit on the same `URO4.260304.011.B1/15051976` fingerprint today (R) |

**Reading:** as of 2026-11-04, `URO4.260304.011.B1` (SPL 2026-03-01) is the newest public coffey build found,
and the owner's unit is on it. Bounded negative: OTAChecker's catalog only, entries 2502–2900. Google's OTA
service can serve builds the catalog hasn't seen.

## 3. Noted in passing (grade **R**, not verified)

A public repository, [`chaitan3/ghostlock-coffey`](https://github.com/chaitan3/ghostlock-coffey), describes itself
as a CVE-2026-43499 (GhostLock) root exploit for the onn 4K Plus (`coffey`) on `URO4.260304.011.B1`, claimed to
work on a locked bootloader with no UART. Its code was **not** opened or used here. Recorded only because it
changes two repo statements: the R2-3 bounded negative ("no prior coffey-specific root work") and the
"public PoCs are jarvis2-specific" hard wall. It's consistent with C14 (GhostLock affected code present in
coffey's kernel). Per-boot kernel root still doesn't touch the bootloader lock (C5).
