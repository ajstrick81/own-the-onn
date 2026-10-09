---
finding_id: AML-F0004
title: "coffey Device-Tree node structure + normalized comparison to CoreELEC s7d"
component: hardware-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0004
  - AML-S0002
source_urls: []
source_revision: "coffey /proc/device-tree node names, 2026-10-07"
related_findings:
  - AML-F0001
status: promoted
---

# coffey Device-Tree node structure + s7d comparison

## Observations (device-reported structure only)
- coffey exposes **132 `/proc/device-tree` entries** when counted as **full
  node names with unit-addresses** (e.g. `drm-vpu@0xff900000`, `rtc@0xfe010288`,
  `memory@00000000`); **130** when counted as **collapsed base names** (`@addr`
  stripped). Same structure, two normalizations — not a discrepancy. The
  normalized comparison below uses the **base-name** form (130) on both sides.
  Property **values** were permission-denied and are NOT captured.
- Normalized comparison vs the CoreELEC **s7d** DT node set (`AML-S0002`
  lineage, 454 nodes):
  - **shared:** 113
  - **coffey-only:** 17 — incl. `amlogic-dt-id`, `compatible`, `serial-number`,
    `valhall` (Mali GPU), `secmon`, `efusekey`, `wifi_pwm_conf`, `cpus`.
  - **reference-only:** 341.

## Interpretation
coffey's visible DT structure sits within the Amlogic s7d family but is a
distinct, smaller node set. The large reference-only count is expected: the
CoreELEC s7d source DT is a full superset, while coffey's figure is only the
**SELinux-visible node-name list from `/proc/device-tree`**, not a complete DTB
dump — so this is a structural/name-level comparison, not a full-DT diff.

## Alternative explanations
Node-name presence/absence can reflect SELinux visibility and DT-overlay
application, not only silicon differences. Names are not values.

## Validation needed / explicitly NOT claimed
- **NOT confirmed:** DT `model`, `compatible` strings, `amlogic-dt-id` value, or
  physical **board revision** — these are property *values*, denied on-device.
  They remain **unresolved** pending a coffey DTB (dtbo partition dump = root,
  or a Director-approved firmware-image carve → AML-E0002 R1).
- The comparison counts depend on the two inputs' capture methods (device
  `/proc/device-tree` names vs CoreELEC source DT); treat as structural.
