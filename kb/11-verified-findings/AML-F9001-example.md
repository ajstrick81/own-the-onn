---
finding_id: AML-F9001
title: "[ILLUSTRATIVE EXAMPLE] inherited IP block identified across two generations"
component: "[example] some-peripheral-controller"
device_model: "[example only]"
soc: "[example only]"
generation: "[example only]"
evidence_scope: related-family
confidence: inferred
source_refs:
  - AML-S0002
source_urls: []
source_revision: ""
related_findings: []
status: draft
---

# AML-F9001 — [ILLUSTRATIVE EXAMPLE] inherited IP block across generations

> **Clearly-labeled example record** showing the finding format and how
> confidence/scope/alternative-explanations are expressed. The `9xxx` id
> range is reserved for examples. This is not a real finding.

## Observations
<Example: the two Device Trees describe the same controller compatible string
and near-identical register offsets.>

## Interpretation
<Example: the peripheral IP block appears inherited between the two
generations.>

## Alternative explanations
<Example: identical DT nodes could be copy-paste boilerplate that does not
match silicon; a register map match in DT is not a silicon-level confirmation.>

## Validation needed
<Example: compare against the datasheet/register map, or a read-only MMIO
probe, before raising from `inferred` to `probable`/`confirmed`.>
