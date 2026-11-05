# CLAUDE.md — agent handoff & working rules

Orientation for a Claude/Chat session picking up this repo, so context isn't re-derived each time. Read this,
then [`STATUS.md`](STATUS.md) for current state. Keep both current as work lands.

## What this repo is

A **local-only, owner-authorized** study of a device the maintainer owns: the onn 4K Plus Streaming
(`coffey`, Amlogic S905X5M). Two intertwined aims:
1. **Telemetry audit** — what the OS + preinstalled apps send by themselves (`findings/`, `method/`, `tools/`).
2. **Root / boot-policy research** — the welded bootloader, runtime-root ceiling, and whether coffey can boot
   an alternate OS (`research/`). Documentation-only; no bypass is published.

## Ground rules (do not break)

- **Owner's own hardware, authorized research.** Defensive/educational framing; nothing here is for attacking
  others' devices.
- **No bypass, exploit, offset, or weaponization published.** Record CVE identities, applicability, and
  enforcement boundaries — not working exploits. A documented boundary is a valid result.
- **No firmware/vendor blobs in git.** Hash-pin them in a `SHA256SUMS` ledger and keep the bytes out (they're
  re-fetchable). CI (`tools/verify_hashes.py`) verifies committed text against the ledgers and skips absent
  blobs.
- **No device-side actions from a cloud session.** Capturing coffey's OTA/kernel/ELF/DTB is the maintainer's
  step on their own machine. Never flash, boot recovery, alter env, or run firmware scripts.
- **Grade everything P/R/B/H/U; never transfer donor data into a coffey conclusion.** coffey cells stay `U`/`B`
  until coffey's own artifacts exist.

## How we search (and why it's worked)

Follow [`research/search-methodology.md`](research/search-methodology.md): enumerate the exact search space
(name every ref checked, including empty ones), pin by commit/hash, make negatives **bounded not provisional**,
keep primary-source-wins, and separate mechanism from inference. This discipline is what makes our negatives
trustworthy — apply it to every lookup.

## Repo map

- `findings/` — per-device telemetry reports · `method/` — reproduce (adb + WireGuard capture) ·
  `tools/` — scripts (incl. `verify_hashes.py`) · `recommendations.md` · `diagrams/` · `blocklists/`
- `research/root-study.md` — bootloader weld, runtime-root ceiling, kernel n-day lane, GhostLock D-bis
- `research/boot-policy-track.md` — alternate-OS track (Phases A–F), the live agenda
- `research/boot-policy-packet-2026-11-02/` — public-artifact results (CE recovery audit, DTB, PQ, prereqs) +
  `public-lookups-addendum/` (boot-chain model, darkknight recon, barrier matrix, PQ v2) + `REVIEWER-NOTES.md`
- `research/boot-policy-packet-round2-2026-11-03/` — CVE timeline, FCC/hardware, community sweep, OTA prestage
- `research/coffey-ota-capture-2026-10-09/` — **coffey's own OTA capture**: acquisition + identity, graded
  findings O1–O13, off-repo artifact ledger, byte-identical `source-notes/`
- `research/coffey-cve-applicability-r4-2026-11-03/` — R3 matrix re-run against coffey's own kernel source
  (`3d26c188ef7e`) and OTA images
- `research/coffey-systemcontrol-authz-2026-11-03/` — Phase F: `systemcontrol` caller authorization from
  coffey's loaded SELinux policy + binary imports (third-party apps can reach it; disclosure pending)
- `research/coffey-dtb-comparison-2026-11-04/` — Phase D: coffey's DT vs vendor/CoreELEC trees built from
  pinned source (coffey = bm202 + 19 onn edits); supersedes the 11-02 coffey column
- `research/coffey-odmext-consumers-2026-11-04/` — Phase E: `odm_ext` contents, consumers, writers (only
  firmware partition outside verified boot)
- `research/coffey-device-checks-2026-11-04/` — owner unit confirmed on the analyzed build, locked + green;
  no newer coffey OTA in the public catalog; a public coffey GhostLock repo noted (R)
- `disclosure/` — **git-ignored** unsent disclosure drafts; never commit or publish
- `research/coffey-boot-dispatch-2026-11-04/` — Phase B: boot-policy map from plaintext ramdisks, steering HALs
  and policy (env + `/misc`; OEM-unlock-allowed = `ubootenv.var.lock`; BL33 logic U)
- `research/codex-task-list*.md` — task blocks handed to the second agent ("Chat")
- `STATUS.md` / `progress.json` — the dashboard (confirmed / hard walls / priority vectors / dead ends)
- `probes/` + `results/` — **minimal probe harness (built 2026-11-05)**: `tools/run_probe.py` runs a probe
  against hash-fingerprinted inputs (paths in git-ignored `probes/local-inputs.json`) and writes append-only
  captures; `tools/verify_offline.py` (CI) checks them, `--rerun` re-runs host probes locally.
  `results/INDEX.md` maps findings PF-1..PF-4 to captures. New probes stay read-only and applicability-level

## Three tracks, one line each

- **Telemetry:** A/Z/C/Z2/D/F summarized via `telemetry/window-summary` (PF-5) and the factory tool's boot
  behaviour via PF-6; E (real voice query), B (screensaver) and a LAN-side scan still need capturing. Commit
  only probe summaries and run `tools/privacy_scan.py` first; raw captures stay outside the repo.
- **Runtime root:** per-boot only, kernel-memory-safety is the sole live lane. Against coffey's own kernel
  (R4): GhostLock/CVE-2026-43499 affected code **present** (`P`); the epoll pair **not applicable**. Runtime
  root ≠ custom ROM (needs bootloader unlock).
- **Boot-policy:** all six phases done to the offline ceiling. What remains needs either a readable BL33
  (blocked, C13) or a separately approved device experiment (track §6). Don't publish invocation details for `systemcontrol` (C15) while disclosure is undecided.

## The one unlock — done

coffey's own OTA, kernel, DTB, and `systemcontrol` ELF were captured on the maintainer's machine (2026-10-09)
and ingested on 2026-11-03: [`research/coffey-ota-capture-2026-10-09/`](research/coffey-ota-capture-2026-10-09/).
Build verified: `onn/coffey/coffey:14/URO4.260304.011.B1/15051976` (SPL 2026-03-01); kernel GKI
`5.15.196-android14-11-g3d26c188ef7e-ab14657224`. The bytes live off-repo (maintainer's `E:\Morphe\device\coffey-ota\`)
and are pinned in that packet's ledger. CVE applicability against this exact kernel is done (R4); next uses
were `systemcontrol` (Phase F), the DT comparison (D), `odm_ext` (E) and boot dispatch (B), all done.

## Working conventions

- Develop on the maintainer's designated branch; commit with clear messages; push only when asked.
- When a packet of reports arrives: verify every file against its `SHA256SUMS`, commit **text only** under
  `research/…`, add an INDEX, update `STATUS.md`/`progress.json` and the relevant track doc, then push.
- Don't open a PR unless asked. Keep the attribution footer on any GitHub comment.
- Update `STATUS.md` + `progress.json` whenever a finding, wall, vector, or dead end changes.
