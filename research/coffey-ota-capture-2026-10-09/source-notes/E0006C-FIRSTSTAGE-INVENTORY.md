# AML-E0006C — First-stage (vendor_boot) module inventory + combined firmware matrix

Date 2026-10-09. Offline, read-only on `vendor_boot.img` (header v4) from the
AML-S0005 OTA. Original image unmodified; ramdisk extracted to a temp dir.

## vendor_boot structure (parsed)
- v4, page_size 2048, vendor_ramdisk_size 27,054,455, dtb_size 81,532.
- **Ramdisk table: 2 fragments** — frag[0] type 1 (boot, 11,873,854 B) and
  frag[1] type 2 **"recovery"** (15,180,601 B). Both **lz4-legacy**.
- **frag[0] (boot) = 52 `.ko`**; frag[1] (recovery) = 0 `.ko`.
- All 52 first-stage modules vermagic `5.15.196-…-g10bd23fd47b5` (= vendor_dlkm
  build; **not** the running GKI uname g3d26c188ef7e — build metadata only, no KMI
  claim). Table: `dlkm/INVENTORY/firststage-modules.tsv`.

## First-stage core SoC drivers (all present)
`amlogic-uart`, `amlogic-i2c`, `amlogic-mmc`(+`cqhci`), `amlogic-clk` +
**`amlogic-clk-soc-s7d`** + `amlogic-aoclk-soc-t5w`, `amlogic-reset`,
`amlogic-watchdog`, **`amlogic-pinctrl-soc-s7d`**, `amlogic-usb` + `amlogic-inphy`,
`amlogic-power`, `amlogic-secmon`, `amlogic-gpio`, `amlogic-mailbox`, `amlogic-pwm`,
`amlogic-spi`, `amlogic-rng`, **`clk-scmi`**, `amlogic-efuse-unifykey`,
`amlogic-cpufreq`, `amlogic-thermal`.

## Boot-time load order (firststage modules.load — the real init dependency chain)
`…uart(3) … secmon(6) … clk-scmi(11) → amlogic-clk(12) → clk-soc-s7d(13) →
aoclk(14) → gpio(15) → pinctrl-soc-s7d(16) → mailbox(17) → pwm(18) →
reset(21) → power(22) → cpufreq(23) → thermal(24) → cqhci(25) → mmc(26) →
efuse-unifykey(27) → i2c(28) → spi(29) → rng(30) …` (50 load entries).
Order corroborates the probe diagrams: **clock/scmi/secmon before consumers**.

## G14 RESOLVED — SCMI clock provider
**`clk-scmi.ko` is present and in first-stage modules.load (pos 11).** So the DTB
`scmi_clk` consumers (PWM G–J) have a shipped provider — even though GKI
`COMMON_CLK_SCMI` is unset, the vendor ships `clk-scmi` as a first-stage module.
(Positive evidence; runtime bind still not device-observed.)

## SoC-ID path substantiated through secure-monitor (coordinator refinement #2)
`amlogic-socinfo.ko` (dlkm) imports **`__arm_smccc_smc_glue`**,
`get_meson_sm_input_base`/`output_base`, `meson_sm_mutex_lock/unlock`, and strings
**`meson64_trustzone_efuse`**, **`socinfo_sharemem_base`**, `efuse_hal_api_arg`.
`amlogic-secmon.ko` (first-stage, load pos 6) **exports** those `meson_sm_*` /
`secmon_sharemem_*` symbols and itself uses `__arm_smccc_smc_glue`. → the vendor
SoC-identification path **reads a TrustZone efuse via an SMC/secure-monitor
shared-memory call** (binary-symbol evidence, not just a module dependency). This
is the coffey identification mechanism — distinct from the mainline
`meson-gx-socinfo` register/syscon 0x47 path.

## Combined shipped-firmware DT-compatible → module matrix
| DT compatible (L1) | module | stage | evidence |
|---|---|---|---|
| amlogic,meson-uart | amlogic-uart.ko | vendor_boot | role/filename + load order |
| amlogic,meson-i2c | amlogic-i2c.ko | vendor_boot | role/filename + load order |
| amlogic,meson-v8-mmc | amlogic-mmc.ko (+cqhci) | vendor_boot | role/filename + load order |
| amlogic,s7d-clkc | amlogic-clk-soc-s7d.ko (+amlogic-clk) | vendor_boot | name = soc-s7d |
| (AO clk) | amlogic-aoclk-soc-t5w.ko | vendor_boot | name |
| amlogic,meson-sc2-reset | amlogic-reset.ko | vendor_boot | role/filename |
| amlogic,meson-sc2-wdt | amlogic-watchdog.ko | vendor_boot | role/filename |
| amlogic,meson-s7d-periphs-pinctrl | amlogic-pinctrl-soc-s7d.ko | vendor_boot | name = soc-s7d |
| amlogic,amlogic-crg-drd-usb2/3 | amlogic-usb.ko + amlogic-inphy.ko | vendor_boot | role/filename |
| amlogic,s7d-power-domain | amlogic-power.ko | vendor_boot | role/filename |
| scmi_clk (PWM G–J) | clk-scmi.ko | vendor_boot | present + modules.load (G14) |
| amlogic,meson-axg-dwmac | dwmac-meson8b.ko (+stmmac) | vendor_dlkm | OF-alias match (AML-F0013) |
| (SoC-ID, secmon) | amlogic-socinfo.ko → amlogic-secmon.ko | dlkm → vendor_boot | SMC/efuse symbols |

## Evidence discipline (refinements)
- First-stage correspondences are by **module name/role + load order**; OF-alias
  confirmation inside each first-stage `.ko` is a minor follow-up (dlkm dwmac is
  alias-confirmed). **Filename/role ≠ source identity.**
- Module **presence + modules.load = configured-to-load-at-boot**, not a
  device-observed runtime bind.
- vermagic = build metadata only; **no KMI-compat claim** from OTA presence.
- `clk-scmi` present ≠ proof it binds the scmi_clk node at runtime.

## Reconciliation with earlier inventories
First-stage (52, vendor_boot) + vendor_dlkm (112) + system_dlkm (15). Core SoC =
first-stage; peripherals/connectivity/eth/media = dlkm; GKI-tracking = system_dlkm.
The two 5.15.192 modules are both **vendor_dlkm** (not first-stage); their runtime
compatibility stays unresolved without device evidence.

## Remaining gaps
Per-driver deferred-probe/failure paths (REL-S refinement #2); OF-alias dump of
first-stage modules; runtime bind evidence (device-gated).
