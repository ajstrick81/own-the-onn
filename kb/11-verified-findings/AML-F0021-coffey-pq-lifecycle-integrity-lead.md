---
finding_id: AML-F0021
title: "coffey system_control exposes factorySetParamsDefault — an HIDL-reachable method that unlinks + reopens the writable PQ DB (conditional integrity op; no arbitrary-content injection)"
component: security
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: probable
source_refs:
  - AML-S0005
  - AML-S0010
source_urls: []
source_revision: "libpqcontrol.so sha256 4849d618…cc1fa + systemcontrol sha256 aec8998d…c8c1a4 (OTA URO4.260304.011.B1, AML-S0005); FactorySetParamsDefault 0x598f0 + CFile::copyTo 0x6b168 re-disassembled in-image (arm-linux-gnueabihf-objdump 2.46); dispatch chain + compiled-policy grants from Codex evidence JSONs (same hashes)"
related_findings:
  - AML-F0018
  - AML-F0020
status: reviewed
---

# coffey factorySetParamsDefault = HIDL-reachable PQ-DB reset (integrity lead, re-verified in-image)

## Observations
1. **Reachable mutate method.** `factorySetParamsDefault` is a shipped named
   handler at 0x80cd8 in `systemcontrol`; registered-impl slot +0x2b0 → 0x2ec52
   → service wrapper 0x34088 → (via linker veneer) imported
   `FactorySetParamsDefault` in `libpqcontrol.so` at 0x598f0 (Codex
   `P5-pq-lifecycle-writer-evidence.json`, same binary hashes).
2. **The lifecycle op (re-disassembled in-image).** `FactorySetParamsDefault`
   (0x598f0, libpqcontrol `4849d618…`) calls `CPQdb::closePqDB` (0x5999c), then
   **`unlink`** (0x59952 and 0x599b8), then `CPQdb::openPqDB` (0x59a04); the
   `/mnt/vendor/param/pq/pq.db` literal is in rodata. The non-separate-database
   branch unlinks the param copy then `GetPqdbPath`+`openPqDB` (recreating it
   from the read-only source per AML-F0018); the separate-database branch handles
   overscan. **The method takes no source-path argument** — no caller-chosen DB
   contents.
   **Branch selection (O3, in-house-confirmed literals):** the branch is a boolean
   at impl object +0xc set by `SetFlagByCfg` (libpqcontrol 0x471f0) from config
   `[PQ] pq.BigSmallDb.en` (literal present in libpqcontrol) with fallback
   `disable`; the packaged `pq_default.ini` sets `pq.BigSmallDb.en=disable`
   (Codex image-read). `disable` ⇒ the **non-separate branch** — i.e. the **unlink
   branch is the one selected under packaged config** (it is *not* gated off).
   The method must still be called and init must succeed.
3. **Writer flags (in-image).** `CFile::copyTo` (0x6b168) opens the destination
   `movs r1,#0x41` = **O_WRONLY|O_CREAT**, `mov r2,#0x180` = **mode 0600**,
   fsyncs, closes — **no O_TRUNC**. New file ownership = creator's creds (the
   service runs as root per init); an existing dest keeps its metadata.
4. **No caller gate.** Consistent with AML-F0020, `systemcontrol` imports no
   caller-identity primitive, so this method inherits no UID/permission check;
   guards present are transport/object(null)/feature/argument only.
5. **Policy supports the write (candidate).** Compiled candidate policy grants
   the `system_control` domain `param_tv_file` create/open/read/write/unlink and
   directory add_name/remove_name/search; app domains have service find +
   binder-call grants (per AML-F0020).

## Interpretation
There is a shipped, HIDL-exposed method that, if reachable and dispatched at
runtime, **resets** the device's persistent PQ database (unlink + recreate from
the packaged read-only source) — an **integrity/availability** operation, not a
confidentiality one and not arbitrary-content injection. Combined with F0020's
confirmed absent caller check and the candidate policy's `param_tv_file` write
grants, this is a concrete **integrity lead** on top of the earlier read-path
disclosure lead.

## Alternative explanations / open caveats
Static only. Not shown: that an untrusted app's call actually reaches this impl
at runtime (live policy selection per F0020, method dispatch, object
initialization), that the unlink branch is taken (operation-success/feature
guards), live labels/DAC on `/mnt/vendor/param/pq/`, and any user-visible effect.
The op cannot inject attacker-chosen DB bytes — it recreates from the packaged
source — so impact is reset/overwrite-to-default, not content control. No
mutation was attempted.

## Validation needed
Static (offline): trace the feature/branch guards in `FactorySetParamsDefault`
to see what makes the unlink branch execute; check whether any *other*
untrusted-callable method influences the `GetPqdbPath` source selection (would
upgrade reset → content control). Device-gated (separate Director-approved
plan): none proposed here — a mutation test is out of scope until the read-side
and live-policy questions are settled. Security-sensitive, Director-gated (cf.
AML-D0002); relay coordination-only.
