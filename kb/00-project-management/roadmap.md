# Roadmap — Amlogic Architecture & Onn Reverse Engineering

## Theory
Amlogic reuses hardware blocks, driver frameworks, bootloader components, and
software interfaces across SoC generations. Architectural similarity does
**not** guarantee binary compatibility or identical security behavior.
Comparing generations — and localizing exactly where they diverge — is the
engine of this project. The Onn 4K Plus ("coffey", S905X5M / S7D) is the
primary experimental target; other generations are reference material.

## Research strategy
Find the stable interfaces first (kernel ABI, Android HAL/vendor-interface
contracts), then study the implementations behind them. A failed
cross-generation experiment is valuable when it tells us *precisely which
assumption was wrong* — record where execution stopped, what was accepted,
and what was rejected.

## Structure
Sections `00`–`11` (see each section README). Records are Markdown +
restricted-YAML frontmatter: findings `AML-F####`, experiments `AML-E####`,
decisions `AML-D####`, sources `AML-S####`. `python kb/tools/validate.py`
checks IDs, required fields, vocabularies, and cross-references.

## Evidence standards
Confidence: `confirmed` · `probable` · `inferred` · `unknown`.
Scope: `exact-device` · `exact-soc` · `related-family` · `general`.
Never silently upgrade an unverified claim; something confirmed on a sibling
chip is not confirmed on coffey. Preserve contradictions and failed
experiments. Prefer read-only experiments.

## Phase 1 — Research Foundation (current)
Completion checklist:

- [x] Repository structure established (`kb/` 00–11)
- [x] Research templates created (`kb/_templates/`)
- [x] Evidence and source standards documented
- [x] Device inventory template available (+ coffey entry `AML-F0001`)
- [x] Record validation implemented (`kb/tools/validate.py`)
- [ ] Implementation reviewed (coordinator review pending)
- [ ] First real research findings entered (coffey inventory + sources seeded;
      more to follow from triaged research inputs)

## Ground rules (inherited from the repo)
Owner's own hardware. Local-first. No working exploits, no weaponized
primitives, no redistribution of vendor code or firmware, no personal data.
Memory-safety work is attack-*surface* analysis and reproduction/patch
validation, done in an emulator — not against a device.
