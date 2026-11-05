# Device checks + OTA currency — 2026-11-04

| File | Content |
|---|---|
| [`COFFEY-DEVICE-CHECKS.md`](COFFEY-DEVICE-CHECKS.md) | Read-only `adb` properties from the owner's unit, OTAChecker currency scan, a noted public coffey GhostLock repo |

Verifies against [`SHA256SUMS.txt`](SHA256SUMS.txt).

## Bottom line

- The owner's unit runs **exactly** the analyzed build (`URO4.260304.011.B1/15051976`), so every offline result applies to it.
- The bootloader reports **locked + green** (`ro.boot.flash.locked=1`): C5 goes from B to P.
- `adbd` and ART are still the shipped `340090000` modules: the R4 rows that hinged on Play updates firm up.
- No newer coffey build appears in OTAChecker entries 2502–2900 (bounded negative).
- A public coffey-specific GhostLock repo exists (R, not opened); it supersedes R2-3's "no coffey root work" negative.
