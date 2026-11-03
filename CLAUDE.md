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
- `research/codex-task-list*.md` — task blocks handed to the second agent ("Chat")
- `STATUS.md` / `progress.json` — the dashboard (confirmed / hard walls / priority vectors / dead ends)

## Three tracks, one line each

- **Telemetry:** mostly done for coffey; scenarios D/E/F + overnight pending.
- **Runtime root:** per-boot only, kernel-memory-safety is the sole live lane; GhostLock/CVE-2026-43499 is a
  *dated candidate* for coffey (SPL 2026-03 predates the fix) — confirm against coffey's own kernel. Runtime
  root ≠ custom ROM (needs bootloader unlock).
- **Boot-policy:** public surface mapped and bounded; every coffey cell `U`; gated on the artifact capture.

## The one unlock

**Capture coffey's own OTA + kernel + DTB + `systemcontrol` ELF** (maintainer, device-side). It settles the
CVE-2026-43499 `H`, feeds Phases A–F, and supersedes the sibling comparators. Target fingerprint to verify
against: `onn/coffey/coffey:14/URO4.260304.011.B1/15051976` (SPL 2026-03-01).

## Working conventions

- Develop on the maintainer's designated branch; commit with clear messages; push only when asked.
- When a packet of reports arrives: verify every file against its `SHA256SUMS`, commit **text only** under
  `research/…`, add an INDEX, update `STATUS.md`/`progress.json` and the relevant track doc, then push.
- Don't open a PR unless asked. Keep the attribution footer on any GitHub comment.
- Update `STATUS.md` + `progress.json` whenever a finding, wall, vector, or dead end changes.
