---
experiment_id: AML-E0001
title: "Onn 4K Plus (coffey) read-only device baseline collection"
research_question: "What are coffey's exact hardware, firmware, kernel, partition, and boot-interface facts, settled on the device itself?"
hypothesis: "A read-only adb session + existing artifacts + public source establish the full baseline without any device modification; some fields (board revision, firmware build id, partition map) are currently unverified and need a device read."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "adb over network to coffey (see CLAUDE.local.md for current IP; confirm reachable)"
  - "Device already set up and owner-operated; USB-debugging/ADB enabled"
  - "A gitignored raw-evidence dir (raw/ is already ignored) to hold dumps off-repo"
result: not-started
artifacts: []
related_findings:
  - AML-F0001
---

# AML-E0001 — coffey read-only device baseline

Establishes coffey's baseline from the device itself, with every step
**read-only** (no setprop, no remount, no fastboot, no flashing, no density/
size changes — see the project's standing "never wm density/size on onn" rule).
Outputs seed `AML-S` observation sources and promote `AML-F` findings; raw
dumps are **never committed** (repo `.gitignore` blocks `raw/`, `dumpsys_*`,
`settings_*`).

## Existing vs. new evidence
- **Already recorded** (`AML-F0001`, from prior public/root-study facts):
  marketing name, codename/platform, SoC, arch, Android 14, SPL 2026-03, kernel
  5.15.196, bootloader welded. This experiment **re-confirms** them against a
  fresh device read and tightens provenance.
- **Not yet verified (new evidence needed):** board revision, exact firmware
  build fingerprint, partition map / sizes / A-B layout, DT model string,
  enabled diagnostic interfaces, exact kernel config hash.

## Procedure (read-only; grouped; each step = command → expected → establishes)

### G1. Identity & build (ADB)
```
adb shell getprop | sort
```
Expect: `ro.product.*`, `ro.board.platform`, `ro.build.fingerprint`,
`ro.build.version.{release,security_patch,sdk}`, `ro.product.cpu.abilist`.
Establishes: device/codename, SoC platform, Android/SPL, **firmware
fingerprint (new)**, abilist (32-bit userland confirm). Source → `AML-S` (adb).

### G2. Kernel & config (ADB)
```
adb shell uname -a
adb shell zcat /proc/config.gz > raw/coffey-config.gz.txt   # off-repo
adb shell cat /proc/version
```
Expect: `5.15.196-android14-11 aarch64`; kernel config symbols. Establishes:
kernel version/arch (re-confirm) + **config hash (new)**. Hash the config,
record the sha256, do **not** commit the raw. Source → `AML-S` (adb).

### G3. SoC / DT model (ADB, read-only)
```
adb shell cat /proc/device-tree/model 2>/dev/null
adb shell cat /proc/device-tree/compatible 2>/dev/null | tr '\0' '\n'
adb shell cat /proc/cpuinfo
```
Expect: Amlogic model/compatible strings, CPU part ids. Establishes: **DT model
(new)**, SoC corroboration. Note: some DT nodes may be SELinux-blocked without
root — record what is and isn't readable (a negative result is a finding).

### G4. Partition metadata (ADB, read-only)
```
adb shell cat /proc/partitions
adb shell ls -l /dev/block/by-name 2>/dev/null
adb shell getprop | grep -iE "slot|boot_part|ab_update"
```
Expect: partition names/sizes, by-name symlinks, A/B slot indicators.
Establishes: **partition map + A/B layout (new)**. Read-only listing only — no
dd, no imaging of vendor partitions (several are unreadable without root; that
boundary is itself a finding, consistent with root-study).

### G5. Diagnostic interfaces (ADB, read-only)
```
adb shell getprop | grep -iE "adb|usb|debuggable|secure"
adb shell ls -l /dev 2>/dev/null | grep -iE "ttyS|ttyFIQ|ttyGS"
```
Expect: adb/usb config, debuggable/secure flags, any exposed serial nodes.
Establishes: enabled interfaces inventory. **Excluded from this phase:**
entering fastboot/bootloader or `fastboot getvar` (requires a reboot into
bootloader = a state change) — defer to a separate, explicitly-approved step.

### G6. Existing artifacts & public source (no device)
- Reconcile against prior `dumpsys`/getprop captures already collected (if any)
  and the published `research/root-study.md`.
- Cross-check SoC/kernel claims against public source (CoreELEC `common_drivers`
  = `AML-S0002`, **related-family**, not device-authoritative).

## Expected observations
Each group yields scalar facts tied to a specific key/command. Confirmed
device facts → `exact-device` confidence `confirmed` (cite the adb `AML-S`);
anything only inferable from CoreELEC/public source stays `related-family`/
`inferred` until the device read confirms it.

## Actual observations
<fill after the read-only session>

## Conclusion
<what the baseline establishes; which AML-F0001 fields moved from prior-public
to device-confirmed; which remain unknown>

## Next steps
- Create one `AML-S` per capture group (type `observation`, scope
  `exact-device`, with per-field key mapping like `AML-S0001`); store raw
  off-repo and record each sha256.
- Promote confirmed fields into `AML-F0001` (and new atomic findings for
  partition map, DT model, interfaces).
- Evidence preservation: timestamp + sha256 every raw artifact; keep raw in
  gitignored `raw/`; record tool versions (adb version, device build id).

## Risk classification
All steps **read-only (R)**. Deferred/not-authorized here: fastboot/bootloader
entry, partition imaging, any `setprop`/remount/flash — each would be a
state-changing step requiring separate Director approval.
