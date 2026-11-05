# coffey device-tree comparison v2 — 2026-11-04 (boot-policy Phase D)

coffey's own shipped device tree compared with vendor and CoreELEC trees built from pinned public source.
Offline only. Reports and scripts verify against [`SHA256SUMS.txt`](SHA256SUMS.txt); the DTBs are pinned in
[`DTB-ARTIFACTS-SHA256SUMS.txt`](DTB-ARTIFACTS-SHA256SUMS.txt) and not committed.

| File | Content |
|---|---|
| [`COFFEY-DTB-COMPARISON-v2.md`](COFFEY-DTB-COMPARISON-v2.md) | Inputs, which tree coffey is, the Phase D axis table, answers for the track |
| [`scripts/build-dtbs.sh`](scripts/build-dtbs.sh) | Fetches pinned sources, builds the donor DTBs, carves coffey's FDT (reproduces every hash) |
| [`scripts/dtdiff.py`](scripts/dtdiff.py) | Semantic DT diff (phandles matched by target path via `#*-cells`) and axis extraction |

## Bottom line

- **coffey's DT is the Amlogic `bm202` reference board plus 19 onn edits** (LEDs, IR remote map, two extra
  unifykeys, a boot arg, a few pin muxes). Every other donor is 5–7× further away.
- The source builds **reproduce CoreELEC's shipped generic DTB byte-for-byte** (`bed657b4…`).
- Against CoreELEC's generic 2 GiB tree: memory, secure carve-out, PSCI, console UART and eMMC match. CoreELEC
  also enables hardware coffey doesn't have (Ethernet, SD, second USB host, CVBS, internal codec), binds a
  different GPU driver, and reserves ~284 MiB more for media. **Candidate, not coffey-ready.**
- Board descriptions don't change the weld: whether the locked bootloader would load anything else is still
  the open question (C5, C13).
