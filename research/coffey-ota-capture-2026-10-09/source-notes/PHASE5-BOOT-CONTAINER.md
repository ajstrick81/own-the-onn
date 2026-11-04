# Phase 5 — coffey bootloader container analysis (passive, offline)

Date 2026-10-09. Read-only on the already-extracted `images/bootloader.img`
(4,100,096 B, sha256 `389daa9963440f9f95ccc13fb31dfe18fa53fbe5a36cd740a17783b3f51ad775`,
from OTA `URO4.260304.011.B1`, AML-S0005). No modification, no execution, no
device contact. **Component metadata is kept strictly separate from assumptions
about execution order.**

## A. Established container metadata (from magics, tables, offsets)

### Signed-container header region `0x0 – ~0x3080`
Amlogic signed-blob format. **9× `@ML ` headers** (`40 4D 4C 20`) at
`0x0, 0x110, 0x1000, 0x1580, 0x1c80, 0x2380, 0x2900, 0x3000, 0x3080`. Each header
carries a u32 tag at +0x4 (per-blob checksum/hash: `0xed31668d`, `0xdb4c0e0b`,
`0x7cee2fd2`, `0x930edfe2`, `0xc51f7a23`, …) and a u32 size at +0xc
(`0x580`=1408, `0x700`=1792, `0x3000` header `0x2ff0`=12272). This is the
descriptor + signature/key-certificate block for the container.
- `0x10000 – 0x30000`: entropy 8.00 — opaque signature/key material
  (classification undetermined offline; see note on entropy).

### BL2 component descriptor table `@0x43820` (`@AMLBOOT`)
Magic `@AMLBOOT` at **0x43820** (NOT 0x4381f — that byte is `0x2c` `,`, a stray
char `strings` prepended; reconciled in AML-F0006). Build string
**`S7D-s905x5m-26030511BBST`** @0x4382c — the only plaintext stage identifier in
the image (SPL build 2026-03-05). Table entries `{4-char tag, LE u32 offset, LE
u64 size}`, offsets are **bootloader-partition-relative**:

| tag | offset | size | region entropy | state |
|---|---|---|---|---|
| BL2E | 0x44000 | 0x1d000 | 7.31 (16.6% zero) | **present** — ARM64 BL2 code/data |
| BL2X | 0x61000 | 0x1b000 | 7.64 (10.5% zero) | **present** — ARM64 BL2 code/data |
| DDRF | 0x7c000 | 0x40000 | 0.00 (100% zero) | **reserved slot, zero-filled in this image** (DDR fw not carried here) |

Offsets are contiguous (0x44000+0x1d000=0x61000; +0x1b000=0x7c000) — a
self-consistent BL2-stage layout. DDRF occupying a zeroed slot is a factual
observation, not an error: the DDR firmware is not stored in this descriptor's
region in this package.

### Opaque payload `0xc0000 – ~0x320000` (~2.5 MB)
Sustained entropy **8.00**, 0.9% zeros. Contains the container's later stages but
**no plaintext stage labels**. Earlier `strings` hits inside this region
(`sCp`, `Bl2`, `DDR(`, `Rwbl2r_`, `ddrs_`) are **false positives** — coincidental
printable byte runs within high-entropy data (verified in hex: surrounded by
random bytes), NOT component identifiers. Do not treat them as stage markers.

### Padding
Zero gaps `0x80000–0xc0000` (96.6% zero) and tail `0x330000–0x3E9000` (99.6%
zero) — alignment/reserved padding.

### Entropy-classification discipline (coordinator refinement #4)
The 8.00-entropy regions (`0x10000–0x30000`, `0xc0000–0x320000`) are
**indistinguishable between compressed, encrypted, and signed-opaque data** by
offline entropy alone. **No encryption is inferred.** The absence of plaintext
`BL31`/`BL32`/`BL33`/`U-Boot`/`SCP` strings is recorded as **UNKNOWN**, not as
evidence of encryption.

## B. Stage-by-stage boot architecture

**Established from the container (metadata only):**
```
[0x0]      @ML signed headers ×9  + signature/key region (0x10000–0x30000, opaque)
[0x43820]  @AMLBOOT BL2 descriptor table  →  BL2E(0x44000) BL2X(0x61000) [DDRF slot empty]
[0xc0000]  opaque signed payload ~2.5MB  (later stages, no plaintext labels)
[padding]  zero gaps / tail
build id:  S7D-s905x5m-26030511BBST
```

**Inferred execution order (Amlogic platform convention — NOT proven by this
container; byte-order ≠ load/exec-order):**
```
BootROM(eROM)
  └─> BL2 / SPL        [BL2E + BL2X ; DDR init normally via DDRF]   ← container-confirmed stage names
        └─> BL30 / SCP           ┐
              └─> BL31 / ATF EL3 ├─ expected in the opaque 0xc0000 payload,
                    └─> [BL32/TEE]│  but NOT individually identifiable offline
                          └─> BL33 / U-Boot ┘
                                └─> Android boot chain (boot_b → init_boot_b, AVB)
```
The SCP/BL31/BL32/BL33 ordering is the documented Amlogic FIP convention, carried
as an **inference**, not read from this image. The container proves only: a
signed header/cert block, a BL2 descriptor table (BL2E/BL2X present, DDRF slot
empty), and one opaque signed payload.

## C. Secure-world note (coordinator refinement #1)
The DT `linux,secmon` (36 MB no-map), `heap-secure`, `secure_vdec_reserved`, and
`mali_protected` are **Device-Tree memory declarations** reserving regions for a
secure monitor / protected media. They indicate an **intended** TrustZone/secure
layout; they are **not** independent verification of TrustZone hardware
enforcement (which would need secure-world attestation or EL3 inspection, out of
offline scope). The BL31/secure-monitor payload itself is inside the opaque
region and not independently verified here.

## D. Provenance preserved
All offsets/sizes/entropy are measured from the one artifact above (OTA-exact,
slot `_b`). Nothing here is cross-attributed to the sibling y0c image. Execution
order is labeled inferred throughout.
