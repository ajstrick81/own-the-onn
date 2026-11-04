# COFFEY OTA — graded findings from the 2026-10-09/10 offline analysis

Consolidates the maintainer's notes in [`source-notes/`](source-notes/) into the repo's P/R/B/H/U grading. Every
row is from coffey's **own** exact-build OTA (`URO4.260304.011.B1`) or a read-only capture from the owner's unit;
no donor data is carried in. Where the original notes overreached, the corrected stance is used and noted.

## Findings

| ID | Finding | Grade | Basis (source note) |
|---|---|---|---|
| O1 | The package is the expected full A/B OTA for `onn/coffey/coffey:14/URO4.260304.011.B1/15051976` (SPL 2026-03-01); ZIP SHA-256 `ec755bd0…b1a7`, payload hash self-consistent | **P** | [`COFFEY-OTA-CAPTURE.md`](COFFEY-OTA-CAPTURE.md) §1–2 |
| O2 | coffey's kernel is GKI **`5.15.196-android14-11-g3d26c188ef7e-ab14657224`**, built **2026-01-03**, clang 17.0.2 | **P** | `boot.img` banner (capture §3); matches `system_dlkm` vermagic (`E0006B`) |
| O3 | Vendor modules (52 first-stage in `vendor_boot`, 112 in `vendor_dlkm`) are built against a different kernel build (`g10bd23fd47b5`); 2 `vendor_dlkm` modules are an older `5.15.192` base. 15 `system_dlkm` modules track the GKI build | **P** | `E0006B`, `E0006C`, `*.load` lists |
| O4 | Base device tree is `s7d_s905x5m_bm202` (4× Cortex-A55, GIC-400, PSCI **0.2** via SMC, `linux,usable-memory` 2 GiB, `linux,secmon` 36 MiB no-map carve-out); `dtbo` carries only dummy battery/charger overlays | **P** | `ANALYSIS.txt`, `DT-CHARACTERIZE.txt`, `E0005`, `E0006` |
| O5 | coffey runs the **Amlogic vendor driver stack**, not mainline: its DT compatibles (`meson-uart`, `meson-i2c`, `meson-v8-mmc`, `crg-drd-usb2/3`) match CoreELEC `common_drivers` @ `8646fbd1` and are absent from mainline's match tables at `af32da41` | **P** (DT ↔ shipped module); runtime bind **U** | `E0006`, `E0006-PROBE-DIAGRAMS`, `E0006C` |
| O6 | SoC identification goes through a vendor `amlogic-socinfo.ko` → `amlogic-secmon.ko` SMC/shared-memory path that reads a TrustZone efuse — not mainline's `meson-gx-socinfo` register path | **P** (binary symbols); runtime **U** | `E0006B`, `E0006C` |
| O7 | Bootloader partition is an Amlogic signed container: 9× `@ML ` signed headers, `@AMLBOOT` table (BL2E/BL2X present, DDRF slot zero-filled), build **`S7D-s905x5m-26030511BBST`**. Everything after the headers (BL2 bodies and the ~1.5 MB later-stage region) is **opaque**: uniform byte statistics and no plaintext stage markers | **P** (layout/statistics) | `BOOTLOADER-INVENTORY.txt`, `PHASE5-BOOT-CONTAINER.md`, `PHASE5-BL33-ENCRYPTION-FINDING.md` |
| O8 | *Corrected:* the opaque stages are **consistent with encryption or headerless compression**; the transform and key are **unresolved**. The 10-09 note's "AES-encrypted, blocked at an OTP-fused BootROM key" was withdrawn by the maintainer on 10-10 as overreach | **H** | `PHASE5-BL33-ENCRYPTION-FINDING.md` (supersession banner) |
| O9 | Consequence: BL33 (U-Boot) cannot be disassembled offline, so whether a locked coffey bootloader would honor a written `bootcmd`/env change stays **indeterminate** — now for a specific reason (opaque BL33), not a vague one | **P** (that it's blocked) / **U** (the env question) | `PHASE5-BL33-ENCRYPTION-FINDING.md` §5 |
| O10 | eMMC partition map from the unit (`/dev/block/by-name`): 31 partitions incl. `env`=p2, `frp`=p3, `factory`=p4, `misc`=p11, `param`=p15, `tee`=p9, `super`=p29; A/B for boot/init_boot/vendor_boot/dtbo/vbmeta/oem/odm_ext/bootloader | **P** (read-only capture) | `by-name.txt` |
| O11 | `super` uses **virtual A/B** (`virtual_ab_device`, metadata v10.2, 3 slots); slot `_b` was active with `-cow` partitions present at capture time | **P** | `lpdump-coffey-slot_b.txt` |
| O12 | `/sys/block/mmcblk0` geometry is permission-denied from shell — physical offsets stay root-gated (consistent with the `env`/`misc`/`param` wall) | **P** (bounded negative) | `sysfs-mmc-geometry.txt` |
| O13 | All four "one unlock" artifacts now exist on the maintainer's machine: OTA, kernel, DTB, **and the `systemcontrol` ELF** (`vendor/bin/systemcontrol`, 350,020 B, `aec8998d…`) + its HIDL libs | **P** (present, hash-pinned); `systemcontrol` analysis **U** | [`COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt) |

## What this changes elsewhere

- **Priority vector #1** (capture) → **done**. Its remaining use is as input: steps below.
- **CVE-2026-43499 (C8 / vector #2):** coffey's GKI kernel was built 2026-01-03, ~7 months before the fix's
  Android cherry-pick (2026-07-23) and first GKI tag (2026-08-05). Because a GKI `boot.img` is Google-built, an
  OEM-side backport can't be in it. That makes the fix's absence likely by date, but it's still `H`: the
  code-level check against `rtmutex`/futex-PI in this exact build is the next step, not done here.
- **Epoll CVEs (vector #3):** the exact base (`5.15.196`, `ab14657224`) is now known, so the backport question
  can be checked against that GKI build instead of a guessed version.
- **Boot-policy Phases A–F:** coffey's own DT, module inventory, and partition map replace the sibling
  comparators for the cells they cover. BL33 remains opaque (O8/O9).
- **twilight `systemcontrol` comparator (vector #6):** superseded for its purpose by coffey's own ELF (O13).

## Not established / open

- Runtime driver bind order, TrustZone enforcement, and which BL31 implementation runs: not observed.
- OTA ZIP signature and AVB/`vbmeta` chains: not verified.
- `systemcontrol` ELF: present but not yet analyzed.
- The 10-10 supersession banner cites `kb/11-verified-findings/AML-F0023` as the authoritative wording; that
  KB was **not found** under `E:\Morphe` (searched to depth 4). The banner text itself is used here.
