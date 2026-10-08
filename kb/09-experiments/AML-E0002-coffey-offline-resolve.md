---
experiment_id: AML-E0002
title: "coffey offline-first resolution: Device Tree identity, kernel arch, partition geometry"
research_question: "Can the AML-E0001 unresolved items (DT identity, kernel bitness, logical+physical partition geometry) be settled by offline analysis of authorized firmware artifacts, without device modification?"
hypothesis: "Device Tree model/compatible, AArch64 kernel confirmation, and both logical (super) and physical (GPT) partition geometry are recoverable offline from boot/vendor_boot, dtbo, and super images — at a confidence/scope set by each artifact's provenance (coffey-exact vs sibling)."
target_device: "Walmart onn 4K Plus"
risk_level: read-only
prerequisites:
  - "Authorized firmware artifacts on hand, OR a Director-approved acquisition of an official firmware package"
  - "WSL Ubuntu analysis host (moria/mithril/payload_dumper/lpdump/dtc toolchain)"
result: not-started
related_findings:
  - AML-F0001
  - AML-F0002
---

# AML-E0002 — coffey offline-first resolution

Resolves the AML-E0001 open items by **offline** analysis of firmware artifacts
on a PC — no device, no privileged on-device operation, no modification. Every
result's confidence/scope is governed by its artifact's **provenance**
(coffey-exact build `URO4.260304.011.B1` → `exact-device`/`exact-soc`; a sibling
S905X5M/s7d image → `related-family`, never silently upgraded).

## Required image artifacts
- `boot.img` / `vendor_boot.img` — carries the kernel `Image` and (on this
  platform) the DTB(s).
- `dtbo.img` — device-tree overlays (board identity, revisions).
- `super.img` — the dynamic/logical partition container (A/B + Virtual A/B).
- The raw partition table (GPT) of the storage image, for **physical** geometry.
- `vbmeta` (context only; verified-boot chain, not re-attested here).

## Acquisition methods & provenance (favor existing authorized artifacts)
1. **Already-authorized artifacts first.** Inventory what is already on hand
   (e.g. prior `Onn Research` captures, our own kernel builds). Record for each:
   source, how it was authorized, sha256, byte length, and **coffey-exact vs
   sibling** scope. Do **not** assume a complete coffey image exists.
2. **Official firmware package (NEW acquisition → Director approval required).**
   Read-only OTA capture (OTACaptor logs the URL; DNS sinkhole prevents apply)
   → `payload_dumper` extracts images on the PC. Execution is gated; planning is
   not.
Provenance record per artifact: origin/URL, package sha256, each extracted
image's sha256 + byte length, extraction tool+version, and scope.

## Analysis tools
moria (identify/extract), mithril (boot posture), payload_dumper (OTA payload),
`lpdump`/`lpunpack` (logical/super), `dtc`/`fdtdump` (DTB/DTBO), `file` +
`readelf` (ELF), `sgdisk`/`parted` (GPT). All offline on the WSL host.

## Procedure (per unresolved item)

### R1. Device Tree identity
Extract the DTB from `boot.img`/`vendor_boot.img` and overlays from `dtbo.img`;
`fdtdump`/`dtc` → `model`, `compatible`, and any board-revision node. This is
the offline path around the SELinux-blocked `/proc/device-tree` reads that
failed in AML-E0001. Expected: Amlogic s7d / S905X5M board compatible strings;
board revision *if* encoded in DT.

### R2. Kernel architecture confirmation (correction #1 — Image ≠ ELF)
- A raw kernel **`Image`** (from `boot.img`) is **not** ELF. Confirm AArch64 by
  its **arm64 Image header**: little-endian `magic` `0x644d5241` ("ARM\x64") at
  offset 0x38, `MZ` at offset 0x0 (EFI stub). `file` → "Linux kernel ARM64 boot
  executable Image".
- A **`vmlinux`** is ELF: `readelf -h` → `ELFCLASS64`, `EM_AARCH64`. Keep these
  two checks distinct and name which artifact each applies to.
- Scope note: on-hand `vmlinux` are 5.15.216 / our builds (sibling), **not**
  coffey's shipped `5.15.196-…-ab14657224` — so coffey-exact confirmation needs
  coffey's own boot `Image`. Turns AML-F0001's `probable` kernel-bitness into
  `confirmed` only with a coffey-exact artifact.

### R3. Partition geometry (correction #2 — logical ≠ physical)
- **Physical (eMMC/GPT):** `sgdisk -p` / `parted` on the raw storage image →
  physical partition names, sizes, offsets — the data `/proc/partitions` denied.
- **Logical (super/dynamic):** `lpdump` on `super.img` → dynamic-partition
  metadata (names, sizes, group, slot); `lpunpack` enumerates logical
  partitions. Report logical and physical as **separate** layers; do not
  conflate the super container's logical map with the eMMC GPT.

## Expected findings & scope
DT model/compatible + board rev (R1); AArch64 kernel (R2); physical GPT + logical
super maps (R3). Each tagged by provenance: coffey-exact artifact →
`exact-device`/`exact-soc` `confirmed`; sibling → `related-family`, kept
distinct from coffey facts.

## Evidence preservation
sha256 + **byte length** + tool+version + source for every artifact and output;
raw images stay off-repo; a private manifest records full hashes, lengths,
commands, exit statuses, timestamps (per AML-TASK-004 correction #3).

## Authorization boundary
Planning and offline analysis of **already-authorized** artifacts may proceed.
**New firmware acquisition requires Director approval before execution.** No
device modification; no privileged on-device operation. Verified-boot facts are
**device-reported state**, not independent cryptographic attestation
(correction #4).

## Actual observations / Conclusion / Next steps
<fill as artifacts are analyzed; promote per-provenance into AML-F0001/F0002 and
new atomic findings; keep unresolved items unresolved until an artifact settles
them (correction #5).>
