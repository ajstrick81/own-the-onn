# Probe harness — design doc (NOT YET IMPLEMENTED)

> **Status: design only.** No probes or runner exist yet. This spec is deliberately written *before* the first
> coffey artifact capture so the shape can be reviewed; it will be built — minimally, seeded with real probes —
> once there is an artifact to run against. Building an empty harness first would be scaffolding with nothing to
> grade. See `STATUS.md` priority vector #1 (the capture that unblocks this).

Adapted from the probe→capture→ledger discipline of the PS5-14.10-Research repo, scaled down to this study. The
goal: make every analysis step **deterministic, re-runnable, and bound to its evidence**, so a finding cites a
probe + a raw capture (reproducible by anyone holding the hash-matched input) rather than prose + a URL.

## 1. Core loop

```
probe (deterministic script)  +  input artifact (named by SHA-256)
        │  run_probe.py
        ▼
capture (raw output, never hand-edited)  ──►  finding cites probe-id + capture-sha256
        │                                        in a report / STATUS.md
        ▼
verify_offline.py re-checks capture hashes (+ probe determinism where inputs are committed) in CI
```

A finding's provenance becomes `probe-id · input-artifact-sha256 · capture-sha256 · grade`, extending today's
`source-url · artifact-sha256` binding into something fully reproducible.

## 2. Two probe classes (this split drives everything)

| Class | Runs where | Input | CI story |
|---|---|---|---|
| **device** | maintainer's machine, against the live box (adb / network capture) | the physical onn | CI cannot run it; CI verifies the committed capture's hash only |
| **host** | any container, against an extracted artifact | a firmware blob (OTA/`vmlinux`/DTB/ELF), **by SHA-256** | CI re-verifies capture hashes; re-runs the probe only if its input is committed (text); full re-run is local when the blob is present |

This mirrors the PS5 repo's hardware-free vs. with-hardware split: `verify_offline.py` validates evidence
without the device; the full probe re-runs where the input exists.

**Firmware blobs stay out of git** (unchanged rule). A host probe's input is referenced by role + SHA-256; the
blob lives on the maintainer's disk / a scratch store, and the capture + hashes are what get committed.

## 3. Layout (when built)

```
probes/
  collection/     # device: package perms, SELinux contexts, mounts, props, /proc readability
  telemetry/      # device: network-capture scenarios A/Z/C/D/E/F
  boot-policy/     # host: boot-dispatch token grep, DTB diff, env-backend id   (track Phases B/D/E)
  pq-hidl/         # host: systemcontrol symbol + authorization probes          (track Phase F)
  kernel/          # host: rtmutex control-flow / CVE-2026-43499 check          (root-study D-bis)
results/          # raw captures, mirroring probes/, append-only, never edited
tools/
  run_probe.py        # run one probe vs a named artifact; write capture + provenance header
  run_probe_batch.py  # run a phase/dir; bounded, resumable
  verify_offline.py    # grows out of today's verify_hashes.py: capture-hash + determinism checks for CI
```

## 4. A probe

Self-contained, deterministic, side-effect-free on the input (read-only). Header declares its contract:

```
# id:        kernel/cve-2026-43499-rtmutex
# question:  does the futex PI requeue path use waiter->task (fixed) or current (vulnerable)?
# class:     host
# input:     coffey vmlinux  (extracted from boot.img; sha256 required, recorded in capture)
# emits:     json { grade, verdict: fixed|vulnerable|indeterminate, evidence_offset, build_id }
# grade:     P if control flow is conclusive; H if only build-id/patch-level inference
# refs:      research/.../COFFEY-R2-1-CVE-TIMELINE.md (the dated fix)
```

Rules for a probe:
- **Deterministic:** same input bytes → same capture (modulo a timestamp line). No network, no clock-dependent
  logic in the graded output.
- **Read-only on input, no device mutation.** Device-class probes never flash/boot/alter env (the repo's hard
  rule); they only read.
- **Self-describing grade logic:** the probe states when its result is `P` vs `H`, so grading isn't ad hoc.
- **Pinned tooling:** any external tool (dtc, erofs-utils, a disassembler) pinned by version in the probe header.

## 5. A capture

Raw stdout/artifact the probe emitted, plus a provenance header the runner prepends:

```
# probe:   kernel/cve-2026-43499-rtmutex @ <probe-file-sha256>
# input:   vmlinux sha256=<...>  role=coffey-kernel  build=URO4.260304.011.B1
# tool:    <pinned versions>
# run:     2026-11-xx utc  host=container
# ---
<raw output>
```

Captures are **append-only evidence** — never edited to "fix" a result; a re-run writes a new capture. A
colliding re-run (same probe+input, different output) is preserved, not overwritten — it's a signal.

## 6. Ledger binding

Extends the current `SHA256SUMS` discipline:
- `results/**` captures are hashed in a ledger like everything else.
- A **findings index** (`results/INDEX.md` or a `findings.json`) maps `finding-id → probe-id → capture-sha256 →
  grade`, and `STATUS.md` / report rows cite that id. A claim with no probe+capture behind it is prose, not a
  finding — flagged in review.
- `verify_offline.py` (CI) fails if a cited capture's hash drifts, or if a committed-input probe no longer
  reproduces its capture. This is the PS5 repo's enforced-evidence idea, on our smaller surface.

## 7. Seed set (first probes to write, once an artifact exists)

In priority order, each tied to an open `STATUS.md` vector:
1. `kernel/cve-2026-43499-rtmutex` — settles vector #2 (the GhostLock `H`).
2. `boot-policy/dispatch-tokens` — the Phase-B token grep (`update`, `recovery_from_*`, `get_avb_mode`, …) over
   the extracted bootloader/env, each hit classified active/dead/handler.
3. `pq-hidl/systemcontrol-auth` — symbol + caller-authorization enumeration of coffey's `systemcontrol` ELF vs
   the Pie donor (Phase F; settles whether the stubbed `permissionCheck` is coffey's reality).
4. `collection/selinux-contexts` — re-run the adb collection as a graded device probe.

## 8. When to build

Trigger: **the first coffey artifact capture lands** (OTA → extracted `vmlinux`/DTB/`systemcontrol`/env). Then
build the *minimal* harness — `run_probe.py` + the four seed probes + `verify_offline.py` — alongside the real
analysis, so the structure is earned by genuine captures. Do **not** build it speculatively before then.

## 9. Explicitly out of scope

The PS5 repo's scale (thousands of probes, 52 numbered phases, a result-mirroring swarm, remote-exec rigs) is
their problem shape, not ours. This harness stays small: tens of probes, hand-curated, each tied to a tracked
question. If the study ever grows a genuine high-volume loop (e.g. fuzzing an extracted service), revisit the
batch-runner/swarm patterns then.
