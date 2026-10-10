---
finding_id: AML-F0008
title: "coffey super logical LP grouping + physical partition table (device-confirmed, slot _b)"
component: partitions
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0007
source_urls: []
source_revision: "URO4.260304.011.B1, slot _b (lpdump metadata v10.2)"
related_findings:
  - AML-F0002
  - AML-F0005
status: promoted
---

# coffey super logical LP grouping + physical partition table (device-confirmed)

Resolves the long-standing AML-E0002 open item (logical super LP grouping) by a
read-only on-device `lpdump` (`AML-S0007`). Upgrades the previously
offline-derived partition findings (`AML-F0002`, `AML-F0005`) to
**device-confirmed, exact-device**.

## Observations
### Logical super (lpdump, metadata v10.2, slot 1 = `_b`)
- Header flag `virtual_ab_device`; metadata slot count 3; metadata max 65536 B.
- Block device `super`: **First sector 2048** (see coordinate-system note below),
  size **3355443200 bytes** (3.125 GiB).
- Groups: `default` (0), **`amlogic_dynamic_partitions_b`** (max **3344957440 B**),
  `cow` (0, Virtual-A/B snapshot group).
- **8 dynamic partitions** in `amlogic_dynamic_partitions_b` (all
  `readonly,updated`): `system_b`, `vendor_b`, `product_b`, `odm_b`,
  `system_ext_b`, `vendor_dlkm_b`, `system_dlkm_b`, `odm_dlkm_b` (+ fragmented
  extents; e.g. `system_b` spans 4 non-contiguous extents, `system_ext_b` 12).
- **8 matching `*-cow`** snapshot partitions in group `cow` (Virtual A/B).
  (Correction: an earlier summary said "9+9"; the lpdump table lists **8 dynamic
  + 8 cow = 16**. Recounted from `lpdump-coffey-slot_b.txt`.)

### Coordinate-system note — "First sector 2048" is NOT an absolute GPT LBA
This value is lpdump's **Block device table → partition `super` → First sector**,
i.e. liblp `LpMetadataBlockDevice.first_logical_sector`: the first 512-byte
sector **within the super partition** available for LP extent allocation (after
the LP geometry + metadata region), expressed in **super-relative** sector space.
It is the alignment offset inside super, **not** super's start LBA on `mmcblk0`.
All extent `linear super N` offsets in the layout are likewise super-relative
512B sectors. The absolute physical GPT start-LBA of `super` (p29) remains
unresolved (root-gated) — do not conflate the two.
- Full extent/sector layout captured in `analysis/lpdump-coffey-slot_b.txt`.

### Physical partition map (`/dev/block/by-name/`, mmcblk0, 31 partitions)
eMMC `mmcblk0` (not UFS). A/B pairs for boot chain + the single `super`:
- `reserved`=p1, `env`=p2, `frp`=p3, `factory`=p4
- `vendor_boot_a/b`=p5/p6, `bootloader_a/b`=p7/p8, `tee`=p9, `logo`=p10,
  `misc`=p11, `dtbo_a/b`=p12/p13, `cri_data`=p14, `param`=p15,
  `odm_ext_a/b`=p16/p17, `oem_a/b`=p18/p19, `boot_a/b`=p20/p21,
  `init_boot_a/b`=p22/p23, `metadata`=p24, `vbmeta_a/b`=p25/p26,
  `vbmeta_system_a/b`=p27/p28, **`super`=p29**, `rsv`=p30, `userdata`=p31.
- eMMC boot HW partitions `mmcblk0boot0/1` present.
- Device fingerprint `onn/coffey/coffey:14/URO4.260304.011.B1/15051976:user/release-keys`,
  `ro.boot.slot_suffix=_b`, bootloader `01.01.260305.112513` (corroborates the
  `26030511` date in the `@AMLBOOT` container string, AML-F0006).

## Interpretation
coffey is a Virtual-A/B (snapshot-updates) device on eMMC with a single `super`
dynamic container (3.125 GiB, group cap 3.344 GB) holding 8 read-only system
partitions on the active `_b` slot; the physical GPT carries 31 named partitions
with A/B duplication of the boot chain. The running device matches the
offline-analyzed OTA build exactly.

## Alternative explanations
None for the logical metadata — `lpdump` reads the on-disk LP metadata directly.
The by-name map is kernel-created symlinks, authoritative for name→device.

## Validation needed / ceiling
**Absolute physical GPT start-LBAs per partition are NOT resolved**: `shell`-user
reads of `/sys/block/mmcblk0/*/start`, `/proc/partitions`, and the raw disk are
**SELinux-denied without root**. Obtaining byte-exact GPT offsets would require
root on coffey or a full factory image (new acquisition — Director-gated, ✗ on
record). The partition *ordering* (p1..p31) and names above are confirmed; their
absolute offsets remain the one open sub-item.
