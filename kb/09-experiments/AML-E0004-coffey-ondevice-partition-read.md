---
experiment_id: AML-E0004
title: "coffey read-only on-device partition enumeration (lpdump + by-name, non-root)"
research_question: "Can the AML-E0002 open items (logical super LP grouping, physical GPT geometry) be resolved on the running coffey device without root or modification?"
hypothesis: "lpdump (super metadata) and /dev/block/by-name are readable by the unprivileged shell user and resolve the logical grouping + physical partition table; absolute GPT offsets may be SELinux-gated."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "Director authorization for a read-only on-device adb step (granted 2026-10-09)"
  - "coffey reachable at 192.168.12.210:5555"
result: done
related_findings:
  - AML-F0008
  - AML-F0002
  - AML-F0005
---

# AML-E0004 — coffey read-only on-device partition enumeration

Read-only, non-root, no modification. Authorized by the Director 2026-10-09 as
the on-device path to close the AML-E0002 geometry gap (vs. the gated
new-firmware-acquisition path, which stays ✗).

## Procedure
1. `adb connect 192.168.12.210:5555`; confirm `adb shell id` = uid 2000 `shell`
   (no root).
2. `adb shell lpdump` → logical/super metadata (groups, partitions, extents,
   block-device table). Saved to `analysis/lpdump-coffey-slot_b.txt`.
3. `adb shell ls -l /dev/block/by-name/` → physical name→block-device map.
   Saved to `analysis/by-name.txt`.
4. `adb shell getprop` ro.build.fingerprint / ro.boot.slot_suffix / bootloader.
5. Attempt physical GPT geometry read-only: `/sys/block/mmcblk0/*/start|size`,
   `/proc/partitions`.

## Expected observations
- lpdump readable by shell → full logical grouping (if LP metadata is
  world-readable on this build).
- by-name readable → physical partition table.
- sysfs/proc block geometry possibly SELinux-denied for the shell domain.

## Actual observations
- `id` = uid=2000(shell), `u:r:shell:s0` — unprivileged, confirmed.
- `lpdump` **succeeded** (metadata v10.2, slot 1/`_b`): super first-logical-sector
  2048 (super-relative, NOT absolute GPT LBA — see AML-F0008 note),
  3355443200 B; group `amlogic_dynamic_partitions_b` cap 3344957440 B; **8 dynamic
  + 8 cow** partitions; `virtual_ab_device`. → full logical grouping (AML-F0008).
- `by-name` **succeeded**: 31 mmcblk0 partitions, A/B boot chain, `super`=p29
  (AML-F0008).
- fingerprint = coffey URO4.260304.011.B1 slot `_b` (matches OTA / AML-S0005);
  bootloader 01.01.260305.112513 (corroborates AML-F0006 `@AMLBOOT` date).
- `/sys/block/mmcblk0/*` and `/proc/partitions` → **Permission denied**
  (SELinux, shell domain). Absolute GPT start-LBAs NOT obtained.

## Conclusion
Logical super LP grouping = **RESOLVED, device-confirmed** (AML-F0008). Physical
partition *table* (names, p-numbers, A/B) = **RESOLVED**. Absolute physical GPT
**byte offsets** = **NOT resolved** on-device without root (SELinux-gated); the
only remaining partition-geometry sub-item. What this does NOT establish: any
root/privileged capability — every read here was within the stock shell domain.

## Next steps
- Absolute GPT offsets: defer to a future root capability or a Director-approved
  factory image; do not re-attempt as shell (confirmed denied).
- Optional: tie each dynamic partition's extent total to its mounted size.
