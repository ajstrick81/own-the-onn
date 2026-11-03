# Tasks for Chat — round 3: CVE applicability sweep for coffey

Public, host-side, read-only desk research. Map CVEs that plausibly apply to **coffey's exact software stack**
across three aggregators and relate each to the own-the-onn tracks. **No exploitation, no PoC execution** —
this is an *applicability assessment*, not a weaponization pass. Follow
[`search-methodology.md`](search-methodology.md) in full; this task lives or dies on bounded, deduplicated,
primary-pinned results.

## Sources (use all three; they're complementary — dedupe by CVE ID)

- **CVE.org** — https://www.cve.org/ — authoritative CNA records; the canonical description + affected ranges.
- **OpenCVE** — https://app.opencve.io/cve/ — best for **enumerating by vendor/product** (subscribe/filter by
  `Linux kernel`, `Google Android`, `Amlogic`); use it to build the candidate list.
- **Tenable** — https://www.tenable.com/cve — enrichment: severity/VPR, exploitability, exploit-availability
  notes. Use it to rank, not to define affected ranges.

A CVE appearing on all three is **one** CVE. Pin each by **CVE ID + the CNA/primary record**, then note which
aggregators corroborate. A Tenable severity is enrichment, not a primary affected-range claim.

## Coffey stack to map against (the search space — enumerate each)

Baseline (from `STATUS.md` / `findings/coffey-2026-09.md`): Android **14**, SPL **2026-03-01**, kernel
**`5.15.196-android14-11`** (GKI `android14-5.15`), SoC **Amlogic S905X5M / S7D**, build `URO4.260304.011.B1`.

| Layer | Query targets | Why it matters |
|---|---|---|
| **Kernel LPE** | `Linux kernel` 5.15.x / `android14-5.15` GKI; subsystems futex/epoll/io_uring/netfilter/perf; CVEs dated after the build + **not in the 2026-03 ASB** | root track — the live lane |
| **Android framework** | `Google Android` ASB CVEs **2026-04 → present** at SPL > 2026-03-01 | root / local-attack surface the device hasn't patched |
| **SoC / vendor** | `Amlogic` (droidlogic, `systemcontrol`, media/codec, secure-boot); S905X5M/S7D | boot-policy + factory-tool track |
| **Bootloader** | Amlogic **U-Boot**, AVB/libavb, TF-A — CVEs touching verified boot / rollback | boot-policy / the weld |
| **Preinstalled userland** | the **WebView/Chromium** version coffey ships; GMS; the factory tool `com.gretzky.hwinfo`; preinstalled Netflix | remote/local attack surface in the telemetry track |
| **Media / DRM** | Widevine / the Amlogic media stack | secure-media boundary |

**Known anchors — extend, don't re-derive** (already in `research/root-study.md`): kernel **CVE-2026-46242**
"Bad Epoll", **CVE-2026-43074** (epoll), **CVE-2026-43499** GhostLock futex-PI (dated in
`research/boot-policy-packet-round2-2026-11-03/COFFEY-R2-1-CVE-TIMELINE.md`). Treat these as the seed; find what
else in the same windows coffey's 2026-03 SPL / early-2026 kernel leaves open.

## Method (per candidate CVE)

1. **Find** via OpenCVE vendor/product enumeration; **confirm** affected/fixed ranges on CVE.org; **enrich**
   (severity, exploit availability) on Tenable.
2. **Decide applicability to coffey by patch-level/version inference** — is the fix in a GKI tag / ASB level
   **after** 2026-03-01 (kernel) or after coffey's SPL (framework)? If so it's a candidate; mark **`H` —
   patch-level inference** (not vulnerable-code proof; OEM backport is the standing competing explanation).
3. **Map to a track** (root / boot-policy / telemetry) and a reachability note: unprivileged-local, privileged,
   remote, or physical — and whether SELinux / the welded bootloader / dm-verity already blunts it.
4. **Record the next discriminating check** (what in coffey's own extracted kernel/build would confirm it).

## Required output

A **deduplicated CVE applicability matrix** — one row per CVE:
`CVE-ID · component/layer · affected range · fixed-in (tag/ASB/version) · in coffey's 2026-03 state? (H) ·
track · reachability · exploit-availability (Tenable) · grade · primary ref · next discriminating check.`

Plus: a **bounded search record** (each site, each vendor/product/query enumerated, and the date), a short
relay summary, and a `SHA256SUMS` for the report(s). Rank the matrix by (plausibly-unpatched × reachability),
not by raw CVSS.

## Hard limits

- **Applicability only — no exploitation, no PoC runs, no offsets.** A CVE being listed is not a coffey fact;
  every coffey cell is `H`/`U` until coffey's own kernel/build is checked.
- **Dedupe across the three sites**; never inflate the count by listing the same CVE three times.
- **Don't transfer** donor/sibling (jarvis2, darkknight, twilight) CVE status onto coffey — same-family is a
  comparator, not proof.
- Keep severity (Tenable) separate from affected-range (CVE.org); a high CVSS on an unreachable path is low
  priority here.

## Priority
Kernel LPE and Android-framework layers first (they feed the root track and are the most likely to be
genuinely unpatched at 2026-03). Vendor/bootloader next (boot-policy). Preinstalled userland + media last.
The decisive confirmation for any `H` row is still coffey's own extracted kernel/build — this sweep tells us
*which CVEs to check first* once that artifact lands.

## Out of scope
Capturing coffey's own OTA/kernel (device-side); running or writing any exploit/PoC; anything device-side.
