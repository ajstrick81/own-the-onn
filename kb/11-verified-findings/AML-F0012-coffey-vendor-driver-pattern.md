---
finding_id: AML-F0012
title: "coffey runs Amlogic vendor driver stack (GKI base + vendor modules); vendor↔mainline compatible-string divergence is a broad pattern (UART/I²C/MMC/USB)"
component: driver-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0006
  - AML-S0008
source_urls: []
source_revision: "coffey DTB + GKI config 5.15.196 vs CoreELEC 8646fbd1 + mainline af32da41"
related_findings:
  - AML-F0011
status: promoted
---

# coffey = GKI base + Amlogic vendor modules; vendor↔mainline divergence is broad

Verified **shipped-DTB (L1) ↔ vendor-source (L3)** correspondences (not proof of
runtime driver binaries — refinement #1).

## Observations
- **The UART divergence generalizes.** For each priority subsystem, coffey's DTB
  compatible is matched by the CoreELEC **vendor** driver, and the **mainline**
  of_match does NOT contain it:
  - **I²C:** L1 `amlogic,meson-i2c`; vendor `i2c-meson.c` of_match = `meson-i2c`,
    `meson-tee-i2c`; **mainline `i2c-meson.c` = meson6/gxbb/axg-i2c only (no
    `meson-i2c`)**. Vendor reset = register-level `meson_i2c_reset_tokens` (no
    reset-controller); `devm_request_irq`; single `devm_clk_get(NULL)`.
  - **eMMC/SD/SDIO:** L1 `amlogic,meson-v8-mmc`; vendor `meson-gx-mmc.c` of_match
    **adds `meson-v8-mmc`→meson_v8_data**; **mainline `meson-gx-mmc.c` has no
    v8-mmc** (gx/gxbb/gxl/gxm/axg only).
  - **USB:** L1 `amlogic,amlogic-crg-drd-usb2/usb3`; vendor dedicated
    `crgdrdphy/phy-aml-crg-drd-usb2/usb3.c` (custom register-level PHY reset);
    **no mainline s7d PHY driver** (mainline uses dwc3-meson-g12a + phy-meson).
- **coffey = GKI base + vendor modules.** Preserved config
  `coffey-config-5.15.196.txt` (7035 lines) has **0 `CONFIG_AMLOGIC_*`** symbols
  → Android **GKI base** config; the Amlogic drivers are **vendor modules** (the
  `common_drivers` tree), not in this config. Generic cores present: I2C, MMC,
  USB_DWC3, ARM_SCMI (+SMC/mailbox transport, RESET_SCMI). `COMMON_CLK_SCMI` NOT
  set; no `SOCINFO` symbol.

## Interpretation
coffey runs the Amlogic **vendor** driver stack layered on an Android GKI base
kernel. A shared/compatible **interface** across generations is not evidence of
an inherited **implementation**; the vendor and mainline stacks diverge in
compatible string, clock-name set, reset handling, and IRQ registration for every
subsystem checked. This refines the SC2-lineage thesis (AML-F0007): lineage is at
the *binding/interface* level, while coffey's *implementation* is the CoreELEC
vendor tree, distinct from mainline.

## Alternative explanations / discipline
- **SoC-ID 0x47** stays mainline-source-level only; `meson_gx_socinfo_init` not
  found in the vendor tree and no SOCINFO in the GKI base → coffey enablement is
  **not determinable** from available evidence (not "disabled", not "enabled").
- Config-based enablement checks have a **ceiling**: a GKI base config cannot
  confirm/deny vendor-module enablement.
- These are source+DTB correspondences; which driver actually probed at runtime
  needs on-device dmesg/sysfs (not taken).

## Validation needed / ceiling
Runtime driver-binding confirmation + the full vendor-module config (not the GKI
base) would require on-device reads or the vendor kernel build artifacts.
