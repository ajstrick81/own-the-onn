# AML-E0006 — Driver & Initialization Architecture (coffey / S7D), offline source-backed

Date 2026-10-09. Read-only, offline. Responds to coordinator AML-RESEARCH-001.
**Three-layer discipline (per brief):** (L1) what coffey's *shipped* DTB declares;
(L2) what *mainline* Linux supports; (L3) what coffey's *vendor* kernel
implements. These overlap but are NOT interchangeable.

## Pinned sources (provenance)
- **coffey shipped DTB** `01_dtbdump_s7d_s905x5m_bm202.dtb.dts` sha256 `197ca22a…` (AML-S0005).
- **CoreELEC common_drivers** commit `8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734` (AML-S0006):
  `drivers/tty/serial/meson_uart.c` sha256 `23d5647d…` (vendor driver = L3).
- **torvalds/linux mainline** commit `af32da41b0327b9c6a37856ba82b6760d6c8d10e` (AML-S0008):
  `arch/arm64/boot/dts/amlogic/amlogic-s7d.dtsi` `d3390720…`,
  `…/amlogic-s7d-s905x5m-bm202.dts` `57cfa302…`,
  `drivers/tty/serial/meson_uart.c` `eb3cd554…`,
  `drivers/soc/amlogic/meson-gx-socinfo.c` `515fa88f…`.

## 1. UART — detailed case study (coordinator priority 1)
| Layer | compatible | reg / IRQ | clocks (names) | driver match | probe internals |
|---|---|---|---|---|---|
| **L1 coffey shipped DTB** | `amlogic,meson-uart` | serial@fe078000 (+fe07c/7e/80000, 7a000); SPI 0xa8–0xac | `clk_uart`, `clk_gate` (clkc CLKID_SYS_UART_A=218…) | → L3 vendor | — |
| **L2 mainline torvalds** | `amlogic,s7d-uart`, `amlogic,meson-s4-uart` | serial@7a000; GIC_SPI 169 edge-rising; **status=disabled** | `xtal`,`pclk`,`baud` (3× xtal) | mainline `meson_uart.c` of_match has `amlogic,meson-s4-uart` (+meson6/8/8b/gx/g12a/a1) | `meson_uart_probe_clocks` gets xtal/pclk/baud; `request_irq`; has_xtal_div2 speed math |
| **L3 coffey vendor driver** | matches `amlogic,meson-uart` (+`amlogic, meson-uart`) ONLY | — | gets `clk_gate` + `clk_uart` | CoreELEC `meson_uart.c` of_match = **only `meson-uart`** (no s4-uart, no s7d-uart) | `meson_uart_probe`: `devm_clk_get("clk_gate")`, `devm_clk_get("clk_uart")`, `devm_request_irq` |

