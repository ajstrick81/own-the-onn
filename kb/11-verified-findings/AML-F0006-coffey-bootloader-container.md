---
finding_id: AML-F0006
title: "coffey bootloader = Amlogic signed @AML container (S7D/s905x5m, BL2-family)"
component: boot-architecture
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
source_urls: []
source_revision: "bootloader partition from OTA URO4.260304.011.B1"
related_findings:
  - AML-F0002
status: promoted
---

# coffey bootloader container inventory (AML-TASK-006)

Extracted from the acquired OTA (`AML-S0005`), offline/read-only. Not repacked,
flashed, or executed. `bootloader.img` 4,100,096 B, sha256 `389daa99…`.

## Observations (byte-level, confirmed)
- Header magic at 0x0 = `@ML ` (40 4d 4c 20); `@AMLBOOT` string at 0x4381f →
  **Amlogic signed bootloader container**.
- Board/build string at 0x4382c: **`S7D-s905x5m-26030511BBST`** (S7D / s905x5m;
  build stamp 26030511 ≈ 2026-03-05).
- Stage tokens `BL2E` (0x43850) and `BL2X` (0x43860) → Amlogic BL2 extension/
  eXtended second-stage markers; `Rwbl2r_` string at 0x358a.
- Single `@AML` container occurrence (0x43820); total 0x3e9000.

## Interpretation
An Amlogic multi-stage **signed** bootloader container for the S7D/s905x5m
platform, carrying BL2-family stages. This maps onto the documented Amlogic
boot chain — BL2 / BL2E / BL2X (second stage), then BL30/BL31 (secure monitor /
ATF) and BL33 (U-Boot) — assembled and signed in one partition image.

## Alternative explanations / uncertainty
- **Deeper stage boundaries are NOT confirmed.** No plaintext `U-Boot`, `BL31`,
  or "ARM Trusted Firmware" strings were found — consistent with signed/
  compressed inner stages. The BL30/BL31/BL33 mapping above is **inferred from
  Amlogic's documented layout**, not delimited by in-file headers here.
- The build string and magics identify the container; they do **not** prove any
  component is executable or that the device would accept it (a recognizable
  header ≠ runnable/accepted). No physical-device validation performed.
- Exact-build package evidence; distinct from what runs in the device's active
  slot.
