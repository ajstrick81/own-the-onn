---
finding_id: AML-F0017
title: "coffey bootloader tail embeds a CRC-valid GPT provisioning TEMPLATE (31 named partitions, package-declared start-LBAs); live absolute offsets still unmeasured"
component: partitions
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
source_urls: []
source_revision: "bootloader.img sha256 389daa99… from OTA URO4.260304.011.B1; CRCs re-verified in-image"
related_findings:
  - AML-F0008
  - AML-F0010
  - AML-F0016
status: promoted
---

# coffey GPT provisioning template in bootloader tail (Codex finding, re-verified)

The bootloader-image tail (previously "function unassigned", AML-F0010) is a GPT
**provisioning template**. Independently re-verified in-image (not on faith).

## Observations (CRC re-verified in-image)
- Protective-MBR-like sector @0x3dfe00 (sig 55aa @0x3dfffe; type-0xee entry has
  sector-count 0 → not a finalized protective MBR).
- **EFI PART header @0x3e0000**: revision 0x10000, hdr_size 92, stored CRC
  **0x269dab13** → recomputed **0x269dab13 MATCH** (CRC field zeroed).
- **Entry array @0x3e0200**: 31 × 128 B, stored CRC **0x397dd1c6** → recomputed
  **0x397dd1c6 MATCH**. Duplicate array @0x3e4200; duplicate header @0x3e8200
  (still declares current-LBA 1 → not a finalized backup GPT).
- 31 entries, all nonzero type GUIDs, ordered without overlap. First few:
  p1 `reserved` LBA 73728 (0x2400000), p2 `env` 221184 (0x6c00000), p3 `frp`
  270336, … p29 `super` 1435648 (0x2bd00000, 3200 MiB), p31 `userdata` 8124416.
- **Placeholders:** header backup-LBA, last-usable-LBA, and userdata end =
  UINT64_MAX (unfinalized, capacity-dependent template). 512-B LBA assumed.

## Interpretation
coffey's bootloader image embeds a **package-level GPT layout template** giving
**package-declared start-LBAs for all 31 physical partitions** (and 30 finite
ends). This **advances G1**: offsets are now available at *template* scope. The
31 names match the device by-name capture (AML-F0008) at the exact p1–p31
numbers, and super's 3200 MiB matches lpdump's 3,355,443,200 B — two independent
corroborations. Corrects the earlier "the OTA supplies no GPT offsets" wording.

## Alternative explanations / discipline
- **Template ≠ live GPT.** CRC validity establishes structure integrity, not
  provenance, authenticity, or live deployment. The UINT64_MAX placeholders mean
  it is not a finalized disk image; the **live absolute start-LBAs remain
  unmeasured** (would need a device read or factory image). Disk-byte addresses
  derived as (1,435,648 + super-relative)·512 are conditional on deployment, not
  measured (keep as such).
- Count 31 matching names corroborates layout association; it does not prove the
  device deployed these exact absolute LBAs.

## Validation needed / ceiling
Compare against an independently authorized read-only on-device GPT read (G1 live);
corroborated by 7Ji/gpt-unbin template format (related-family, not vendor source).
