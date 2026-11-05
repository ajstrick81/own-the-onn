# COFFEY odm_ext consumers (boot-policy Phase E)

**Date:** 2026-11-04. **Scope:** offline, read-only. coffey's `odm_ext` image (OTA `URO4.260304.011.B1`, slot
`_b`, SHA-256 `ca11823c…f55e`) was loop-mounted read-only (`ro,noload`) from a copy. Consumers were found by
string scans of every ELF, config, jar and app (dex/so inside APKs) in the unpacked `vendor`, `odm`,
`system_ext`, `product` and `system` trees, and by the loaded SELinux policy (same CIL set and resolver as
[`../coffey-systemcontrol-authz-2026-11-03/`](../coffey-systemcontrol-authz-2026-11-03/)). Nothing was run on a
device.

Track correction #6 applies: a path reference is not proof a file is loaded, and **nothing here asserts a
path from shell-controlled bytes to a privileged parser that wasn't shown.**

## 1. What odm_ext is (grade **P**)

| Property | Value | Source |
|---|---|---|
| Mount | `/dev/block/by-name/odm_ext` → `/mnt/vendor/odm_ext`, ext4, `ro,noatime,nosuid,nodev,nodelalloc,nomblk_io_submit,errors=panic`; `wait,slotselect,first_stage_mount` | `vendor/etc/fstab.amlogic` |
| **Integrity** | **No `avb` fstab flag**: the only read-only firmware mount without one (system, system_ext, system_dlkm, vendor, product, odm, vendor_dlkm, odm_dlkm and oem all carry `avb`). **Not listed in `vbmeta` or `vbmeta_system`** (which cover boot, init_boot, vendor_boot, dtbo, vendor, product, odm, oem, the dlkm partitions, and system/system_ext/system_dlkm) | fstab; vbmeta images |
| Labels | files `param_tv_file` (`/mnt/vendor/odm_ext(/.*)?`, also unused `/odm_ext`); block `param_block_device` | `vendor_file_contexts` |
| Image | 16 MiB ext4, created and last written 2026-03-19 09:29 (same day as the system/vendor build), mount count 0 | superblock |

## 2. Contents and consumers

| File (under `etc/tvconfig/`) | On coffey | Referenced by | Process · domain · uid | Parser | Edge |
|---|---|---|---|---|---|
| `pq/pq.db` (1,421,312 B; 112 tables; `PQ_VersionTable`: Amlogic PQ Tool 2.0, s905x5m, 2024-04-24) | **present** | `libpqcontrol.so` (literal path; also `pq_db_path` in `pq_default.ini`) | `systemcontrol` · `system_control` · **root** | SQLite (`libsqlite`) | **proven reference** |
| `pq/pq_default.ini` | **present** | `libpqcontrol.so` | same, root | INI (`CConfigFile`-style) | **proven reference** |
| `pq/UI_PQSetting.bin` | **present** (default copy) | `libpqcontrol.so` | same, root | binary struct | proven reference; the live copy is `/mnt/vendor/param/pq/UI_PQSetting.bin` per `pq_default.ini` |
| `pq/pq_ext.db`, `pq/overscan.db`, `pq/ldim.bin`, `panel/Amlogic_dv.cfg`, `panel/dv_config.bin` | **absent** | `libpqcontrol.so` | same, root | SQLite / binary / text | possible edge only if the file existed |
| `model/model_sum.ini`, `audio/AMLOGIC_AUDIO_EFFECT_DEFAULT.ini`, `audio/AUDIO_EFFECT.ini` | **absent** | `audio.primary.amlogic.so` and 6 `soundfx` libs (`libbalance`, `libhpeqwrapper`, `libtreblebasswrapper`, `libvirtualsurround`, `libvirtualx`, `libms12v2dapwrapper`) | audio HAL `vendor.audio-hal` · `hal_audio_default` · **audioserver** | INI | possible edge only if the file existed |
| `tvconfig.conf`, `tv_default.xml`, `tvscan.conf`, `tv_rrt_define.xml`, `tv_setting_config.cfg` | present | **no reference found** in any scanned binary or app; the `persist.vendor.tvconfig.path` property is declared in `vendor_property_contexts` but no reader was found | — | — | **unconsumed** (bounded) |
| `chmod_files.sh` (generic recursive-`chmod` helper) | present | **no reference** in any rc/script/binary; **no domain may `execute` `param_tv_file`** | — | — | **inert** |

