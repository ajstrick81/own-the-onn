# AML-E0006 — I²C / MMC / USB init-probe sequence diagrams (source-backed)

Date 2026-10-09. Offline. Built from the **L3 vendor driver source** (CoreELEC
`common_drivers` @ `8646fbd1`) with **L1 shipped-DTB** dependency inputs
(coffey DTB, AML-S0005). **Refinement #1:** these are the *vendor-source* probe
flows that correspond to coffey's DTB bindings; they are **not** proof the
production device loads these exact modules at runtime (that is AML-E0006B /
on-device evidence). Reset/clock/IRQ facts are read from the driver `.probe`.

## I²C — `meson_i2c_probe` (drivers/i2c/busses/i2c-meson.c)
DT inputs (L1): `compatible="amlogic,meson-i2c"`, 1 reg window, `clocks=<&clkc
CLKID_SYS_I2C_M_{A..E}>` (218/227–231 range), `interrupts` SPI 0xa0–0xa4. No
reset-controller (reset is register-level `meson_i2c_reset_tokens`).
```mermaid
sequenceDiagram
    participant DT as DTB node (meson-i2c)
    participant DRV as meson_i2c_probe (L3 vendor)
    participant CLK as clkc (CLKID_SYS_I2C_M_x)
    participant IRQ as GIC SPI 0xa0-0xa4
    participant CORE as i2c core
    DRV->>DRV: devm_kzalloc(meson_i2c)
    DRV->>CLK: devm_clk_get(dev, NULL)  %% single anonymous clock
    DRV->>DT: platform_get_resource(MEM,0) -> devm_ioremap_resource
    Note over DRV,DT: tee variant also reads of_property "tee_id"
    DRV->>IRQ: platform_get_irq(0); devm_request_irq(meson_i2c_irq)
    DRV->>CLK: clk_prepare(clk)
    DRV->>DRV: fill adap (algo=meson_i2c_algorithm, of_node)
    DRV->>DRV: pm_runtime_enable + autosuspend + get_sync
    DRV->>CLK: clk_get_rate(clk) -> i2c->clk_rate
    DRV->>CORE: i2c_add_adapter(adap)
```
Deps: clkc gate clock → prepare; GIC IRQ; register-level soft-reset only.

## MMC/eMMC/SDIO — `meson_mmc_probe` (drivers/mmc/host/meson-gx-mmc.c)
DT inputs (L1): `compatible="amlogic,meson-v8-mmc"` (vendor-added entry →
`meson_v8_data`), **3 reg windows** (controller / clk-tree / pin-mux),
`clocks= core, mux0, mux1, clkin0, clkin1[, clkin2]` + `mux_div`,
`resets=<&reset RESET_SD_EMMC_{A/B/C}>` (152/153/154), IRQ 0xb0/0xb1/0xb2.
```mermaid
sequenceDiagram
    participant DT as DTB node (meson-v8-mmc)
    participant DRV as meson_mmc_probe (L3 vendor)
    participant RST as reset (RESET_SD_EMMC_x) / device_reset
    participant CLK as clkc (core/mux0/mux1/clkin/mux_div)
    participant IRQ as GIC SPI 0xb0-0xb2
    participant MMC as mmc core
    DRV->>MMC: mmc_alloc_host(meson_host)
    DRV->>RST: (optional) device_reset(dev)
    DRV->>DT: get 3 MEM resources -> regs / clk_tree_base / pin_mux_base (ioremap)
    DRV->>IRQ: platform_get_irq(0)
    DRV->>DT: (optional) pinctrl "clk-gate" state
    DRV->>CLK: devm_clk_get("core"); clk_prepare_enable(core_clk)
    DRV->>CLK: meson_mmc_clk_init() %% mux0/mux1/clkin0-2 + mux_div parents/rates
    DRV->>DRV: meson_mmc_cfg_init()
    DRV->>IRQ: request_threaded_irq(meson_mmc_irq + _thread, IRQF_ONESHOT[|TRIGGER_HIGH for SDIO])
    DRV->>MMC: mmc_add_host()
```
Deps: core clock gate → mux tree (DVFS of card clock); optional reset; threaded
IRQ. **SDIO path** differs (IRQF_TRIGGER_HIGH, global `sdio_host`, card-irq
handling) — one driver serves eMMC (C)/SD (B)/SDIO (A) by the reg/clock set.

## USB2 PHY — `amlogic_crg_drd_usb2_probe` (drivers/usb/crgdrdphy/phy-aml-crg-drd-usb2.c)
DT inputs (L1): `compatible="amlogic,amlogic-crg-drd-usb2"`, reg (phy base +
reset base + per-port cfg), `clock-names="crg_general"`, props `portnum`,
`reset-level` (default 0x84), optional `usb-phy-trim-reg`, `usb-clk-reg`. The
**controller** is DWC3 (`CONFIG_USB_DWC3=y`, dual-role); this driver is the PHY.
```mermaid
sequenceDiagram
    participant DT as DTB node (crg-drd-usb2)
    participant DRV as amlogic_crg_drd_usb2_probe (L3 vendor)
    participant REG as PHY/reset/cfg MMIO
    participant CLK as crg_general clock
    participant PHY as usb phy framework / DWC3
    DRV->>DT: of_get_property "portnum" (ports to init)
    DRV->>DT: (optional) devm_gpiod_get_index (vbus gpio)
    DRV->>DRV: of_device_get_match_data -> pdata
    DRV->>REG: ioremap phy_base; ioremap reset_base (reset-level prop)
    loop per port (portnum)
        DRV->>REG: ioremap phy_cfg_base[i]
    end
    DRV->>DT: (optional) ioremap usb-phy-trim-reg / usb-clk-reg
    DRV->>CLK: get/enable crg_general
    DRV->>REG: custom register-level PHY reset (usb_reset_bit / phy_reset_level_bit)
    DRV->>PHY: usb_add_phy_dev(); INIT_DELAYED_WORK (set_mode / ACA detect)
```
Deps: `crg_general` clock; **register-level PHY reset (no reset-controller)**;
DWC3 core consumes this PHY. **No mainline s7d PHY equivalent** (mainline uses
dwc3-meson-g12a + phy-meson-g12a-usb2/usb3).

