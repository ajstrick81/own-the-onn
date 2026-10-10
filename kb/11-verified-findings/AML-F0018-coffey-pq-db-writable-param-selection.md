---
finding_id: AML-F0018
title: "coffey PQ database selection prefers a non-empty writable copy at /mnt/vendor/param/pq/pq.db (shipped libpqcontrol.so GetPqdbPath)"
component: display-pq
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0010
source_urls:
  - "https://github.com/khadas/android_vendor_amlogic_common/blob/992853c992d9206c3c0aedbb44415b0777155661/frameworks/services/systemcontrol/PQ/utils/CConfigFile.cpp#L418"
source_revision: "libpqcontrol.so sha256 4849d618…cc1fa from OTA URO4.260304.011.B1 (AML-S0005); symbol/strings/import-table re-verified in-image"
related_findings:
  - AML-F0020
status: promoted
---

# coffey PQ DB selection prefers writable /mnt/vendor/param copy (Codex finding, re-verified in-image)

## Observations
Shipped `vendor/lib/libpqcontrol.so` (sha256 `4849d618…cc1fa`, from OTA
URO4.260304.011.B1) exports `CConfigFile::GetPqdbPath(char*)`
(`_ZN11CConfigFile11GetPqdbPathEPc`) at virtual address **0x6bea8**, size
**824 bytes** — reproduced in-image via `readelf -s`.

The four PQ path literals are present in loadable rodata (verified with
`strings`): `/mnt/vendor/param/pq/pq.db` (referenced **twice**),
`/mnt/vendor/odm_ext/etc/tvconfig/pq/pq.db`, `/odm/etc/tvconfig/pq/pq.db`, and
the config key `pq_db_path`. The function's relocation-backed PLT import table
(Codex `pq-path-selection-binary-evidence.json`) resolves `stat`,
`CConfigFile::GetString`, `CFile::copyTo`, and `CFile` ctor/dtor.

Per the resolved flow (Codex annotated disasm against this binary; instruction
addresses in that artifact): `GetPqdbPath` `stat()`s `/mnt/vendor/param/pq/pq.db`
and, on a positive-size result, returns that path directly; otherwise it reads
config `[PQ] pq_db_path` (default `/mnt/vendor/odm_ext/...`), falls back to
`/odm/etc/tvconfig/pq/pq.db`, and `CFile::copyTo`s a usable source into
`/mnt/vendor/param/pq/pq.db` before returning it.

Shipped SELinux `vendor_file_contexts` labels `/mnt/vendor/param(/.*)?` and
`/mnt/vendor/odm_ext(/.*)?` both `param_tv_file` (AML-S0005, in-image).

## Interpretation
The persistent writable copy at `/mnt/vendor/param/pq/pq.db` is a real,
preferred node in the shipped selection path — not merely a string. A populated
param copy short-circuits the odm/odm_ext read-only sources.

## Alternative explanations
Returning a path does not prove the param file exists on any given device, that
the copy succeeded, or what its contents are; missing-source/copy-error branches
log and still return a path. The `param_tv_file` label is shared by read-only
odm_ext assets and the writable param state, so the label alone does not
establish who may write the param copy.

## Image-level metadata (packaged sources)
Codex read-only mounts of the OTA images (`packaged-pq-file-metadata.json`):
`/odm_ext/etc/tvconfig/pq/pq.db` = 1,421,312 B, UID/GID 0:0, mode 0644, actual
image xattr `u:object_r:param_tv_file:s0`; `pq_default.ini` = 2,496 B, 0:0, 0644,
same label. No alternate `pq.db` in ODM. These confirm the read-only source the
selection falls back to is a **benign, public config file** the `system_control`
domain may read (ties the F0020 read-disclosure ceiling to non-sensitive PQ data,
not keys). (Image-level labels/DAC; not re-mounted independently here.)

## Validation needed
The **writable** `/mnt/vendor/param/pq/pq.db` copy preferred by `GetPqdbPath` is
**not** supplied by these images, so its live content, owner, label, and mode
remain unknown. Device-gated (separate read-only plan): confirm whether
`/mnt/vendor/param/pq/` is populated and its DAC/MAC write permissions; determine
which process/context performs the `copyTo` and whether any lower-privileged path
can influence the source or the param contents. Ties to AML-F0020 (does
`system_control` expose a PQ-DB mutation reachable without a caller check).
