# Boot-policy evidence packet — 2026-11-02 (Codex)

First results against the [`../codex-task-list.md`](../codex-task-list.md) tasks for the
[boot-policy track](../boot-policy-track.md). Public-artifact retrieval + host-side **static** analysis only —
no device connection, no firmware script executed, no flashing, no live boot. See
[`RELAY-SUMMARY.md`](RELAY-SUMMARY.md) first.

## What's committed here (text only)
| File | Covers task | One-line result |
|---|---|---|
| [`COFFEY-CE-RECOVERY-AUDIT.md`](COFFEY-CE-RECOVERY-AUDIT.md) | Task 2 (Phase C) | **Stock CoreELEC recovery is state-changing** — writes the persistent boot env via `fw_setenv` (11 assignments), reboots with no rollback; **fails a read-only boundary**. coffey acceptance still unresolved. |
| [`COFFEY-PUBLIC-ARTIFACT-MANIFEST.md`](COFFEY-PUBLIC-ARTIFACT-MANIFEST.md) | Task 1 | Hash-pinned CoreELEC release `22.0-Piers_rc1` + Nov-3 nightly, donor DTBs, upstream S7D, U-Boot sources, PQ donor source, slimBOX helper. darkknight OTA **not obtained**. |
| [`COFFEY-DTB-COMPARISON.md`](COFFEY-DTB-COMPARISON.md) | Task 3 | Semantic DT diff (upstream BM202 vs CE generic/Xiaomi/Ugoos). coffey column is `B — pending artifact` throughout. |
| [`COFFEY-PQ-ANCHORS.md`](COFFEY-PQ-ANCHORS.md) | Task 4 | PQ/HIDL donor call-chains (`factorySetParamsDefault`, `getPQDatabaseInfo`, …). Every coffey ELF offset `Pending`; donor permission helper is stubbed — no coffey authorization conclusion. |
| [`COFFEY-DONOR-PREREQS.md`](COFFEY-DONOR-PREREQS.md) | Task 5 | Prereq matrix: every donor (N3/N4/N6/S7/N2) assumes root / unlocked bootloader / working external boot. **None is a locked-device bypass.** slimBOX `Unlock_Bootloader.cmd` = standard `fastboot flashing unlock`, no custom payload. |
| [`SHA256SUMS`](SHA256SUMS) | — | Integrity ledger for the **full** 363-file packet (incl. the binaries below). The six text reports above re-verify against it. |
| [`PACKET-README.md`](PACKET-README.md) | — | Codex's original packet README. |

## What's deliberately **not** committed (binaries — out of git by policy)
The full packet (~77 MB, delivered as 5 ZIP parts) also contains the two complete CoreELEC images
(`release.img.gz`, `nightly-new.img.gz`), extracted recovery initramfs, compiled/decompiled donor DTBs,
`KERNEL.IMG`, host `.deb` utilities, and the PQ donor `.cpp` sources. These are public reference material and
firmware blobs; per the repo's no-firmware-redistribution rule they are **not** stored in the repo. Their
exact URLs, sizes and SHA-256 are all in `COFFEY-PUBLIC-ARTIFACT-MANIFEST.md`, so anyone can re-fetch and
re-verify them against `SHA256SUMS`.

## Bottom line
These resolve **public-artifact / comparator** questions only. **No coffey acceptance, root, parser-input
control, or authorization gap is established.** The decisive next step is unchanged and device-side: Adam's
coffey OTA capture → hash/extract → build-specific boot-dispatch/verification map. Do **not** boot the donor
recovery as a substitute — the recovery audit shows it mutates persistent state.
