---
finding_id: AML-F0013
title: "coffey shipped module inventory: 127 .ko (112 vendor_dlkm + 15 system_dlkm); vendor amlogic-socinfo loaded at boot; core SoC drivers are first-stage; GKI/vendor vermagic split"
component: firmware-modules
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
source_urls: []
source_revision: "OTA URO4.260304.011.B1 vendor_dlkm (sha256 42606eff…) + system_dlkm (7f6f41c8…)"
related_findings:
  - AML-F0012
  - AML-F0011
status: promoted
---

# coffey shipped firmware module inventory (AML-E0006B)

Offline inventory of the exact-build OTA's `.ko` modules (read-only EROFS mount).
Full table `dlkm/INVENTORY/modules.tsv`; analysis `E:\Morphe\device\coffey-ota\analysis\E0006B-MODULE-INVENTORY.md`.

## Observations
- **127 modules** = 112 `vendor_dlkm` + 15 `system_dlkm`; all **AArch64**.
- **vermagic split:** 15 modules = exactly the running kernel uname
  `5.15.196-…-g3d26c188ef7e-ab14657224` (system_dlkm↔GKI); 109 = a different
  vendor build `5.15.196-…-g10bd23fd47b5`; 1 = `…-g0f5f1e32f6f4-ab21793`; **2 =
  older `5.15.192-…-ab19762`**. GKI KMI/`modversions` bridges the ABI across the
  build-hash difference (not vermagic equality).
- **`amlogic-socinfo.ko` present and in `vendor modules.load` (line 36)** —
  a **vendor** SoC-ID module (`name=amlogic_socinfo`, `depends=amlogic-secmon,
  amlogic-debug`), i.e. identification via the secure-monitor (SMC) path, NOT the
  mainline `meson-gx-socinfo` 0x47 driver.
- **Two-stage driver split:** vendor_dlkm = peripherals/connectivity (Wi-Fi/BT,
  Ethernet `stmmac`+`dwmac-meson8b`, DVB/media, audio, PCIe, RTC, crypto,
  socinfo, `i2c-dev`). The **core SoC drivers are first-stage (vendor_boot)**:
  `*-uart.ko`, `*-clk-soc-s7d.ko`+`amlogic-clk.ko`, `reset.ko` (from a vendor_boot
  string scan — partial). I²C-bus / MMC / USB-PHY are **not** in dlkm → first-stage
  or builtin (unresolved, G15).
- **DT-alias match:** only `amlogic,meson-axg-dwmac` → `dwmac-meson8b.ko` matches
  by OF-alias among dlkm modules (Ethernet). No SCMI-clock module in dlkm.

## Interpretation
coffey's shipped firmware confirms the GKI-base + vendor-module structure
(AML-F0012): system_dlkm tracks the GKI kernel; vendor_dlkm carries vendor
peripherals built against a separate vendor kernel build. SoC identification on
coffey is a **vendor secmon path** (`amlogic-socinfo` → `amlogic-secmon`), not the
mainline gx-socinfo 0x47 driver — the 0x47 mapping stays mainline-source-level.

## Alternative explanations / discipline
- **Presence + `modules.load` ≠ runtime-observed load** — it shows
  configured-to-load-at-boot, not a captured runtime bind.
- **Alias/filename match ≠ source identity** — `amlogic-socinfo` is a vendor
  module; not asserted to be any specific upstream source.
- Identities from `.modinfo`/ELF headers only; modules not disassembled.

## Validation needed / ceiling
vendor_boot ramdisk cpio unpack for the complete first-stage module list +
load order (G15); runtime bind evidence needs on-device dmesg/sysfs (not taken).

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
