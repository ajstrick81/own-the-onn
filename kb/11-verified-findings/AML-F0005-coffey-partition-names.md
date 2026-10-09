---
finding_id: AML-F0005
title: "coffey physical partition names & A/B by-name map (geometry unresolved)"
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0004
source_urls: []
source_revision: "coffey /dev/block/by-name, 2026-10-07"
related_findings:
  - AML-F0002
status: promoted
---

# coffey physical partition names & A/B by-name map

## Observations (device-reported)
- 34 `/dev/block/by-name` entries mapping to `mmcblk0pN` (eMMC). Partitions
  carry **A/B slots** (`_a`/`_b`) for: `boot`, `bootloader`, `dtbo`,
  `init_boot`, `odm_ext`, `oem`, `vbmeta`, `vbmeta_system`, `vendor_boot`.
- Non-slotted include `env`, `frp`, `factory`, `cri_data` (physical partitions).
- Logical super members (`odm`, `odm_dlkm`, `product`, `vendor`, `system…`)
  appear under `/dev/block/mapper` (see `AML-F0002`), distinct from this
  physical by-name list.

## Interpretation
Confirms the physical partition **naming/slot layout** of coffey's eMMC: a
standard Android A/B + dynamic-partition arrangement with a dedicated
`bootloader`, `dtbo`, `init_boot`, and `vendor_boot` per slot.

## Alternative explanations
by-name symlinks are a device-reported mapping; they do not themselves give
sizes/offsets.

## Validation needed / explicitly NOT claimed (kept unresolved)
- **Physical sizes/offsets (GPT geometry):** UNRESOLVED — `/proc/partitions`
  permission-denied (AML-E0001 + AML-S0004 both show it empty/denied).
- **Logical super metadata** (per-partition sizes, groups): UNRESOLVED — needs
  `lpdump` on a coffey `super.img`.
- Both await a Director-approved coffey firmware image (AML-E0002 R3); keep
  physical and logical geometry reported **independently**.
