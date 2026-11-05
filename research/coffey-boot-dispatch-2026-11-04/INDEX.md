# Boot-policy map — 2026-11-04 (boot-policy Phase B)

coffey's boot dispatch reconstructed from everything plaintext in its own OTA: ramdisks, steering HALs, fstab
and the loaded SELinux policy. Offline only. Reports and scripts verify against [`SHA256SUMS.txt`](SHA256SUMS.txt);
binaries and ramdisks are pinned in [`DISPATCH-INPUTS-SHA256SUMS.txt`](DISPATCH-INPUTS-SHA256SUMS.txt) and not
committed.

| File | Content |
|---|---|
| [`COFFEY-BOOT-POLICY-MAP.md`](COFFEY-BOOT-POLICY-MAP.md) | Sources and plaintext bound, who steers boot, writers/callers by policy, the Phase B path table |
| [`scripts/bootimg_split.py`](scripts/bootimg_split.py) | Splits vendor_boot/boot/init_boot ramdisks, prints cmdline and bootconfig |
| [`scripts/rd_extract.py`](scripts/rd_extract.py) | Pure-Python lz4-legacy/gzip + newc-cpio extractor (regular files only, path-confined) |

## Bottom line

- `bootloader.img` has **no plaintext dispatch logic** (zero hits for every Phase-B token), so what U-Boot
  decides stays **U**.
- On the Android side, boot is steered through the **U-Boot env** as well as `/misc`. Both the boot-control
  HAL and the OEM-lock HAL are **`systemcontrol` clients**; the "OEM unlocking allowed" state is env
  `ubootenv.var.lock`.
- `/misc` is writable only by system boot/update components. `fastbootd` refuses flash, erase and `set_active`
  on locked devices.
- `shell` may call the OEM-lock HAL, and apps may reach `systemcontrol` (C15); both reach the same `lock`
  variable. "Unlock allowed" isn't "unlocked", and whether the bootloader honors it remains C5.
- Recovery offers sideload/SD/USB updates (checked against `otacerts.zip`), wipes including **`param`**, and
  reads an Amlogic `factory_update_param.aml` from removable media whose authentication isn't visible (H).
