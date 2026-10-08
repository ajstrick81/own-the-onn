---
experiment_id: AML-E0001
title: "Onn 4K Plus (coffey) read-only device baseline collection"
research_question: "What are coffey's exact hardware, firmware, kernel, partition, and boot-interface facts, as reported by the device itself?"
hypothesis: "A read-only adb session + existing artifacts + public source establish the full baseline without any device modification; some fields (board revision, firmware build id, partition map, DT identifiers, config hash) are currently unverified and need a device read."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "adb over network to coffey (see CLAUDE.local.md for current IP; confirm reachable)"
  - "Device already set up and owner-operated; USB-debugging/ADB enabled"
  - "A gitignored raw-evidence dir (raw/ is already ignored) to hold dumps off-repo"
result: done
artifacts:
  - "off-repo scratch: raw/ captures + manifest.tsv (sha256, exit codes, timestamps); not committed"
related_findings:
  - AML-F0001
  - AML-F0002
  - AML-F0003
---

# AML-E0001 — coffey read-only device baseline

Establishes coffey's baseline from the device itself, every step **read-only**
(no setprop, remount, fastboot, flashing, or density/size change — see the
standing "never wm density/size on onn" rule). Outputs seed `AML-S` observation
sources and promote `AML-F` findings; raw dumps are **never committed** (repo
`.gitignore` blocks `raw/`, `dumpsys_*`, `settings_*`).

