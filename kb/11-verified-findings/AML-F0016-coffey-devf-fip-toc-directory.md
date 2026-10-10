---
finding_id: AML-F0016
title: "coffey bootloader DEVF = TF-A FIP with readable ToC identifying SCP/BL30, BL31, BL32, BL33 (+vendor BL40?) by standard UUID; payloads opaque (G5 advanced, G12 open)"
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0009
source_urls: []
source_revision: "bootloader.img sha256 389daa99… from OTA URO4.260304.011.B1; parse re-verified in-image"
related_findings:
  - AML-F0010
status: promoted
---

# coffey DEVF TF-A FIP directory (Coordinator/Codex finding, re-verified in-image)

Independently reproduced on `bootloader.img` (not taken on faith). Corrects and
extends AML-F0010.

## Observations (verified byte-for-byte in the image)
- **Outer @AMLBOOT table @0x43820: version 2, 5 contiguous 16-byte descriptors
  `{tag, LE u32 off, LE u32 size, u32 reserved=0}`** (u32-size+reserved, not u64):
  | tag | off | size | end |
  |---|---|---|---|
  | BBST | 0x0 | 0x44000 | 0x44000 |
  | BL2E | 0x44000 | 0x1d000 | 0x61000 |
  | BL2X | 0x61000 | 0x1b000 | 0x7c000 |
  | DDRF | 0x7c000 | 0x40000 | 0xbc000 (zero-filled) |
  | **DEVF** | **0xbc000** | **0x26f000** | **0x32b000** |
  Build field is exactly `S7D-s905x5m-26030511` (20 B); **`BBST` is the first
  descriptor tag, NOT a build suffix** (corrects AML-F0010).
- **DEVF @0xbc000**: 16-byte nonzero prefix, then **TF-A FIP ToC** at 0xbc010
  (magic `0xaa640001`, serial 0x100, flags 2), 5× 40-byte entries @0xbc020
  (uuid16 + off8 + size8 + flags8), zero terminator, all flags 0:
  | identity | UUID bytes | rel off | size | file start (base 0xbc000) |
  |---|---|---|---|---|
  | SCP/BL30 | 9766fd3d89bee849ae5d78a140608213 | 0x2000 | 0x10260 | 0xbe000 |
  | vendor (BL40?) | 8a52127a4a35a344be316a2093f3287c | 0x13000 | 0x18470 | 0xcf000 |
  | BL31 | 47d4086d4cfe98469b952950cbbd5a00 | 0x2c000 | 0x40470 | 0xe8000 |
  | BL32 | 05d0e18953dc13478d2b500a4b7a3e38 | 0x6d000 | 0x80470 | 0x129000 |
  | BL33 | d6d0eea7fcead54b97829934f234b6e4 | 0xee000 | 0x180260 | 0x1aa000 |
- **Image tail NOT wholly zero**: 2,960 nonzero bytes between 0x3dffbf and
  0x3e825b after DEVF (function unassigned).

## Interpretation
The region I earlier called an opaque payload (AML-F0010) is **DEVF**, a TF-A
FIP whose **ToC directory is readable without keys** and identifies the later
boot stages by standard TF-A UUID: **SCP/BL30, BL31 (ATF EL3), BL32 (TEE), BL33
(U-Boot)**, plus a vendor UUID that is a **BL40 candidate** (P1 packer size
correspondence 96 KiB+0x470; inferred, not UUID-decoded). **G5 advances**:
later-stage *identity* is established; **payload implementation remains opaque**
(~8-bit entropy, no plaintext/compression magics) so the exact ATF impl/version
(**G12**) stays unresolved.

## Alternative explanations / discipline
- **DEVF base 0xbc000 vs magic 0xbc010**: base 0xbc000 is supported because for
  all five entries the final 16 bytes before the computed end are nonzero and
  padding starts exactly at the end; using 0xbc010 shifts every range 16 B.
  Vendor reader offset convention not inspected → base is strongly-supported,
  not proven. Both-base hashes preserved in Codex `coffey-fip-directory.json`.
- Directory identity is **stronger than payload identity**: UUIDs name intended
  components; they do **not** decode the wrapper, identify code, validate
  signatures, or prove runtime execution / secure-boot acceptance.
