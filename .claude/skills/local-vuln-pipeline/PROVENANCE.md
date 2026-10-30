# Provenance: local-vuln-pipeline

This is a **methodology skill**, not vendored code. Upstream is a standalone
Python pipeline (GPU + llama.cpp + a 14B model); none of it is copied here. Only
the workflow/methodology was distilled into `SKILL.md`.

| | |
|---|---|
| Upstream | https://github.com/theteatoast/local-vuln-research-pipeline |
| Nature of upstream | Fully-local whitebox vuln-research pipeline: deterministic code graph for discovery, local 14B LLM for exploitability judgement only |
| What was taken | The methodology/step model (Steps 0–9, source/sink/sanitizer taint model, memory analyzers, networkx chain synthesis, prioritization heuristics) |
| What was NOT taken | All code, `config.yaml`, models, llama.cpp, NVD download tooling — no install, no GPU, no network |
| Adapted by | Rewritten as a Claude methodology skill scoped to the user's authorized GhostLock / Onn-root + firmware lanes; Claude plays the "exploitability judge" role the upstream 14B model plays |
| Added | 2026-10-30 |

## Why methodology-only

The user asked for a skill form (not a tool install). Upstream needs a 16GB GPU,
llama.cpp, and a 14B GGUF — not available/appropriate as an in-repo dependency.
The valuable, portable part is the **trace-first-judge-second** discipline and the
step ordering, which transfer directly to the GhostLock/libpng/system_control and
moria/mithril firmware work.

## If you ever want the real tool

Install it standalone outside this repo (e.g. `E:\Tools\lvrp`), per its README:
llama.cpp + Qwen2.5-Coder-14B GGUF + a 0.5B draft model, NVD API key, then
`python run_audit.py <repo> --resume`. Keep it out of this git tree (it's not
part of the morphe patches project). Review the upstream code before running it —
it executes Semgrep, downloads CVE data, and drives a local model.

## Updating

Re-read the upstream README, diff the step model against `SKILL.md`, and update
the methodology if the pipeline's ordering or analyzer set changed.
