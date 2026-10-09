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
  - AML-S0005
source_urls: []
source_revision: "coffey /proc/device-tree node names 2026-10-07; DT values from OTA base DT (AML-S0005)"
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

## DT values — RESOLVED from the OTA base DT (AML-S0005, exact-build)
The base Device Tree carved from the acquired OTA's `vendor_boot` gives
(exact-device for build URO4.260304.011.B1):
- **`amlogic-dt-id = "s7d_s905x5m_bm202"`**
- **`compatible = "s7d_s905x5m_bm202"`**  (platform **s7d**, SoC **S905X5M**,
  board code **`bm202`**)
- GPU node declares `arm,malit60x` (a Mali/Valhall-class **compatibility
  string**); CPU `arm,cortex-a55` — consistent with cpuinfo (part 0xd05).
  Per review #5: the exact Mali product is **not** inferable from the
  `arm,malit60x` compatible alone — recorded as the declared compatible only.
The `dtbo` partition held only **overlays** (`dummy-battery`/`dummy-charger`);
board identity was taken from the **base DT**, not inferred from overlays.

## Still not independently established
- **`bm202`** is the firmware's **board identifier** from the DT; it is not an
  independently-read hardware revision stamp. Treat as the DT-declared board id.
- The 130/132 structural comparison depends on capture method (device
  `/proc/device-tree` names vs CoreELEC source DT); treat as structural.