`libpqcontrol.so` is loaded only by `vendor/bin/systemcontrol` (the only ELF listing it as `NEEDED`; a few
toybox links couldn't be read and are excluded). It also opens the raw block device
**`/dev/block/by-name/cri_data`** (`pq_wb_path`, white-balance data).

**Integrity inside the consumer:** `libpqcontrol` runs CRC-16 checks on some LUT/bin data
(`Lut crc error…`, `CRC check failed…`) and version/chip checks on `pq.db` (`pq.db don't match chip!`). A CRC
detects corruption; it doesn't authenticate data. No signature or hash verification strings were found (**H**
that none exists).

## 3. Who can change the bytes (grade **P**, loaded policy)

| Path to new bytes | Allowed for | Reading |
|---|---|---|
| Write the `odm_ext` block device (`param_block_device`) | `init`, `update_engine`, `fsck`, `e2fs` | OTA and filesystem tooling only. Not apps, `shell`, or `system_control` |
| Remount a labeled filesystem rw | `init`, `vold` | — |
| Write files labeled `param_tv_file` | `system_control`, `priv_app`, `platform_app`, `system_app`, `tvserver`, `dtvkitserver`, `hdcp_rx22`, `hdcp_rp22`, `tee`, `init`, `vendor_init` | Doesn't reach `odm_ext` itself (read-only mount). It does reach the **writable** `/mnt/vendor/param` partition, which carries the same label and holds the live PQ copies (`/mnt/vendor/param/pq/`, created `0755 root` by `systemcontrol.rc`, so DAC further limits non-root writers) |
| Write `cri_data` raw (`cri_block_device`) | `system_control` only | PQ white-balance store |
| Execute anything labeled `param_tv_file` | **nobody** | — |

## 4. Consumer graph

```
                 OTA (update_engine) / init / fsck / e2fs            [only software writers]
                                   │ block write
                                   ▼
   odm_ext (ext4, RO mount, NO AVB/dm-verity) ──read──► libpqcontrol ─► systemcontrol (root)
      pq.db, pq_default.ini, UI_PQSetting.bin                 │            SQLite · INI · binary
      (+5 referenced-but-absent PQ/panel files)               │ CRC/version checks only
      (+3 referenced-but-absent audio INIs) ──read──► audio HAL (audioserver), soundfx libs
      (5 TV config files: unconsumed;  chmod_files.sh: inert)
                                                              │ writes (save*/factory*/SSM)
                                                              ▼
                              /mnt/vendor/param/pq/*  (rw, param_tv_file)  ◄── read back by libpqcontrol
                              /dev/block/cri_data      (raw, white balance)
```

**Proven edges:** `odm_ext` → root `systemcontrol` (SQLite/INI/binary readers); `systemcontrol` → `param`/`cri_data`
writable copies → back into its own readers.
**Possible edge (H), from C15:** an app that can call `systemcontrol` can drive its PQ write methods, which
change the `/mnt/vendor/param/pq` and `cri_data` data that `libpqcontrol` later parses. These are the service's
own value writes, not raw attacker files, and nothing was traced or tested.
**Not shown:** any path from `shell` or an app to the bytes of `odm_ext` itself.

## 5. Answers for the track

- **The baseline is confirmed and sharpened:** `odm_ext` is read-only and outside AVB/dm-verity (was B, now
  **P**), and it's the *only* firmware partition with no AVB coverage at all.
- **Its privileged consumer is root `systemcontrol`.** It parses an unauthenticated SQLite database and INI
  from that partition at runtime. Software can only change those bytes via OTA/init/fsck tooling (P).
  Physical eMMC access is outside this analysis.
- **Integrity gap, stated as a boundary:** anything able to write the `odm_ext` partition gets persistent,
  unverified input to a root parser that survives reboot and isn't caught by verified boot. No software path
  to that write was found for apps or `shell`.
- Five config files and a shell script on `odm_ext` have no consumer on this build.

## 6. Limits

- String-level consumer discovery; dynamic path construction (e.g. from properties) would be missed. The
  one tvconfig property found has no reader.
- `/mnt/vendor/param` contents weren't captured (runtime data, not in the OTA).
- No disassembly; the parsers' robustness is not assessed and no files were fed to them.
