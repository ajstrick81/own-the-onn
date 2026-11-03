# Tasks for Codex — coffey boot-policy track

**Context:** Continue the boot-policy / alternate-OS investigation framed in
[`boot-policy-track.md`](boot-policy-track.md). All work is **host-side, read-only, offline analysis of public
artifacts**. No device access, no flashing, no script execution, no live boot. Produce the deliverables named
in each task with pinned revisions and SHA-256 for every artifact. **A documented enforcement boundary is a
valid result — do not manufacture a bypass.**

**Evidence discipline:** keep the P/R/B/H/U classification (see `boot-policy-track.md` §1). A different URL is
not independent confirmation. Similar strings/symbols are leads; build-specific control flow decides
applicability. Do not import donor offsets, keys, DTB, or images into any coffey conclusion.

**Suggested order:** Task 2 first — it is the only task that yields a complete deliverable with zero
dependencies. Task 1 runs alongside it (it supplies 2's input). Then 3/4/5 as the public donor set lands.

## Task 1 — Acquire & pin the public artifact set (no device needed)
Download and record (URL, date, SHA-256, source commit/branch) for:
- One official CoreELEC release **and** one nightly for the closest S905X5M / S7D generic target.
- The `darkknight` (Xiaomi Box 5, MOB2MB-5P, S905X5M) firmware/OTA from N1/N2, if a provenance-backed copy is
  reachable.
- Upstream `amlogic-s7d.dtsi` at a pinned commit (S5) and the S7D BM202 patch (S4).
- The G12B U-Boot config at its pinned commit (S1) and the U-Boot `source`/`env` docs (S2/S3).

**Deliverable:** `COFFEY-PUBLIC-ARTIFACT-MANIFEST.md` — one row per artifact with hash, provenance, and what it
is a comparator *for*. Flag anything that could not be retrieved rather than omitting it.

## Task 2 — Audit the CoreELEC recovery image (Phase C)
Inspect the downloaded CoreELEC release **without booting it or running its scripts**. Determine: image
format, kernel, initramfs contents, entry scripts, environment backend, and **every persistent write** — raw
writes, mounts, env migration (`fw_setenv`), partition-metadata changes, reboot flags. Trace normal **and**
error paths, not just a `fw_setenv` grep. Correlate behavior with the official build recipe; do not assume the
current source branch equals the downloaded artifact.

**Deliverable:** `COFFEY-CE-RECOVERY-AUDIT.md` — side-effect inventory + a verdict on whether this installer
*could* fit a read-only boundary (hypothetically; still not authorized to run on coffey).

## Task 3 — Upstream vs vendor DT comparison skeleton (Phase D, donor half)
Build the semantic diff **table structure** comparing upstream S7D DT (S5) and the CoreELEC/Xiaomi/Ugoos S7D
references against the recorded coffey vendor-DT baseline (`boot-policy-track.md` §2). Fields: root compatible/
model + includes; phys/usable/reserved memory; UART compatible/clocks/IRQs/enabled; PSCI declaration +
firmware assumptions; USB controller/PHY/role; storage + partition metadata; GPU/video/secure-memory deps.
Fill the donor/upstream columns now; leave the coffey column as the recorded baseline, marked
**B — pending artifact**.

**Deliverable:** `COFFEY-DTB-COMPARISON.md` — populated for public sources, explicit `U`/`pending` where
coffey's own DT is needed. **Do not** claim coffey can boot any of these.

## Task 4 — PQ source-anchor map (Phase F prep, donor half)
Using the N5 anchors (preserve the `MOUDLE` spelling): `CFG_ALL_PQ_MOUDLE_ENABLE`, `mPQConfigFile->GetString`,
`mPQdb`, `mSSMAction->SSMReadDnlpMode`, `CPQControl::LoadPQSettings`, `CPQControl::SetBacklight`, and the
`factorySetParamsDefault` / `getPQDatabaseInfo` method names — collect candidate reference implementations from
public sources and map the string/symbol → function → call-relationship structure. Mark every edge as **lead
only** until it can be cross-checked against coffey's matching ELF.

**Deliverable:** `COFFEY-PQ-ANCHORS.md` — symbol/string catalog with public-source call relationships and a
column for "coffey ELF offset — pending."

## Task 5 — Donor prerequisite matrix (N3/N4/N6/S7)
Tabulate each alternate-OS / odm_ext / unlock report by the prerequisites it *actually assumes*: root-capable
adbd · unlocked bootloader · already-working external boot · debug build. Make explicit which reports are
**not** locked-device bypasses (expected: all of them).

**Deliverable:** `COFFEY-DONOR-PREREQS.md`. For N6's `Unlock_Bootloader.cmd`: document its contents and
prerequisites from inspection **only — do not run it or any bundled executable.**

## Explicitly out of scope for Codex
- **Capturing coffey's own OTA / bootloader / DTB / `systemcontrol` ELF** — that requires the physical device
  (OTACaptor URL capture → `payload_dumper`) and is Adam's step. Codex cannot source these.
- Anything device-side: flashing, env edits, slot changes, PQ resets, booting recovery media, invoking any
  HIDL method.
- Promising unbrickability or a working CoreELEC port.

## Return format
For each finding: `ID · claim · target build · artifact SHA-256 · source revision · file+offset/line ·
observation · interpretation · competing explanations · next discriminating check.` Plus a one-paragraph relay
summary: what is now resolved, what only improved a comparator, and the single most informative next step.
