# own-the-onn — status dashboard

> Single front page for where the study stands. Evidence-weighted and deliberately candid: a documented
> enforcement boundary is a result, and un-met goals are stated plainly. Grades use **P** inspected primary ·
> **R** first-hand report · **B** inherited baseline · **H** hypothesis/lead · **U** unresolved. Updated
> 2026-11-12 (onn 4K **Pro** unlock ingest — sibling-silicon AVB-unlock evidence, C19/vector #5; prior:
> 2026-11-04 coffey OTA capture ingested; CVE applicability R4; systemcontrol authorization; DT comparison v2;
> boot-policy phases B/E; device checks). Machine-readable mirror: [`progress.json`](progress.json).

Device: **onn 4K Plus Streaming** (`coffey` / `DV6116N` / `CS116K4`), Amlogic **S905X5M** (S7D), Android 14,
kernel `5.15.196-android14-11-g3d26c188ef7e-ab14657224` (GKI, built 2026-01-03), SPL `2026-03-01`, build
`URO4.260304.011.B1`.

## Milestone meter (subjective, evidence-weighted)

| Track | Goal | Score |
|---|---|---|
| Telemetry audit | What the box sends by itself | **8/10** — A/Z/C/Z2/D/F summarized via probe (PF-5, PF-6); E (voice), B (screensaver) and the LAN-side scan still to capture |
| Root (runtime) | Per-boot kernel root on coffey | **1/10** — GhostLock affected code confirmed in coffey's kernel (P); no coffey exploit attempted |
| Boot-policy / alternate-OS | Map the weld; can coffey boot CoreELEC | **2/10** — all six phases done to the offline ceiling (A, B to plaintext, C, D, E, F); the weld itself is untouched and BL33's decisions stay U. Sibling-silicon AVB-unlock evidence (C19, R) reopens the *unlock* question (not alternate-OS) with offline checks pending (vector #3) |

