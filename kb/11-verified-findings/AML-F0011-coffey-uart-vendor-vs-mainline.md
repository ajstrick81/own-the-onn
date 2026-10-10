---
finding_id: AML-F0011
title: "coffey UART binds the CoreELEC vendor meson-uart driver, NOT the mainline s7d-uart→meson-s4-uart fallback (three-layer divergence)"
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
source_revision: "coffey DTB (AML-S0005) vs CoreELEC 8646fbd1 + mainline af32da41"
related_findings:
  - AML-F0007
status: promoted
---

# coffey UART: vendor stack, not the mainline S7D fallback

## Observations
- **L1 coffey shipped DTB:** UART nodes `serial@fe078000` (+fe07c/7e/80000, 7a000)
  declare `compatible = "amlogic,meson-uart"`, clock-names `clk_uart`,`clk_gate`
  (clkc CLKID_SYS_UART_A=218…), IRQ SPI 0xa8–0xac.
- **L3 coffey vendor driver** (CoreELEC `meson_uart.c` @8646fbd1, sha256
  `23d5647d…`): of_match table = `{ "amlogic,meson-uart" }`, `{ "amlogic, meson-uart" }`
  **only**. Probe `meson_uart_probe`: `devm_clk_get(dev,"clk_gate")`,
  `devm_clk_get(dev,"clk_uart")`, `devm_request_irq`.
- **L2 mainline** (torvalds `af32da41`): `amlogic-s7d.dtsi` UART `serial@7a000`
  `compatible = "amlogic,s7d-uart","amlogic,meson-s4-uart"`, clocks xtal/pclk/baud,
  `status="disabled"`; mainline `meson_uart.c` of_match has `amlogic,meson-s4-uart`
  (+meson6/8/8b/gx/g12a/a1); probe `meson_uart_probe_clocks` gets xtal/pclk/baud,
  `request_irq`.

## Interpretation
coffey's DTB clock-names (`clk_uart`/`clk_gate`) match the CoreELEC vendor driver,
not the mainline driver (xtal/pclk/baud) → coffey runs a **self-consistent vendor
UART stack** bound via `amlogic,meson-uart`. The mainline `s7d-uart →
meson-s4-uart` fallback is a **separate, independent upstreaming** that coffey's
shipped stack does NOT use. Concrete proof that a *shared/compatible interface*
(both "a meson UART") is not evidence of an *inherited implementation* — the
three layers (shipped DTB / mainline / vendor) diverge in compatible string,
clock-name set, IRQ registration, and speed math.

## Alternative explanations
Could the mainline driver bind coffey's DTB? No — mainline of_match lacks
`amlogic,meson-uart`; the vendor of_match lacks `meson-s4-uart`/`s7d-uart`. The
binding is mutually exclusive by compatible string.

## Validation needed / ceiling
Runtime confirmation (which driver actually probed) would need an on-device
`/sys/bus/platform/drivers` or dmesg read (device step, not taken). This is a
source+DTB binding claim (L1↔L3 compatible + clock-name match), not a runtime
probe-order claim.

## Framing (coordinator refinement #1, 2026-10-09)
State this as a **verified shipped-DTB → vendor-source correspondence**: coffey's
DTB declares `amlogic,meson-uart` with clock-names that match the CoreELEC vendor
driver's of_match + probe. It does **not** independently prove the exact
production runtime driver implementation (that needs the matching vendor-kernel
binary or runtime evidence). Generalized across subsystems in AML-F0012.
