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
| [`scripts/scan_ta_uuid.py`](scripts/scan_ta_uuid.py) | The scanner (ASCII + both packed byte-orders), read-only, reproducible |
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
- **Check §2.1 is now run (2026-11-12): MISS.** coffey does not ship the Pro's AVB TA as a loadable TA and no
  readable coffey binary references the UUID (P, bounded) — the easy transfer is ruled out; a built-in secure
  service stays U behind the C13 opacity wall. Checks §2.2 (storeboot-writability) and §2.3 (USB-boot gate)
  remain open. Every other coffey cell stays `U`/`B`/`H`.

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

Go to the originals; this summary is no substitute for their docs, and any real use of their method should
follow their guidance and their warnings.