## Cross-subsystem dependency summary
```
clkc (s7d-clkc) ──gate/mux──> I2C(clk) · MMC(core+mux tree) · USB(crg_general)
reset: I2C=register-level soft-reset; MMC=RESET_SD_EMMC_x (+optional device_reset);
       USB=register-level PHY reset  (none use a shared reset-controller phandle for the data path)
GIC ──SPI──> I2C(0xa0-a4) · MMC(0xb0-b2) · (USB IRQs via DWC3 core)
pinctrl@4000 ──pinmux──> I2C pads, MMC clk-gate/pins
DWC3 core (GKI) ──consumes──> crg-drd USB PHY (vendor)
```

## Evidence classification
- **Source-backed (L3 vendor), DTB-corroborated (L1):** every probe step + clock/
  reset/IRQ dependency above (read from driver `.probe` + coffey DTB properties).
- **NOT established:** that the production device loads these exact modules/that
  this is the runtime probe order (needs AML-E0006B module inventory + on-device
  dmesg/sysfs). Diagram = vendor-source init flow, not a captured runtime trace.
- **Open:** SDIO-specific card-IRQ timing; USB3 PHY probe (phy-aml-crg-drd-usb3.c,
  analogous, not yet diagrammed); DWC3 glue binding details.

---
# G16 — alias-backed matrix + deferred-probe / failure paths (2026-10-09)

## Alias-backed DT-compatible → first-stage module (confirmed from .ko modinfo of: aliases)
| DT compatible (L1) | first-stage module | OF-alias evidence |
|---|---|---|
| amlogic,meson-uart (+ "amlogic, meson-uart") | amlogic-uart.ko | `of:N*T*Camlogic,meson-uart` (+ `_meson-uart` space-variant) |
| amlogic,meson-i2c | amlogic-i2c.ko | `of:N*T*Camlogic,meson-i2c` (+ `meson-tee-i2c`) |
| amlogic,meson-v8-mmc | amlogic-mmc.ko | aliases `meson-gx/gxbb/gxl/gxm/axg/v8-mmc` (one module, all gens) |
| amlogic,meson-sc2-wdt | amlogic-watchdog.ko | `of:...Cmeson-sc2-wdt` |
| amlogic,saradc | amlogic-adc.ko | `of:...Csaradc` |
| amlogic, amlogic-crg-drd-usb2/3 | amlogic-usb.ko | `of:...Camlogic,_amlogic-crg-drd-usb2` (space→`_`) |
| amlogic,s7d-clkc / meson-sc2-reset / meson-s7d-periphs-pinctrl / scmi_clk | amlogic-clk-soc-s7d / amlogic-reset / amlogic-pinctrl-soc-s7d / clk-scmi | **no module OF-alias** — these register via `OF_DECLARE`/`CLK_OF_DECLARE` (early providers), not module-autoload aliases; present as first-stage modules loaded early. Binding is by OF provider registration, not alias autoload. |

So UART/I²C/MMC/WDT/SARADC/USB bindings are now **OF-alias-confirmed** (L1 DTB ↔
L3 module). Clock/reset/pinctrl/SCMI bind as OF-declared providers (no alias) —
their presence + early load order (secmon→clk-scmi→clk→pinctrl→reset) is the
evidence, not an alias.

## Deferred-probe & failure paths (from vendor `.probe`, L3)
Ordered `modules.load` (clocks/secmon before consumers) minimizes defers, but the
kernel driver model still uses `-EPROBE_DEFER` when a provider is not yet ready.
- **I²C** `meson_i2c_probe`: `devm_clk_get` → `PTR_ERR` (**-EPROBE_DEFER if clkc
  not ready**, else -E on real failure); `ioremap` fail → `PTR_ERR(regs)`;
  `platform_get_irq` < 0 → return irq (**can be -EPROBE_DEFER** if the irqdomain
  isn't up); `clk_prepare` fail → return; tee variant missing `tee_id` → fail.
- **MMC** `meson_mmc_probe` (most defer-aware): pinctrl get → `if ret !=
  -EPROBE_DEFER dev_err`; `device_reset_optional` → **EPROBE_DEFER-aware**;
  3× `ioremap` → `PTR_ERR` hard-fail; `devm_clk_get("core")` → `PTR_ERR` →
  `goto err_core_clk` (**defers until clkc ready**); `meson_mmc_clk_init` fail →
  `goto err_init_clk`; `request_threaded_irq` fail → err.
- **USB2 PHY** `amlogic_crg_drd_usb2_probe` (register-level, mostly hard fail):
  no usb port → `-ENOMEM`; missing `of_device_get_match_data` → `-EINVAL`;
  `ioremap` phy/reset/per-port cfg fail → `PTR_ERR` (no defer; depends on crg_general clock only).
Interpretation: MMC and I²C are the real deferred-probe consumers (wait on the
clkc provider = `amlogic-clk`/`amlogic-clk-soc-s7d`), which is exactly why those
clock modules load first (positions 11–13) ahead of mmc(26)/i2c(28). USB PHY is
reg-driven and fails hard on missing resources rather than deferring.
**Discipline:** these defer/fail branches are the driver source's execution
paths; actual runtime defer/retry behavior is not device-observed here.
