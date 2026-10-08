# Cross-generation compatibility matrix (template)

Compare SoC generations across the six research areas. One matrix per
question; add columns as generations are studied. Every cell carries a
**confidence** tag so an inference on one chip is never silently read as a
fact on another.

Confidence tags: `C` confirmed · `P` probable · `I` inferred · `U` unknown.

## Example: boot-container / verified-boot

| Aspect | S905X4 (prior gen) | S905X5M / S7D (coffey) | Notes |
|---|---|---|---|
| Boot image container | `U` | `U` | |
| BL2 / DDR-init stage | `U` | `U` | |
| U-Boot `lock` env mechanism | `U` | `I` | |
| AVB / verified-boot policy | `U` | `C` locked | |
| Rollback protection | `U` | `U` | |

## How to use
1. Copy a table, retitle it for one question (e.g. "epoll LPE applicability").
2. Fill cells with a short value **plus** a confidence tag.
3. For any `C`/`P` cell, cite the finding (`AML-F####`) that backs it in Notes.
4. Differences between columns are findings too — record them, don't just tabulate.
