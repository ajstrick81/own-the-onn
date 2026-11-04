# AML-E0006B — Production firmware module inventory (coffey, offline)

Date 2026-10-09. Read-only, offline, on the exact-build OTA (AML-S0005,
`URO4.260304.011.B1`). No device, no modification, no new acquisition. Images
and modules kept off-repo under `E:\Morphe\device\coffey-ota\dlkm\`.

## Extraction provenance
`payload_dumper` → `vendor_dlkm.img` (22,065,152 B, sha256 `42606eff…`, EROFS/LZ4)
and `system_dlkm.img` (757,760 B, sha256 `7f6f41c8…`, EROFS/LZ4). Mounted
**read-only** (`mount -t erofs -o loop,ro`, WSL kernel erofs). Module trees:
`vendor_dlkm:/lib/modules`, `system_dlkm:/lib/modules/5.15.196-android14-11-g3d26c188ef7e-ab14657224`.
Full table: `dlkm/INVENTORY/modules.tsv` (part · module · sha256 · arch · vermagic).

## Inventory summary
- **127 modules total**: **112 vendor_dlkm** + **15 system_dlkm**. All **AArch64**.
- **vermagic distribution** (KMI/build evidence):
  - 15 → `5.15.196-…-g3d26c188ef7e-ab14657224` = **exactly the running kernel uname** (system_dlkm tracks GKI).
  - 109 → `5.15.196-…-g10bd23fd47b5` = a **different vendor build** (vendor_dlkm).
  - 1 → `5.15.196-…-g0f5f1e32f6f4-ab21793`; 2 → **`5.15.192-…-ab19762`** (older base).
  - Interpretation: vendor modules built against a different kernel build than the
    running one; **GKI KMI / `modversions` (symbol CRCs) bridges the ABI**, not
    vermagic equality. The two 5.15.192 modules are notably older — flagged.

## Where the subsystem drivers actually live (two-stage split)
- **vendor_dlkm (2nd stage)** = peripherals/connectivity/media: Wi-Fi/BT
  (`8822cs`,`8852bs`,`aml_bt`,`rtk_btusb`,`sdio_bt`,`cfg80211`,`mac80211`),
  **Ethernet** (`stmmac`,`stmmac-platform`,`dwmac-meson8b`,`dwmac-meson`,
  `dwmac-dwc-qos-eth`,`amlogic-mdio-g12a`,`mdio-mux`), DVB/media, audio codecs,
  PCIe, RTC, crypto-dma, **`amlogic-socinfo`**, `i2c-dev` (userspace i2c, not the
  bus driver).
- **vendor_boot (1st stage ramdisk)** = the **core SoC drivers** (from
  vendor_boot.img module-name references): **`*-uart.ko`**, **`*-clk-soc-s7d.ko`
  + `amlogic-clk.ko`**, **`reset.ko`** (uart / s7d clock controller / reset).
  (vendor_boot module list is partial here — from an uncompressed-string scan;
  full enumeration needs a ramdisk cpio unpack, G15.)
- **Consequence:** the E0006 subsystems split by stage — **UART / clk(clkc) /
  reset = first-stage (vendor_boot)**; **Ethernet = dlkm**; **I²C-bus / MMC / USB
  PHY not seen in dlkm** → first-stage or builtin (to confirm via ramdisk unpack).

## DT compatible → shipped-module matrix (evidence-graded)
| DT compatible (L1) | shipped module | where | evidence |
|---|---|---|---|
| amlogic,meson-axg-dwmac | `dwmac-meson8b.ko` (+stmmac) | vendor_dlkm | **OF-alias match** in module |
| (SoC-ID) | **`amlogic-socinfo.ko`** (vendor; name=amlogic_socinfo; depends amlogic-secmon,amlogic-debug) | vendor_dlkm, **in `modules.load` line 36** | present + boot-load-listed |
| amlogic,meson-uart | `*-uart.ko` | vendor_boot 1st-stage | name reference (partial) |
| amlogic,s7d-clkc | `*-clk-soc-s7d.ko`,`amlogic-clk.ko` | vendor_boot 1st-stage | name reference (partial) |
| (reset) | `reset.ko` | vendor_boot 1st-stage | name reference (partial) |
| amlogic,meson-i2c / meson-v8-mmc / crg-drd-usb2/3 | — | not in dlkm | first-stage/builtin — unresolved (G15) |
| (SCMI clock) | — | none in dlkm | consistent with COMMON_CLK_SCMI unset (G14) |

## Answers to the coordinator's questions
- **SoC-ID (Finding C) — resolved to shipped-artifact level:** coffey ships and
  boot-loads a **vendor** `amlogic-socinfo` module (via `amlogic-secmon`, i.e. an
  SMC path to the secure monitor), **distinct from** the mainline
  `meson-gx-socinfo` 0x47 driver. The 0x47 mapping stays mainline-source-level;
  coffey's own identification path is the vendor secmon module. **Presence +
  modules.load ≠ runtime-observed load** (refinement preserved).
- **SCMI clock (G14):** **no SCMI-clock module** in dlkm (consistent with GKI
  `COMMON_CLK_SCMI` unset). The DTB `scmi_clk` provider remains unresolved —
  could be first-stage/builtin; not evidenced in dlkm.

## Evidence discipline (coordinator refinements)
- **Presence in firmware ≠ loaded at runtime.** `modules.load` membership shows
  *configured-to-load-at-boot*, still not a runtime-observed bind.
- **Compatible/alias/filename match ≠ source-code identity** (e.g.
  `amlogic-socinfo` is a vendor module, NOT proof it is the mainline source).
- All module identities are by `.modinfo`/ELF; not disassembled.

## Open (gap register)
G15 vendor_boot ramdisk cpio unpack (full first-stage module list + modules.load);
G14 SCMI clk provider; G11 SoC-ID runtime; plus the standing runtime-bind ceiling.
