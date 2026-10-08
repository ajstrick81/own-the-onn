# 10 — Source Library

The source registry: every GitHub project, datasheet, CVE record, writeup, or
primary observation we cite. One file per source (`AML-S####`) in `sources/`,
using `../_templates/source.md`.

Findings reference sources by id (`source_refs: [AML-S0001]`), so a claim's
provenance is always one hop away and the validator can confirm the reference
resolves.

**Credibility is a required field:**
- `primary` — the actual code/config/datasheet, or a reproducible observation.
- `secondary` — a maintainer/researcher writeup of primary material.
- `tertiary` — an aggregator/news/forum summary (useful as a lead, never as
  the sole backing for a `confirmed` finding).
