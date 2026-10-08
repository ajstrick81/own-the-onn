# kb — Amlogic Architecture Knowledge Base

A maintainable, Git-friendly research knowledge base for systematic study of
Amlogic-based Android TV devices, with the Walmart onn 4K Plus ("coffey",
S905X5M / S7D) as the primary experimental target. It sits alongside the
[privacy study](../README.md) and [root & firmware research](../research/root-study.md)
and follows the same ground rules: owner's own hardware, local-first, **no
working exploits, no vendor code/firmware redistribution, no personal data.**

See [`00-project-management/roadmap.md`](00-project-management/roadmap.md) for
the theory and phase plan.

## Structure

| Section | Purpose |
|---|---|
| `00-project-management` | Objectives, roadmap, decisions (`AML-D####`) |
| `01-device-inventory` | Exact models, SoCs, kernels, bootloader state |
| `02-soc-generations` | Amlogic family tree + cross-generation matrices |
| `03-hardware-architecture` | CPU, memory, buses, GPIO, clocks, interrupts |
| `04-boot-architecture` | Boot ROM, BL2, BL31, U-Boot, boot images, AVB |
| `05-security` | TrustZone, TEE, fuses, verified boot, SELinux |
| `06-android-linux` | Kernel, drivers, HALs, services, SELinux policy |
| `07-interfaces` | ADB, UART, USB, recovery, debug interfaces |
| `08-firmware` | Partitions, updates, extraction, image formats |
| `09-experiments` | Hypotheses, procedures, results (`AML-E####`) |
| `10-source-library` | Source registry (`AML-S####`) |
| `11-verified-findings` | Promoted, reviewed conclusions (`AML-F####`) |
| `_templates` | Record templates |
| `research-inputs` | Raw inputs, preserved separately — not evidence |
| `tools` | `validate.py` + `kbrecord.py` |

## Records

Every record is a Markdown file with a restricted-YAML frontmatter block
(top-level keys only; scalars and simple lists). IDs:

- `AML-F####` finding · `AML-E####` experiment · `AML-D####` decision ·
  `AML-S####` source. The `9xxx` range is reserved for illustrative examples.

Copy a template from `_templates/`, fill the frontmatter, write the body.
Findings cite sources by id (`source_refs: [AML-S0001]`).

### Evidence standards (enforced)

- **Confidence:** `confirmed` · `probable` · `inferred` · `unknown`.
- **Scope:** `exact-device` · `exact-soc` · `related-family` · `general`.
- A `confirmed` finding must cite a source. `confirmed` at `related-family`/
  `general` scope is flagged — confirm it is confirmed *for that scope*, not
  upgraded from another device.
- **Exact-device rule:** a finding with `evidence_scope: exact-device` must name
  a specific device (`device_model`) **and** be backed by a device-appropriate
  source. Source *existence* is not proof of device-scope support: a
  `confirmed`/`probable` exact-device claim must cite at least one source whose
  own `scope` is `exact-device` (an on-device observation counts). At
  `inferred`/`unknown` confidence this is a warning, not a block.
- **Prefer atomic findings** for significant technical claims (one claim per
  `AML-F####`). Keep per-field confidence only in composite records — device
  inventories and compatibility matrices.
- Preserve contradictions and failed experiments. Never silently upgrade.

## Validate

```bash
python kb/tools/validate.py
```

Checks ID format + uniqueness, required fields, controlled vocabularies, the
confirmed-needs-a-source rule, and that every cross-reference resolves. Exit
0 = clean, 1 = errors. Warnings never fail the run. No PyYAML or other
dependency required (stock Python 3).

## Contributing a finding

1. Settle the claim against a **primary** source; register it in
   `10-source-library/` if not already there.
2. Draft the finding in the relevant topic section (03–08) with honest
   confidence/scope and the alternative explanations.
3. Run `validate.py`.
4. Promote to `11-verified-findings/` (`status: promoted`) only after review.
