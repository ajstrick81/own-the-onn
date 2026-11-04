# own-the-onn — status dashboard

> Single front page for where the study stands. Evidence-weighted and deliberately candid: a documented
> enforcement boundary is a result, and un-met goals are stated plainly. Grades use **P** inspected primary ·
> **R** first-hand report · **B** inherited baseline · **H** hypothesis/lead · **U** unresolved. Updated
> 2026-11-03 (coffey OTA capture ingested; CVE applicability R4). Machine-readable mirror: [`progress.json`](progress.json).

Device: **onn 4K Plus Streaming** (`coffey` / `DV6116N` / `CS116K4`), Amlogic **S905X5M** (S7D), Android 14,
kernel `5.15.196-android14-11-g3d26c188ef7e-ab14657224` (GKI, built 2026-01-03), SPL `2026-03-01`, build
`URO4.260304.011.B1`.

## Milestone meter (subjective, evidence-weighted)

| Track | Goal | Score |
|---|---|---|
| Telemetry audit | What the box sends by itself | **7/10** — one device, scenarios D/E/F + overnight pending |
| Root (runtime) | Per-boot kernel root on coffey | **1/10** — GhostLock affected code confirmed in coffey's kernel (P); no coffey exploit attempted |
| Boot-policy / alternate-OS | Map the weld; can coffey boot CoreELEC | **2/10** — public surface mapped; coffey's own OTA/kernel/DTB/ELF now captured (Phase A done), Phases B/D/E/F not yet filled from them |

**Top-level unmet:** no root, no bootloader unlock, and no alternate-OS boot. coffey's own OTA is captured and
its DT, modules, and bootloader container are mapped, but the CVE and `systemcontrol` analyses on it haven't
been done. Nothing here demonstrates a bypass.

## Confirmed (P / R / B)

| # | Finding | Grade | Where |
|---|---|---|---|
| C1 | No ACR packages; no app holds screen/TV-input capture perms | P | `findings/coffey-2026-09.md` |
| C2 | No background mic use; every mic use is a ~5 s foreground press | P | `findings/coffey-2026-09.md` |
| C3 | Phones home while idle/screen-off (mostly Google + installed apps); Netflix logs while asleep | P | `findings/coffey-2026-09.md` |
| C4 | Preinstalled factory test tool runs system-privileged; retail upload flow dormant | P | `findings/coffey-2026-09.md` |
| C5 | Bootloader welded — OEM-unlock disabled, AVB locked, verified-boot green (bootloader-enforced) | B | `research/root-study.md` §A |
| C6 | Factory-tool userland doors are real but SELinux-boxed (system-UID, not root) | P | `research/root-study.md` §B/C |
| C7 | Stock CoreELEC recovery is **state-changing** (writes env via `fw_setenv`, no rollback) — fails a read-only boundary | P | `research/boot-policy-packet-2026-11-02/.../COFFEY-CE-RECOVERY-AUDIT.md` |
| C8 | CVE-2026-43499 futex-PI fix dated: first GKI tag 2026-08-05, first ASB Nov 2026 | P/R | `research/boot-policy-packet-round2-2026-11-03/COFFEY-R2-1-CVE-TIMELINE.md` |
| C9 | FCC IDs `2AYYS-CS116K4Y`/`…K4O` (Luxshare); FORESEE 16 GB eMMC + S905X5M | P/R | `research/boot-policy-packet-round2-2026-11-03/COFFEY-R2-2-FCC-HARDWARE-ACCESS.md` |
| C10 | coffey's exact-build OTA captured (ZIP SHA-256 `ec755bd0…b1a7`); metadata matches `onn/coffey/coffey:14/URO4.260304.011.B1/15051976` field by field | P | `research/coffey-ota-capture-2026-10-09/COFFEY-OTA-CAPTURE.md` |
| C11 | coffey kernel = GKI `5.15.196-android14-11-g3d26c188ef7e-ab14657224`, built 2026-01-03; vendor modules built against a different kernel build | P | `research/coffey-ota-capture-2026-10-09/COFFEY-OTA-FINDINGS.md` O2–O3 |
| C12 | coffey runs the Amlogic **vendor** driver stack (DT compatibles match CoreELEC `common_drivers`, not mainline); base DT `s7d_s905x5m_bm202`, PSCI 0.2, 2 GiB usable | P | `…/COFFEY-OTA-FINDINGS.md` O4–O6 |
| C13 | Bootloader = signed Amlogic container (build `S7D-s905x5m-26030511BBST`); every stage body after the headers is opaque | P (layout) / H (encrypted vs. packed) | `…/COFFEY-OTA-FINDINGS.md` O7–O9 |
| C14 | coffey kernel source = `kernel/common` `3d26c188ef7e` (branch point of `android14-5.15-2026-01`). **CVE-2026-43499 (GhostLock) and CVE-2026-99169 affected code present**; Bad Epoll, CVE-2026-43074, -23259, -99221 **not applicable** | P | `research/coffey-cve-applicability-r4-2026-11-03/` |

