---
finding_id: AML-F0009
title: "coffey clock/reset index tables device-confirmed (S7D s7d-clkc + SC2-reset binding, S7D index namespace)"
component: hardware-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0006
source_urls: []
source_revision: "coffey DT (AML-S0005) vs CoreELEC common_drivers commit 8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734"
related_findings:
  - AML-F0007
status: promoted
---

# coffey clock/reset index tables (device-confirmed)

## Observations
Resolved coffey's peripheral clock/reset wiring to concrete indices via the
upstream S7D binding headers (`s7d-clkc.h` 256 CLKIDs; `amlogic,meson-s7d-reset.h`
92; `amlogic,meson-sc2-reset.h` 87) at commit `8646fbd1…`, and confirmed against
coffey's flattened DTB numeric cells:
- **SARADC:** coffey `clocks=<.. 0xee 0x18 0x16>` = CLKID_SYS_SAR_ADC=238,
  CLKID_SAR_ADC=24, CLKID_SAR_ADC_SEL=22; `resets=<.. 0x53>` = RESET_SAR_ANA=83. ✓
- **I²C A:** coffey `clocks=<0x09 0xe3>` → 0xe3 = CLKID_SYS_I2C_M_A=227. ✓
- **SD/eMMC A/B/C resets:** RESET_SD_EMMC_A/B/C = 152/153/154 (contiguous).
- Other resolved (source-level): UART A/C/D/E=218/220/221/222; I²C B–E=228–231;
  ETH SYS_ETHPHY=204 / ETH_RMII=99 / FCLK_CLK50M=13; USB SYS_USB=226; SPICC0=225.

## Interpretation
The clock controller binding is **S7D-new** (`amlogic,s7d-clkc`); the reset
controller binding is **inherited-SC2** (`amlogic,meson-sc2-reset` @0x2000) **but
the reset index namespace is S7D-specific** (defined in `amlogic,meson-s7d-reset.h`,
not the sc2 header). The resolved indices are EXACT (compatible + index match
coffey's compiled DT). This refines AML-F0007: SC2 lineage is at the reset
*binding/driver* level, while the *index table* is an S7D namespace.

## Alternative explanations
Index numbers could in principle differ between the public BSP and the shipped
blob — ruled out for the checked peripherals by direct numeric match against
coffey's flattened DTB (device-authoritative).

## Validation needed / ceiling
SCMI clock-domain indices (`CLKID_SCMI_*`, s7d-scmi-clkc.h) not resolved here
(header not fetched) — UNKNOWN, not guessed. Runtime clock/reset state not
dumped (no on-device clk tree read); this is a DT-wiring claim, not a runtime
behavior claim.
