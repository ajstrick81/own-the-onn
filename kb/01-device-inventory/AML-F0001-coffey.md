---
finding_id: AML-F0001
title: "Device inventory — onn 4K Plus (coffey)"
component: device-inventory
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0001
  - AML-S0003
source_urls: []
source_revision: "URO4.260304.011.B1 (build 15051976), SPL 2026-03-01"
related_findings:
  - AML-F0002
  - AML-F0003
status: promoted
---

# Device inventory — onn 4K Plus (coffey)

All values are **device-reported** (getprop / kernel interfaces), not
independent hardware measurements.

| Field | Value | Confidence | Source |
|---|---|---|---|
| Marketing name | onn. 4K Plus Streaming (brand onn) | confirmed | AML-S0003 |
| Codename / platform | coffey / s7d | confirmed | AML-S0003 |
| SoC | Amlogic S905X5M (`ro.soc.model AMLS905X5M`) | confirmed | AML-S0003 |
| SoC family / generation | S7D | confirmed | AML-S0003 |
| CPU core | ARM Cortex-A55 (impl 0x41, part 0xd05, ARMv8-A) | confirmed | AML-S0003 |
| Userland arch | 32-bit (`abilist armeabi-v7a,armeabi`) | confirmed | AML-S0003 |
| Kernel bitness | 64-bit GKI (arm64) | probable | AML-S0003 |
| Android version | 14 (SDK 34) | confirmed | AML-S0003 |
| Security patch level | 2026-03-01 | confirmed | AML-S0003 |
| Kernel version | 5.15.196-android14-11-g3d26c188ef7e-ab14657224 (clang 17, +pgo +bolt +lto) | confirmed | AML-S0003 |
| Firmware build id | URO4.260304.011.B1 (build 15051976), coffey-user, release-keys | confirmed | AML-S0003 |
| Bootloader / verified boot | flash locked, verifiedbootstate green, AVB 1.2 (sha256), vbmeta state locked | confirmed | AML-S0003 |
| Board revision | not obtainable read-only (DT model absent, DT compatible denied) | unknown | — |

## Notes
Device identity is settled against the device's own build properties and kernel
interfaces (AML-S0003, read-only), re-confirming and tightening the earlier
public-derived facts (AML-S0001 / `root-study.md`).

Discipline: `uname` returns `armv8l` from a 32-bit adb shell, which does not by
itself prove a 64-bit kernel; the arm64-GKI claim (`ab14657224`) is marked
**probable** pending a 64-bit-context confirmation. Board revision stays
`unknown` — the Device-Tree `model` node is absent and `compatible` is
permission-denied without root (recorded, not escalated). The locked /
verifiedbootstate-green / AVB values are **device-reported state**, not an
independent cryptographic attestation (the device reports the bootloader's
outcome; we did not re-verify the AVB chain).

Partition/boot architecture → `AML-F0002`; diagnostic interfaces → `AML-F0003`.