## Hard walls (what blocks us)

| Wall | Why it holds |
|---|---|
| Welded bootloader | Enforced in signed Amlogic ROM/BL2, not a flippable flag → no flashing, no persistence, no custom ROM |
| SELinux on factory tool | System-UID writes confined to a tiny domain; not root |
| dm-verity / AVB | Any `boot`/`system`/`vendor` write bricks at next boot on a locked device |
| `env`/`misc`/`param` unreadable w/o root | Can't back them up → bootloader/env experiments stay documented-not-run |
| Kernel exploit is arm64 from-scratch | Public GhostLock work is build/offset/RAM-specific to the sibling `jarvis2`; the epoll PoCs (x86_64) don't apply to coffey's build at all (C14) |
| BL2/BL33 opaque offline | Stage bodies after the signed headers show uniform byte statistics and no markers, so U-Boot's env/`bootcmd` handling can't be read offline (C13) |

## Ranked priority vectors (active leads)

| Rank | Vector | State | Next discriminating step |
|---|---|---|---|
| 1 | ~~Capture coffey's own OTA + kernel + DTB + `systemcontrol` ELF~~ | **DONE** (captured 2026-10-09, ingested 2026-11-03) | now an input to #2/#3 and Phases B/D/E/F — `research/coffey-ota-capture-2026-10-09/` |
| 2 | CVE-2026-43499 applicability + the ranked post-March CVE check-list | **P — affected code present** (R4); remaining H rows: `adbd`/ART (Mainline-updatable), framework, `wpa_supplicant` patch state | device-side: read the unit's `com.android.adbd`/`com.android.art` versions + wireless-debugging state; offline: framework patch comparison, unpack `odm`/`oem` |
| 3 | ~~Two epoll CVEs (Bad Epoll / CVE-2026-43074) arm64 root~~ | **closed — not applicable to coffey's build** (R4) | see dead ends; re-check only if coffey takes an OTA to a newer GKI release |
| 4 | **UART / serial-console path to the env/misc/param wall** | **H — candidate pads found** | match board rev to owner's retail unit label, then continuity/scope-probe the actual board |
| 5 | darkknight provenance-backed OTA (build-identity comparator) | U | capture from darkknight's real update flow, match build identity |
| 6 | twilight (Box S 3rd Gen) A14 OTA — `systemcontrol` ELF comparator | **deprioritized** — coffey's own `systemcontrol` ELF is now in hand | only useful as a cross-device comparison after coffey's ELF is analyzed |

## Dead ends / closed vectors (bounded negatives — do not re-run)

| Closed | Bounded as | Source |
|---|---|---|
| Newer public Android 12–14 `CPQControl`/`systemcontrol` source | all 1 branch + 67 tags of Amlogic frameworks repo (2016–2020), AOSP yukawa a12/13/14/main + BayLibre pkg, enumerated ROM-dump set | `…/COFFEY-PQ-ANCHORS-AD14-DELTA-v2.md` |
| Provenance-backed **darkknight** stock OTA | not found publicly; Xiaomi guide is docs not firmware; OS3.0.2.0 is a Box 5 *MAX* (`MOB1MB-5M`) report, model-code mismatch vs `MOB2MB-5P` | `…/COFFEY-DARKKNIGHT-OTA-RECON.md` |
| Prior coffey-specific root/CoreELEC/unlock work | bounded negative across CoreELEC Discourse/4PDA/XDA/freaktab/Reddit/GitHub + listed queries; only user-space ADB debloat exists | `…/COFFEY-R2-3-COMMUNITY-SWEEP.md` |
| ~~UART pinout from public docs~~ | **reopened → lead found:** FCC photo review (R2-5) found a candidate 4-pad `GND/TX/RX/GND` header; now priority vector #4, no longer a dead end | `…/COFFEY-R2-5-FCC-PHOTO-REVIEW.md` |
| Booting donor CoreELEC recovery as a shortcut | disqualified — it mutates persistent env (C7) | `…/COFFEY-CE-RECOVERY-AUDIT.md` |
| Runtime root → custom ROM | impossible without bootloader unlock (two separate locks) | `research/root-study.md` §D-bis |
| Epoll CVEs (Bad Epoll CVE-2026-46242, CVE-2026-43074) on coffey | not applicable: coffey's `eventpoll.c` (commit `3d26c188ef7e`) lacks the 5.15.209 refcount refactor that introduced both; the earlier "present" claim matched the newer branch tip | `research/coffey-cve-applicability-r4-2026-11-03/` |
| Amlogic `pppoe_wrapper` / DroidLogic subtitle CVEs (119737–119739) | no matching binary/service in `system`/`system_ext`/`product`/`vendor` (policy leftovers only); `odm`/`oem` not unpacked | same |

See [`research/search-methodology.md`](research/search-methodology.md) for how negatives are bounded.