**Evidence framing (coordinator refinement #3):** getprop build fingerprints,
hardware properties, and Device Tree identifiers are **device-reported**
evidence. They establish what the running software reports, not independently
verified physical-hardware facts. Record them as such; do not overstate.

## Existing vs. new evidence
- **Already recorded** (`AML-F0001`, prior public/root-study facts): marketing
  name, codename/platform, SoC, arch, Android 14, SPL 2026-03, kernel
  5.15.196, bootloader welded. This experiment re-confirms them against a fresh
  device read and tightens provenance.
- **New evidence needed:** board revision, firmware build fingerprint, partition
  map / sizes / A-B + dynamic (super) layout, DT model/compatible, enabled
  diagnostic interfaces, exact kernel config hash.

## Procedure (read-only; each step → expected → establishes; capture exit code + timestamp)

### G1. Identity & build (ADB)
```
adb shell getprop > raw/coffey-getprop.txt      # privacy-scrub before any publication (#7)
```
Keys of interest: `ro.product.*`, `ro.board.platform`, `ro.build.fingerprint`,
`ro.build.version.{release,security_patch,sdk}`, `ro.product.cpu.abilist`,
`ro.boot.*`. Establishes device/codename, SoC platform, Android/SPL, firmware
fingerprint (new), abilist. **Device-reported** (#3).

### G2. Kernel & config (ADB) — preserve compressed artifact first (#1)
```
adb exec-out 'cat /proc/config.gz' > raw/coffey-config.gz     # binary-safe; hash THIS original
adb shell uname -a ; adb shell cat /proc/version
```
Hash `raw/coffey-config.gz` (sha256) **before** any local `gunzip`. If
`/proc/config.gz` is absent or unreadable, **record the failure + exit code**
(do not substitute). Establishes kernel version/arch (re-confirm) + config hash
(new).

### G3. SoC / Device Tree (ADB) — binary first, then render (#2)
```
adb exec-out 'cat /proc/device-tree/model'       > raw/dt-model.bin        2>raw/dt-model.err
adb exec-out 'cat /proc/device-tree/compatible'  > raw/dt-compatible.bin   2>raw/dt-compatible.err
adb shell cat /proc/cpuinfo > raw/coffey-cpuinfo.txt
```
Preserve the raw binary DT props, hash them, **then** produce human-readable
(`tr '\0' '\n'`) copies for reading. Establishes DT model/compatible (new,
device-reported) + CPU part ids. Some DT nodes may be SELinux-blocked without
root — record exactly which are inaccessible (#8), do not escalate.

### G4. Partitions incl. logical/dynamic (ADB, read-only) (#4)
```
adb shell cat /proc/partitions > raw/coffey-partitions.txt
adb shell ls -l /dev/block/by-name 2>raw/by-name.err
adb shell ls -l /dev/block/mapper  2>raw/mapper.err      # dynamic (super) logical partitions
adb shell getprop | grep -iE "slot_suffix|boot_part|ab_update|dynamic_partitions|super"
adb shell cat /proc/cmdline > raw/coffey-cmdline.txt      # androidboot.slot_suffix, etc.
```
Account for A/B **and** dynamic/super logical partitions where listable without
root. `lpdump`/`dmctl` typically need elevated privileges — if unavailable,
**record the permission denial** (#8), do not escalate. Read-only listing only:
**no dd / no imaging** of any partition (several are unreadable without root —
that boundary is itself a finding, per root-study).

### G5. Diagnostic interfaces (ADB, read-only) (#5)
```
adb shell getprop | grep -iE "adb|usb|debuggable|ro.secure|persist.sys.usb"
adb shell ls -l /dev 2>/dev/null | grep -iE "ttyS|ttyFIQ|ttyGS|ttyAML"
```
A `/dev/ttyS*` node is an **exposed serial device node**, **not** a physically
verified external UART header — distinguish the two. Physical UART confirmation
requires hardware probing and is **out of scope** here (deferred, separate
approval).

### G6. Existing artifacts & public source (no device)
Reconcile against any prior captures and published `research/root-study.md`;
cross-check SoC/kernel against CoreELEC `common_drivers` (`AML-S0002`,
**related-family**, not device-authoritative).

## Evidence manifest (#6)
For every command, record: the command string, **exit code**, **collection
timestamp (UTC)**, **adb version** (`adb version`), **device build id**
(`ro.build.fingerprint`), the artifact path, and its **sha256**. Store the
manifest alongside the raw captures in gitignored `raw/` (never committed).

## Evidence preservation & privacy
- Hash (sha256) + timestamp every raw artifact; keep all raw in gitignored
  `raw/`. Record tool versions.
- **Privacy review before any publication (#7):** scrub complete property dumps
  for identifiers (serial, Wi-Fi/BT MAC, accounts, IMEI-like, GSF/Android IDs,
  SSIDs) — `tools/privacy_scan.py` assists. Only scrubbed, field-level facts
  reach `AML-S`/`AML-F`; raw dumps stay off-repo.
- **Inaccessible files / permission denials are recorded explicitly (#8).** A
  denial is a finding, not a prompt to escalate. No privileged operation is
  introduced to obtain missing information.

## Expected observations
Scalar facts tied to a specific key/command. Device-confirmed facts →
`exact-device` `confirmed` (cite the adb `AML-S`); CoreELEC/public-only
inferences stay `related-family`/`inferred` until the device read confirms.

## Actual observations
Run 2026-10-08T23:24Z, adb 1.0.41, build `URO4.260304.011.B1` (15051976). All
14 steps executed read-only; raw + sha256 manifest held off-repo. Recorded into
`AML-S0003`; facts promoted to `AML-F0001` (identity), `AML-F0002` (partitions/
boot), `AML-F0003` (interfaces). Key reads: `ro.soc.model AMLS905X5M`, platform
`s7d`, Cortex-A55; kernel `5.15.196-android14-11-g3d26c188ef7e-ab14657224`;
userland 32-bit; AVB 1.2 locked / verifiedbootstate green; dynamic + Virtual
A/B super partitions (dm-verity) on eMMC `mmcblk0`; adb-over-tcp:5555, user
build (`ro.debuggable=0`).

## Evidence summary
- **Confirmed (device-reported):** SoC AMLS905X5M / s7d; Cortex-A55; Android 14
  (SDK 34), SPL 2026-03-01; firmware `URO4.260304.011.B1`; kernel 5.15.196 exact
  tag; 32-bit userland; AVB-1.2 locked verified boot (green); A/B + Virtual A/B
  dynamic/super partitions under dm-verity; eMMC mmcblk0 (31 parts); ADB over
  TCP, non-debuggable user build; serial nodes ttyS0 (root) / ttyS1 (BT).
- **Unresolved / access-denied (no escalation):** partition sizes/offsets
  (`/proc/partitions` denied); kernel cmdline (`/proc/cmdline` denied); DT
  model (absent) and DT compatible (denied) → **board revision unknown**;
  authoritative super-partition map (`lpdump`, needs privilege).
- **Hypotheses needing further evidence:** 64-bit kernel (probable from
  `ab14657224` GKI, but `uname` in a 32-bit shell can't prove it); full
  partition layout obtainable only via an approved offline-image method.

## Conclusion
AML-F0001 fields SoC, kernel, Android/SPL, verified-boot, and **firmware build
id** moved from prior-public to **device-confirmed**; partition/boot and
interface baselines are newly established (`AML-F0002`, `AML-F0003`). Board
revision and exact partition geometry remain `unknown` by read-only means.

## Next steps
- One `AML-S` per capture group (type `observation`, scope `exact-device`,
  per-field key mapping like `AML-S0001`); raw off-repo, each sha256 recorded.
- Promote confirmed fields into `AML-F0001`; new atomic findings for partition
  map, DT model, interfaces.

## Risk classification
All steps **read-only (R)**. Deferred / not authorized here: fastboot or
bootloader entry, partition imaging, `lpdump`/privileged reads, any
setprop/remount/flash — each would be state-changing and needs separate
Director approval.
