# Public lookup addendum for Claude

Date: 2026-11-02 (America/Chicago). Public, host-side research only. No device access or repository commit occurred.

This addendum pre-stages four research areas for the coffey boot-policy track. It does not supply coffey's OTA, DTB, bootloader, or `systemcontrol` ELF; those remain target-specific inputs.

| Deliverable | Result |
|---|---|
| `COFFEY-PQ-ANCHORS-AD14-DELTA.md` | No public Android 12/13/14 `CPQControl` source/call graph located. Existing Pie donor remains lead-only; authorization unknown. |
| `COFFEY-BOOT-CHAIN-MODEL.md` | Stage/signature/rollback model separates public architectural comparators from S7D/coffey unknowns. No S7D stage-by-stage verifier map found. |
| `COFFEY-DARKKNIGHT-OTA-RECON.md` | Xiaomi TV and Google OTA endpoint families documented as leads; no endpoint or package verified for darkknight. OS3.0.2.0 is an owner report with product-name ambiguity. |
| `COFFEY-CE-GENERIC-BARRIER-MATRIX.md` | Device-tree, dispatch, verification, storage, video, and secure-media prerequisites summarized; all coffey boot cells remain U. |

Classification continues to use P/R/B/H/U from the project handoff. A same-SoC or same-vendor observation stays a comparator unless the exact board/build matches. In particular, Xiaomi Box S 3rd Gen (`twilight`) and Chromecast (`sabrina`) are not darkknight; older Amlogic signing/config code is not S7D proof.

## Best next evidence

When Adam's OTA capture becomes available, preserve the unmodified archive, URL/redirects/headers, date, source/target build, package metadata and SHA-256. That may establish darkknight package provenance and provide a vendor boot/FIP corpus for the model. For Phase F, the matching coffey `systemcontrol` ELF with hash and Build ID remains the decisive source for caller authorization. For Phase B, exact bootloader artifacts and per-stage metadata are required before turning the architectural sketch into a build-specific verification map.

