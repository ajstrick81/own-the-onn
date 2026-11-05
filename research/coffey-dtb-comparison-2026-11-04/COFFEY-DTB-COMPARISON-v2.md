# COFFEY DTB comparison v2 — coffey's own device tree vs vendor and CoreELEC trees (boot-policy Phase D)

**Date:** 2026-11-04. **Scope:** offline comparison of coffey's shipped base device tree against device trees
built from pinned public source. No device contact, nothing flashed or booted. Supersedes the coffey column of
[`../boot-policy-packet-2026-11-02/COFFEY-DTB-COMPARISON.md`](../boot-policy-packet-2026-11-02/COFFEY-DTB-COMPARISON.md),
where every coffey cell was "B — pending artifact".

> Correction #2 of the track applies throughout: **a matching board description is not boot authorization.**
> Nothing here says coffey's locked bootloader would load any of these trees or an alternate kernel.

## 1. Inputs (grade **P**)

| Tree | How obtained | SHA-256 (FDT) |
|---|---|---|
| **coffey** (shipped) | `vendor_boot` DTB section of OTA `URO4.260304.011.B1`, cut to its FDT header's `totalsize` (81,532 B, equal to `vendor_boot` `dtb_size`) | `0c76b1efcd2a20f9707b40c4fb37f690f4629e3cb48929bd80de3bc958c7c2d0` |
| vendor `s7d_s905x5m_bm202` | built from CoreELEC `common_drivers` | `e8985b53…024c` |
| CoreELEC generic `s7d_s905x5m_2g` | built, same source | `bed657b45796b24d0c94173deb0a13a25f3bf3a306b34aeabe50b5bbdabfeb88` |
| CoreELEC Xiaomi 3rd Gen / Ugoos X5M Pro / Odroid C5 / vendor bm201 | built, same source | in [`DTB-ARTIFACTS-SHA256SUMS.txt`](DTB-ARTIFACTS-SHA256SUMS.txt) |

