---
finding_id: AML-F0014
title: "coffey first-stage (vendor_boot) module inventory: 52 .ko core SoC drivers; clk-scmi present (SCMI clock provider); socinfo SoC-ID via secure-monitor SMC/efuse"
component: firmware-modules
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
source_urls: []
source_revision: "vendor_boot.img (v4) from OTA URO4.260304.011.B1"
related_findings:
  - AML-F0013
  - AML-F0012
status: promoted
---

# coffey first-stage module inventory + SoC-ID secure-monitor path (AML-E0006C)

Offline unpack of `vendor_boot.img` (v4) ramdisk from the exact-build OTA.
Analysis: `E:\Morphe\device\coffey-ota\analysis\E0006C-FIRSTSTAGE-INVENTORY.md`.

## Observations
- vendor_boot v4, 2 ramdisk fragments (boot type-1, recovery type-2; both
  lz4-legacy). **frag[0] boot = 52 `.ko`**; recovery = 0. 50-entry modules.load.
- **Core SoC drivers are first-stage:** amlogic-uart, amlogic-i2c, amlogic-mmc
  (+cqhci), amlogic-clk + **amlogic-clk-soc-s7d** + amlogic-aoclk-soc-t5w,
  amlogic-reset, amlogic-watchdog, **amlogic-pinctrl-soc-s7d**, amlogic-usb +
  amlogic-inphy, amlogic-power, **amlogic-secmon**, **clk-scmi**, gpio/mailbox/
  pwm/spi/rng/efuse-unifykey/cpufreq/thermal.
- **Load order (dependency chain):** uart(3) … secmon(6) … clk-scmi(11) →
  amlogic-clk(12) → clk-soc-s7d(13) → pinctrl-soc-s7d(16) → reset(21) → power(22)
  → mmc(26) → i2c(28). Clocks/secmon before consumers — corroborates the probe
  diagrams (AML-E0006).
- **G14 resolved:** `clk-scmi.ko` present + in modules.load → the DTB `scmi_clk`
  provider is a shipped first-stage module (despite GKI COMMON_CLK_SCMI unset).
