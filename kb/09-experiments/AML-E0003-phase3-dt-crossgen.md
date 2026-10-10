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
result: done
related_findings:
  - AML-F0004
  - AML-F0007
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

## Actual observations / Conclusion (DONE — source-backed)
Upstream S7D/SC2 DT source fetched (`AML-S0006`, CoreELEC common_drivers
5.15.196_20260225). Comparison run → `AML-F0007`:
- coffey DT = upstream board `s7d_s905x5m_bm202` (name match).
- **SC2 inheritance confirmed at source:** `meson-s7d.dtsi` reuses
  `meson-sc2-reset`/`meson-sc2-wdt`.
- **s7d-specific:** `s7d-clkc`, `s7d-power-domain` (absent in sc2 ref).
- **Identical register bases** for uart/mmc/sd/sdio/eth/usbphy (coffey ≡ s7d ref).
- **Shared both gens:** meson-uart, meson-i2c.
Discipline: identical compatible+reg = identical DT-level binding, not a
silicon-mask identity proof. Phase-3 first comparison complete; further
subsystems (pinctrl pin maps, clock/reset index tables) can extend it later.

## Lineage Matrix extension (2026-10-09, coordinator assignment AML-E0003)
Full per-subsystem matrix (reset/wdt · clock/power · uart/i2c · mmc/sd/sdio ·
interrupts · usb/ethernet) with the 5-class taxonomy (Exact-DT-match /
Shared-binding / Shared-driver / Similar-interface / Unknown) in
`E:\Morphe\device\coffey-ota\analysis\E0003-LINEAGE-MATRIX.md` (sha256 anchors
for coffey DT + all three upstream files inline). Key results:
- **Inherited SC2 IP (driver-level):** `meson-sc2-reset` @0x2000, `meson-sc2-wdt`
  @0x2100 — present in coffey AND `meson-s7d.dtsi` (ln 701/448) AND
  `meson-sc2.dtsi`.
- **S7D-new:** `s7d-clkc`, `s7d-power-domain`, CRG-DRD USB2/USB3 phys
  (`@fe358000/fe348000/+080`, reg bases absent from SC2 ref), gpio-intc primary
  compatible, ethernet `@fe368000` reg placement.
- **Shared both gens (generic/long-standing):** `meson-uart`
  (`@fe078000`+4 more), `meson-i2c` (`@66000`×5) — exact compatible **and**
  literal reg base in both s7d and sc2 source; ARM GIC (generic).
- **Similar-interface / different binding:** MMC/SD/SDIO — reg bases
  (`@fe08c000/fe08a000/fe088000`) reused across gens, but coffey/S7D binds
  `meson-v8-mmc` while SC2 ref binds a different mmc compatible at those bases.

### Method correction logged (self-audit)
The first pass's space-stripped substring search gave **false negatives** on reg
bases (adjacent `0x0 0xADDR` cells merged). Re-verified against **un-stripped**
source by literal grep: UART/I²C/MMC/SD/SDIO/reset/wdt reg bases ARE in both
gens; eth/usbphy reg bases are s7d-only. Matrix reflects the corrected check.

## Evidence refinements addressed (coordinator REL-…-N, items 1–5)
1. **DT-binding ≠ silicon identity** — enforced in the matrix; every row's class
   is a DT/driver-binding claim, explicitly not a mask-identity claim.
2. **coffey extracted DT ↔ upstream board + includes** — coffey flattened DTB
   (compiled, all includes resolved; `amlogic-dt-id = s7d_s905x5m_bm202`) matches
   the upstream `s7d_s905x5m_bm202.dts` board by name; per-subsystem compatible +
   literal reg bases reconciled above. (Full source-vs-source property diff of
   resolved includes = next pass; compiled blob can't be line-diffed to source.)
3. **Bootloader markers 0x4381f/0x43820 reconciled** — see
   `analysis/BOOTLOADER-INVENTORY.txt` addendum: `strings` reported 0x4381f only
   because byte 0x4381f = `0x2c` (ASCII `,`) immediately precedes the real magic;
   the Amlogic container magic `@AMLBOOT` begins at **0x43820** (`0x40`='@').
   One marker, not two overlapping.
4. **No encryption inferred from absent BL31/U-Boot strings** — recorded; the
   container exposes a plaintext component descriptor table (BL2E/BL2X/DDRF with
   LE offset+size), so missing BL31/U-Boot *plaintext* is left UNKNOWN, not
   "encrypted".
5. **Upstream revision** — branch `5.15.196_20260225` + per-file sha256 are the
   reproducibility anchors now recorded in AML-S0006 and the matrix header. Exact
   commit SHA was not captured at fetch time → logged as an open item to pin on
   next source touch (does not affect any current claim).
