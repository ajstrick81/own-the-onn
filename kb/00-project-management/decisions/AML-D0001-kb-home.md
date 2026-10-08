---
decision_id: AML-D0001
title: "Knowledge-base home and GhostLock publication boundary"
question: "Where does the Amlogic KB live, and how is memory-safety (GhostLock) material handled given the repo is public?"
status: decided
decision: "Build the KB as a kb/ subtree inside the public own-the-onn repo; defer any GhostLock content pending review."
supporting_evidence: []
revisit_if:
  - "The project decides to publish a GhostLock reproduction/patch-validation case study."
  - "The KB outgrows a subtree and warrants its own repo."
---

# AML-D0001 — Knowledge-base home and GhostLock publication boundary

## Question
Where should the Amlogic architecture knowledge base live, and how should
memory-safety research (the GhostLock / CVE-2026-43499 Option A work) be
handled, given `own-the-onn` is a public repository with explicit ground
rules (no working exploits, no vendor code/firmware redistribution, no
personal data)?

## Options considered
- **kb/ subtree in own-the-onn (chosen).** Self-contained subtree; existing
  privacy study and `root-study.md` untouched. Infrastructure is public;
  sensitive content is gated per the repo's ground rules.
- **New private repo.** Most conservative; nothing public. Rejected for the
  scaffold — the infrastructure is harmless and the repo already models the
  right posture — but remains available for sensitive working material.
- **Restructure own-the-onn into the 00–11 scheme.** Cleanest single
  structure but churns the existing public layout and breaks links. Rejected.

## Decision
KB lives at `kb/` inside `own-the-onn`. The AML-TASK-001 scaffold
(templates, source registry, validation, section READMEs, illustrative and
already-public seed records) is committed publicly. GhostLock Option A
content is **deferred**: the reproduction + patch-validation story is a
candidate for a future public case study, but the exploitation-direction
material (stack re-groom, futex re-entrancy aliasing) stays out of the public
repo and in the private working area regardless.

## Rationale
The existing repo already enforces the posture the roadmap's evidence
standards formalize. A subtree preserves that work, keeps one source of
truth, and lets harmless infrastructure be public while sensitive material
stays gated — consistent with "you own the glass," analysis not weaponization.
