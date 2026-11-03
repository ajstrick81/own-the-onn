# Reviewer notes — public-lookups addendum

Reviewer: Claude, 2026-11-03. Cross-check of the five addendum reports for accuracy and thoroughness. The
reports were first confirmed **byte-identical** to the author's re-uploaded originals (all five match
`COFFEY-PUBLIC-LOOKUPS-SHA256SUMS.txt`). This file is a separate review layer and is deliberately **not**
covered by that sums file, so the original reports stay hash-consistent.

**Overall:** accurate, P/R/B/H/U labels correctly applied, no coffey overreach — every coffey cell is properly
`U`/`B`. Three follow-ups:

## R1 — PQ-AD14 negative result is not fully bounded (open gap → re-sweep queued)
`COFFEY-PQ-ANCHORS-AD14-DELTA.md` names only the **Pie** branch of
`Amlogic-Lineage/android_vendor_amlogic_common_frameworks` plus two unrelated old trees. The most likely home
of a newer `CPQControl` is a **newer branch of that same repo** (android-11/12/13, or `r`/`s`/`t`-named
branches); the report doesn't state it swept those. Also un-checked: **AOSP Amlogic reference boards**
(`yukawa`/`sei610`) and **ROM-dump mirrors** (dumpyara-style) that carry recent `systemcontrol`. Read the
conclusion as "not found in the sources searched," not "public sweep exhausted." A tightly-scoped re-sweep of
these three avenues is queued before Phase F's donor search is treated as closed.

## R2 — jarvis2 citation URL differs from the source of record
`COFFEY-BOOT-CHAIN-MODEL.md` cites the GhostLock write-up at
`hack.ec/posts/2026-10-27-adb-to-root-on-a-locked-android-tv/`; the source originally supplied for this study
is `acheronsec.com/research/adb-to-root-on-a-locked-android-tv/`. Same slug and date — almost certainly a
mirror/alias of the same article, but the provenance should be reconciled and one canonical URL chosen. (The
rest of that report is sound: Amlogic BL2/ARB is correctly kept separate from Android AVB rollback, and the
TL1 signer is correctly marked a G12-era comparator, not S7D.)

## R3 — darkknight "MAX" detail also carries a positive signal
`COFFEY-DARKKNIGHT-OTA-RECON.md` frames OS3.0.2.0 as a naming conflict needing corroboration (correct). Worth
noting the same detail cuts partly *toward* darkknight: the OS3.0.2.0 owner report carries **`device=darkknight`
and system model `MiTV-AZFU0`** — the same codename and system model as the Box 5 (`MOB2MB-5P`) comparator. The
likeliest reading is "same darkknight software family, marketing label (`MAX`) possibly mis-stated by the
owner," not "different product." Status stays `U`/`R` (no fingerprint or package), but the shared `MiTV-AZFU0`
is mild evidence *for* applicability, not only against it.

## No action needed on
- `COFFEY-CE-GENERIC-BARRIER-MATRIX.md` — clean decomposition; `twilight`/`MiTV-AFMU0` (Box S 3rd Gen) vs
  `darkknight`/`MiTV-AZFU0` (Box 5) is internally consistent across all reports.
- Image hashes (`21fc5199…`, `d2af9209…`) — match the packet manifest.