**Key result:** coffey does **NOT** use the mainline `s7d-uart → meson-s4-uart`
fallback. coffey's shipped DTB declares `amlogic,meson-uart` and the CoreELEC
vendor driver matches exactly that — a *different* driver path, clock-name set
(clk_uart/clk_gate vs xtal/pclk/baud), and IRQ registration (devm_ vs plain) than
mainline. The coffey DTB clock-names match the CoreELEC driver → coffey runs a
self-consistent **vendor** UART stack end-to-end. The mainline s7d/s4 fallback is
a parallel, independent upstreaming coffey's shipped stack does not exercise.
→ Concrete demonstration that a *shared/compatible interface* (both are "a meson
UART") is **not** proof of an *inherited implementation*.

## 2. Compatible-string → driver binding matrix (seed; L1 coffey → L3 vendor)
| subsystem | L1 compatible | L3 vendor driver (match) | mainline (L2) equivalent | class |
|---|---|---|---|---|
| UART | amlogic,meson-uart | meson_uart.c (`meson-uart`) | s4-uart fallback (NOT used by coffey) | SIMILAR-interface / vendor-impl |
| I²C | amlogic,meson-i2c | (CoreELEC i2c-meson) | meson-axg/… | vendor-impl |
| eMMC/SD/SDIO | amlogic,meson-v8-mmc | (CoreELEC mmc) | meson-gx/sm1 mmc | vendor-impl (binding S7D-gen) |
| Ethernet | amlogic,meson-axg-dwmac + snps | stmmac + amlogic glue | same snps dwmac | DRIVER-shared (snps) |
| USB | amlogic,amlogic-crg-drd-usb2/3 | CoreELEC crg-drd | (not in mainline s7d yet) | vendor-impl |
| Clock | amlogic,s7d-clkc | CoreELEC s7d clk | mainline s7d clk (different) | vendor-impl |
| Reset | amlogic,meson-sc2-reset | CoreELEC sc2 reset | — | inherited-SC2 binding |
| Pinctrl | amlogic,meson-s7d-periphs-pinctrl | CoreELEC pinctrl-meson | mainline `amlogic,pinctrl-s7d`/`-s7` (different) | vendor-impl |
(Rows beyond UART are the binding targets; per-driver probe tracing = follow-on.)

## 3. SoC identification (coordinator Finding C)
Mainline `meson-gx-socinfo.c` (`515fa88f…`): `{ "S7D", 0x47 }`, package
`{ "S905X5M", 0x47, 0x1, 0xf }`. Mechanism: reads **`AO_SEC_SD_CFG8` (0xe0)** via
a **syscon regmap** (`syscon_node_to_regmap`), then `socinfo_to_major/minor/pack`.
- **Corroboration:** S7D=0x47 is an independent, hardware-register-derived
  identifier matching our S7D classification (so far established via DT
  compatible strings). It strengthens the S7D call at the *source* level.
- **Caveats (per brief):** (a) this is the GX-family driver; whether coffey's
  vendor kernel enables it / routes s7d through it is **unverified**;
  (b) `AO_SEC_SD_CFG8` is an AO *secure* register — not assumed shell-readable;
  (c) no register-access experiment attempted. UNKNOWN until kernel-config +
  socinfo-node presence in coffey's DT are checked.

## 4. Linux → secure-firmware boundary (coordinator Finding D) — 4-layer model
| layer | coffey (L1/L3) | mainline (L2) |
|---|---|---|
| Linux subsystem driver | CPU idle/hotplug, regulators via PSCI consumers | same |
| kernel firmware interface | **`psci { compatible="arm,psci-0.2"; method="smc"; }`**; CPUs `enable-method=psci`; cpuidle `arm,psci-suspend-param` | PSCI **1.0** per brief; `secure-monitor` `amlogic,meson-gxbb-sm` |
| firmware implementation | **BL31/ATF in the opaque bootloader payload** (AML-F0010) — ownership/impl NOT independently verified | — |
| hardware controller | s7d power-domain / clock / reset controllers (AML-E0005) | — |

**Divergence:** coffey ships **PSCI 0.2**; mainline s7d declares PSCI 1.0. Both
route through SMC to a secure monitor; coffey's secure-monitor payload is the
opaque BL31 region — interface defined, implementation unverified.

## 5. Memory note (coordinator Finding A)
Mainline bm202 `model="Amlogic S905X5M BM202 Development Board"`, `compatible=
"amlogic,bm202","amlogic,s7d"`, `memory@0 reg=<0 0 0 0x80000000>` = 2 GiB
dev-board default. coffey's **own shipped DTB** declares
`memory@0 { linux,usable-memory = <0 0 0 0x80000000> }` = **2 GiB usable** —
so 2 GiB is corroborated *for coffey* (not merely assumed from the dev board),
though `usable-memory` is a usable window (secure carveouts reduce it), not a
proven total-DRAM figure.

## Evidence classification / unresolved
- **Documented + device-matched:** UART L1↔L3 binding (coffey DTB clock-names
  match vendor driver); PSCI 0.2 node; 2 GiB usable-memory.
- **Source-documented (mainline), coffey-enablement UNVERIFIED:** s7d/s4 UART
  fallback, SoC-ID 0x47 via AO_SEC_SD_CFG8, PSCI 1.0.
- **Not claimed:** runtime init ORDER (DT deps ≠ boot/probe order); TrustZone
  enforcement; which exact ATF/BL31 impl runs.
- **Open (gap register):** per-driver probe tracing for I²C/MMC/USB; coffey
  kernel-config for socinfo; AO-pinctrl; SCMI clocks.

---
# E0006 expansion (2026-10-09) — I²C / MMC / USB three-layer + config layer

Responds to coordinator REL-20261009-Q review. Evidence refinement #1 applied:
all driver results below are **verified shipped-DTB (L1) ↔ vendor-source (L3)
correspondences**, NOT proof of the exact production runtime driver (which needs
matching kernel binary / runtime evidence). Pinned: CoreELEC `8646fbd1`,
mainline `af32da41`.

## Pattern confirmed: vendor-vs-mainline divergence is BROAD (not UART-only)
| subsys | L1 coffey DTB compatible | L3 vendor of_match (file) | L2 mainline of_match (file) | clocks (L1) | reset / IRQ (L3) | verdict |
|---|---|---|---|---|---|---|
| UART | amlogic,meson-uart | `meson-uart`,`meson, meson-uart` (meson_uart.c) | meson-s4-uart (+6/8/8b/gx/g12a/a1) (meson_uart.c) | clk_uart, clk_gate | devm_request_irq | **divergent** (coffey≠mainline) |
| I²C | amlogic,meson-i2c | `meson-i2c`,`meson-tee-i2c` (i2c-meson.c) | **meson6/gxbb/axg-i2c only — NO `meson-i2c`** (i2c-meson.c) | 1 clk (devm_clk_get NULL) | register-level `meson_i2c_reset_tokens` (no reset-controller); devm_request_irq | **divergent** |
| eMMC/SD/SDIO | amlogic,meson-v8-mmc | gx/gxbb/gxl/gxm/axg **+ `meson-v8-mmc`→meson_v8_data** (meson-gx-mmc.c) | gx/gxbb/gxl/gxm/axg **— NO v8-mmc** (meson-gx-mmc.c) | core, mux0/1, clkin0-2, mux_div | reset_control + irq | **divergent** (vendor-added v8) |
| USB2/USB3 PHY | amlogic,amlogic-crg-drd-usb2/usb3 | dedicated `phy-aml-crg-drd-usb2/usb3.c` (crgdrdphy/) | **none for s7d** (mainline = dwc3-meson-g12a + phy-meson-g12a-usb2/3) | crg_general | custom register-level PHY reset | **divergent** (vendor-proprietary PHY) |

**Conclusion:** the UART finding (AML-F0011) generalizes. For every priority
subsystem, coffey's shipped DTB uses a **vendor** compatible string whose match
lives in the CoreELEC vendor driver, and the **mainline** driver's of_match does
NOT contain coffey's string (UART/I²C/MMC) or has no s7d driver at all (USB PHY).
coffey runs the Amlogic **vendor** driver stack, not mainline. (AML-F0012.)

## Config layer — coffey = GKI base + Amlogic vendor modules
Preserved config `coffey-config-5.15.196.txt` (7035 lines, 1953 set symbols) has
**zero `CONFIG_AMLOGIC_*` symbols** → it is the Android **GKI base config**; the
Amlogic drivers above ship as **vendor modules** (the `common_drivers` tree) NOT
represented in this config. Consequences:
- Generic cores present (GKI): `CONFIG_I2C=y`, `CONFIG_MMC=y`, `CONFIG_USB_DWC3=y`
  (DUAL_ROLE, OF_SIMPLE), `ARM_SCMI_PROTOCOL=y`, `ARM_SCMI_TRANSPORT_SMC=y`,
  `ARM_SCMI_TRANSPORT_MAILBOX=y`, `RESET_SCMI=y`.
- **SoC-ID (Finding C, resolved to its ceiling):** no `SOCINFO` symbol in the GKI
  base config, and `meson_gx_socinfo_init` is **not found** in the CoreELEC vendor
  tree. So there is **no positive evidence** coffey runs the 0x47 gx-socinfo path;
  enablement is **not determinable from a GKI base config** (would be a vendor
  module if present). The 0x47 mapping stays **mainline-source-level**; coffey
  runtime identification remains **unverified** (refinement #2 preserved).
- **SCMI clock (Finding/parallel):** `# CONFIG_COMMON_CLK_SCMI is not set` →
  the standard SCMI clock provider is NOT in the GKI base. The DTB's `scmi_clk`
  consumers (PWM G–J) would need a vendor-module SCMI clock provider; whether one
  exists is **undetermined** (vendor modules not in this config). SCMI protocol +
  SMC/mailbox transport + RESET_SCMI ARE present.

## AO-pinctrl (G3 — partly resolved)
coffey's shipped DTB declares **only** `pinctrl@4000`
(`amlogic,meson-s7d-periphs-pinctrl`). **No separate AO-domain pinctrl node** is
present in the extracted DT (`aobus` appears only as a reg-name of an unrelated
node). So AO pinmux is either folded into the periphs bank or simply not exposed
in this DTB — not a separate controller here.

## Firmware/PSCI (refinement #3 preserved)
PSCI 0.2 + SMC remains an **interface declaration**; the BL31/ATF implementation
is the opaque bootloader payload (AML-F0010) and is **not** independently
verified. SCMI-over-SMC (`ARM_SCMI_TRANSPORT_SMC=y`, `RESET_SCMI=y`) confirms a
second SMC-based firmware interface is compiled in (GKI base).

## Bootloader headers (refinement #4 preserved)
The `@ML `/`@AMLBOOT` headers and BL2E/BL2X/DDRF table are **identifiable
metadata + candidate signature regions**; no signature has been
**cryptographically verified**. High entropy / isolated strings remain
**insufficient** proof of encryption or stage identity (refinement #5).
