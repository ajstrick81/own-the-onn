# COFFEY boot-policy map (boot-policy Phase B)

**Date:** 2026-11-04. **Scope:** offline, read-only reconstruction of coffey's boot dispatch from everything
that is **plaintext** in its own OTA (`URO4.260304.011.B1`): the `vendor_boot` boot and recovery ramdisks, the
`init_boot` ramdisk, the vendor HALs that steer boot, the fstab, and the loaded SELinux policy. Nothing was
run, flashed, or rebooted. Inputs are hash-pinned in [`DISPATCH-INPUTS-SHA256SUMS.txt`](DISPATCH-INPUTS-SHA256SUMS.txt).

> **The ceiling.** The stages that actually decide what boots, BL2 → BL31 → BL33/U-Boot, are opaque in
> `bootloader.img` (C13). Every row below that depends on what U-Boot *does* with an input is **U**. This map
> records the inputs userspace and recovery can set, who may set them, and what is verified, not the
> bootloader's decision.

## 1. Sources and the plaintext bound (grade **P**)

| Source | Result |
|---|---|
| `bootloader.img` (4,100,096 B) | **Zero hits** for every Phase-B token (`bootcmd`, `storeboot`, `switch_bootmode`, `get_rebootmode`, `recovery_from_udisk/sdcard/flash`, `aml_autoscript`, `autoscr`, `usb_burning`, `*_burningcfg`, `aml_sdc_burn`, `imgread`, `bootm`, `get_avb_mode`, `get_valid_slot`, `saveenv`, `fw_setenv`, `upgrade_step`, `bootfromnand`, …). Only the `@ML`/`@AMLBOOT` headers are plaintext |
| `vendor_boot` v4 | page 2048; kernel cmdline `bootconfig`; **bootconfig** `androidboot.dynamic_partitions=true`, `androidboot.dtbo_idx=0`, `androidboot.boot_devices=soc/fe08c000.mmc`, `use_uvm=1`. Two ramdisks: `frag0` (type 1, boot: 77 files) and `recovery` (type 2: 231 files, 212 symlinks) |
| `init_boot` v4 | ramdisk only (4 files: first-stage `init`) |
| `boot` v4 | kernel only, no ramdisk |
| U-Boot env defaults | **not in the OTA**. `env` lives only on the device's `env` partition (p2), which isn't readable without root |

Ramdisks were extracted twice (WSL `lz4`+`cpio`, and the pure-Python [`scripts/rd_extract.py`](scripts/rd_extract.py))
with identical file counts and ramdisk hashes.

## 2. Who steers boot from Android (grade **P**: imports, strings, policy)

| Component | Domain · user | Touches | How |
|---|---|---|---|
| Boot-control HAL `android.hardware.boot-service` | `hal_bootctl_default` | `/misc` bootloader control block (A/B slot metadata), **U-Boot env** (`ubootenv.var.bootcmd`, `/dev/block/env`), `bootloader_a/_b`, `mmcblk0boot0/1`; strings `reboot for ARB`, `slotselect_other` | Links `SystemControlClient` and imports `getBootEnv`/`setBootEnv`, so env writes go via `systemcontrol`. Policy also lets it write `misc`, `env`, `bootloader` and `boot` block devices directly |
| OEM-lock HAL `android.hardware.oemlock-service.droidlogic` | `hal_oemlock_default` | **`ubootenv.var.lock`** ("1: can unlock, 0: can not unlock") via `setOemUnlockAllowedByDevice/ByCarrier` | Links `SystemControlClient` (`get/setBootEnv`). Its own help text advertises a `dumpsys`-based set option |
| `systemcontrol` (root) | `system_control` | env writer (`ubootenv.var.` prefix check only) | C15 |
| `fastbootd` (recovery) | `fastbootd` | flash/erase/`set_active` | AOSP lock enforcement: refuses flash, erase, download and `set_active` **on locked devices**, keyed on `ro.boot.verifiedbootstate` (set by the bootloader) |
| `update_engine` / `uncrypt` / `vold` / `init` | — | `misc` BCB (recovery commands), slots | stock AOSP |

### Who may write the dispatch inputs (loaded policy)

| Input | Writers allowed |
|---|---|
| `/misc` (BCB: `boot-recovery`, slot metadata) | `hal_bootctl_default`, `init`, `vendor_init`, `uncrypt`, `update_engine`, `vold`, `vendor_misc_writer`, `mtectrl`. **No apps or shell** |
| `env` (U-Boot environment, incl. `lock`, `bootcmd`) | `system_control`, `hal_bootctl_default`, `fastbootd`, `hal_graphics_composer_default` |
| `bootloader` devices | `fastbootd`, `hal_bootctl_default`, `update_engine` |
| `boot` | `hal_bootctl_default`, `update_engine` |
| `vbmeta` | `fastbootd`, `init`, `update_engine` |

### Who may call the steering HALs

| HAL | find | binder call |
|---|---|---|
| boot control (`hal_bootctl_default`) | `system_server`, `update_engine`, `update_verifier`, `vold`, `snapshotctl`; AIDL service also findable by `shell`, `system_app`, `atrace`, `traceur_app` | `system_server`, `update_engine`, `update_verifier`, `vold`, `snapshotctl`, `dumpstate`, **`system_control`** (not shell) |
| OEM lock (`hal_oemlock_default`) | `system_server`, `dumpstate`; AIDL service also by **`shell`**, `system_app`, `atrace`, `traceur_app` | `system_server`, `dumpstate`, **`shell`** |
| `systemcontrol` | see C15: third-party apps, priv/platform/system apps, vendor HALs | — |

