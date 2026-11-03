# Tasks for Chat — round 2 (public lookups while coffey OTA is pending)

Continuation of [`codex-task-list.md`](codex-task-list.md) for the [boot-policy track](boot-policy-track.md)
and [`root-study.md`](root-study.md). **Public, host-side, read-only** — no device access, no firmware-script
execution, no flashing/boot. These are the last high-value public lookups; beyond them, general searching is
low-yield until coffey's own artifacts land.

## Search discipline (apply to every task)

The round-1 PQ sweep improved sharply when the prompt named exact sources and demanded a *bounded* result.
Do the same here:

1. **Enumerate the search space explicitly.** Name every repo, branch, tag, forum, database, and query string
   you check — including the ones that returned nothing. "I searched" is not evidence; "I checked refs X, Y, Z
   and queries A, B, C" is.
2. **Pin everything.** Every source ref by full Git commit / release tag / filing ID / archived URL + date;
   every downloaded artifact by SHA-256. A bare URL without a pin or hash is a lead, not a finding.
3. **Make negatives bounded, not provisional.** Don't stop at "none found." State *exactly what was searched*
   so "not found" becomes defensible (as the PQ v2 did: "all 1 branch + 67 tags, dated"). Distinguish
   "exhausted this enumerated set" from "nothing exists anywhere."
4. **Separate mechanism from inference.** A string/symbol/log match is a lead (`H`), not proof of control flow
   or a coffey fact. Keep P/R/B/H/U labels on every row. A same-SoC or same-vendor hit stays a comparator
   unless the exact board/build matches.
5. **Never transfer donor offsets, keys, DTBs, or images into a coffey conclusion.** coffey cells stay
   `U`/`B` until coffey's own artifacts exist.
6. **Record competing explanations and the next discriminating check** for each finding.

Return format per finding: `ID · claim · P/R/B/H/U · target/build · artifact SHA-256 · source ref ·
file+locator · observation · interpretation + competing explanation · next discriminating check.` Plus a relay
summary and a SHA-256 list. Package as text reports (binaries stay out of git; hash-pin and link them).

---

## Task R2-1 — CVE-2026-43499 (GhostLock futex-PI) patch timeline — *highest value*
Pin when the **futex PI requeue use-after-free fix** (CVE-2026-43499) landed in the **`android14-5.15` GKI
branch**, and which **Android Security Bulletin / patch level** first shipped it — then compare against
coffey's recorded **2026-03-01** patch level and the sibling onn 4K Pro's 2026-06-01.
- **Enumerate:** the CVE record (NVD / CVEProject/cvelistv5 / kernel.org CNA); the Android Security Bulletins
  for the months around the fix (name each month checked); the GKI `android14-5.15` branch commit/tag history
  for the fixing commit (`futex` / `requeue_pi` / `rt_mutex` waiter revalidation) and the first android14-5.15
  release tag that contains it; the upstream stable 5.15.y backport commit.
- **Required result:** a dated determination — "fix in commit `<sha>`, android14-5.15 release `<tag>` (date),
  Android patch level `<YYYY-MM>`" → therefore coffey at 2026-03-01 is **{before/after}** the fix. Mark the
  coffey conclusion `H` (patch-level inference) until coffey's own kernel/build is confirmed; it still upgrades
  `root-study.md` D-bis from "candidate" to a dated applicability statement.

## Task R2-2 — FCC ID + teardown for the onn 4K Plus "coffey" — *untapped hardware avenue*
Mine public hardware documentation for the eventual bootloader/serial-console route (the `env`/`misc`/`param`
partitions are unreadable without root, so UART/test-point access is the only non-root path to back them up).
- **Enumerate:** the **FCC OET database** — find the FCC ID for the onn 4K Plus Streaming device (2026,
  Walmart house brand; applicant likely an ODM such as SDMC/Amlogic partner, not "onn"). Pull internal photos,
  label/ID filing, and any RF/user-manual exhibit. Then named teardowns (XDA, Reddit r/Onn / r/GoogleTV,
  YouTube, FCCID.io) for **UART test-point location, eMMC package, and any boot/console log**.
- **Required result:** a hardware-access sheet — FCC ID (pinned), internal photo links, and any identified UART
  pads / eMMC part / boot-log text. Clearly mark anything inferred vs. photographed. No electrical assumptions
  transferred without a photo.

## Task R2-3 — Community-report sweep for *this exact device*
Determine whether any prior public root / CoreELEC / alternate-boot work exists for **onn coffey specifically**
(round 1 searched S905X5M generally, never this exact device).
- **Enumerate and name each:** CoreELEC Discourse, 4PDA, XDA-Developers, freaktab, Reddit (r/Onn,
  r/AndroidTV, r/GoogleTV), and GitHub — with the exact queries used (`onn coffey`, `onn 4K Plus S905X5M`,
  `onn S905X5M root`, `onn coffey CoreELEC`, device codename `coffey` + Amlogic, etc.).
- **Required result:** a **bounded** verdict — either a pinned lead (repo/thread + commit/post ID) or "no prior
  public work on coffey found across the enumerated forums + queries," listing each venue and query so the
  negative is defensible.

## Task R2-4 — Pre-stage the coffey OTA endpoint + fingerprint format
Make Adam's imminent on-device OTA capture fast to verify (mirror the darkknight OTA recon method).
- **Enumerate:** the `bgondell/onn-update-blocker` repo (already in our credits) for onn OTA hosts/domains;
  XDA onn firmware threads for posted `ro.build.fingerprint` strings; Google's `SystemUpdateService` /
  `android.googleapis.com/packages/ota-api/...` pattern as used by Google-TV devices; and any public onn
  coffey build fingerprint (`onn/...`) or OTA log.
- **Required result:** the **expected** onn coffey build-fingerprint shape and OTA endpoint/host (marked `H`,
  explicitly *not* a downloaded image), plus the exact fields to capture on-device so provenance is immediate:
  full `ro.build.fingerprint`, incremental/build ID, security patch, the update-service request params, the
  returned package URL + advertised size/hash, HTTP headers/redirects, and the local SHA-256 of the unmodified
  package.

---

## Priority
R2-1 and R2-2 first (R2-1 advances the root track with a concrete dated answer; R2-2 opens the only non-root
hardware path to the bootloader/env blocker). R2-3 is cheap diligence; R2-4 directly smooths the pending
capture. After these four, stop public lookups and wait for coffey's OTA + `systemcontrol` ELF + DTB.

## Out of scope
Capturing coffey's own OTA/ELF/DTB (device-side, Adam's step); anything device-side; running any firmware
script or installer; promising a bypass or unbrickability.
