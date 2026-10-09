---
experiment_id: AML-E0003
title: "Phase 3 — coffey base DT vs upstream S7D/S905X5M cross-generation comparison"
research_question: "Which of coffey's DT subsystems are inherited IP (identical implementation) vs similar interfaces across the Amlogic S7D/SC2 lineage?"
hypothesis: "coffey (s7d) reuses prior-generation (SC2) IP for some controllers while introducing s7d-specific blocks; node-name similarity must be distinguished from implementation identity."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "coffey base DT (extracted, AML-S0005)"
  - "upstream S7D/SC2 DT source (CoreELEC linux-amlogic) — NOT yet local; needs a passive source fetch"
result: in-progress
related_findings:
  - AML-F0004
---

# AML-E0003 — Phase 3 cross-generation DT comparison (begun)

Offline, read-only, source-backed. No device, no new firmware.

## coffey base-DT subsystem characterization (from AML-S0005 vendor_boot DT)
`dts` sha256 `197ca22a…`, 4682 lines. Priority areas:
- **CPU topology:** 4× `arm,cortex-a55` (armv8), `cpu-idle-states`, OPP-v2 (DVFS);
  GIC `arm,cortex-a15-gic` (GIC-400 class); `armv8-pmuv3`, `armv8-timer`.
- **Clocks:** `amlogic,s7d-clkc` (+ `meson_clk_msr@48000`). **s7d-specific.**
- **Resets:** `amlogic,meson-sc2-reset`. **SC2-generation IP reused.**
- **Power:** `amlogic,s7d-power-domain`. **s7d-specific.**
- **Watchdog:** `amlogic,meson-sc2-wdt`. **SC2-generation IP reused.**
- **Interrupts:** GIC @fff01000; interrupt-controller@4080.
- **Peripherals:** eth@fe368000 (+phy); 5× `amlogic,meson-i2c`; `amlogic,meson-v8-mmc`
  (mmc/sd/sdio@fe08*); 5× `amlogic,meson-uart`; spi-nand/spi-nor; USB2+USB3
  `amlogic-crg-drd-usb2/usb3` (usbphy20/21/30/31); saradc; pinctrl@4000;
  `amlogic,vdin-s7d` (video-in, s7d-specific); crypto `sha_dma`/`sha3_dma`.

## Initial cross-generation reading (hypothesis-level, NOT yet source-confirmed)
coffey s7d appears to **inherit SC2-generation IP** for reset and watchdog
(`meson-sc2-*`) while using **s7d-new** clock controller, power domain, and
video-in. This is the project's "architectural DNA" thesis with concrete
compatible-string evidence. **Discipline:** a shared *compatible string* is a
**similar interface / likely-shared driver binding**, not proof of an identical
silicon implementation — that distinction needs the upstream source.

## What's needed to complete (next)
Upstream **S7D and SC2 DT sources** (CoreELEC `linux-amlogic` device DTS) are
**not local** (the on-hand `common_drivers` kernel tree has no s7d board DTS).
Fetching those `.dts/.dtsi` from the public CoreELEC repo (a passive **source**
fetch, not firmware) would let us diff register bases, clock/reset indices,
interrupt maps, and memory regions to classify each subsystem **identical vs
similar**. Pending that fetch (and Director nod on the source fetch).

## Actual observations / Conclusion
<fill once upstream DT sources are fetched and the subsystem-level diff is run.>
