---
decision_id: AML-D0002
title: "Coordinator decisions on Phase 1 review (AML-TASK-001)"
question: "How should the validator strictness, finding granularity, GhostLock publication, and CoreELEC-vs-production distinction be resolved for Phase 1?"
status: decided
decision: "Warning (not error) for confirmed+non-device scope; prefer atomic findings; GhostLock stays private pending a separate Director decision; keep CoreELEC and production-Onn findings distinct."
supporting_evidence:
  - AML-D0001
revisit_if:
  - "Director reviews GhostLock provenance + disclosure and decides on publication."
---

# AML-D0002 — Coordinator decisions on Phase 1 review

## Question
On reviewing AML-TASK-001, four open questions needed rulings: validator
strictness, finding granularity, GhostLock publication, and the
CoreELEC-vs-production distinction.

## Options considered
See the implementation report's "unresolved" list and the 2026-10-08
coordinator response.

## Decision
1. **Validator strictness** — keep `confirmed` + non-device-scope a **warning**.
   Confirmation is always interpreted within the declared evidence scope.
2. **Granularity** — prefer **atomic findings** for significant technical
   claims; retain per-field confidence in composite inventories/matrices.
3. **GhostLock** — keep materials **private** for now. Publication requires a
   separate Director decision after provenance and disclosure review.
4. **CoreELEC vs production** — preserve the distinction between CoreELEC
   research findings and verified production-Onn findings (enforced via source
   scope: CoreELEC = `related-family`, device readouts = `exact-device`).

## Rationale
These keep the KB honest about scope without over-blocking early research, and
hold the line between reproduction/patch-validation work and any publication or
exploitation step. The exact-device evidence rule (AML-TASK-002) mechanizes
decision 4 so a non-device source cannot silently back a device-scope claim.
