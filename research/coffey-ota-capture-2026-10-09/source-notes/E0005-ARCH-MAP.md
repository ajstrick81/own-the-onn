# AML-E0005 — Hardware Architecture Map (coffey / S7D), offline source-backed

Date 2026-10-09. Read-only, offline. No device contact beyond the prior
AML-E0004 read-only capture.

**Inputs & provenance (commit-pinned):**
- coffey flattened base DT `analysis/vbdt/01_dtbdump_s7d_s905x5m_bm202.dtb.dts`
  (sha256 `197ca22a…`, AML-S0005) — device-authoritative for coffey.
- Upstream CoreELEC/common_drivers **commit `8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734`**
  (branch 5.15.196_20260225; all three DT files byte-identical at this commit,
  sha256 preserved — AML-S0006). Index-table headers fetched at the same commit:
  `include/dt-bindings/clock/s7d-clkc.h` (256 CLKIDs),
  `include/dt-bindings/reset/amlogic,meson-s7d-reset.h` (92),
  `include/dt-bindings/reset/amlogic,meson-sc2-reset.h` (87).

Taxonomy (as AML-E0003): EXACT / BINDING / DRIVER / SIMILAR / UNKNOWN.
Discipline: documented DT binding ≠ silicon identity; indices below are the
DT-level clock/reset wiring, device-confirmed where coffey's raw numeric cells
match the source-resolved number.

## 1. Clock / reset index tables (symbolic → resolved number)
Clock controller `amlogic,s7d-clkc` (phandle 0x15 in coffey DTB); reset
controller `amlogic,meson-sc2-reset` @0x2000 (phandle 0x16); plus an SCMI clock
domain (`scmi_clk`, separate — its `CLKID_SCMI_*` live in s7d-scmi-clkc.h, not
resolved here, flagged UNKNOWN-here).

| Peripheral (DT node) | clocks (CLKID=idx) | resets (RESET=idx) |
|---|---|---|
| saradc @fe026000 | SYS_SAR_ADC=238, SAR_ADC=24, SAR_ADC_SEL=22 | SAR_ANA=83 |
| i2c@66000 (A) | SYS_I2C_M_A=227 | — |
| i2c@66400 (B) | SYS_I2C_M_B=228 | — |
| i2c@66800 (C) | SYS_I2C_M_C=229 | — |
| i2c@66c00 (D) | SYS_I2C_M_D=230 | — |
| i2c@67000 (E) | SYS_I2C_M_E=231 | — |
| serial@fe078000 (UART A) | SYS_UART_A=218 | — |
| serial@fe07c000 (UART C) | SYS_UART_C=220 | — |
| serial@fe07e000 (UART D) | SYS_UART_D=221 | — |
| serial@fe080000 (UART E) | SYS_UART_E=222 | — |
| mmc@fe08c000 (eMMC) | SYS_SD_EMMC_C=211, SD_EMMC_C_SEL=196, SD_EMMC_C=198, GP0_PLL=14 | SD_EMMC_C=154 |
| sd@fe08a000 | SYS_SD_EMMC_B=210, SD_EMMC_B_SEL=193, SD_EMMC_B=195, FCLK_DIV2=1 | SD_EMMC_B=153 |
| sdio@fe088000 | SYS_SD_EMMC_A=209, SD_EMMC_A_SEL=190, SD_EMMC_A=192, GP0_PLL=14, FCLK_DIV2=1 | SD_EMMC_A=152 |
| ethernet@fe368000 | SYS_ETHPHY=204, FCLK_DIV2=1, FCLK_CLK50M=13 | — |
| mdio-mux@360000 | SYS_ETHPHY=204, FCLK_CLK50M=13, ETH_RMII=99 | — |
| usbphy20/21, crg(drd/udc) | SYS_USB=226 | (USB resets RESET_USB* in s7d-reset header, bank RESET0) |
| spi@50000 (spicc0) | SYS_SPICC0=225, SPICC=189 | — |
| pwm A–F @58000–58a00 | PWM_{A..F}_SEL=169/172/175/178/181/184 | — |
| pwm G–J @58c00–59200 | CLKID_SCMI_PWM_{G..J} (SCMI domain, UNKNOWN-here) | — |
| vpu | VAPB=167, SYS_VPU_INTR=237, VPU_0=144, VPU_1=147, VPU=148 | — |
| vdec (dos) | SYS_DOS=203, VDEC=127, HCODEC=141, HEVCF=134 | — |

**Device-confirmed (coffey raw numeric == source-resolved):**
- saradc: coffey `clocks=<.. 0xee 0x18 0x16>` = 238/24/22 ✓; `resets=<.. 0x53>` = 83 = RESET_SAR_ANA ✓.
- i2c@66000: coffey `clocks=<0x09 0xe3>` → 0xe3 = 227 = CLKID_SYS_I2C_M_A ✓.
- SD/eMMC reset bank: RESET_SD_EMMC_A/B/C = 152/153/154 (contiguous).

Classification: clock/reset **index tables = EXACT** (compatible + resolved
index both match coffey). Clock controller binding itself = S7D-new
(`s7d-clkc`); reset controller binding = inherited-SC2 (`meson-sc2-reset`), but
the **S7D reset index namespace** (s7d-reset.h) is S7D-specific.

## 2. Pin controllers & GPIO banks
`pinctrl@4000` = `amlogic,meson-s7d-periphs-pinctrl` (periphs domain, phandle 0x19).
- `bank@4000`: reg mux `@0x4000` len `0x4c`, gpio `@0x40c0` len `0x2cc`;
  `gpio-controller`; `gpio-ranges = <&self 0 0 0x54>` → **84 GPIOs** (periphs bank).
