---
decision_id: AML-D0003
title: "Scope of the Amlogic generational-reuse hypothesis"
question: "How far does hardware/software architecture reuse carry across Onn generations, and what does that reuse let us conclude about shared security behavior?"
status: decided
decision: "Related Amlogic Onn generations reuse substantial hardware and vendor-software architecture while preserving Android interfaces. That reuse guides comparisons; shared security behavior and bugs require separate evidence."
supporting_evidence:
  - AML-F0007
  - AML-F0011
  - AML-F0012
  - AML-F0015
revisit_if:
  - "A related Amlogic generation shows a different reset/clock index map for shared block names."
  - "A vendor framework binding fails to trace back to a common Amlogic ancestor."
  - "The Realtek-based Onn lineage (e.g. the Wayne stick) is traced to a primary source, enabling a cross-vendor comparison."
---

# AML-D0003 — Scope of the Amlogic generational-reuse hypothesis

## Question
The Director's hypothesis: most Onn chips are similar because of design
complexity, mass production, and the need for cross-generation Android
compatibility. How far does that hold, and what does inherited architecture
let us infer about shared vulnerabilities?

## Options considered
- **Broad form** — "most Onn chips are similar." Rejected: scope exceeds our
  comparisons (only S7D↔SC2 is rigorous) and spans more than one silicon
  vendor, where register-map inheritance is unlikely.
- **Over-narrow form** — "the vendor stack does not inherit." Rejected: this
  discards AML-F0007 (S7D inherits SC2 reset/wdt bindings), which is itself
  vendor-layer inheritance.
- **Refined form (adopted)** — Amlogic-family reuse of hardware and vendor
  *frameworks*, with generation-specific *implementations* behind stable
  Android interfaces; reuse as a research heuristic, not proof of shared bugs.

## Decision
Record the refined form (see front matter). Three claims are deliberately
separated so none is overstated:
1. **Hardware register-map / DT-binding reuse** — strong, device-evidenced.
2. **Vendor-software architecture** — frameworks inherit; implementations
   diverge. The security-relevant delta lives in the implementations.
3. **Android interfaces (HAL/GKI)** — preserved by design; relevant to
   comparing reachability, dependencies, and patch applicability, but not a
   guarantee of safety.

Scope boundary: **Amlogic family only.** Cross-vendor register inheritance is
unlikely; software-layer similarity may still exist. The Realtek Onn lineage
stays `unverified` pending a primary source.

## Rationale
Reuse is real and device-confirmed: AML-F0007 (binding inheritance),
AML-F0015 (57 shared reset names at identical indices — inheritance *with*
in-place edits, i.e. "frameworks inherit, implementations diverge" in one
record), and AML-F0011 / AML-F0012 (coffey runs the vendor driver stack, not
mainline). This is why reuse is a legitimate shortcut for guiding comparisons.

Reuse does not imply shared bugs. GhostLock (CVE-2026-43499, source-confirmed
on coffey .196, kept private per AML-D0002) is the worked counter-example in
both directions: it sits in the shared/GKI-adjacent rtmutex/futex-PI core —
so stable interfaces *are* security-relevant — yet its presence on any other
generation would still require separate per-device confirmation. Stable
interfaces also do not make the shared kernel vulnerability-free.

The falsifiers above make this a testable hypothesis rather than a posture:
a divergent index map for shared block names, or a vendor binding without a
common ancestor, would break the reuse claim at the hardware layer.
