# COFFEY DTB comparison

Date: 2026-11-02 (America/Chicago). Public artifact retrieval and host-side static analysis only. No device connection, firmware script execution, flashing, live boot, HIDL invocation or repository commit occurred. Host extraction/decompression utilities and researcher-written parsers were used; recovered firmware scripts and binaries were treated as data.

Classification: **P** inspected public source/artifact; **R** author report, not reproduced; **B** inherited project baseline; **H** inference/lead; **U** unresolved. A donor observation is not a coffey observation. Artifact hashes identify bytes, not trustworthiness or device compatibility.

Paths are relative to the evidence package root. `artifacts/` contains retrieved sources; `release/` and `nightly-new/` contain extracted files. Full image archives are separate deliverables, with URLs and hashes in the manifest.

## Inputs and interpretation

Upstream: Linux `6628e7d4c6b25c8d18f1345e3a20d21829aae7e4` amlogic-s7d.dtsi plus BM202 board DTS. CoreELEC donor sources: common_drivers `4dbe1c27ae176fde4c1cbef7506618fd7f62b976`, selected by release recipe `75626f5a6e955cdee0aa1a4c97b0d8660e1ea1af`. Compiled donor DTBs were independently extracted from the release image and decompiled with host dtc 1.6.1. Decompilation cannot reconstruct includes; the include column comes from pinned source. Compilation was not reproduced, so source-to-DTB identity is semantic comparison, not a byte-identical build claim.

Xiaomi column below means **CoreELEC Xiaomi Box S 3rd Gen**, not darkknight stock firmware. No darkknight DTB was obtained. Ugoos means X5M Pro. Coffey fields are **B — pending artifact** throughout.

| Field | Upstream BM202 | CE generic s7d_s905x5m_2g | CE Xiaomi 3rd Gen | CE Ugoos X5M Pro | Coffey recorded baseline |
|---|---|---|---|---|---|
| Root identity | amlogic,bm202 + amlogic,s7d; Amlogic S905X5M BM202 Development Board | Literal compatible `amlogic, s7d` (embedded space); model Amlogic | Same inherited compatible; model Xiaomi 3rd Gen | Same inherited compatible; model Ugoos X5M Pro | B: S7D/S905X5M family; exact root properties U |
| Includes | amlogic-s7d.dtsi + binding headers | s7d_s905x5m_bm201.dts + coreelec_s7d_common.dtsi | s7d_s905x5m_2g.dts | s7d_s905x5m_4g_1gbit.dts → 4g → 2g | U — original source include ancestry unavailable |
| Physical vs usable RAM | memory reg: base 0, length 0x80000000 (2 GiB) | linux,usable-memory 0x80000000; not an independent physical-RAM measurement | Inherits 2 GiB usable cap | linux,usable-memory 0xf0000000 (3.75 GiB cap) | B: 2 GiB; recorded usable-memory 0x80000000 |
| Secure reservation | 36 MiB at 0x05000000, no-map | linux,secmon same 36 MiB; additional ramoops, iotrace, graphics/CMA/video regions | Inherited regions; consult full recovered DTS | Inherited vendor region model; consult full recovered DTS | U — full reserved-memory map pending |
| Other media pools | No media pool graph in these selected upstream files | codec_mm_cma 0x1b000000; secure_vdec 0x1000000; heap-gfx 0x5800000; heap-fb 0x11000000; some zero-size placeholders | Vendor codec/secure-memory nodes inherited | Vendor codec/secure-memory nodes inherited | U — do not copy sizes into coffey |
| Console UART | s7d-uart → meson-s4-uart; serial@7a000; SPI 169 rising; xtal/pclk/baud all xtal; disabled in DTSI, enabled in board DTS | meson-uart; serial@7a000; SPI 169 rising; clk_uart; okay | Same console node | Same console node | B: meson-uart; complete clocks/IRQ/enabled state pending |
| Other UARTs | Not declared in selected DTSI | Vendor serial@fe078000 etc.; clk_uart + clk_gate | Board-specific availability inherited/overridden | Board-specific availability inherited/overridden | U — distinguish console from Bluetooth UART |
| PSCI | arm,psci-1.0, smc | arm,psci-0.2, smc | Same inherited declaration | Same inherited declaration | B: PSCI 0.2 SMC; actual firmware capabilities unmeasured |
| USB controller/PHY | No USB nodes in selected files | CRG OTG/DRD/UDC and host-DRD; USB2/USB3 PHY nodes; vendor controller-type properties | Inherits vendor graph; no stock-device proof | Adds software USB connector/endpoint links and regulator supply changes | U — controller, role policy, PHY tuning pending |
| Storage | No MMC/partition nodes in selected files | meson-v8-mmc eMMC, SD, SDIO; disabled NAND with bootloader partition metadata | SDIO/SD controllers disabled by board source; eMMC retained | SD UHS modes and supply changes; eMMC retained | B: A/B known; exact DT storage map pending |
| Partition metadata | None in selected files | Disabled NAND node includes partition definitions; not a live eMMC GPT | Same distinction | Same distinction | B: odm_ext slots/param observed; no donor partition offsets applicable |
| GPU/video | No complete GPU/video graph in selected files; secure-monitor power controller exists | arm,mali-valhall-csf; vendor codec_mm and Dolby Vision S7D; memory-region references | Same vendor stack plus board overrides | Same vendor stack plus board overrides | U — matching drivers, firmware and secure-media access pending |

Omitted nodes in these upstream files are not proof that the entire upstream kernel lacks the feature. Device trees describe configuration; neither compatible strings nor nodes prove successful hardware access, key provisioning or boot authorization.

## Navigation and follow-up

Use release/dt/*.dts for merged trees and artifacts/cd-*.dts[i] for the selected source include chain. Generic merged UART begins around line 1526; PSCI around 261; memory/reservations around 3805; storage around 1735; USB around 1586. Decompiled phandle numbers are local to that blob and must not be transferred between trees.

When Adam supplies coffey's own DTB, hash it before decompilation and replace each B/U cell with exact paths/properties. Compare active nodes and resolved phandles, not only string hits. No donor here is certified to boot coffey.

### DT-01 — Vendor and upstream UART/PSCI differ

- Target build: CoreELEC 22.0-Piers_rc1 Generic
- Artifact SHA-256: `bed657b45796b24d0c94173deb0a13a25f3bf3a306b34aeabe50b5bbdabfeb88`
- Source revision: `4dbe1c27ae176fde4c1cbef7506618fd7f62b976`
- File + locator: `release/flash/device_trees/s7d_s905x5m_2g.dtb` — merged /psci and /soc/apb4@fe000000/serial@7a000
- Observation: P: vendor UART and PSCI declarations are present in shipped donor DTB.
- Interpretation: Supports architectural comparison with inherited coffey baseline.
- Competing explanations / limits: Does not identify coffey driver implementation or demonstrate compatibility.
- Next discriminating check: Compare Adam’s exact DTB and kernel configuration.
