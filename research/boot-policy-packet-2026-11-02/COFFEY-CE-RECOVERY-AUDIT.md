# COFFEY CoreELEC recovery audit

Date: 2026-11-02 (America/Chicago). Public artifact retrieval and host-side static analysis only. No device connection, firmware script execution, flashing, live boot, HIDL invocation or repository commit occurred. Host extraction/decompression utilities and researcher-written parsers were used; recovered firmware scripts and binaries were treated as data.

Classification: **P** inspected public source/artifact; **R** author report, not reproduced; **B** inherited project baseline; **H** inference/lead; **U** unresolved. A donor observation is not a coffey observation. Artifact hashes identify bytes, not trustworthiness or device compatibility.

Paths are relative to the evidence package root. `artifacts/` contains retrieved sources; `release/` and `nightly-new/` contain extracted files. Full image archives are separate deliverables, with URLs and hashes in the manifest.

## Verdict

**The selected stock recovery setup does not fit a strict read-only boundary.** Once running in its intended setup condition, it can write the persistent boot environment. Its read-only mount of the USB FAT filesystem does not prevent writes to internal environment storage. Whether coffey accepts or can execute this image is entirely unresolved.

This is a static audit of the recovered initramfs, bundled script, environment configuration and pinned build recipes. It inventories visible writes and external execution boundaries. It is not an exhaustive proof about every kernel/driver/binary side effect or arbitrary externally supplied hook. No live success, failure or rollback behavior was reproduced.

## Image structure and exact build correlation

The release recovery.img is an Android boot image, header version 0, 2048-byte pages. Its LZO kernel is 3,465,987 bytes at offset 2048; its Zstandard-compressed newc ramdisk is 1,508,122 bytes at offset 3,469,312. Decompression identifies Linux 5.15.196, built October 3, 2026. Header command line is empty: actual command-line inputs remain bootloader-dependent.

The extracted ramdisk contains init, functions, fw_env.config, BusyBox, fw_setenv and runtime libraries. It contains no platform_init or post-flash hook. Complete entries are in inventory.json. No recovered executable was run.

The pinned aml_recovery recipe builds a dedicated kernel and initramfs_recovery, wraps them through mkbootimg and installs recovery.img. initramfs_recovery depends on libc, BusyBox and u-boot-tools. The pinned BusyBox recipe copies init/functions and substitutes distribution, kernel-name and system-size tokens. Substituting CoreELEC, kernel.img and 512 produces a byte-identical release init; functions and fw_env.config also match their source. The project-specific linux recipe pins kernel source 968a93c28223f72ff94e706eabb0277292bac878, branch 5.15.196_20260306. The generic top-level linux recipe is not the applicable kernel selection.

The November 3 nightly also contains Linux 5.15.196. Its init differs at line 1012: the SYSTEM checksum copy now uses UPDATE_SYSTEM.md5 instead of UPDATE_KERNEL.md5. This corrects a source-name mix-up in that update branch; it does not establish a security issue or change the setup environment-writing verdict. functions, fw_env.config and fw_setenv bytes are identical between the retained release and nightly.

## Setup path and failure behavior

1. init creates volatile directories and mounts devtmpfs/proc/sysfs/tmpfs; sources functions.
2. It parses /proc/cmdline. If BOTH boot and disk are absent, do_aml_autoscript runs before the ordinary boot sequence.
3. It selects LABEL=COREELEC and mounts /flash ro,noatime. An optional post-flash.sh is sourced if present; none ships on the inspected FAT image.
4. It waits up to 15 iterations for /dev/env. If that block node and /flash/aml_autoscript exist, it skips the script's first 72 bytes, translates lines beginning setenv into fw_setenv commands, and evaluates them individually.
5. It prints completion and calls do_reboot. Missing prerequisites also lead to do_reboot. There is no transaction, per-variable result check or rollback in the loop. A failed mount enters an interactive debug shell and can return; this is not a fail-closed read-only exit.

The Linux conversion is not the same as executing the full U-Boot script: defenv, standalone saveenv, run commands and the conditional fdtaddr line are not translated by the anchored setenv expression. The bootcmd value contains a future conditional saveenv. Do not describe this path as resetting the whole environment to defaults.

## Persistent-write and execution-boundary inventory

Locators below refer to release/recovery/root/init. “Conditional” means a visible branch, not proof it succeeds in the minimal recovery environment.

