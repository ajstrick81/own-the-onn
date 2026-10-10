---
finding_id: AML-F0023
title: "coffey BL2E/BL2X/DEVF-FIP(incl BL33) payloads show UNIFORM byte-frequencies under the run tests + no directly-visible framed-format/ELF/U-Boot markers in the scanned bytes; no plaintext implementation or framed compressed instance established there; CONSISTENT WITH encryption, headerless/arithmetic compression, or other packaging — transform + key UNRESOLVED. Corrects F0010 'ARM64 code' over-read."
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: probable
source_refs:
  - AML-S0005
source_urls: []
source_revision: "bootloader.img sha256 389daa99… from OTA URO4.260304.011.B1; statistical battery + marker scan re-run in-image; Codex controls cross-checked"
related_findings:
  - AML-F0010
  - AML-F0016
status: promoted
---

# coffey boot-chain payload opacity classification (Phase 5, passive/offline)

Advances the "payload opaque / entropy≠encryption UNKNOWN" disposition of AML-F0010
and AML-F0016 — but does NOT resolve it to a proven cipher. Full analysis (itself
corrected 2026-10-10 to this stance):
`E:\Morphe\device\coffey-ota\analysis\PHASE5-BL33-ENCRYPTION-FINDING.md`.
Read-only, no decrypt attempted. Wording tightened per Codex reconciliation
(CLAUDE-BL33-RECONCILIATION-2026-10-10), DATA re-verified in-image.

## Observations — CONFIRMED (reproduced independently by Coordinator/Codex)
Battery on each stage body (padding/trailers excluded):
| stage | body range | entropy | chi-square (255 df, uniform≈255) | ECB dups | serial-corr |
|---|---|---|---|---|---|
| BL2E body | 0x46000–0x5e000 | ~7.90 | 262.3 | 0 | −0.0046 |
| BL2X body | 0x61000–0x79000 | ~7.90 | 228.0 | 0 | −0.0022 |
| BL33 (FIP entry UUID d6d0eea7…) | 0x1aa000–0x32a260 | 7.9999 | 253.3 | 0 / 98,342 | −0.00019 |

- BL33 range reproduces sha `693afa5b…` = F0016 FIP ToC BL33 entry exactly. Codex
  reproduced chi 253.316, entropy 7.999884, serial −0.000190, 0 dup-blocks.
- **Marker scan: ALL ZERO** in the BL33 range AND the whole 4,100,096 B image —
  `@ZSTD`, zstd `28b52ffd`, lz4 `04224d18`, gzip `1f8b08`, ELF, `U-Boot`, `bootcmd`,
  `boot_flag`, zstd-skippable. (Independently reproduced; Codex concurs.)
- Per-stage shape: `[zero-pad][opaque body ~7.9][00000000 ffffffff 00000000
  ffffffff delimiter][high-entropy trailer][zero-pad]`; 0000/ffff delimiter
  identical at BL2E (0x5e000) and BL2X (0x79000) tails — Amlogic stage trailer.
- Only `@ML` headers (0x0–0x3080) + `@AMLBOOT` table + build `S7D-s905x5m-26030511`
  (0x43820) + the F0016 FIP **ToC directory** (0xbc010) are plaintext/structured.

## Interpretation — scoped to what the tests show
The bodies are **consistent with uniform byte frequencies under the run tests**
(chi-square, 16-byte ECB-repeat, adjacent-byte correlation, 4 KB windowed entropy).
Passing these does NOT establish statistical randomness or cryptographic security.

**Not established in the scanned bytes:**
- **A plaintext ARM64 implementation.** Plaintext code would present ~6.0–6.5
  entropy with opcode structure + low-entropy windows; none seen. Near-uniform
  whole-region statistics do **not** exclude a small embedded plaintext fragment.
