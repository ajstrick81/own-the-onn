---
finding_id: AML-F0002
title: "coffey partition & boot architecture (A/B + Virtual A/B dynamic, AVB-locked)"
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0003
source_urls: []
source_revision: "URO4.260304.011.B1"
related_findings:
  - AML-F0001
status: promoted
---

# coffey partition & boot architecture

## Observations (device-reported, read-only)
- `ro.boot.dynamic_partitions = true`, `ro.virtual_ab.enabled = true`,
  `ro.build.ab_update = true`, `ro.treble.enabled = true`,
  `ro.boot.slot_suffix = _b` (booted slot B at capture).
- `/dev/block/mapper` shows dm-verity-backed **logical (super) partitions** on
  the `_b` slot — `odm_b`, `odm_dlkm_b`, `product`, `oem` — each with a
  `*-verity` device and a `*-cow` (Virtual A/B snapshot) node.
- Backing storage is **eMMC** `mmcblk0` (with `mmcblk0boot0/boot1`); 31 physical
  partitions `mmcblk0p1..p31` are present via `/dev/block/by-name`.
- Verified boot: `ro.boot.flash.locked = 1`, `ro.boot.verifiedbootstate =
  green`, `ro.boot.vbmeta.device_state = locked`, AVB `avb_version 1.2`,
  `hash_alg sha256`. (vbmeta digest captured off-repo, not reproduced here.)

## Interpretation
coffey uses an Android A/B + **Virtual A/B** scheme with dynamic (super)
partitions under dm-verity, on locked verified boot (AVB 1.2) — consistent with
the "welded bootloader" conclusion, now with concrete device-reported detail.

## Alternative explanations
These are software-reported states; a fully compromised/instrumented device
could misreport. On a stock locked user build that is not a realistic concern,
but the facts remain "device-reported," not externally measured.

## Validation needed
- Partition **sizes/offsets** are unknown: `/proc/partitions` and
  `/proc/cmdline` are permission-denied without root (recorded, not escalated).
- `lpdump` (authoritative super-partition metadata) typically needs elevated
  privileges; not run. A full partition map remains an open item for a
  separately-approved method (e.g. offline analysis of an obtained image).