**Top-level unmet:** no root, no bootloader unlock, and no alternate-OS boot **on coffey**. coffey's own OTA is
captured and analyzed (kernel CVEs, DT, `systemcontrol`, `odm_ext`), but the bootloader that enforces the lock
stays opaque (C13). Nothing here demonstrates a bypass. New (2026-11-12): two sibling 4K **Pro** models have a
first-hand **AVB-lock** unlock on the same build train / SoC (C19, R) — a lead that makes coffey's unlock
question empirical rather than assumed, pursued offline first (vector #3); it does **not** touch hardware secure
boot or the alternate-OS wall.

## Confirmed (P / R / B)

| # | Finding | Grade | Where |
|---|---|---|---|
| C1 | No ACR packages; no app holds screen/TV-input capture perms | P | `findings/coffey-2026-09.md` |
| C2 | No background mic use; every mic use is a ~5 s foreground press | P | `findings/coffey-2026-09.md` |
| C3 | Phones home while idle/screen-off (mostly Google + installed apps); Netflix logs while asleep | P | `findings/coffey-2026-09.md` |
| C4 | Preinstalled factory test tool runs system-privileged; retail upload flow dormant | P | `findings/coffey-2026-09.md` |
| C5 | Bootloader welded — OEM-unlock disabled, AVB locked, verified-boot green (bootloader-enforced). Owner's unit reports `ro.boot.flash.locked=1`, `verifiedbootstate=green`, `vbmeta.device_state=locked`, `sys.oem_unlock_allowed=0`, `ro.oem_unlock_supported` unset (2026-11-04/05) | P (lock state, device-reported) / B (that it can't be flipped) | `research/root-study.md` §A; `research/coffey-device-checks-2026-11-04/`; probe `results/INDEX.md` PF-4 |
| C6 | Factory-tool userland doors are real but SELinux-boxed (system-UID, not root) | P | `research/root-study.md` §B/C |
| C7 | Stock CoreELEC recovery is **state-changing** (writes env via `fw_setenv`, no rollback) — fails a read-only boundary | P | `research/boot-policy-packet-2026-11-02/.../COFFEY-CE-RECOVERY-AUDIT.md` |
| C8 | CVE-2026-43499 futex-PI fix dated: first GKI tag 2026-08-05, first ASB Nov 2026 | P/R | `research/boot-policy-packet-round2-2026-11-03/COFFEY-R2-1-CVE-TIMELINE.md` |
| C9 | FCC IDs `2AYYS-CS116K4Y`/`…K4O` (Luxshare); FORESEE 16 GB eMMC + S905X5M | P/R | `research/boot-policy-packet-round2-2026-11-03/COFFEY-R2-2-FCC-HARDWARE-ACCESS.md` |
| C10 | coffey's exact-build OTA captured (ZIP SHA-256 `ec755bd0…b1a7`); metadata matches `onn/coffey/coffey:14/URO4.260304.011.B1/15051976` field by field | P | `research/coffey-ota-capture-2026-10-09/COFFEY-OTA-CAPTURE.md` |
| C11 | coffey kernel = GKI `5.15.196-android14-11-g3d26c188ef7e-ab14657224`, built 2026-01-03; vendor modules built against a different kernel build | P | `research/coffey-ota-capture-2026-10-09/COFFEY-OTA-FINDINGS.md` O2–O3 |
| C12 | coffey runs the Amlogic **vendor** driver stack (DT compatibles match CoreELEC `common_drivers`, not mainline); base DT `s7d_s905x5m_bm202`, PSCI 0.2, 2 GiB usable | P | `…/COFFEY-OTA-FINDINGS.md` O4–O6 |
| C13 | Bootloader = signed Amlogic container (build `S7D-s905x5m-26030511BBST`); every stage body after the headers is opaque | P (layout) / H (encrypted vs. packed) | `…/COFFEY-OTA-FINDINGS.md` O7–O9 |
| C14 | coffey kernel source = `kernel/common` `3d26c188ef7e` (branch point of `android14-5.15-2026-01`). **CVE-2026-43499 (GhostLock) and CVE-2026-99169 affected code present**; Bad Epoll, CVE-2026-43074, -23259, -99221 **not applicable** | P | `research/coffey-cve-applicability-r4-2026-11-03/`; probe `results/INDEX.md` PF-1 |
| C15 | Root `systemcontrol` HIDL service (`setBootEnv`, `writeSysfs`, key/property writes among ~300 methods) is **reachable at the SELinux layer by third-party apps** (`untrusted_app`, `untrusted_app_32`), not by `shell`/adbd; no caller-identity API imported (in-process check absent: H); its own policy can't write bootloader/boot/vbmeta/super/misc/param partitions | P (policy, imports) / U (end-to-end) | `research/coffey-systemcontrol-authz-2026-11-03/`; probe `results/INDEX.md` PF-3 |
| C16 | coffey's shipped device tree = Amlogic `bm202` reference board + 19 onn edits; CoreELEC generic 2g matches on memory/secmon/PSCI/console UART/eMMC but enables absent hardware, binds a different GPU driver, reserves ~284 MiB more media memory (candidate, not coffey-ready) | P | `research/coffey-dtb-comparison-2026-11-04/` |
| C17 | `odm_ext` is the only firmware partition outside verified boot (no fstab `avb`, not in vbmeta); its PQ database/INI are parsed by root `systemcontrol` with CRC/version checks only; only `init`/`update_engine`/`fsck`/`e2fs` may write it (no app/shell path found) | P | `research/coffey-odmext-consumers-2026-11-04/` |
| C18 | Android-side boot steering goes through the U-Boot env as well as `/misc`; boot-control and OEM-lock HALs are `systemcontrol` clients; OEM-unlock-allowed = env `ubootenv.var.lock`, reachable by `shell` (OEM-lock HAL) and apps (via C15); `/misc` writable only by system boot/update components; `fastbootd` lock-gated; `bootloader.img` has no plaintext dispatch logic | P (inputs, policy) / U (what BL33 does) | `research/coffey-boot-dispatch-2026-11-04/`; probe `results/INDEX.md` PF-2 |
| C19 | Two sibling onn **4K Pro** models have a first-hand persistent **AVB-lock** unlock: `jarvis` (same build train `URO4.260304.011.B1/15051976` as coffey) and `jarvis2` (same `S905X5M/S7D` SoC). 2024 route = set `ubootenv.var.storeboot` via SystemControl → unsigned EL2 payload off a one-use USB gate → AVB trusted-app (UUID `023f8f1a…`, cmd 3) writes secure state `1→0` (`flash.locked=0`, vbmeta unlocked, orange). No key forged; "specific to the tested bootloader." Authors state it is **not** a hardware-secure-boot defeat or BL33 replacement. **coffey-untested** | R | `research/onn-pro-unlock-ingest-2026-11-12/` |

## Hard walls (what blocks us)

| Wall | Why it holds |
|---|---|
| Welded bootloader | Hardware secure boot (signed ROM/BL2) + BL33 replacement stay welded → no custom first-stage, no custom ROM. **But the _AVB_ lock is shown flippable on sibling S905X5M/S7D silicon** (C19, R): a TEE AVB trusted-app writes secure state `1→0`, which would ungate `fastbootd` and enable persistent (flashed) root. coffey's own bootloader build differs (fixed-address payload won't port, C13); whether coffey's AVB path is reachable is now empirical, not assumed — vector #5 |
| SELinux on factory tool | System-UID writes confined to a tiny domain; not root |
| dm-verity / AVB | Any `boot`/`system`/`vendor` write bricks at next boot on a locked device |
| `env`/`misc`/`param` unreadable w/o root | Can't back them up → bootloader/env experiments stay documented-not-run |
| Kernel exploit is arm64 from-scratch | ~~Public GhostLock work is jarvis2-specific~~ — **superseded 2026-11-04:** a public repo claims a coffey-specific GhostLock port for `URO4.260304.011.B1` (R, not opened). The epoll PoCs don't apply to coffey's build (C14). Per-boot root still leaves the bootloader lock intact (C5) |
| BL2/BL33 opaque offline | Stage bodies after the signed headers show uniform byte statistics and no markers, so U-Boot's env/`bootcmd` handling can't be read offline (C13) |

## Ranked priority vectors (active leads)

