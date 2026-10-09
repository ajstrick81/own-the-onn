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
Provenance record per artifact, kept **separately** (refinement #4):
origin/URL, **exact build identifier**, **A/B slot relationship**, package +
per-image **sha256** and byte length, extraction tool+version, and
**correspondence with the running device** (does it match coffey's
`URO4.260304.011.B1` / slot `_b`, and how was that correspondence established).
**Scope rule (refinement #5):** a package advertising the same version string
is **not** automatically `exact-device` — version-match alone never upgrades a
finding; exact-device requires verified correspondence to the running build,
not just a matching label. Absent that, scope stays `related-family`/`exact-soc`.

## Analysis tools
moria (identify/extract), mithril (boot posture), payload_dumper (OTA payload),
`lpdump`/`lpunpack` (logical/super), `dtc`/`fdtdump` (DTB/DTBO), `file` +
`readelf` (ELF), `sgdisk`/`parted` (GPT). All offline on the WSL host.

## Procedure (per unresolved item)

### R1. Device Tree identity
**Discover the actual firmware layout first** — do not assume DTBs live in
`boot.img`/`vendor_boot.img`. On Amlogic they may be in `dtb.img`/`dtbo.img`, a
vendor `dtb` partition, appended to the kernel, or need vendor-specific
extraction (refinement #2). Once located, `fdtdump`/`dtc` → `model`,
`compatible`, board-revision node. This is the offline path around the
SELinux-blocked `/proc/device-tree` reads that failed in AML-E0001. Expected:
Amlogic s7d / S905X5M compatible strings; board revision *if* encoded in DT.

### R2. Kernel architecture confirmation (correction #1 — Image ≠ ELF)
- A raw kernel **`Image`** (from `boot.img`) is **not** ELF. Confirm AArch64 by
  the **arch-specific arm64 Image header**: little-endian `magic` `0x644d5241`
  ("ARM\x64") at offset 0x38. The `MZ` at offset 0x0 is only present when the
  **EFI stub** is compiled in — **do not require `MZ`** (refinement #1); the
  0x38 magic is the authoritative check. `file` typically → "Linux kernel ARM64
  boot executable Image".
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
- An OTA payload typically ships images (incl. `super`) but **no raw GPT** —
  treat a missing physical GPT as an **expected limitation, not a failure**
  (refinement #3). Record whatever logical (super) and physical (GPT, if a
  factory/full image provides it) geometry each artifact actually yields,
  independently.

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

## Toolchain validation (y0c sibling, related-family — NOT coffey)
Director-authorized dry-run 2026-10-09 on `E:/Morphe/device/y0c-uro1` validated
the method (full provenance off-repo in `scratchpad/y0c-dryrun`):
- **R1 tooling OK** (`extract-dtb`+`dtc`); lesson: `dtbo.img` = overlays, so
  coffey `model`/`compatible` must come from the **base DT** (boot/vendor_boot).
- **R2 method validated end-to-end**: boot v4 → extract kernel → **decompress
  (gzip)** → ARM64 Image magic `0x644d5241` @0x38. Lesson: decompress before the
  header check.
- **R3**: `lpdump`/`lpunpack` **not exercised** — y0c has no packed `super.img`.
  Its partition images (odm/vendor/product…) are **EROFS (LZ4) filesystems**,
  **not** ext4 and **not** Android-sparse (confirmed by `file` + EROFS
  superblock; `simg2img` → "Invalid sparse file format"). Corrects the earlier
  "raw ext4" guess. coffey R3 needs a coffey `super.img`.
Nothing here promoted to coffey.

## Acquisition status (coffey, AML-TASK-005)
A coffey **exact-build OTA** is acquired PC-side (no device): `AML-S0005`
(URO4.260304.011.B1, archive sha256 `ec755bd0…`, fingerprint-matched to the
device, signed). 17-partition payload inventory recorded. This **unblocks**:
- **R1** (dtbo + base DTB from boot/vendor_boot → model/compatible values),
- **R2** cross-confirm (coffey boot Image → ARM64 header),
- **R3 sizes** (per-partition sizes from the payload manifest).
Still **not** obtainable from an A/B OTA (expected): physical GPT offsets and
super LP grouping (need on-device `lpdump` or a factory image).

## Actual observations / Conclusion / Next steps (coffey)
<next: extract boot/vendor_boot/dtbo only (payload_dumper --partitions), verify
against manifest hashes, then promote R1 DT values + R2 cross-confirm into
AML-F0004/F0001 (exact-device, source AML-S0005); keep physical GPT + super
grouping unresolved.>
