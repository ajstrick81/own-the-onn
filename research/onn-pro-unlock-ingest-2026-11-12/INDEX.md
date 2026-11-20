# onn 4K Pro unlock ingest — 2026-11-12

External first-hand reports (**R**) that two sibling onn **4K Pro** devices have a persistent bootloader
**AVB-lock** unlock, ingested and mapped onto coffey's (4K **Plus**) own confirmed findings. Documentation-only;
no bypass, offset, or key is published (the sources publish none either). All coffey-side follow-ups are
offline, read-only on the already-captured OTA. Sources are web pages pinned by URL + fetch date + verbatim
quotes ([`SOURCES.md`](SOURCES.md)); this packet adds no firmware blobs, so it carries no new `SHA256SUMS`.

| File | Content |
|---|---|
| [`ONN-PRO-UNLOCK-MECHANISM.md`](ONN-PRO-UNLOCK-MECHANISM.md) | What the 2024 `jarvis` + 2026 `jarvis2` projects claim: the overlap table, the AVB-unlock chain (storeboot env → USB/EL2 payload → AVB trusted-app), and the authors' own scope limits |
| [`COFFEY-APPLICABILITY.md`](COFFEY-APPLICABILITY.md) | How it maps onto coffey's C13/C15/C18; ranked offline discriminating checks (AVB TA UUID grep, storeboot-writability, USB-boot gate); what it changes for root vs alternate-OS |
| [`COFFEY-TA-UUID-SCAN.md`](COFFEY-TA-UUID-SCAN.md) | **Vector #3 check §2.1, run 2026-11-12:** offline scan of coffey's own images for the AVB TA UUID — **no hit** (bounded negative on the loadable-TA path, P; built-in-service path stays U behind C13) |
| [`COFFEY-STOREBOOT-WRITE.md`](COFFEY-STOREBOOT-WRITE.md) | **Vector #3 check §2.2, run 2026-11-12:** coffey's `systemcontrol` env writer permits `ubootenv.var.storeboot` (prefix-only gate, no protected-key list) — Android-side write unobstructed (P); bootloader honoring stays U (C13) |
| [`EXTERNAL-COFFEY-TOOLS-2026-11-19.md`](EXTERNAL-COFFEY-TOOLS-2026-11-19.md) | **R, 2026-11-19:** source-read review of `ShaneBreazeale/OnnDemand-4kplus` (coffey temp root + root SSH on our exact build; mechanism unstated, not GhostLock-labelled; one unit) and `kushmint/onn-unlock-probe` (read-only AVB lock-bit check against TA `023f8f1a…`; `--toggle-test` defects). Cited, not vendored |
| [`PROPOSAL-UNLOCK-PROBE-READONLY.md`](PROPOSAL-UNLOCK-PROBE-READONLY.md) | Track-§6 proposal (**run 2026-11-20**, deviations recorded): read-only probe on coffey to close §2.1's built-in-TA "U" — binary pinning, preconditions, procedure, side effects, evidence handling |
| [`COFFEY-UNLOCK-PROBE-RESULT.md`](COFFEY-UNLOCK-PROBE-RESULT.md) | **P, 2026-11-20 — first on-device boot-policy evidence:** coffey's TEE opens a session to AVB TA `023f8f1a…` from an unprivileged adb shell and reads `1` (locked); TA is built in. Closes §2.1; C5's flippability → H. Also records the unit's OTA to `16202347` (C22) |
| [`evidence/`](evidence/) | Probe JSON + run metadata, hash-pinned in [`evidence/SHA256SUMS.txt`](evidence/SHA256SUMS.txt) (built binary + source hashes listed off-repo) |
| [`scripts/scan_ta_uuid.py`](scripts/scan_ta_uuid.py) | The §2.1 scanner (ASCII + both packed byte-orders), read-only, reproducible |
| [`SOURCES.md`](SOURCES.md) | Exact URLs, fetch date, and verbatim field dumps (tested-profile.json, unlock-after-reset.json, the mechanism strings) |

## Bottom line

- **Two exact overlaps with coffey:** the 2024 Pro (`jarvis`) ships the **identical build train**
  (`URO4.260304.011.B1` / `15051976`); the 2026 Pro (`jarvis2`) is the **identical SoC** (`S905X5M` / `S7D`).
- **The unlock flips the _AVB_ lock, not hardware secure boot.** 2024 does it by setting
  `ubootenv.var.storeboot` via **SystemControl**, booting an **unsigned EL2 payload** off a one-use USB gate,
  which calls an **AVB trusted-app** (UUID `023f8f1a-…`, cmd 3) to write secure state `1 → 0`. No key was
  forged; the chain is "specific to the tested bootloader." 2026 reaches the same AVB outcome by an undocumented
  transport (no USB).