| Rank | Vector | State | Next discriminating step |
|---|---|---|---|
| 1 | ~~Capture coffey's own OTA + kernel + DTB + `systemcontrol` ELF~~ | **DONE** (captured 2026-10-09, ingested 2026-11-03) | now an input to #2/#3 and Phases B/D/E/F — `research/coffey-ota-capture-2026-10-09/` |
| 2 | CVE-2026-43499 applicability + the ranked post-March CVE check-list | **P — affected code present** (R4); remaining H rows: framework, `wpa_supplicant` patch state. **Unit confirmed (2026-11-04):** on the analyzed build; `adbd`/ART still the shipped `340090000` modules | offline: framework patch comparison, unpack `odm`/`oem`; device: wireless-debugging state |
| 3 | **Test the onn 4K Pro AVB-unlock preconditions against coffey's own artifacts (C19)** | **§2.1 done 2026-11-12 (MISS, P-bounded); §2.2/§2.3 open** | AVB TA UUID `023f8f1a…` **absent** from coffey's 11 loadable TAs, boot images, TEE clients + `systemcontrol` (no hit, any byte-order) — easy transfer ruled out; built-in service stays U behind C13 (`…/COFFEY-TA-UUID-SCAN.md`). Still open: can coffey `systemcontrol` set `ubootenv.var.storeboot` (§2.2); bound the USB-boot gate (§2.3) |
| 4 | ~~Two epoll CVEs (Bad Epoll / CVE-2026-43074) arm64 root~~ | **closed — not applicable to coffey's build** (R4) | see dead ends; re-check only if coffey takes an OTA to a newer GKI release |
| 5 | **UART / serial-console path to the env/misc/param wall** | **H — candidate pads found** | match board rev to owner's retail unit label, then continuity/scope-probe the actual board |
| 6 | darkknight provenance-backed OTA (build-identity comparator) | U | capture from darkknight's real update flow, match build identity |
| 7 | twilight (Box S 3rd Gen) A14 OTA — `systemcontrol` ELF comparator | **deprioritized** — coffey's own ELF analyzed (C15) | only useful as a cross-device comparison (does the same policy ship elsewhere?) |
| 8 | **`systemcontrol` app-reachability (C15)** | P policy / U end-to-end | **disclosure decision first**; any device-side confirmation is a separate, maintainer-approved proposal under track §6, and never a write method |

## Dead ends / closed vectors (bounded negatives — do not re-run)

| Closed | Bounded as | Source |
|---|---|---|
| Newer public Android 12–14 `CPQControl`/`systemcontrol` source | all 1 branch + 67 tags of Amlogic frameworks repo (2016–2020), AOSP yukawa a12/13/14/main + BayLibre pkg, enumerated ROM-dump set | `…/COFFEY-PQ-ANCHORS-AD14-DELTA-v2.md` |
| Provenance-backed **darkknight** stock OTA | not found publicly; Xiaomi guide is docs not firmware; OS3.0.2.0 is a Box 5 *MAX* (`MOB1MB-5M`) report, model-code mismatch vs `MOB2MB-5P` | `…/COFFEY-DARKKNIGHT-OTA-RECON.md` |
| ~~Prior coffey-specific root/CoreELEC/unlock work~~ | **reopened 2026-11-04:** the 11-03 bounded negative held for its search set, but a public coffey GhostLock root repo (`chaitan3/ghostlock-coffey`, R, not opened) now exists. Still no public coffey CoreELEC/unlock work found | `…/COFFEY-R2-3-COMMUNITY-SWEEP.md`; `research/coffey-device-checks-2026-11-04/` |
| ~~UART pinout from public docs~~ | **reopened → lead found:** FCC photo review (R2-5) found a candidate 4-pad `GND/TX/RX/GND` header; now priority vector #4, no longer a dead end | `…/COFFEY-R2-5-FCC-PHOTO-REVIEW.md` |
| Booting donor CoreELEC recovery as a shortcut | disqualified — it mutates persistent env (C7) | `…/COFFEY-CE-RECOVERY-AUDIT.md` |
| Runtime root → custom ROM | impossible without bootloader unlock (two separate locks) | `research/root-study.md` §D-bis |
| KernelPatch / APatch as a route in | kernel fits on paper (arm64, 5.15, `KALLSYMS=y`), but static patching needs a booted modified `boot.img` (locked + AVB) and runtime loading needs a prior kernel compromise; a post-unlock/post-exploit tool, not a way in | `research/root-study.md` §D-ter |
| Epoll CVEs (Bad Epoll CVE-2026-46242, CVE-2026-43074) on coffey | not applicable: coffey's `eventpoll.c` (commit `3d26c188ef7e`) lacks the 5.15.209 refcount refactor that introduced both; the earlier "present" claim matched the newer branch tip | `research/coffey-cve-applicability-r4-2026-11-03/` |
| Amlogic `pppoe_wrapper` / DroidLogic subtitle CVEs (119737–119739) | no matching binary/service in `system`/`system_ext`/`product`/`vendor` (policy leftovers only); `odm`/`oem` not unpacked | same |

See [`research/search-methodology.md`](research/search-methodology.md) for how negatives are bounded.