- **Source pins:** `common_drivers` commits `4dbe1c27…` (selected by the CoreELEC 22.0-Piers_rc1 recipe) and
  `8646fbd1…` (E0005's pin). Both produce **byte-identical** DTBs for all six boards. Standard `dt-bindings`
  headers from AOSP `kernel/common` at coffey's own kernel commit `3d26c188ef7e`. `cpp` 15.2 + `dtc` 1.7.2.
- **Build reproduces CoreELEC's shipped bytes.** The `s7d_s905x5m_2g` build is SHA-256 `bed657b4…eb88`,
  **identical** to the DTB extracted from the CoreELEC release image in the 11-02 packet (DT-01). So these
  source builds are what CoreELEC ships, not approximations.
- **Method:** each FDT decompiled with `dtc -s` (sorted) and compared node by node with
  [`scripts/dtdiff.py`](scripts/dtdiff.py). Phandles are matched by the path of the node they point to, walking
  specifiers by each provider's `#*-cells`, so independent phandle numbering doesn't create false
  differences. Rebuild with [`scripts/build-dtbs.sh`](scripts/build-dtbs.sh) (re-run from scratch; all hashes
  reproduced).

## 2. Which tree coffey is (grade **P**)

| coffey vs. | Nodes only in coffey | Nodes only in other | Property differences |
|---|---|---|---|
| **vendor bm202** | 4 | 4 | **19** |
| vendor bm201 | 7 | 24 | 95 |
| CoreELEC generic 2g | 34 | 18 | 99 |
| CoreELEC Xiaomi 3rd Gen | 35 | 20 | 103 |
| CoreELEC Ugoos X5M Pro | 34 | 33 | 118 |
| CoreELEC Odroid C5 | 40 | 43 | 135 |

**coffey's device tree is the Amlogic `bm202` reference board with onn product edits.** Root
`compatible`/`amlogic-dt-id` = `s7d_s905x5m_bm202`, no `model`. All 661 nodes line up with bm202 except these:

| Area | coffey | bm202 |
|---|---|---|
| LEDs (`/gpio_leds`) | `red_led` + `white_led` (both off by default), `product = "coffey"` | `pwr_led` (on) |
| IR remote (`/custom_maps`) | 1 map, `customcode 0xf708`, 60-key keymap (onn remote) | 4 maps, `customcode 0xfb04` |
| Front key (`/gpio_keypad`) | `key_code 0xd4` | `0x258` |
| Unifykeys | **21** keys; adds `key_19 nfxoemmodel` and `key_20 facAutoAging`, both `key-permit = read, write, del` | 19 keys |
| `/chosen` bootargs | adds `dm_mod.reserved_bio_based_ios=8` | `usbcore.autosuspend=-1` only |
| Pin muxes | UART-D with CTS/RTS (4-wire); PDM mic input on GPIOZ (`z11/z12`); SPI-A `mosi` only | UART-D 2-wire; PDM on GPIODV; full SPI-A |
| Misc | `amhdmitx vrr_en = 0`; `sdio` uses clock parent `0x01` (fclk_div2) | no `vrr_en`; parent `0x0e` (gp0 PLL); `aml_kt kt_host_key_max_len = 0x20` |

## 3. Phase D axes — coffey vs. the CoreELEC trees (grade **P** unless noted)

| Axis | coffey (shipped) | CoreELEC generic 2g / Xiaomi / Ugoos | Reading |
|---|---|---|---|
| Root identity | `compatible = "s7d_s905x5m_bm202"`, `amlogic-dt-id` | `compatible = "amlogic, s7d"`, `coreelec-dt-id`, `model` | Different identity scheme; CoreELEC's own bootloader-side DT selection keys on its IDs |
| Memory | `linux,usable-memory` 2 GiB, no `reg` (filled at boot) | same 2 GiB (Ugoos: 3.75 GiB) | match (2g/Xiaomi) |
| Secure carve-out | `linux,secmon` 36 MiB @ `0x05000000`, no-map | identical | match |
| Media pools | `codec_mm_cma` 364 MiB, `heap-fb` 56 MiB | 432 MiB, 272 MiB | **differ**: CoreELEC reserves ~284 MiB more of a 2 GiB box |
| PSCI | `arm,psci-0.2`, `smc` | identical | match |
| Console UART | `serial@7a000` okay, `amlogic,meson-uart` | identical | match (also `serial@fe078000` okay in all; C/D/E disabled in all) |
| eMMC | `mmc@fe08c000` okay | okay | match |
| SD / SDIO | SD **disabled** (no slot), SDIO okay (Wi-Fi) | 2g: SD okay; Xiaomi: SDIO disabled | coffey has no SD slot |
| USB | `crgdrd`/`crgotg` + `usbphy20/30` okay; **`crg@fe340000`, `usbphy21/31` disabled** (single port) | all seven USB nodes okay | CoreELEC enables a second host controller coffey doesn't wire |
| Ethernet | `ethernet@fe368000` + MDIO **disabled** (no RJ45) | okay | absent on coffey |
| Analog AV / codec | `cvbsout`, `vdac`, internal codec `t9015` **disabled** | okay | absent on coffey |
| GPU | `valhall`: `arm,malit60x`, `arm,malit6xx`, `arm,mali-midgard` | `arm,mali-valhall-csf` | **different GPU driver binding** (vendor kernel vs. CoreELEC kernel) |
| Audio graph | `auge_sound` routing (42 property differences vs. 2g) | CoreELEC routing | board-specific; not compared further |
| Debug | `/jtag` status **okay** (also in bm202) | `/jtag` disabled | DT pin-mux node only; says nothing about whether JTAG is fused off (**U**) |

## 4. Answers for the track

- **Is there a coffey-matching public tree?** Yes. Vendor `s7d_s905x5m_bm202` is coffey's tree minus 19 onn
  edits (P). It's in CoreELEC's `common_drivers` source. Whether a CoreELEC release image ships a bm202 DTB
  wasn't checked here.
- **Would the CoreELEC generic 2 GiB tree describe coffey?** Partly. Memory, secure carve-out, PSCI, console
  UART and eMMC match. It also enables Ethernet, SD, a second USB host, CVBS and the internal codec, none of
  which coffey enables. It binds a different GPU driver and reserves far larger media pools. It's a
  **candidate, not coffey-ready** (the acceptance wording stands), and bm202 + the §2 edits is the closer start.
- **Nothing here changes the weld.** These are board descriptions; authorization stays with the locked,
  opaque bootloader (C5, C13).

## 5. Cross-links

- **C15 (`systemcontrol`):** coffey's unifykey table marks `nfxoemmodel` and `facAutoAging` (a factory
  burn-in flag, by name) as `read, write, del`. Those permits govern the unifykey driver that `writeUnifyKey`
  reaches. Recorded as context for the disclosure; no access was attempted.
- **Vector #4 (UART):** the kernel's console node is `serial@7a000` on all trees; mapping it to the FCC-photo
  pads stays a hardware step.

## 6. Limits

- Compared base DT only; coffey's `dtbo` (dummy battery/charger overlay) isn't applied here.
- Property-level only for vendor nodes; driver behaviour behind a binding isn't asserted.
- Decompilation can't recover source includes. The bm202 match is by compiled content, not by source lineage.