- **It's a root-persistence path, not an alternate-OS path.** Post-unlock, both patch the Android boot image
  (`boot_b` / `init_boot_b`) for persistent Magisk. The authors are explicit it does **not** enable custom
  first-stage/BL33 — so **CoreELEC/custom ROM stays blocked** by coffey's C13 wall.
- **For coffey this is a lead, not a result (R).** It reopens the C5 "can't be flipped" baseline (graded `B`)
  with a same-silicon counterexample at the AVB layer, and gives three concrete **offline** checks on coffey's
  captured artifacts.
- **Checks §2.1 + §2.2 run (2026-11-12).** §2.1 **MISS** — coffey ships none of the Pro's AVB TA as a loadable
  TA and no readable binary references the UUID (P, bounded); the easy transfer is ruled out. §2.2 **YES** —
  coffey's `systemcontrol` will write `ubootenv.var.storeboot` (prefix-only gate, no protected-key list), so the
  Android-side startup redirect is unobstructed (P). Both halves that remain — does the bootloader *honor* the
  changed `storeboot`, and does it *boot a USB payload* (§2.3) — collapse onto coffey's opaque BL32/BL33 (C13),
  movable only by a readable secure-world image or the UART lead (vector #5). Every other coffey cell stays
  `U`/`B`/`H`.
- **2026-11-19 — two coffey-targeted external tools (R).** `onn-unlock-probe`'s read-only mode can settle §2.1's
  built-in-TA question **on the device** without root — proposed as a §6 experiment, not run.
  `OnnDemand-4kplus` claims temp root + root SSH on our exact build (one unit; it does not name its bug, and its
  tests reused an existing root session), which would open the `env`/`misc`/`param` wall if it reproduces.
- **2026-11-20 — the read-only probe ran on the owner unit: HIT.** coffey's TEE exposes the jarvis2 AVB trusted app
  (built in, no `.ta` file), an unprivileged adb shell can open it, and it reads `1` (locked). §2.1 is closed; the
  lock is a TEE-held flag, so C5's "can't be flipped" baseline drops to H. The write side was deliberately not
  tested. The unit had OTA'd to `16202347` (kernel and SELinux policy unchanged).

## What changed in the dashboards
- **New confirmed row C19 (R)** in [`../../STATUS.md`](../../STATUS.md) / [`progress.json`](../../progress.json).
- **Welded-bootloader wall** reworded: the weld is now shown flippable at the **AVB layer** on sibling silicon
  (R); hardware secure boot / BL33 stay welded.
- **New priority vector:** test the Pro unlock's preconditions against coffey's own captured artifacts (offline).
- **Boot-policy track** Phase B annotated: the Pro chain instantiates the `storeboot`/USB tokens Phase B greps
  for; the AVB-TA-UUID grep is added as the next offline discriminating check.

## Credits

All of the primary work ingested here is **OpenEnsemble's**, not ours. The author independently found and
proved the onn 4K Pro AVB-lock unlock and root — the `storeboot`/SystemControl redirect, the EL2 payload, the
AVB trusted-app call, the Magisk boot-image patch — and did the hard, risky part: running it on real hardware
(bricking a first unit in the process), documenting the exact build profiles, hashes, and recovery limits, and
publishing the mechanism and its honest caveats. This packet only *reads* that work and reasons about whether it
could transfer to a different board (coffey). Credit for the mechanism, the testing, and the evidence discipline
belongs to them:

- **2024 onn 4K Pro (`jarvis` / SNA):** `openensemble/onn-4k-pro-unlock-root` ·
  `https://openensemble.github.io/onn-4k-pro-unlock-root/`
- **2026 onn 4K Pro (`jarvis2`):** `openensemble/onn-4k-pro-2026-unlock-root`

Two follow-on projects brought that work to **our** board, the onn 4K Plus (`coffey`), and this packet's coffey
results depend on them:

- **ShaneBreazeale — `ShaneBreazeale/OnnDemand-4kplus`** (`https://github.com/ShaneBreazeale/OnnDemand-4kplus`): the
  first public coffey port — temporary root + root SSH, tested on our exact original build `15051976`, with clear
  scope and security caveats ([review](EXTERNAL-COFFEY-TOOLS-2026-11-19.md) §1).
- **kushmint — `kushmint/onn-unlock-probe`** (`https://github.com/kushmint/onn-unlock-probe`): the non-destructive
  AVB lock-bit check. Its read-only mode, built from source and run on our unit, produced C21 — coffey's TEE exposes
  the same AVB trusted app ([result](COFFEY-UNLOCK-PROBE-RESULT.md); [review](EXTERNAL-COFFEY-TOOLS-2026-11-19.md) §2).

Go to the originals; this summary is no substitute for their docs, and any real use of their method should
follow their guidance and their warnings.