- 49 pin-mux state nodes (function → pad groups → drive/bias). Full table in
  `e0005_arch.out`. Representative:

| state node | function | groups | drive/bias |
|---|---|---|---|
| i2c0_pins1 | i2cm_a | i2cm_a_sda_cc1, i2cm_a_scl_cc2 | ds=3, bias-disable |
| i2c1_pins1..4 | i2cm_b | sda/scl on c6/c7, dv1/dv2, h6/h7, x17/x18 | ds=3, bias-disable |
| i2c2_pins1..3 | i2cm_c | dv5/dv6, h0/h1, h8/h9 | ds=3, bias-disable |
| i2c3_pins1 | i2cm_d | x10/x11 | ds=3, bias-disable |
| i2c4_pins1..2 | i2cm_e | c2/c3, d2/d3 | ds=3, bias-disable |
| d_uart2 | uart_d | tx_z0,rx_z1,cts_z2,rts_z3 | bias-pull-up |
| e_uart2/e_uart3 | uart_e | tx/rx on z11/z12, z8/z9 | bias-pull-up |
| ao_to_sd_uart_pins / ao_uart_pins | uart_b | tx/rx on c, d | bias-pull-up |
| sd_iso7816_pins | iso7816 | clk_h8, data_h9 | bias-pull-down |
| hdmitx_hpd_gpio | gpio_periphs | GPIOH_1 | bias-disable |
| diseqc_in/out | diseqc_* | diseqc_in / diseqc_out | bias-pull-down |

(Note: `pinctrl@4000` is the **periphs** controller; an AO/always-on pinctrl may
exist in a separate domain — not enumerated here. GPIO bank letter names
GPIOC/D/H/X/Z observed in the pad group names.)

## 3. Reserved-memory regions (coffey, device-authoritative)
| region | base/size | compatible | flags |
|---|---|---|---|
| ramdump_bl33z@0 | reg 0x0 len 0x1800000 (24M) | — | — |
| ramoops@0x7400000 | 0x7400000 len 0x100000 | ramoops | pstore/console |
| linux,iotrace | 0x4f00000 len 0x100000 | amlogic,iotrace | — |
| **linux,secmon** | **0x5000000 len 0x2400000 (36M)** | shared-dma-pool | **no-map** (secure monitor / TEE) |
| linux,meson-fb | 0x1f800000 len 0x800000 | amlogic,meson-fb | framebuffer |
| heap-gfx / heap-fb | size 0x5800000 / 0x3800000 | shared-dma-pool | reusable |
| heap-secure / mali_protected@c0000000 | dynamic | heap-secure-mem / mali-reserved | no-map (secure) |
| codec_mm_cma | size 0x16c00000 (364M) | shared-dma-pool | reusable |
| secure_vdec_reserved | size 0x1000000 | amlogic,secure-vdec-reserved | no-map (secure) |
| di_cma / vdin1_cma / linux,cma | dynamic / 0x800000 | shared-dma-pool | reusable |

Security-relevant: `linux,secmon` (36M no-map) is the secure-monitor/TEE carve;
`heap-secure`, `mali_protected`, `secure_vdec_reserved` are no-map secure pools
(protected-media path). Documented bindings only — no runtime behavior claimed.

## 4. Interrupt routing
Global `interrupt-parent = <0x01>` → GIC `interrupt-controller@fff01000`
(`arm,cortex-a15-gic`, GIC-400 class; 62 interrupt properties in the tree). SPI
numbers per peripheral captured in the AML-E0003 matrix (e.g. UART A–E
0xa8–0xac; I²C A–E 0xa0–0xa4; eth 0x4a; mmc/sd/sdio 0xb2/0xb1/0xb0; saradc 0xb5).
A second-level GPIO IRQ mux `interrupt-controller@4080`
(`amlogic,meson-s7-gpio-intc`) routes pad interrupts up to the GIC.

## 5. Dependency graph (DT-level, documented bindings)
Roots (controllers) → consumers:
```
xtal(24MHz) ──> s7d-clkc(0x15) ──clocks──> UART A/C/D/E, I2C A–E, SD/eMMC A/B/C,
                                           ETH+MDIO, USB(crg), SPICC, PWM A–F,
                                           VPU, VDEC, SARADC
                 scmi_clk ───────clocks──> PWM G–J  (SCMI domain, separate)
meson-sc2-reset(0x16 @0x2000) ──resets──> SARADC(83), SD/eMMC A/B/C(152/153/154),
                                           USB* (RESET0 bank)   [S7D reset index ns]
meson-sc2-wdt @0x2100 ──clk──> xtal
periphs-pinctrl@4000(0x19, 84 GPIO) ──pinmux──> I2C A–E, UART B/D/E, ISO7816,
                                           HDMI-HPD, DiSEqC
GIC@fff01000(0x01) <──interrupts── (all SPI peripherals); gpio-intc@4080 <── pad IRQs
reserved-memory ──dma-pool──> VPU/VDEC/Mali (codec_mm, heap-gfx/fb, secure pools);
                              secmon(no-map) ← ATF/TEE
```

## Separation of evidence
- **Documented bindings (source+DT):** everything above — compatible strings,
  reg ranges, clock/reset indices, pinmux groups, reserved-memory nodes.
- **Device-confirmed:** the clock/reset indices spot-checked against coffey's
  flattened numeric cells (saradc, i2c, SD/eMMC resets).
- **Observed runtime behavior:** NONE claimed here (would need on-device clk/reset
  state dumps — not collected; out of the read-only scope used so far).
- **Unresolved / UNKNOWN:** SCMI clock-domain indices (s7d-scmi-clkc.h not
  fetched); AO-domain pinctrl (separate controller, not enumerated); actual PLL
  frequencies at runtime; physical GPT offsets (root-gated, per AML-F0008).
