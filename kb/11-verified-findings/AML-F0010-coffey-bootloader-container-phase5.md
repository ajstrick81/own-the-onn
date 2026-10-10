---
finding_id: AML-F0010
title: "coffey bootloader container internal map: @ML signed headers, @AMLBOOT BL2 table (BL2E/BL2X present, DDRF empty), opaque signed payload"
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
source_urls: []
source_revision: "bootloader partition from OTA URO4.260304.011.B1 (sha256 389daa99…)"
related_findings:
  - AML-F0006
status: promoted
---

# coffey bootloader container internal map (Phase 5, passive/offline)

Extends AML-F0006 with the internal layout of `bootloader.img` (4,100,096 B,
sha256 `389daa99…`). Full analysis: `E:\Morphe\device\coffey-ota\analysis\PHASE5-BOOT-CONTAINER.md`.
Read-only; component metadata kept separate from execution-order assumptions.

## Observations (established from magics/tables/offsets)
- **9× `@ML ` signed headers** at 0x0,0x110,0x1000,0x1580,0x1c80,0x2380,0x2900,
  0x3000,0x3080; u32 checksum/tag at +0x4, u32 size at +0xc (0x580/0x700/0x2ff0).
  Signature/key region 0x10000–0x30000 (entropy 8.00, opaque).
- **`@AMLBOOT` BL2 descriptor table @0x43820** (build `S7D-s905x5m-26030511BBST`,
  the only plaintext stage id). Entries {tag, LE u32 off, LE u64 size},
  bootloader-relative, contiguous:
  - **BL2E** off 0x44000 sz 0x1d000 — present (entropy 7.31, ARM64 code).
  - **BL2X** off 0x61000 sz 0x1b000 — present (entropy 7.64, ARM64 code).
  - **DDRF** off 0x7c000 sz 0x40000 — **reserved slot, zero-filled** (100% zero);
    DDR firmware not carried in this descriptor region in this package.
- **Opaque signed payload 0xc0000–~0x320000 (~2.5 MB)**, entropy 8.00, no
  plaintext stage labels.
- Zero padding 0x80000–0xc0000 and tail 0x330000–0x3E9000.

## Interpretation
The bootloader partition is an Amlogic multi-blob **signed** container: a header/
signature/cert block, a BL2 descriptor table (BL2E+BL2X present, DDRF slot
empty), and one large opaque signed payload carrying the later stages.

## Alternative explanations / discipline (coordinator refinements)
- **Entropy ≠ encryption (#4):** the 8.00-entropy regions are indistinguishable
  between compressed, encrypted, and signed-opaque data offline. No encryption is
  claimed. Absence of plaintext `BL31`/`BL32`/`BL33`/`U-Boot`/`SCP` strings =
  UNKNOWN, not "encrypted."
- **False-positive markers:** earlier `strings` hits `sCp`/`Bl2`/`DDR(`/`ddrs_`/
  `Rwbl2r_` fall inside high-entropy data (random printable runs) and are NOT
  component labels. Only the structured low-entropy table tags (BL2E/BL2X/DDRF)
  are real.
- **Execution order is inferred, not proven (#2):** the Amlogic FIP convention
  (eROM→BL2→BL30/SCP→BL31/ATF→[BL32]→BL33/U-Boot) is carried as an inference;
  the container's byte order is not its load/exec order.
- **Secure-world (#1):** DT `linux,secmon`/`heap-secure`/etc. are reservation
  declarations of intent, not verified TrustZone hardware enforcement; the
  BL31/secure-monitor payload is inside the opaque region, not independently
  verified.

## Validation needed / ceiling
Individual later stages (SCP/BL31/BL32/BL33) are not identifiable offline from
this signed image. Would need vendor FIP tooling / keys (not in hand) or a
debug/UART boot trace (device step, out of current scope).

## CORRECTIONS (2026-10-09, Coordinator/Codex finding, re-verified in-image → AML-F0016)
- The outer @AMLBOOT table has **5 descriptors**, not 3: **BBST**(0x0,0x44000) and
  **DEVF**(0xbc000,0x26f000) were missed here. `BBST` is the **first descriptor
  tag**, NOT a build suffix — the build field is exactly `S7D-s905x5m-26030511`.
- Descriptor layout is `{tag, u32 off, u32 size, u32 reserved=0}` (the u64-size
  reading above gives the same numbers only because reserved=0).
- The "opaque payload ~0xc0000" is **DEVF @0xbc000**, a **TF-A FIP** whose ToC
  (magic 0xaa640001) **identifies SCP/BL30, BL31, BL32, BL33 (+vendor BL40?) by
  standard UUID** — later-stage identity is NOT inaccessible without keys
  (payloads stay opaque; G12 open). See AML-F0016.
- The image tail is **not wholly zero** (2,960 nonzero bytes 0x3dffbf–0x3e825b;
  function unassigned). The earlier `sCp`/`Bl2`/`DDR(` false-positive note stands
  for the high-entropy payloads, but the DEVF **directory** is real structure.

## CORRECTIONS (2026-10-09/10, re-verified in-image → AML-F0023)
- BL2E/BL2X "ARM64 code" above is an **over-read**. Their bodies are sustained
  ~7.90 entropy / ~0% zeros, **random-indistinguishable** (no plaintext code
  window); the 7.31/7.64 aggregate came only from the zero-padding envelopes.
  Battery (uniform chi-square, zero ECB repeats, null serial-corr, no low-entropy
  windows) + marker scan **exclude** plaintext code and Huffman-class compressed
  plaintext, but are **consistent with encryption OR headerless arithmetic
  compression** — specific transform + key UNRESOLVED (not proven encryption, not
  a proven fused-key block). See AML-F0023 (softened 2026-10-10 per Codex controls).
