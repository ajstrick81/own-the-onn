---
finding_id: AML-F0000
title: ""
component: ""
device_model: ""
soc: ""
generation: ""
evidence_scope: unknown        # exact-device | exact-soc | related-family | general
confidence: unknown            # confirmed | probable | inferred | unknown
source_refs: []                # AML-S#### ids from 10-source-library
source_urls: []                # raw URLs if no registered source yet
source_revision: ""            # commit hash / build id the claim was read from
related_findings: []           # AML-F#### ids
status: draft                  # draft | reviewed | promoted
---

# <finding_id> — <title>

## Observations
<What was actually seen: the exact code, config line, log, or measurement.
Quote primary sources; do not paraphrase a claim into a fact.>

## Interpretation
<What the observations mean. State the strongest supported conclusion only.>

## Alternative explanations
<Other things that could produce the same observation. If none, say why.>

## Validation needed
<Concrete, preferably read-only, steps that would raise confidence or settle
the scope. This is what turns `inferred`/`probable` into `confirmed`.>
