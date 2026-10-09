---
finding_id: AML-F0007
title: "S7D↔SC2 DT lineage: SC2 reset/wdt IP inherited, s7d-specific clock/power (source-backed)"
component: soc-generations
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-soc
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0006
source_urls: []
source_revision: "coffey extracted DT vs CoreELEC common_drivers 5.15.196_20260225"
related_findings:
  - AML-F0004
status: promoted
---

# S7D ↔ SC2 Device-Tree lineage (source-backed)

Source-backed comparison of coffey's extracted base DT (`AML-S0005`) against the
upstream CoreELEC S7D/SC2 DT source (`AML-S0006`).

## Provenance link
coffey's extracted DT carries `amlogic-dt-id = "s7d_s905x5m_bm202"`, matching
the upstream board file **`s7d_s905x5m_bm202.dts`** by name — coffey's shipped
DT corresponds to the CoreELEC/Amlogic s7d_s905x5m_bm202 board definition.

## Observations (coffey / meson-s7d.dtsi / meson-sc2.dtsi)
- **Inherited from SC2 (confirmed at source):** `amlogic,meson-sc2-reset` and
  `amlogic,meson-sc2-wdt` appear in coffey AND in `meson-s7d.dtsi` (lines 701,
  448) AND in `meson-sc2.dtsi`. The S7D SoC dtsi itself reuses the SC2 reset and
  watchdog bindings.
- **S7D-specific:** `amlogic,s7d-clkc` and `amlogic,s7d-power-domain` present in
  coffey + s7d ref, **absent** from sc2 ref → genuinely new in S7D. (`vdin-s7d`
  video-in is likewise s7d-named.)
- **Identical register bases** (coffey ≡ meson-s7d.dtsi): serial `@fe078000`,
  mmc `@fe08c000`, sd `@fe08a000`, sdio `@fe088000`, ethernet `@fe368000`,
  usbphy `@fe358000`.
- **Shared across both generations:** `amlogic,meson-uart` and
  `amlogic,meson-i2c` (5 instances each in coffey / s7d / sc2) — common
  peripheral IP lineage.

## Interpretation
Concrete, source-confirmed instance of the project's "architectural DNA" thesis:
S7D (S905X5M) **inherits SC2-generation IP** for reset and watchdog while
introducing S7D-specific clock and power-domain controllers, and reuses the
long-standing meson UART/I2C peripheral bindings. coffey's shipped DT matches the
s7d_s905x5m_bm202 board.

## Alternative explanations / discipline
- "Identical compatible + identical register base" is strong evidence of an
  **identical driver binding / DT-level implementation**; it is a **DT-level**
  claim, not a silicon-mask identity proof.
- A shared `compatible` string denotes a shared/compatible **interface**, not
  necessarily bit-identical hardware.
- The upstream source is the public BSP; coffey's extracted DT is the authority
  for coffey, and the two agree on the above.
