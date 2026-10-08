# AML-TASK-001 — Implementation Report

**Phase:** 1 — Research Foundation
**Deliverable:** maintainable, Git-friendly Amlogic research knowledge base,
built as a `kb/` subtree in the public `own-the-onn` repo (per decision
`AML-D0001`).
**Branch:** `feat/aml-kb-scaffold` (not pushed — held for coordinator/director review).

## What was built

- **Sections 00–11** created, each with a README stating its purpose and the
  record type it holds.
- **Templates** (`_templates/`): finding, experiment, decision, source,
  device-inventory, and a cross-generation compatibility matrix.
- **Source registry** (`10-source-library/sources/`): per-source records
  `AML-S####` with url / repo / commit / files / credibility / scope.
- **Record validation** (`tools/validate.py` + `tools/kbrecord.py`):
  stdlib-only; checks ID format + uniqueness, required fields, controlled
  vocabularies, the "confirmed must cite a source" rule, and cross-reference
  resolution. Exit 0 clean / 1 on error; warnings never fail.
- **README** (`kb/README.md`) with structure, record rules, evidence
  standards, and a contribution flow.
- **Originals preserved separately** (`research-inputs/`), explicitly *not
  evidence*.
- **Seed records:** real — `AML-S0001` (coffey on-device id), `AML-S0002`
  (CoreELEC common_drivers tree, scoped `related-family`), `AML-F0001`
  (coffey device inventory, from already-public facts), `AML-D0001` (this
  home/boundary decision). Illustrative — `AML-E9001`, `AML-F9001` (the
  `9xxx` range is reserved for examples).

## Validation status

`python kb/tools/validate.py` → **6 records, 0 errors, 0 warnings.**
Negative-tested: bad ID format, out-of-vocabulary scope, and a dangling
`source_refs` id are all caught with exit 1.

## Design decisions made (and why)

1. **Markdown + restricted-YAML frontmatter, one parser, zero dependencies.**
   The repo's Python has no PyYAML. Rather than add a dependency, records use
   a top-level-keys-only subset (scalars, flow lists, block lists) parsed by
   `kbrecord.py`. Keeps `validate.py` runnable on a stock Python 3.
2. **Source registry as per-file records, not one big YAML.** Better git
   diffs/history, and it reuses the same parser and the same cross-reference
   check findings use.
3. **`kb/` subtree, existing layout untouched.** Preserves the privacy study
   and `root-study.md` and their links; infrastructure is public while
   sensitive material stays gated (`AML-D0001`).
4. **`9xxx` id range reserved for illustrative records** so examples never
   collide with real numbering and are obviously examples.

## Unresolved / for coordinator + director review

1. **Confidence granularity.** Frontmatter `confidence` is one value per
   record, but device-inventory and matrices are naturally *per-field*. Current
   approach: per-field confidence in the body table, record-level confidence =
   the record's overall standing. Is that the convention we want, or should
   multi-fact records be split into atomic findings?
2. **Validator strictness on `confirmed` + non-device scope.** Currently a
   **warning**, not an error. Keep it a warning (flag, don't block) or
   promote to an error?
3. **GhostLock entry.** Deferred by `AML-D0001`. Open question for the
   director: publish a reproduction + patch-validation case study (exploitation
   steps excluded), or keep all GhostLock material private? This needs a
   decision before any GhostLock record is written here.
4. **Production-source equivalence is unproven and must stay visible.**
   `AML-S0002` is deliberately `related-family`, not `exact-device`: the
   CoreELEC tree is a stand-in, not coffey's signed vendor kernel. Any future
   finding leaning on sandbox results must carry that scope until equivalence
   is established. Flagging so it is not quietly upgraded.
5. **CI hook (optional).** Should `validate.py` run in CI on PRs to the repo?
   Low effort; would keep records honest as contributors are added.
6. **`research-inputs/` and `.gitignore`.** Raw inputs with identifiers should
   stay out of the repo entirely. Confirm whether `S7DResearch.txt` and prior
   dumps are safe to commit as-is or need stripping first.

## Next (pending review)
- Triage research inputs into registered sources + draft findings.
- Director decision on items 2 and 3; coordinator review of item 1.