- Descriptor `{off,size,reserved}` (u32) supersedes F0010's u64-size reading
  (same numbers because reserved=0). P1 is a different platform/version (v1 vs
  coffey v2) — grammar reference only (AML-S0009).

## ADDENDUM (2026-10-10) — reference packaging tool resolves container STRUCTURE
Source: authorized acquisition + STATIC inspection of 5 revision-pinned Khadas
objects (repo khadas/u-boot, commit ee291cdb…; all 5 Git blob IDs verified; tool
`acpu-imagetool` = stripped x86-64 ELF, inspected via strings/ELF/Capstone/objdump,
NOT executed). Codex round-3 (CLAUDE-ROUND3-PACKAGING-FINDINGS). **Reference impl,
NOT confirmed = coffey's build; structure only — no BL33 decode, no key, no
confidence upgrade to encryption/key-location/env/policy.**
- **+0x6000 shift = full-vs-compact LAYOUT CONSTANTS** (supersedes the conjectural
  "extra records push payloads"). CLI parser @0x40c470: `full`=layout1, `compact`=
  layout2. Stage-dir assignment @0x40da40 — **compact offsets BL30 0x2000 / BL40
  0x13000 / BL31 0x2c000 / BL32 0x6d000 / BL33 0xee000 match coffey's acquired DEVF
  exactly; full offsets (+0x6000 each) match the reference header.** ⇒ **coffey DEVF
  uses the COMPACT layout.** Header classes return len 0x8000 (full)/0x2000 (compact);
  compact total extent 0x26f000 = coffey DEVF extent.
- **6 extra reference records = per-stage CERTIFICATE PAIRS** (BL30/BL40/BL31/BL32/
  BL33/KRNL), each 0xe00 = two 0x700 halves (first=chipset L3 cert, second=device L3
  cert). Reference template: BL40/BL31/BL32 both halves populated; BL30/BL33/KRNL
  first-half all-zero → 9 populated halves. ⚠️ compact class ALSO exposes cert
  getters — **fewer directory entries ≠ absence of cert processing** (don't infer
  coffey skips certs).
- **@ML half fields resolved (label-derived, PUBLIC — not secrets/payload hashes):**
  +0x4 = first 4 SHA-256 bytes of a TYPE label (`AML: Chipset/Device Level-3
  Certificate`) = type tag, NOT a payload checksum (closes the N2 +0x4 uncertainty);
  +0x4e0 = first 16 SHA-256 bytes of a DUID label (`DUID/CERT: … LEVEL-3 CERTIFICATE:
  <stage>`). Host SHA-256 reproduced both for all 9 halves. `DBLK_PAYLOAD_END` at
  +0x4d0. Extent at +0xc = LE 0x700 (1792), not 0x70000.
- **16-byte pre-FIP prefix = a NONCE buffer** (reference designates it; tool
  conditionally copies a supplied 16B value, else keeps template bytes — does NOT
  itself generate one). coffey prefix `4229886e…`, ref `43501c8d…`; coffey nonce
  origin/quality/key-derivation UNKNOWN.
- **Header SHA-256 footer verified in BOTH images** (full@0x7fe0, compact@0x1fe0):
  SHA-256 of header-minus-last-0x20 == stored footer, for reference-full (0x8000) AND
  coffey-compact (0x2000 @ bootloader.img+0xbc000). = **UNKEYED container-integrity
  digest** — tamper-evident, says NOTHING about a secure-boot signature boundary or
  whether firmware accepts modified input.
- Script plumbing (REFERENCE build, not coffey key material): `gen-device-fip.sh`
  calls `create-device-fip --header-layout=full` with per-stage RSA L3 keys +
  **AES-256 payload keys for BL30/BL33** + pre-signed BL40/BL31/BL32. Consistent with
  (NOT proof of) coffey BL33 being AES-encrypted. `common.mk` NOT acquired (outside
  the 5) → final recipe/build-env propagation uninspected at that include boundary.

## Validation needed / ceiling
Packaging-structure gap CLOSED for the 5 acquired reference objects. Still open:
coffey's exact build invocation + `common.mk`; coffey BL33 transform/key (opaque);
env consumption; G12 (exact ATF/BL31 impl); G6 (DDR fw location). No keys/decryption
attempted; reference ≠ coffey attribution preserved.
