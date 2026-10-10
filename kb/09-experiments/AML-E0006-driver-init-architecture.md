---
experiment_id: AML-E0006
title: "Driver & Initialization Architecture — three-layer (shipped DTB / mainline / vendor) driver map, UART case study, SoC-ID, PSCI firmware boundary"
research_question: "For coffey's key subsystems, what driver actually binds (vendor L3) vs what mainline supports (L2) vs what the shipped DTB declares (L1), and where is the Linux→secure-firmware boundary?"
hypothesis: "coffey binds CoreELEC vendor drivers via vendor-specific compatible strings that differ from mainline S7D support; a shared/compatible interface is not proof of an inherited implementation."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "coffey shipped DTB (AML-S0005)"
  - "mainline + CoreELEC driver/DT source at pinned commits (AML-S0006, AML-S0008)"
result: done
related_findings:
  - AML-F0011
  - AML-F0012
  - AML-F0013
  - AML-F0014
  - AML-F0009
  - AML-F0007
---

# AML-E0006 — Driver & Initialization Architecture (three-layer)

Offline, source-backed. Responds to coordinator AML-RESEARCH-001. Full deliverable:
`E:\Morphe\device\coffey-ota\analysis\E0006-DRIVER-MAP.md`. Three layers kept
distinct: L1 shipped DTB / L2 mainline Linux / L3 coffey vendor kernel.
Pinned: mainline `af32da41…` (AML-S0008), CoreELEC `8646fbd1…` (AML-S0006/S0008).

## Procedure
1. Resolve each subsystem's L1 compatible from coffey's DTB.
2. Find the L3 vendor driver whose of_match table matches that compatible
   (CoreELEC common_drivers) and the L2 mainline equivalent.
3. For UART (priority 1): trace match table → probe → clock acquisition → IRQ.
4. SoC-ID: inspect mainline socinfo mechanism + value; assess coffey enablement.
5. PSCI/secure-monitor: map the Linux→firmware boundary (4-layer model).

## Actual observations (this pass — UART + SoC-ID + PSCI done; other drivers seeded)
- **UART (case study):** coffey DTB = `amlogic,meson-uart` (clk_uart/clk_gate);
  CoreELEC vendor `meson_uart.c` of_match = **only `meson-uart`** (probe:
  devm_clk_get clk_gate+clk_uart, devm_request_irq). Mainline = `amlogic,s7d-uart`/
  `amlogic,meson-s4-uart` (xtal/pclk/baud, request_irq, status=disabled). **coffey
  does NOT use the mainline s7d→s4 fallback** — self-consistent vendor stack. →
  AML-F0011.
- **SoC-ID:** mainline `{ "S7D", 0x47 }` / `{ "S905X5M", 0x47, 0x1, 0xf }` read from
  AO_SEC_SD_CFG8 (0xe0) via syscon regmap — corroborates S7D at source level;
  coffey enablement + AO-reg readability UNVERIFIED (no register experiment).
- **PSCI boundary:** coffey DTB `arm,psci-0.2` + method smc (mainline s7d = PSCI
  1.0) → SMC to secure monitor (BL31 in opaque bootloader payload, AML-F0010).
  4-layer model: driver → PSCI/SMCCC → fw impl (unverified) → hw controller.
- **Memory:** coffey own DTB declares 2 GiB `linux,usable-memory`; mainline bm202
  is a 2 GiB **dev board** — 2 GiB corroborated for coffey, not just assumed.

## Conclusion
Confirms the three-layer thesis concretely: coffey runs CoreELEC **vendor** driver
implementations bound via vendor compatible strings that diverge from mainline
S7D support; shared interface ≠ inherited implementation. UART is the reproducible
exemplar. Does NOT establish runtime init ORDER, TrustZone enforcement, or the
exact ATF impl. result=in-progress (I²C/MMC/USB per-driver probe tracing pending).

## Expansion done (2026-10-09, REL-20261009-Q review response) → AML-F0012
- **I²C/MMC/USB three-layer:** divergence pattern CONFIRMED broad. I²C vendor
  `meson-i2c`/`meson-tee-i2c` vs mainline meson6/gxbb/axg-i2c (no `meson-i2c`);
  MMC vendor adds `meson-v8-mmc` vs mainline none; USB vendor crg-drd PHY vs no
  mainline s7d PHY. coffey runs the vendor stack for all.
- **Config layer:** preserved config is the **GKI base** (0 CONFIG_AMLOGIC_*) →
  vendor-module enablement NOT determinable; SoC-ID gx-socinfo neither found in
  vendor tree nor in GKI config → coffey 0x47 enablement unverified (ceiling).
  `COMMON_CLK_SCMI` not set (scmi_clk provider undetermined); SCMI protocol+SMC+
  RESET_SCMI present.
