---
experiment_id: AML-E0005
title: "Hardware Architecture Map — clock/reset index tables, pinctrl pin-maps, reserved-memory, dependency graph (S7D/coffey)"
research_question: "What are coffey/S7D's clock and reset index tables, pin-controller pin-maps, reserved-memory regions, and the dependency graph relating the major hardware blocks — from offline source + the extracted DT?"
hypothesis: "coffey's clock/reset wiring resolves to concrete indices via the upstream s7d-clkc/s7d-reset binding headers, and the extracted DT carries the authoritative pinmux and reserved-memory layout; indices are device-confirmable against coffey's flattened numeric cells."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "coffey extracted base DT (AML-S0005)"
  - "upstream S7D DT + dt-bindings headers (AML-S0006, commit 8646fbd1)"
result: done
related_findings:
  - AML-F0007
  - AML-F0009
---

# AML-E0005 — Hardware Architecture Map (S7D / coffey)

Offline, read-only, source-backed. Extends AML-E0003. Full map in
`E:\Morphe\device\coffey-ota\analysis\E0005-ARCH-MAP.md`. Upstream pinned to
**commit `8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734`** (all 3 DT files
byte-identical at this commit; index headers fetched at same commit).

## Procedure
1. Fetch the index-table binding headers at the pinned commit:
   `s7d-clkc.h` (256 CLKIDs), `amlogic,meson-s7d-reset.h` (92),
   `amlogic,meson-sc2-reset.h` (87).
2. Parse each key peripheral's `clocks`/`resets` symbolic refs in meson-s7d.dtsi;
   resolve symbol→number via the headers (iterative `BASE + N` evaluation).
3. Spot-confirm resolved indices against coffey's flattened DTB numeric cells.
4. Extract `pinctrl@4000` bank geometry + all pin-mux state nodes from coffey DT.
5. Extract `reserved-memory` regions + interrupt routing from coffey DT.
6. Build the controller→consumer dependency graph.

## Actual observations
### Clock/reset index tables (EXACT, device-confirmed where checked)
- Clock controller `s7d-clkc` (S7D-new binding); reset `meson-sc2-reset` @0x2000
  (inherited-SC2 binding) but the **S7D reset index namespace** is S7D-specific.
- Resolved indices (examples): UART A/C/D/E = CLKID_SYS_UART_A/C/D/E 218/220/221/222;
  I²C A–E = SYS_I2C_M_A..E 227–231; SD/eMMC A/B/C clocks 209/210/211 + sel/div,
  resets 152/153/154; ETH SYS_ETHPHY=204, ETH_RMII=99, FCLK_CLK50M=13; USB
  SYS_USB=226; SARADC 238/24/22 + reset 83.
- **Device-confirmed:** saradc coffey `clocks=<.. 0xee 0x18 0x16>`=238/24/22 and
  `resets=<.. 0x53>`=83; i2c@66000 `clocks=<0x09 0xe3>`=227=CLKID_SYS_I2C_M_A.
- SCMI clock-domain indices (PWM G–J via `scmi_clk`) = UNKNOWN here
  (s7d-scmi-clkc.h not fetched) — flagged, not guessed.

### Pin controllers / GPIO banks
- `pinctrl@4000` = `amlogic,meson-s7d-periphs-pinctrl`; `bank@4000` mux `@0x4000`
  (0x4c), gpio `@0x40c0` (0x2cc), **84 GPIOs** (gpio-ranges last cell 0x54).
- 49 pin-mux state nodes extracted (function→pad groups→drive/bias): I²C A–E,
  UART B/D/E, ISO7816, HDMI-HPD, DiSEqC, etc. Pad banks C/D/H/X/Z seen in group
  names. (AO-domain pinctrl is a separate controller, not enumerated.)

### Reserved-memory (18 regions)
Secure/no-map: `linux,secmon` 0x5000000+0x2400000 (36M, TEE/secure-monitor),
`heap-secure`, `mali_protected@c0000000`, `secure_vdec_reserved`. Media DMA
pools: `codec_mm_cma` 364M, `heap-gfx`/`heap-fb`, `meson-fb`. Debug: `ramoops`
(pstore), `iotrace`, `ramdump_bl33z`.

### Interrupt routing
Global `interrupt-parent=<0x01>` → GIC `@fff01000` (GIC-400 class). GPIO pad IRQs
via second-level `interrupt-controller@4080` (meson-s7-gpio-intc) → GIC. Per-SPI
numbers in the AML-E0003 matrix.

### Dependency graph
xtal→s7d-clkc→(all gated peripherals); scmi_clk→PWM G–J; meson-sc2-reset(S7D
index ns)→SARADC/SD-eMMC/USB; periphs-pinctrl(84 GPIO)→I²C/UART/ISO7816/HDMI-HPD/
DiSEqC; GIC←all SPIs, gpio-intc←pad IRQs; reserved-memory→VPU/VDEC/Mali + secmon←ATF.

## Conclusion
coffey/S7D clock & reset wiring resolves to concrete, source-backed indices,
device-confirmed where checked (EXACT class). Pinmux, reserved-memory, and
interrupt routing mapped from the device-authoritative extracted DT. What this
does NOT establish: runtime clock/reset/PLL state (no on-device dump), AO-pinctrl
and SCMI-clock indices (not fetched), and physical GPT offsets (root-gated,
AML-F0008). Documented bindings are kept separate from observed runtime behavior
(none claimed) and unresolved items (listed).

## Next steps
- Optional: fetch s7d-scmi-clkc.h to close the SCMI PWM indices; enumerate
  AO-domain pinctrl; map clock/reset index tables to the SC2 namespace to
  quantify the S7D-vs-SC2 reindex (extends the AML-E0003 lineage claim).