- **A directly-visible framed instance of the scanned formats** (`@ZSTD`, zstd/lz4/
  gzip magic). One compressible-**code** control was strongly non-uniform
  (zstd-9/19 chi-square ~10,454 / 31,694), but a single control does **not**
  characterize all inputs, stream variants, or enclosing transforms — Zstandard
  itself combines raw/RLE/FSE/Huffman mechanisms and cannot be reduced to one
  fingerprint.

**Consistent with (these tests cannot separate):**
- Encryption (strong cipher, non-ECB mode) — the leading hypothesis.
- Headerless arithmetic/range-coded compression (LZMA-class can be near-uniform,
  no byte-level fingerprint, no visible magic).
- Zstandard storing already-incompressible input as raw blocks (Codex control:
  stays uniform — but requires the input itself to already be random).
- Compressed-then-encrypted / packaged (fits the reference pipeline; see addendum).

**Explicitly NOT established:** the specific transform (cipher vs compression), the
cipher/mode, key derivation, and **key location**. Uniform+markerless is *necessary*
not *sufficient* for "encrypted." **Signing, encryption, and compression are kept
distinct:** a signature/trailer may be random-looking, but **signing alone does not
conceal a payload or make its full contents uniform** — it would leave the body
readable. So signing is not an explanation for whole-payload uniformity; encryption
or (some) compression would be.

## CORRECTION to AML-F0010 (robust — stands)
F0010 labeled BL2E (ent 7.31) / BL2X (ent 7.64) "ARM64 code". **Over-read:** a
**plaintext ARM64 implementation was not established by that inspection.** The
bodies are ~7.90 entropy / ~0% zeros under the run tests; the lower aggregate came
entirely from the zero-padding envelopes (BL2E 0x0–0x2000 & 0x1a800–end; BL2X
0x18000–end, 100% zero). No plaintext code window was observed in the bulk (a small
embedded fragment is not excluded). This correction is independent of the
encryption question.

## ADDENDUM (2026-10-10) — reference compression pipeline (Codex), reconciled
Codex: the cached S7D **reference** build zstd-compresses BL33 (`amfc_compress`:
`@ZSTD`+origLE32+compLE32+zstd, level 9, gated `CONFIG_AML_BL33_COMPRESS_ENABLE`),
then optionally signs via `dv-device-fip` → `.device.signed`. coffey's production
flags are unknown; markers for that wrapper are absent from coffey (verified above).
- A **compressed-then-encrypted/packaged** BL33 is one model consistent with the
  evidence: an **encrypting or compressing** stage could produce the uniform
  statistics while any inner structure is hidden (hence no markers). **Plausible
  model, not a confirmed coffey pipeline;** signing is not part of that explanation.
- DEVF directory: production = 5 entries, reference template = 11; first 5
  UUIDs/sizes/flags match; every reference payload offset = production + 0x6000
  (header-layout difference, not a decoded wrapper).
- **Agreed next structural target:** the `gen-device-fip.sh` / S7D device-fip
  Makefile chain (implementation not in local files). It **may clarify structure;
  whether it yields decoding information or key handling is unknown** — this claims
  neither that a key exists nor that a decoder will be found. Hashes unchanged
  (BL33 693afa5b…, container 389daa99…).

## Ceiling / consequence (unchanged in practice)
- **BL33 remains UNDECODED offline.** No visible wrapper, decoder, decrypt path, or
  key was found in any pass. Whether decode is "blocked at a fused BootROM key" is a
  **platform hypothesis** (standard Amlogic secure-boot), NOT established here.
- For AML-F0022 `setBootEnv`: offline proof of whether the locked/AVB bootloader
  honors a written `bootcmd` stays **INDETERMINATE** — the consuming BL33 payload is
  opaque and un-interpretable offline.
- Residual decode paths are device-interactive and Director-gated (brick/key-loss
  risk), none offline: BootROM USB/ADNL dump · hardware key/transform extraction ·
  out-of-band decoded BL33. Reference device-fip study may clarify structure but is
  not guaranteed to yield a decoder.