- **SoC-ID path (refinement #2 substantiated):** `amlogic-socinfo.ko` imports
  `__arm_smccc_smc_glue`, `get_meson_sm_input/output_base`, `meson_sm_mutex_*`
  and strings `meson64_trustzone_efuse`, `socinfo_sharemem_base` →
  identification reads a **TrustZone efuse via an SMC / secure-monitor
  shared-memory call**. `amlogic-secmon.ko` (first-stage) exports those symbols
  and uses `__arm_smccc_smc_glue`.

## Interpretation
coffey's SoC identity is obtained through the Amlogic **secure-monitor (SMC)
efuse** path (`amlogic-socinfo` → `amlogic-secmon`), not the mainline
`meson-gx-socinfo` register/syscon 0x47 driver. All core S7D subsystem drivers
ship as first-stage vendor modules with a load order matching the clock-before-
consumer probe dependencies. Completes the shipped-firmware DT→module matrix
(first-stage + vendor_dlkm + system_dlkm).

## Alternative explanations / discipline
- Presence + modules.load = configured-to-load-at-boot, **not** a device-observed
  runtime bind. First-stage correspondences are name/role + load-order (OF-alias
  dump of first-stage .ko is a follow-up); dlkm dwmac is alias-confirmed.
- vermagic = build metadata; no KMI-compatibility claim from OTA presence.
- `__arm_smccc_smc_glue` import proves an SMC code path is linked; it does not
  prove the exact runtime call sequence (not disassembled).

## G16 refinement (alias-backed + defer paths, 2026-10-09)
OF-alias-confirmed L1↔module: `amlogic,meson-uart`→amlogic-uart; `meson-i2c`
(+tee)→amlogic-i2c; `meson-v8-mmc`(+gx/gxbb/gxl/gxm/axg)→amlogic-mmc;
`meson-sc2-wdt`→amlogic-watchdog; `saradc`→amlogic-adc; `crg-drd-usb2/3`→
amlogic-usb (alias normalizes the space to `_`). Clock/reset/pinctrl/scmi carry
**no module OF-alias** — they register via `OF_DECLARE`/`CLK_OF_DECLARE` (early
providers), evidenced by presence + early load order, not autoload aliases.
Deferred-probe: MMC and I²C defer on the clkc provider (`-EPROBE_DEFER` from
`devm_clk_get`), which is why amlogic-clk/-clk-soc-s7d load (pos 11–13) before
mmc(26)/i2c(28); USB2 PHY is register-driven and hard-fails on missing resources.
Source execution paths; runtime defer/retry not device-observed.

## Validation needed / ceiling
Per-driver deferred-probe/failure paths; first-stage OF-alias confirmation;
device-observed runtime binding (device-gated, not taken).

## Codex artifact-backed correction — 2026-10-09

This section supersedes earlier CPU-ID attribution to `amlogic-socinfo`.
The shipped first-stage **amlogic-cpuinfo.ko** (SHA256
`eec63018e8b6a16337d775821bedfc42d840da2f5725af4ef8ba29ed1e4a33c7`)
is configured in first-stage modules.load line 7. Static disassembly corroborates
the pinned vendor CPU-ID source: DT command 0x82000044, request argument 2,
zero remaining arguments, successful status 0, response version u32 2, then
16 ID bytes copied from shared-memory offset 4. Byte indices 0/1/2/3 in that
ID buffer are major/minor/package/misc per the vendor header. S7D major is 0x47.
Mainline at the pinned project revision agrees on 0x47, but its register layout
is major/package/minor/misc from high to low byte. Do not conflate these layouts.

**amlogic-socinfo.ko** exposes the separate `socdata` interface. Its disassembled
`meson64_trustzone_efuse` helper serves NOCS read/write commands selected from
DT (0x82000039/0x82000038), not proof of the CPU-ID call. Its symbols alone
did not justify the earlier identification claim. The shipped socdata module
hash matches the preserved inventory. Neither module was executed.

Source reference: AML-S0006 (CPU-ID driver and headers at its existing pin).
The derived full report and 22-file hash manifest are retained in the Director's
Codex outputs as COORDINATOR-SOC-ID-AND-GAP-RECONCILIATION-2026-10-09.md and
soc-id-source-artifact-hashes.json. Actual returned IDs, runtime binding, and
the interface supplying Android's reported identity string remain unobserved.
Presence plus modules.load establishes configured loading, not execution order.

## CORRECTION — CPU/SoC-ID path is amlogic-cpuinfo, NOT amlogic-socinfo (2026-10-09, Codex disasm, cross-checked)
The "SoC-ID path" claim above (title + body attributing identification to
`amlogic-socinfo` via `meson64_trustzone_efuse`) is **superseded**. Codex static
disassembly + vendor source (re-reconciled) show:
- **CPU/SoC identity = first-stage `amlogic-cpuinfo.ko`** (DT `/cpu_info`,
  compatible `amlogic, cpuinfo`, `cpuinfo_cmd = 0x82000044`, load pos 7 after
  secmon pos 6; SHA256 `eec63018…`). Probe: read DT cmd → get secmon output mem +
  mutex → SMC with x0=cmd, x1=2, x2–7=0 → `__arm_smccc_smc_glue`; success =
  status 0 && out u32[0]==2; copies 16 ID bytes from shared-mem off 4
  (byte 0/1/2/3 = major/minor/package/misc; S7D major = 0x47).
- **`amlogic-socinfo.ko` = a SEPARATE `socdata`/NOCS interface** (DT `/soc_info`,
  `amlogic, socdata`; NOCS read 0x82000039 / write 0x82000038 / auth 0x820000f0);
  its `meson64_trustzone_efuse` serves NOCS read/write, **not** CPU-ID. The
  earlier socinfo→efuse→SoC-ID chain was a conflation.
Both route through `amlogic-secmon` (SMC), but they are distinct functions. S7D
major 0x47 agrees numerically with mainline, but the vendor CPU-ID byte order
(major/minor/package/misc) differs from mainline's register bit-packing — do not
equate them. Runtime bind / returned ID still unobserved. See
COORDINATOR-SOC-ID-AND-GAP-RECONCILIATION (Codex outputs).