## 3. Boot-policy map (Phase B table)

| Path | Entry condition | Media / source | Handler | Verification | Slot dependence | Persistent side effects | Evidence | Confidence |
|---|---|---|---|---|---|---|---|---|
| **Normal boot** | default | eMMC `boot`/`init_boot`/`vendor_boot`/`dtbo` + dynamic partitions | BL33 (opaque) → GKI kernel → first-stage init | AVB: `vbmeta` covers boot/init_boot/vendor_boot/dtbo/vendor/product/odm/oem/dlkm; `vbmeta_system` covers system/system_ext/system_dlkm; **`odm_ext` uncovered** (C17) | `slotselect` on every firmware mount; slot from BCB and/or env | none by itself | fstab, vbmeta images | P (inputs) / U (BL33 logic) |
| **Slot switch / OTA** | `update_engine` → boot-control HAL | OTA payload | boot-control HAL; env via `systemcontrol`; bootloader A/B devices | OTA payload signature (update_engine) | marks other slot active | writes `misc` BCB, env (`bootcmd`), possibly `mmcblk0boot*` (`reboot for ARB`) | HAL strings/imports, policy | P (who/what) / H (exact writes) |
| **Recovery** | BCB `boot-recovery` in `/misc` (written by recovery tooling, `uncrypt`, `update_engine`, `vold`, `init` on `reboot recovery`) | `vendor_boot` recovery ramdisk | `recovery` + Amlogic `librecovery_ui_ext` | ramdisk inside AVB-verified `vendor_boot` | — | per menu action | `libbootloader_message`, recovery strings | P |
| ↳ **Apply update** from ADB / SD / USB (`Udisk`) | recovery menu | `adb sideload`, `/sdcard`, `/udisk` | `update_engine_sideload` | package checked against `otacerts.zip` (`b153417b…`) | full OTA only (sideload refuses incremental on VAB) | installs OTA | recovery strings | P (path) / H (verification depth) |
| ↳ **`factory_update_param.aml`** | recovery reads `/udisk/` or `/sdcard/factory_update_param.aml` | removable media | Amlogic recovery extension | **not visible** (no signature strings near it); packages it names would still go through the OTA check | — | whatever the param file requests (Amlogic convention: recovery commands) | strings only | **H** |
| ↳ **Wipe data / cache / param** | recovery menu | — | recovery | — | — | erases `userdata` / cache / **`param`** (PQ + settings partition) | menu strings | P |
| ↳ **fastbootd** | recovery menu "Enter fastboot" / reboot to fastboot | USB fastboot (PID `4EE0`) | `fastbootd` + Amlogic fastboot HAL | **locked → no flash/erase/download/`set_active`** (`ro.boot.verifiedbootstate`) | — | none while locked | fastbootd strings | P (stock AOSP code) |
| ↳ **adbd in recovery** | recovery | USB (PID `D001`); prop also sets `service.adb.tcp.port=5555` | `adbd --root_seclabel=u:r:su:s0` | `ro.adb.secure=1`, `ro.debuggable=0` (user build) | — | — | recovery `init.rc`, `prop.default` | P (config) / H (what user-build recovery adbd allows: normally sideload only) |
| **OEM-unlock allowed flag** | Settings (via `system_server`) or the HAL's dumpsys interface (`shell` may call it) | env `ubootenv.var.lock` | OEM-lock HAL → `systemcontrol` | none beyond SELinux | — | writes env `lock` | HAL strings/imports, policy | P (path) / **U** (whether BL33 honors it; C5) |
| **Bootloader fastboot / USB burning / SD/USB autoscript** (`aml_autoscript`, `recovery_from_udisk`, `usb_burning`, `aml_sdc_burn.ini`) | key combos / env / USB host | USB / SD | BL2/BL33 (opaque) | U | U | U (CoreELEC's recovery shows this class writes env: C7) | **no plaintext evidence anywhere in coffey's OTA** | **U** (bounded negative in plaintext) |

## 4. What this settles and what it doesn't

- **Settled (P):** Android-side boot steering on coffey runs through the **U-Boot env** as well as `/misc`. Both
  the boot-control and OEM-lock HALs are `systemcontrol` clients, so the root service from C15 is the env
  writer for slot/boot commands and the unlock-allowed flag.
- **Settled (P):** fastbootd's flashing paths are lock-gated on the bootloader-reported state, and `/misc`
  isn't writable by apps or shell.
- **New boundary observations:** `shell` may call the OEM-lock HAL (which exposes a set option for the
  unlock-allowed flag), and an app may reach `systemcontrol` (C15). Both reach the *same env variable that the
  "OEM unlocking" toggle uses*. "Unlock allowed" isn't "unlocked"; unlocking still needs the bootloader's
  own fastboot path, which is opaque. Nothing was invoked.
- **Not settled (U):** what BL33 does with `bootcmd`, `lock`, the BCB, or removable media, and whether
  `factory_update_param.aml` is authenticated. These need either a readable BL33 (blocked, C13) or a device
  experiment under track §6.

## 5. Limits

- String/import/policy level; no disassembly, no control flow.
- U-Boot env defaults and the device's live env aren't in the OTA and weren't read.
- Recovery runs with its own SELinux policy (`sepolicy` in the recovery ramdisk); §2's policy tables are
  normal-mode only.
