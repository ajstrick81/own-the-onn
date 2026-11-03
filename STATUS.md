# own-the-onn — status dashboard

> Single front page for where the study stands. Evidence-weighted and deliberately candid: a documented
> enforcement boundary is a result, and un-met goals are stated plainly. Grades use **P** inspected primary ·
> **R** first-hand report · **B** inherited baseline · **H** hypothesis/lead · **U** unresolved. Updated
> 2026-11-03. Machine-readable mirror: [`progress.json`](progress.json).

Device: **onn 4K Plus Streaming** (`coffey` / `DV6116N` / `CS116K4`), Amlogic **S905X5M** (S7D), Android 14,
kernel `5.15.196-android14-11`, SPL `2026-03-01`, build `URO4.260304.011.B1`.

## Milestone meter (subjective, evidence-weighted)

| Track | Goal | Score |
|---|---|---|
| Telemetry audit | What the box sends by itself | **7/10** — one device, scenarios D/E/F + overnight pending |
| Root (runtime) | Per-boot kernel root on coffey | **1/10** — a dated candidate CVE, no coffey exploit attempted |
| Boot-policy / alternate-OS | Map the weld; can coffey boot CoreELEC | **2/10** — public surface mapped, every coffey cell U |

**Top-level unmet:** no root, no bootloader unlock, no alternate-OS boot, and no coffey-specific kernel/boot
artifact has been analyzed. Nothing here demonstrates a bypass.

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

## Hard walls (what blocks us)

| Wall | Why it holds |
|---|---|
| Welded bootloader | Enforced in signed Amlogic ROM/BL2, not a flippable flag → no flashing, no persistence, no custom ROM |
| SELinux on factory tool | System-UID writes confined to a tiny domain; not root |
| dm-verity / AVB | Any `boot`/`system`/`vendor` write bricks at next boot on a locked device |
| `env`/`misc`/`param` unreadable w/o root | Can't back them up → bootloader/env experiments stay documented-not-run |
| Kernel exploit is arm64 from-scratch | Public PoCs (epoll CVEs, GhostLock) are x86_64 / jarvis2-specific; triggers port, post-ex doesn't |

## Ranked priority vectors (active leads)

| Rank | Vector | State | Next discriminating step |
|---|---|---|---|
| 1 | **Capture coffey's own OTA + kernel + DTB + `systemcontrol` ELF** | pending (device-side) | OTACaptor → hash → `payload_dumper`; unblocks all Phases A–F + settles C8 |
| 2 | CVE-2026-43499 applicability to coffey's kernel | H (patch-level) | extract coffey `vmlinux`, check `rtmutex.c` control flow / build ID vs fix |
| 3 | Two epoll CVEs (Bad Epoll / CVE-2026-43074) arm64 root | H, un-finished exploit-dev | emulator-first arm64 post-ex; never on-device |
| 4 | UART / serial-console path to the env/misc/param wall | U | inspect FCC internal-photo exhibits for pads (task R2-5), then owner's board |
| 5 | darkknight provenance-backed OTA (build-identity comparator) | U | capture from darkknight's real update flow, match build identity |
| 6 | twilight (Box S 3rd Gen) A14 OTA — `systemcontrol` ELF comparator | U (EROFS unread) | read EROFS (`dump.erofs`) once the 1.14 GB OTA is on a capable host |

## Dead ends / closed vectors (bounded negatives — do not re-run)

| Closed | Bounded as | Source |
|---|---|---|
| Newer public Android 12–14 `CPQControl`/`systemcontrol` source | all 1 branch + 67 tags of Amlogic frameworks repo (2016–2020), AOSP yukawa a12/13/14/main + BayLibre pkg, enumerated ROM-dump set | `…/COFFEY-PQ-ANCHORS-AD14-DELTA-v2.md` |
| Provenance-backed **darkknight** stock OTA | not found publicly; Xiaomi guide is docs not firmware; OS3.0.2.0 is a Box 5 *MAX* (`MOB1MB-5M`) report, model-code mismatch vs `MOB2MB-5P` | `…/COFFEY-DARKKNIGHT-OTA-RECON.md` |
| Prior coffey-specific root/CoreELEC/unlock work | bounded negative across CoreELEC Discourse/4PDA/XDA/freaktab/Reddit/GitHub + listed queries; only user-space ADB debloat exists | `…/COFFEY-R2-3-COMMUNITY-SWEEP.md` |
| UART pinout / boot log from public docs | not in FCC filing text or EDN teardown text (`U`); image inspection still open (R2-5) | `…/COFFEY-R2-2-FCC-HARDWARE-ACCESS.md` |
| Booting donor CoreELEC recovery as a shortcut | disqualified — it mutates persistent env (C7) | `…/COFFEY-CE-RECOVERY-AUDIT.md` |
| Runtime root → custom ROM | impossible without bootloader unlock (two separate locks) | `research/root-study.md` §D-bis |

See [`research/search-methodology.md`](research/search-methodology.md) for how negatives are bounded.
