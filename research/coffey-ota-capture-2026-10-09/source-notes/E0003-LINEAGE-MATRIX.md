# AML-E0003 — Hardware Lineage Matrix (coffey S7D ↔ SC2), offline source-backed

Date: 2026-10-09. Read-only. No device contact.

**Inputs (reproducibility anchors):**
- coffey extracted base DT (flattened): `analysis/vbdt/01_dtbdump_s7d_s905x5m_bm202.dtb.dts`, sha256 `197ca22af083e6c4856c2cd8f44f92b9519f4bb60f1db89f6077e18583a1ff42` (AML-S0005).
- Upstream (AML-S0006, CoreELEC/common_drivers branch `5.15.196_20260225`):
  - `meson-s7d.dtsi` sha256 `5055a50140701b9dfaa41b20d33fd4aeb61a72d6b4ca5d8018d55b7801ff1d61`
  - `meson-sc2.dtsi` sha256 `b6cc02b76042ca97315b1537473225da14169457b88a88da1c91b3017ed705ca`
  - `s7d_s905x5m_bm202.dts` sha256 `533e0d5b2b83cba110115733d26b237757bf116d4f6b591394ff5bc8a6479c1d`

**Classification taxonomy (coordinator-specified):**
- `EXACT` — Exact DT property match (compatible + literal reg base) in s7d ref
- `BINDING` — Shared compatible binding
- `DRIVER` — Shared driver implementation (same compatible → same upstream driver)
- `SIMILAR` — Similar interface, implementation differences
- `UNKNOWN` — Insufficient evidence

**Discipline (refinements #1, #4):** DT identity is a *device-tree / driver-binding* claim, never a silicon-mask identity proof. A reg base absent from source is not evidence of difference unless the node is positively present-and-different. Absence of plaintext BL31/U-Boot strings is NOT taken as proof of encryption/compression.

| Subsystem | coffey node | compatible | reg base | IRQ (GIC SPI) | clk / reset deps | in s7d-ref | in sc2-ref | Class | Lineage reading |
|---|---|---|---|---|---|---|---|---|---|
| **Reset** | `reset-controller@2000` | `amlogic,meson-sc2-reset` | `0x2000` | — | — | yes (ln 701) | yes | DRIVER / INHERITED | SC2-gen reset IP reused by S7D; `meson-s7d.dtsi` itself declares the sc2 compatible |
| **Watchdog** | `watchdog@2100` | `amlogic,meson-sc2-wdt` | `0x2100` | — | clk `xtal` | yes (ln 448) | yes | DRIVER / INHERITED | SC2-gen watchdog IP reused by S7D |
| **Clock** | `clock-controller` | `amlogic,s7d-clkc` | (periphs blk) | — | xtal + plls | yes | **no** | BINDING / S7D-NEW | New clock controller in S7D; absent in SC2 ref |
| **Power domain** | `power-domains` | `amlogic,s7d-power-domain` | — | — | — | yes | **no** | BINDING / S7D-NEW | New power-domain controller in S7D |
| **UART** | `serial@fe078000` (+ `fe07c/fe07e/fe080000`, `7a000`) | `amlogic,meson-uart` | `0xfe078000` (+…) | `0xa8`–`0xac`, `0xa9` | clk_uart, clk_gate | yes (reg literal) | yes (reg literal) | EXACT / DRIVER (both gens) | Long-standing meson UART IP; identical compatible + literal reg base in both s7d and sc2 |
| **I²C** | `i2c@66000` … `@67000` (×5) | `amlogic,meson-i2c` | `0x66000`–`0x67000` | `0xa0`–`0xa4` | clkc gate | yes | yes | EXACT / DRIVER (both gens) | Shared meson I²C IP across generations |
| **eMMC** | `mmc@fe08c000` | `amlogic,meson-v8-mmc` | `0xfe08c000` | `0xb2` | core/mux/clkin | yes (compat+reg) | reg yes, **compat no** | SIMILAR | Reg base reused across gens, but `meson-v8-mmc` compatible is S7D-gen binding; SC2 ref binds a different mmc compatible at the base → interface similar, driver binding differs |
| **SD** | `sd@fe08a000` | `amlogic,meson-v8-mmc` | `0xfe08a000` | `0xb1` | core/mux/clkin | yes | reg yes, compat no | SIMILAR | as eMMC |
| **SDIO** | `sdio@fe088000` | `amlogic,meson-v8-mmc` | `0xfe088000` | `0xb0` | core/mux/clkin | yes | reg yes, compat no | SIMILAR | as eMMC |
| **GIC** | `interrupt-controller@fff01000` | `arm,cortex-a15-gic`, `arm,cortex-a9-gic` | `0xfff01000` | ppi `0x9` | — | yes | yes | BINDING (generic ARM) | GIC-400-class; generic ARM binding shared by both gens — not an Amlogic-lineage signal |
| **GPIO IRQ mux** | `interrupt-controller@4080` | `amlogic,meson-s7-gpio-intc`, `amlogic,meson-gpio-intc` | `0x4080` | — | — | yes (s7 + fallback) | fallback only | SIMILAR / S7-NEW primary | S7-specific primary compatible with the generic meson-gpio-intc fallback shared across gens |
| **Ethernet** | `ethernet@fe368000` | `amlogic,meson-axg-dwmac`, `snps,dwmac-4.00` | `0xfe368000` (s7d-only) | `0x4a` | stmmaceth, clkin0/1 | reg yes | reg **no** | BINDING / S7D-placed | Synopsys dwmac + AXG glue (generic binding); reg base is S7D-specific placement, not in SC2 ref |
| **USB2 phy / DRD** | `usbphy20@fe358000`, `usbphy21@fe348000` | `amlogic, amlogic-crg-drd-usb2` | `0xfe358000` / `0xfe348000` | — | crg_general | reg yes | reg **no** | EXACT / S7D-NEW | CRG-DRD USB2 glue; reg bases s7d-only |
| **USB3 phy / DRD** | `usbphy30@fe358080`, `usbphy31@fe348080` | `amlogic, amlogic-crg-drd-usb3` | `0xfe358080` / `0xfe348080` | — | — | reg yes | reg **no** | EXACT / S7D-NEW | CRG-DRD USB3 glue; reg bases s7d-only |

## Summary by lineage class
- **Inherited SC2 IP (DRIVER-level, source-confirmed):** reset (`meson-sc2-reset`), watchdog (`meson-sc2-wdt`). The S7D SoC dtsi itself re-declares the SC2 compatibles — strongest cross-gen evidence.
- **S7D-new blocks:** clock (`s7d-clkc`), power-domain (`s7d-power-domain`), USB2/USB3 CRG-DRD phys (s7d-only reg bases), GPIO-intc primary compatible, ethernet reg placement.
- **Shared across both generations (generic/long-standing IP):** UART, I²C (exact compatible + literal reg base in both), ARM GIC (generic).
- **Similar interface, different binding:** MMC/SD/SDIO — reg bases reused across gens, but S7D binds `meson-v8-mmc` where SC2 binds a different mmc compatible at the same bases.

## Known limits / not claimed
- No silicon identity is asserted from DT similarity (refinement #1).
- IRQ numbers are coffey GIC SPI indices from the flattened DTB; a per-node IRQ diff vs SC2 source is a further pass (clock/reset *index tables* and pinctrl pin-maps not yet tabulated).
- Exact upstream **commit SHA** not captured at fetch time; branch `5.15.196_20260225` + per-file sha256 above are the current reproducibility anchors (refinement #5 — see note in AML-S0006 follow-up).
