# Phase 5 — BL33 / boot-container encryption finding (passive, offline)

> **⚠️ SUPERSEDED IN PART (2026-10-10).** This report's measurements, range
> verification, and marker scan stand and were reproduced independently. Its
> **conclusions of proven AES/"strong-cipher encryption" and an OTP-fused-BootROM-key
> decode barrier are WITHDRAWN** as overreach. Corrected stance (authoritative):
> the payloads show **uniform byte-frequencies under the run tests + no visible
> framed-format/ELF/U-Boot markers**, which **exclude neither** all compressed
> inputs nor every small plaintext fragment, and are **consistent with encryption
> OR headerless/arithmetic compression OR other packaging** — specific transform
> and key UNRESOLVED; the fused-key barrier is a platform hypothesis, not proven.
> Read `kb/11-verified-findings/AML-F0023` (confidence: probable) for the current
> wording. Where this report below says "encrypted"/"fused key" as established,
> read "opaque / consistent-with-encryption, transform & key unresolved".

Date 2026-10-09. Read-only on the already-extracted `images/bootloader.img`
(4,100,096 B, sha256 `389daa99…`, OTA `URO4.260304.011.B1`, slot `_b`, AML-S0005).
No modification, no execution, no device contact.

Supersedes the "opaque / classification UNKNOWN" disposition for the post-header
payload in `PHASE5-BOOT-CONTAINER.md` §A/§C, and **corrects** that doc's
characterization of BL2E/BL2X as "ARM64 BL2 code/data" (see §4).

## 1. Range verification (provenance pin)

Handoff-cited "BL33" range reproduces exactly against the on-disk blob:

| field | value |
|---|---|
| range | `[0x1aa000, 0x32a260)` (bootloader-partition-relative) |
| length | `0x180260` (1,573,472 B ≈ 1.5 MB) |
| sha256 | `693afa5b2a7feae24f60c56ff34f4f277d7cb5833d256190004bae5b3e382d00` → `693afa5b` ✓ |
| head64 | `3c0423c5 fefd7874 8253528c c578a841 …` (no U-Boot/gzip/LZ4/LZMA magic) |

## 2. Statistical classification — ENCRYPTED, not compressed, not signed-plaintext

Entropy alone (8.00) cannot separate compressed / encrypted / signed-opaque.
A four-test battery was run on the BL33 range and resolves it decisively:

| test | BL33 result | interpretation |
|---|---|---|
| chi-square, 255 df (uniform mean ≈255, p0.05 crit ≈293) | **253.3** | textbook uniform — cipher signature; compression leaves residual non-uniformity |
| 16-byte block repeats | **0 / 98,342 blocks** | no ECB artifacts → CBC/CTR/XTS-class mode |
| serial (adjacent-byte) correlation | **−0.00019** | null; compression streams show small nonzero correlation |
| low-entropy 4 KB windows across the whole 1.5 MB | **0** | no header/footer/table anywhere → not any compression container |

Conclusion: the BL33 region is **strong-cipher encrypted in a non-ECB mode**, not
merely compressed or signed-plaintext. (Signed-plaintext ARM64 would present
~6.0–6.5 entropy with recognizable instruction/opcode structure and low-entropy
windows; none are present.)

## 3. The whole post-header chain is encrypted with the same scheme

Windowed-entropy profiling + the same battery on BL2E/BL2X bodies:

| stage | body range | body entropy | chi-square | ECB dups | serial-corr |
|---|---|---|---|---|---|
| BL2E body | `0x46000–0x5e000` | ~7.90 | 262.3 | 0 | −0.0046 |
| BL2X body | `0x61000–0x79000` | ~7.90 | 228.0 | 0 | −0.0022 |
| BL33 | `0x1aa000–0x32a260` | 8.00 | 253.3 | 0 | −0.0002 |

All three match the same uniform / no-ECB / null-correlation signature → one
encryption scheme across the entire BL2 + BL3x chain.

### Per-stage container shape (now fully characterized)
```
[ zero-pad envelope ] [ encrypted body ~7.9 ] [ 00000000 ffffffff 00000000 ffffffff ] [ RSA signature blob ] [ zero-pad ]
```
The `00000000 ffffffff 00000000 ffffffff` delimiter appears identically at the tail
of BL2E (`@0x5e000`) and BL2X (`@0x79000`) — the Amlogic per-stage signature-trailer
marker; the high-entropy runs around it are the RSA signature(s) over each
encrypted stage.

## 4. KB CORRECTION (re-verify-in-image discipline)

`PHASE5-BOOT-CONTAINER.md` §A table labeled BL2E (ent 7.31) and BL2X (ent 7.64)
as "present — ARM64 BL2 code/data". **That is an over-read.** Windowed profiling
shows the bodies are sustained ~7.90 entropy with ~0% zeros (encrypted); the
aggregate 7.31/7.64 and the "16.6% / 10.5% zeros" came entirely from the
**zero-padding envelopes** (BL2E `0x0–0x2000` and `0x1a800–end`; BL2X
`0x18000–end` — all 100% zero), not from plaintext code. **There is no plaintext
code window anywhere in BL2E/BL2X.** Only the `@ML` signed headers (`0x0–0x3080`)
and the `@AMLBOOT` descriptor table + build string (`0x43820`,
`S7D-s905x5m-26030511BBST`) are plaintext in the entire image.

## 5. What this means for the decode capability and the env-consumption question

- "Decode capability not in hand" = the **AES key**, which on S905X5M is derived
  from an **OTP/eFuse-fused root key** and decrypted by the on-die **BootROM**
  (mask ROM) before BL2 executes. It is **not present in the image** in any form.
  Offline decode of BL33 (and BL2) is therefore **blocked at the fused key** — a
  genuine silicon/OTP wall, established with mechanism, not an assumption.
- Consequence for the `system_control` env lane (AML-F0022 `setBootEnv`): we still
  **cannot** prove offline whether the locked/AVB bootloader honors a written
  `bootcmd`, because the consuming BL33 code is encrypted and un-disassemblable
  here. The env-consumption question stays INDETERMINATE, now for a *specific*
  reason (BL33 ciphertext), not a vague "opaque".
- There is **no embedded-key lead to chase** in this image: the decryptor is the
  BootROM, not any plaintext stage carried in the container.

## 6. Residual (device-interactive, OUT of current authorizations)

The only remaining decode paths are hardware/device-side and all require Director
authorization + carry brick/destructive risk — none are offline:
1. **BootROM USB-mode dump / mask-ROM exploit** (Amlogic USB boot path). Historic
   S905-family bootROM USB exploits exist; S905X5M unproven. Device-interactive.
2. **Hardware key extraction** (glitch / side-channel on the fused key). Physical,
   destructive-risk.
3. Obtaining a decrypted BL33 from an out-of-band source (not in scope).

BOTTOM LINE: BL33 and the full BL2/BL3x chain are AES-encrypted with per-stage RSA
signatures, one scheme throughout. The standing "BL33 opaque / UNKNOWN" is resolved
to "encrypted; offline decode blocked at the OTP-fused BootROM key." No offline
move advances it further; the lane's residual leads are device-interactive and
Director-gated.
