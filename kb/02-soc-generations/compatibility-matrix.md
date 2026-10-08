# Cross-generation compatibility matrices (working)

Seeded from `../_templates/compatibility-matrix.md`. One matrix per question;
every cell carries a confidence tag so an inference on one chip is never read
as a fact on another.

Confidence tags: `C` confirmed · `P` probable · `I` inferred · `U` unknown.
For any `C`/`P` cell, cite the backing finding (`AML-F####`) in Notes.

## Boot / verified-boot

| Aspect | prior gen (e.g. S905X4) | S905X5M / S7D (coffey) | Notes |
|---|---|---|---|
| Boot image container | `U` | `U` | |
| U-Boot `lock` env mechanism | `U` | `I` | 8-field bitfield via SystemControl get/setBootEnv (root-study, analysis) |
| AVB / verified-boot policy | `U` | `C` locked | AML-F0001; OEM-unlock disabled, AVB green |
| Rollback protection | `U` | `U` | |

## Kernel LPE class applicability

| Aspect | general ARM64 5.15 | coffey 5.15.196 | Notes |
|---|---|---|---|
| unprivileged user namespaces | varies | `I` disabled | config, per root-study; confirm with AML-S0001 |
| nftables LPE surface | varies | `I` absent | per root-study; confirm against config |
| io_uring / userfaultfd / perf | varies | `I` present | per root-study; confirm against config |

> These cells are seeded from the published `root-study.md` narrative and are
> marked `I`/`P` pending promotion to confidence-tagged findings in
> `11-verified-findings/` with a cited source revision. Do not read them as
> `confirmed` until that promotion happens.
