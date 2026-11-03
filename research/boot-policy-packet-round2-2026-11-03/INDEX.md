# Round-2 public lookups — 2026-11-03 (Chat)

Results for [`../codex-task-list-round2.md`](../codex-task-list-round2.md). Public, host-side, read-only — no
device access, no OTA/kernel bytes downloaded. All five text reports verify against `SHA256SUMS.txt`. Start
with [`COFFEY-R2-RELAY.md`](COFFEY-R2-RELAY.md).

| File | Task | Result |
|---|---|---|
| [`COFFEY-R2-1-CVE-TIMELINE.md`](COFFEY-R2-1-CVE-TIMELINE.md) | R2-1 | **GhostLock futex-PI fix dated.** Upstream `3bfdc639…`; Android cherry-pick `74b647b4` (2026-07-23); first GKI tag **`android14-5.15-2025-07_r5`** (released **2026-08-05**); first ASB listing **Nov 2026** (A-496407345); stable 5.15.212. Coffey's **2026-03-01** SPL and the sibling's 2026-06-01 both **predate the fix → `H`** (patch-level inference, not a vulnerable-code proof; OEM backport is the competing explanation). Upgrades `root-study.md` D-bis from "candidate" to a dated determination. |
| [`COFFEY-R2-2-FCC-HARDWARE-ACCESS.md`](COFFEY-R2-2-FCC-HARDWARE-ACCESS.md) | R2-2 | FCC IDs **`2AYYS-CS116K4Y`** / **`2AYYS-CS116K4O`** (applicant Luxshare); internal-photo + label exhibits linked. EDN teardown confirms **FORESEE `FEMDNN016G` 16 GB eMMC**, 2× Micron DDR4, Amlogic S905X5M. Codenames `DV6116N / coffey / CS116K4`. **UART pad/pinout/boot-log: `U`** — not established by any public source. |
| [`COFFEY-R2-3-COMMUNITY-SWEEP.md`](COFFEY-R2-3-COMMUNITY-SWEEP.md) | R2-3 | **Bounded negative:** no coffey-specific root / CoreELEC / unlock / alternate-boot work across the enumerated venues+queries (CoreELEC Discourse, 4PDA, XDA, FreakTab, Reddit, GitHub — each query listed). Only hits are user-space **ADB debloat** profiles (`Gathin23/cleanyourtv` pinned, `picajoso/tv-vibehack-javipas`) — not boot-policy access. |
| [`COFFEY-R2-4-OTA-CAPTURE-PRESTAGE.md`](COFFEY-R2-4-OTA-CAPTURE-PRESTAGE.md) | R2-4 | Public OTA catalog entry (OTAChecker #2594): coffey target fingerprint **`onn/coffey/coffey:14/URO4.260304.011.B1/15051976:user/release-keys`**, incremental `15051976`, SPL `2026-03-01`, OTA token `db1ba0cd…` on `android.googleapis.com` → `redirector.gvt1.com`. **Metadata comparator only** (no bytes fetched). Plus the exact on-device capture-fields checklist. |
| [`COFFEY-R2-5-FCC-PHOTO-REVIEW.md`](COFFEY-R2-5-FCC-PHOTO-REVIEW.md) | R2-5 | **Candidate UART header found in the FCC photos (`H`):** a **4-pad row with silk-screen reading "GND / TX / RX / GND"** on p.3 of internal-photo exhibit **7952340** (CS116K4Y), mirrored on p.3/Config 2 of **7952199** (CS116K4O). Photo lead only — not a verified UART, no pin order/voltage inferred; the EDN teardown images showed no comparably clear labeled header. Board-revision match to the owner's retail unit **unresolved**. First concrete lead on the serial-console path to the `env`/`misc`/`param` wall. |

## Bottom line
R2-1 advances the root track with a dated answer; R2-2/R2-3/R2-4 bound their questions and improve comparators.
**Nothing establishes a coffey fact** — authorization, boot policy, UART access, vulnerable-kernel status, and
any current-unit build all stay `U`/`H`. The decisive next step is unchanged and device-side: capture coffey's
own current fingerprint + update-service response and preserve the unmodified OTA package (local SHA-256). That
one capture anchors the kernel/DTB/`systemcontrol` analysis.

Cross-check note: the R2-4 catalog fingerprint (`URO4.260304.011.B1`, SPL `2026-03-01`) **matches** the build
and patch level already recorded in `findings/coffey-2026-09.md` — consistent, but still a catalog record, not
a capture of the current unit.