| ID | Location / condition | Write or action | Boundary / qualification |
|---|---|---|---|
| CE-W01 | 1026–1058; boot/disk absent; env and script present | Individual fw_setenv updates | Intended setup behavior; internal persistent environment backend. |
| CE-W02 | bundled aml_autoscript setenv lines | bootfromnand, upgrade_step, ce_on_emmc, cfgload_env, cfgloadsd, cfgloadusb, cfgloademmc, bootfromsd, bootfromusb, bootfromemmc, bootcmd | Eleven assignments. cfgload/boot values alter later boot dispatch; not a signature bypass claim. |
| CE-W03 | 428–453, reboot helper | Move init log to /storage/init-previous.log, sync, unmount, reboot | During early setup /storage is an unmounted ramdisk directory, so log move is volatile; later mounted storage makes it persistent. Reboot operational side effects remain device-specific. |
| CE-W04 | 165–174, FOLDER mount branch | Mount containing filesystem rw, bind a subdirectory, then remount /flash ro | A caller-requested ro mount is not a universal no-write guarantee. Journal/metadata behavior is filesystem-dependent. |
| CE-W05 | 455–557, filesystem repair | fsck automatic repair; forced -y repair on failure; reboot/poweroff branches | /usr/sbin/fsck is not present in the minimal recovered ramdisk. Latent generic path, not an observed successful recovery write. |
| CE-W06 | 487–497 | fatlabel repairs CE_FLASH label | fatlabel absent in minimal ramdisk; latent conditional metadata write. |
| CE-W07 | 592–604 | Remount /flash rw and remove firmware/update leftovers | Conditional filenames absent from inspected stock FAT. |
| CE-W08 | 606–644 | Mount storage rw; create per-host overlay directory | Live mode uses tmpfs; disk-backed storage can persist writes. |
| CE-W09 | 646–678 | Edit syslinux/grub defaults; delete alternate configs | Conditional menu files absent from inspected Generic FAT. |
| CE-W10 | 698–725, 770–950 | Create update workspace, extract/move/decompress files, generate checksum files, delete update files and flags | Error branches also call cleanup. Failure is not equivalent to no writes. |
| CE-W11 | 303–349, 1000–1023 | dd kernel/SYSTEM files; possible raw block target; bootloader update.sh; user-update.sh | Conditional ordinary update branch. Exact target depends on command line and filesystem. Dynamic update scripts are outside this closed artifact set. |
| CE-W12 | 222–224, 587–589, 635–637, 1016–1021, 1161–1164 | Source post-sysroot.sh/post-flash.sh/mount-storage.sh; execute user-update.sh/platform_init | Hooks absent from inspected recovery/FAT. If supplied externally, effects cannot be bounded by this audit. |
| CE-W13 | 1368–1385 | Select resize/reset/restore systemd targets; write/delete persistent init log | The init script selects targets; actual partition resize/reset/restore occurs downstream and is not proven by the selection alone. |
| CE-W14 | 1347–1394 | chroot kernel-overlays-setup; switch_root to systemd | End of this audit's initramfs boundary; complete downstream userspace not audited. |
| CE-V01 | init 10–28, 1152–1158, 1280–1294; functions | Runtime dirs, progress/log pipes, sysfs CPU settings, proc printk, resolver file | Volatile filesystem or runtime configuration; distinguish from persistent media writes. |

No GPT rewrite or A/B slot-selection command appears in the closed setup path. That narrower observation does not rule out writes by dynamic hooks, selected systemd targets, drivers or later U-Boot dispatch. No persistent reboot flag is explicitly written by do_reboot itself; bootfromnand and upgrade_step are explicit environment state changes in the setup payload.

## Environment backend

The installed fw_env.config lists /dev/nand_env and /dev/env, offset zero, environment size 0x10000 and sector size 0x10000. The package uses U-Boot tools 2016.03 with CoreELEC patches. The multiple-entries patch skips candidates that cannot be opened O_RDWR; the NAND patch changes low-level handling. Do not read the generic config comment as proof of redundant environments on this board. Successful writes still require the actual device node, access and backend implementation.

The fw_setenv executable is preserved and hashed, but not executed. The recipes and configuration establish intended storage behavior; this audit does not prove that every byte of the binary was reproducibly built from those sources.

### CE-01 — Environment writes are part of setup

- Target build: CoreELEC 22.0-Piers_rc1 Generic
- Artifact SHA-256: `c002a557cee265c256a8fd0a909a07e1aa5caf69582091d9de60fd7e2fdc711f`
- Source revision: `75626f5a6e955cdee0aa1a4c97b0d8660e1ea1af`
- File + locator: `release/recovery/root/init` — lines 1026–1058 and 1302–1303
- Observation: P: parsed setenv lines are evaluated as fw_setenv; unconditional reboot follows branch.
- Interpretation: Stock setup is not read-only.
- Competing explanations / limits: No coffey execution or backend acceptance demonstrated.
- Next discriminating check: Match coffey boot dispatch and env backend from Adam’s future artifact set.

### CE-02 — Source-to-image correlation

- Target build: CoreELEC 22.0-Piers_rc1 Generic
- Artifact SHA-256: `3d761364f31c4ce2fe588d969dbbd172b709a899fd0c371ff2899b225cffc3f0`
- Source revision: `75626f5a6e955cdee0aa1a4c97b0d8660e1ea1af`
- File + locator: `artifacts/ce-packages__sysutils__busybox__scripts__init` — full file with three documented substitutions
- Observation: P: normalized source matches release init byte-for-byte.
- Interpretation: Confidence applies to this script and release.
- Competing explanations / limits: Not whole-build reproducibility or complete driver audit.
- Next discriminating check: Keep script hash alongside image hash; trace any new release separately.
