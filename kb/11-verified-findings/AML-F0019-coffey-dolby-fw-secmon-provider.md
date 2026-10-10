---
finding_id: AML-F0019
title: "coffey /dev/dolby_fw provider lives in first-stage amlogic-secmon.ko (dolby_fw_ioctl/fops present; secure-monitor-mediated path to Dolby firmware)"
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0006
source_urls:
  - "https://github.com/CoreELEC/common_drivers/blob/8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734/drivers/secmon/dolby_fw.c"
  - "https://github.com/CoreELEC/common_drivers/blob/8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734/drivers/secmon/dolby_fw.h"
source_revision: "amlogic-secmon.ko sha256 6279fcc7…88ab9 from vendor_boot ramdisk (OTA URO4.260304.011.B1); symbols/relocations re-verified in-image"
related_findings:
  - AML-F0013
status: promoted
---

# coffey Dolby firmware provider in first-stage amlogic-secmon.ko (Codex finding, re-verified in-image)

## Observations
The first-stage `amlogic-secmon.ko` extracted from the shipped vendor_boot
ramdisk (sha256 `6279fcc7…88ab9`) contains, verified in-image via `readelf`:

- `dolby_fw_ioctl` (size **7148** B), `dolby_fw_probe` (**504** B),
  `dolby_fw_init` (**72** B), plus `dolby_fw_open`/`dolby_fw_release` — byte
  sizes match Codex `dolby-kernel-provider-binary-evidence.json` exactly.
- `dolby_fw_fops` with relocations routing the ioctl slots (offsets 80/88) to
  the `dolby_fw_ioctl` CFI jump-table entry, and open/release/probe/remove
  slots to their respective CFI trampolines (R_AARCH64_JUMP26, in-image).

Shipped DT (decompiled) carries an enabled `dolby_fw` node, compatible
`amlogic, dolby_fw`, `mem_size=0x100000` (1 MiB); the secmon node declares
SMC function IDs 0x82000020 / 0x82000021 / 0x8200002a (input/output/shared
size). CoreELEC `drivers/secmon/dolby_fw.{c,h}` at commit `8646fbd1…` (AML-S0006)
builds `dolby_fw.o` into `amlogic-secmon` and assigns Dolby SMC IDs
0x82000052–0x8200005a; the shipped disassembly corroborates SMC
base/offset construction and `__arm_smccc_smc_glue` calls (Codex artifact).

## Interpretation
The kernel-side provider for the userspace `/dev/dolby_fw` path (used by the
OEM `DOLBYSFW` MS12 conversion helper `vendor/bin/dolby_fw_dolbyms12`) is a real
ioctl dispatcher inside the shipped first-stage secure-monitor module, bridging
userspace to secure firmware via SMC — not just a reference in another component.

## Alternative explanations
Presence of symbols, fops wiring, and DT node are configured/static facts; they
do not establish probe success, returned buffer addresses/sizes, or that any
conversion runs on-device. The CoreELEC source agrees with packaging but does
not make every reference length/verification check byte-identical to coffey.

## Validation needed
The Linux driver cannot explain the secure-world transform/authentication —
that requires separate BL31/BL32 firmware evidence (FIP UUIDs alone do not
identify the handlers; see AML-F0016). Device-gated: observe probe success,
negotiated shared size, and runtime access to `/dev/dolby_fw`. No vulnerability
is claimed from provider identification alone.