- **AO-pinctrl (G3):** coffey DTB has only `pinctrl@4000` periphs — no separate
  AO-pinctrl node.
Refinement #1 applied throughout: results are shipped-DTB↔vendor-source
correspondences, not proven production runtime behavior.

## AML-E0006B production module inventory DONE (2026-10-09) → AML-F0013
127 shipped .ko (112 vendor_dlkm + 15 system_dlkm, all AArch64). Vendor
`amlogic-socinfo.ko` present + in modules.load (vendor secmon SoC-ID path, NOT
mainline gx-socinfo 0x47). Core SoC drivers (uart/clk-s7d/reset) are first-stage
(vendor_boot); Ethernet dwmac-meson8b in dlkm (OF-alias match). vermagic split:
system_dlkm==running GKI uname; vendor_dlkm==separate vendor build (KMI bridges).
Report: analysis/E0006B-MODULE-INVENTORY.md. Presence+modules.load != runtime bind.

## Next steps (offline, read-only)
- Source-backed per-driver init/probe *diagrams* for I²C/MMC/USB (sequence).
- S7D↔SC2 reset-index delta (G9); SCMI vendor clk-provider search (G4).
- Updated architectural lineage conclusions (binding-level lineage vs vendor impl).

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

## Second-stage dlkm consumer identified — Codex 2026-10-09

Exact-build vendor init modules_load.rc invokes /vendor/bin/modules_load via
exec_start on early-init. Shipped ARM32 loader static disassembly reads
/vendor/lib/modules/modules_load_list: 58 entries, 43 vendor + 15 system.
Vendor/system lib/modules symlinks point to their dlkm partitions. Relative
system paths resolve through the loader-selected version directory. All list
entries reconcile with inventoried module artifacts. This consumer uses direct
finit_module calls rather than modprobe dependency resolution; its loop ignores
insertion results, so service completion would not prove successful loading.
Runtime load/bind remains unobserved. init_boot supplies the generic ramdisk;
boot.img itself has ramdisk size zero. Existing OTA extracted only, no device.
Derived evidence: COORDINATOR-DLKM-LOADING-TRACE-2026-10-09.md,
dlkm-configured-loading-map.tsv and second-stage-insmod-references.tsv in
Director Codex outputs; full file hashes in dlkm-init-audit-provenance.json.
Source scope: AML-S0005 exact-build OTA; vendor/system/init_boot extracted from
its existing payload using installed payload_dumper.

## Cross-stage dependency and ABI audit — Codex 2026-10-09

All 179 module artifacts match preserved hashes: 52 first-stage, 112 vendor_dlkm,
15 system_dlkm; 177 unique binaries (i2c-dev/dwc_otg copies are identical).
All 461 declared dependency edges have shipped providers. No main-list strong
module-symbol provider appears after its consumer, and no distinct main-list
modules duplicate exported symbol names. These checks assume earlier requests
succeed and do not establish actual insertion or binding.

All 179 contain __versions. 4,710 available module-to-module CRC comparisons
match; no conflicting expected CRC values were found across imported-symbol
version records. 50 Bluetooth provider/import pairs lack individual expected
CRC records; the source commit named by the device kernel build permits a
missing individual version entry with a warning. This is distinct from an
absent whole __versions section or an actual mismatch.

Kernel source pin resolved: 3d26c188ef7e87e52ea1fa0092db760a55e2ae4c,
https://android.googlesource.com/kernel/common/+/3d26c188ef7e87e52ea1fa0092db760a55e2ae4c/kernel/module.c .
With versions present, same_magic ignores the kernel-release prefix; all 179
module vermagic suffixes agree. This narrows the ABI explanation, not complete
compatibility: 12,040 import occurrences lack a shipped-module export and may
be kernel-provided. The shipped kernel's full export/CRC set remains unresolved.

Signature trailers occur in all 15 system modules and none of the 164 vendor/
first-stage artifacts. Trailers were parsed, not cryptographically verified.
GKI signature protections and runtime enforcement remain separate checks.

The system modules.dep describes 58 consumer paths while the partition ships
15 modules; 12 named dependency providers in that file are absent from the
combined artifacts. Do not treat that generic metadata as the packaged module
set or proof of a broken live boot. The actual 58-entry second-stage consumer
list (43 vendor + 15 system) is reconciled against artifacts separately.

Derived tables and machine summaries are retained in Codex outputs; no runtime
actions, commit or publication. Detailed overview deferred at Director request.
