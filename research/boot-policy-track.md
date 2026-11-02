# coffey boot-policy & alternate-OS track

> **Status: scaffold / agenda, not a result.** This file frames the "can coffey boot an alternate OS
> (CoreELEC / custom ROM), and what does the bootloader actually verify" question and holds the plan to
> answer it. **No boot bypass, bootloader unlock, AVB bypass, or working CoreELEC port is established.** The
> decisive evidence — coffey's own bootloader/firmware artifact set plus an exact CoreELEC recovery image,
> inspected offline — has **not** been obtained yet. Sections below are placeholders to fill once those
> artifacts are in hand.
>
> This track is the companion to [`root-study.md`](root-study.md): that file concludes flashing a custom ROM
> requires breaking the welded bootloader (section A + the runtime-root-vs-unlock table). This file is the
> disciplined attempt to *map* that weld rather than assume it.

Origin: external research handoff by Codex (`ONN-COFFEY-CLAUDE-HANDOFF-2026-11-02`, rev 2), reviewed and
reframed here. Source IDs `S*`/`F*`/`N*` below refer to that handoff's source map (reproduced in §Sources).

## 0. The question

1. Does coffey expose any authenticated maintenance / recovery path that could load a non-stock image?
2. What does each such path actually **verify**, and does it **mutate persistent state** (env, slots, PQ db)?
3. Is there any route to an alternate OS (CoreELEC) that does **not** require first unlocking the bootloader?

Working assessment (from `root-study.md` + this handoff): **no.** The weld is bootloader-enforced, and every
alternate-OS report found so far for this SoC family either targets a different/unlockable board or already
assumes root / an unlocked bootloader / a working external boot. This file exists to confirm or refute that
against coffey's own artifacts, not to assume it.

## 1. Evidence classification (carried from the handoff)

- **P** primary source inspected · **R** first-hand report, not reproduced here · **B** inherited project
  baseline · **H** hypothesis needing coffey-specific evidence · **U** unresolved / insufficient access.
- A different URL is not independent confirmation. A README that cites a forum corroborates that a workflow
  exists, not that its mechanism is valid. Shared SDK ancestry ≠ identical config, keys, or OTP provisioning.

## 2. Inherited baseline (B — reconcile against the live collection before use)

| Item | Inherited value |
|---|---|
| Target | onn. 4K Plus Streaming, device `coffey` |
| Platform | Amlogic **S7D / S905X5M** |
| Software | Android 14; security patch 2026-03-01 |
| Kernel | `5.15.196-android14-11` |
| Memory | 2 GiB (DTB usable `0x80000000`) |
| Security state | verified boot green, vbmeta `device_state` locked, SELinux enforcing |
| Slots | A/B present |
| `odm_ext` | read-only ext4 mount, `nosuid,nodev`; prior analysis placed it **outside** AVB/dm-verity |
| `param` | writable mount, `nosuid,nodev` (mount writable ≠ shell-writable contents) |
| Boot packaging | OTA carries Amlogic `@AMLBOOT`/device-FIP with BL2E/BL2X |
| Vendor DT | `amlogic,meson-uart`; PSCI 0.2 via SMC (do **not** substitute mainline S7D bindings) |
| Service | `systemcontrol` runs as root in `u:r:system_control:s0`; owns `get/setBootEnv` → `env` partition |
| PQ / HIDL | `factorySetParamsDefault()` (no-arg, reaches reset/reseed — **has** persistent side effects); `getPQDatabaseInfo(int32_t)` side effects unresolved |

> Analysis identity is **fingerprint + bootloader version + board id + active slot + artifact SHA-256** — not
> marketing generation or purchase year. A recorded handler offset is meaningful only for its matching ELF.

## 3. Priority comparator: darkknight (Xiaomi Box 5) — N1/N2

Closest known firmware sibling: **Xiaomi Box 5, MOB2MB-5P, codename `darkknight`, S905X5M, Android 14, 2 GB**.
Owner docs report build `UD2A.240505.001.W1.OS2.0.7.0.UZFAABX`, kernel
`5.15.153-android14-11-g...-abOS2.0.7.0.UZFAABX`, with a partition listing that includes `odm_ext_a/b`,
`param`, `oem_a/b` and boot slots. Same SoC, same Android, same RAM class — a better boot/partition comparator
than jarvis2 (which matched the *kernel* for the root track but is a different board).

Caveat: similar hardware ≠ identical partition layout, service policy, boot keys, or unlock behavior. Treat any
darkknight image strictly as **host-side comparison material**; import no offsets, keys, DTB, or images into
coffey. The darkknight unlock/backup workflow explicitly **requires an already-unlocked bootloader + rooted
GSI via DSU** — it is not a locked-device bypass.

## 4. Corrections to keep (do not regress — from handoff §7)

1. Same S905X5M SoC ≠ identical U-Boot policy, keys, or OTP.
2. A correct DTB does not solve bootloader rejection (board *description* ≠ *authorization*).
3. External boot is not "read-only" merely because the OS image lives on USB.
4. A HIDL method declared without a visible check does not prove missing authorization.
5. A no-argument method is not harmless: `factorySetParamsDefault()` mutates persistent PQ state.
6. An env firmware path (e.g. an odm_ext Dolby reference) is not proof coffey executes unverified firmware.
7. Mainline compatibility strings / driver ancestry do not imply a vendor vulnerability.
8. Do not assume generic S7D USB/HDMI recovery or boot-partition protections from older-family docs.
9. Do not promise unbrickability.
10. A mainline/CoreELEC support entry is not an official coffey support declaration.

## 5. Plan — Phases A–F (fill once artifacts exist)

Each phase is **host-side, read-only** with respect to the device. These are offline artifact-analysis tasks;
the search tokens below are **tokens to grep in extracted files, not commands to run on the device.**

### Phase A — Ground & preserve existing evidence  _(status: BLOCKED — no artifacts in-repo)_
Locate the latest collection report, matching OTA, bootloader container, DTB/DTBO, boot/vendor_boot, AVB
reports, `systemcontrol` ELF+libs, init files, VINTF manifests, SELinux artifacts. Record for each: path,
size, SHA-256, build/fingerprint, extraction tool+version, relation to the live collection. Preserve
originals; never silently merge across OTA builds.
**Acceptance:** `COFFEY-ARTIFACT-MANIFEST.md` + an explicit missing-prerequisite list.

### Phase B — Reconstruct boot dispatch offline  _(depends on A)_
Grep extracted images for: `update`, `switch_bootmode`, `get_rebootmode`, `bootcmd`, `storeboot`;
`recovery_from_udisk/sdcard/flash`; `aml_autoscript`, `recovery.img`, `autoscr`, `source`;
`usb_burning`, `*_burningcfg`, `aml_sdc_burn.ini`; `imgread`, `bootm`, `get_avb_mode`, `get_valid_slot`;
`saveenv`, `fw_setenv`, env import/export; verification/rollback diagnostics.
For each hit classify: active default · persisted env value · help string · dead code · handler. Follow
cross-refs into callers + verification routines. Separate OTA-packaged defaults from the live persisted env.
**Table:** Path · Entry condition · Media/source · Handler · Verification · Slot dependence · Persistent side
effects · Evidence offset · Confidence. **Acceptance:** `COFFEY-BOOT-POLICY-MAP.md`.

### Phase C — Audit the exact CoreELEC recovery image  _(independent of A; needs the image)_
Obtain one official identified release/nightly; record URL, date, hash, source commits. Inspect on host
**without booting it or running its scripts.** Determine image format, kernel, initramfs contents, entry
scripts, env backend, and **all persistent writes** (raw writes, mounts, env migration, partition-metadata
changes, reboot flags) — trace normal *and* error paths, not just a `fw_setenv` grep.
**Acceptance:** `COFFEY-CE-RECOVERY-AUDIT.md` — side-effect inventory + verdict on whether it fits the
read-only boundary. No live boot in this phase.

### Phase D — Compare board descriptions without transplanting  _(depends on A)_
Diff coffey vendor DT vs exact-build CoreELEC Xiaomi/Ugoos/C5 refs and upstream S7D [S5]: root compatible/
model + includes; phys/usable/reserved memory; UART compatible/clocks/IRQs/enabled; PSCI + firmware
assumptions; USB controller/PHY/role; storage + partition metadata; GPU/video/secure-memory deps.
**Acceptance:** `COFFEY-DTB-COMPARISON.md` semantic diff. A generic 2 GiB DTB is a candidate, not coffey-ready.

### Phase E — Expand odm_ext consumers  _(depends on A)_
Map each candidate consumer to boot stage, privilege, path resolution, integrity check, parser, mutability.
Search logo/EDID/firmware/PQ references, then confirm *actual* load branches; separate immutable packaged
input from writable copies/reseeds.
**Acceptance:** `COFFEY-ODMEXT-CONSUMERS.md` consumer graph, proven vs possible edges; no assumed path from
shell-controlled bytes to a privileged parser.

### Phase F — Finish PQ/HIDL caller authorization  _(depends on A)_
Reconcile the recorded handler offset against the exact ELF+hash. Trace service registration, Binder/HIDL
transport access, SELinux service-discovery/call policy, UID/PID checks, wrappers, callee checks, file access.
Map side effects of `factorySetParamsDefault()` **offline — do not invoke**; establish prerequisites of
`getPQDatabaseInfo()` before calling it a safe query.
**Acceptance:** `COFFEY-PQ-AUTHORIZATION.md` — authorized caller classes + precise unresolved checks; report
separately whether each method is declared / registered / discoverable / callable / able to reach a sensitive
op. (PQ anchors from N5, preserve the `MOUDLE` spelling: `CFG_ALL_PQ_MOUDLE_ENABLE`, `mPQConfigFile->GetString`,
`mPQdb`, `mSSMAction->SSMReadDnlpMode`, `CPQControl::LoadPQSettings`, `CPQControl::SetBacklight`.)

## 6. Boundaries (hard limits for this track)

Host-side artifact inspection, documentation, continuation of read-only analysis **only**. Do **not**: execute
installers, flash partitions, alter boot env, change slot state, invoke PQ resets, disable updates, load
foreign bootloaders, or boot recovery media. Even a reboot changes operational state; "no host write" is not
enough if the invoked firmware/recovery writes on its own. A device experiment is a separate, concrete
proposal with exact image hash, expected behavior, persistent-side-effect assessment, and recovery
prerequisites. **A documented enforcement boundary is a successful result — do not manufacture a bypass to
look productive.**

## 7. Return packet (produce as artifacts land)

`COFFEY-ARTIFACT-MANIFEST.md` · `COFFEY-BOOT-POLICY-MAP.md` · `COFFEY-CE-RECOVERY-AUDIT.md` ·
`COFFEY-DTB-COMPARISON.md` · `COFFEY-ODMEXT-CONSUMERS.md` · `COFFEY-PQ-AUTHORIZATION.md` ·
`COFFEY-MULTILINGUAL-COMPARISON.md` + a relay summary (what changed, evidence IDs, blockers, next check).
Priority after grounding: **B and C**, then E/F where material permits. Per-evidence record:
ID · claim · target build · artifact SHA-256 · source revision · file+offset/line · observation ·
interpretation · competing explanations · next discriminating check.

## 8. Sources (from the handoff; verify/pin before relying on any)

Primary (P): S1 Amlogic U-Boot G12B config (pinned commit) · S2 U-Boot `source` cmd · S3 U-Boot env ops ·
S4 Amlogic S7D BM202 patch (2025-03) · S5 upstream `amlogic-s7d.dtsi` · S10 AOSP AVB + boot-flow.
First-hand reports (R): S6 HK1 SC2 UART log · S7 twilight dualboot (unlocked/rooted prereq) · F1–F8 CoreELEC
Discourse threads (Xiaomi Box S 3rd Gen, HD+ stick, X96 M200/S7D, BuzzTV/Homatics, Ugoos X5M Pro, older Onn
S905Y2, HK1, Homatics env).
Non-English (R/U): N1/N2 darkknight owner docs + unlock/backup · N3 4PDA X88 root-dependent odm_ext overlay ·
N4 4PDA full-dump (external boot assumed) · N5 4PDA X96 Air PQ source anchors · N6 slimBOX X96 M200 corpus
(`Unlock_Bootloader.cmd` — inspect, do not run) · N7 ZNDS X88 report · N8 Habr/Bastion S905X hardware-security
method · N9 secondary/blocked sources.
Tooling leads: S8 pyamlboot (no coffey guarantee) · S12 CoreELEC/common_drivers branches + `coreelec.org/dtb`
(no coffey entry found) · S13 fork release notes.

Full URLs live in the originating handoff doc; pin a revision when acquiring any artifact.

## 9. Credits

- **Codex** — the external research handoff (`ONN-COFFEY-CLAUDE-HANDOFF-2026-11-02`, rev 2) this track is built
  from: the source corroboration, evidence discipline, corrections list, and Phase A–F plan.
- The upstream and community authors behind the sources above — Amlogic (S7D DT), the U-Boot and AOSP AVB
  documentation, the CoreELEC developers and forum contributors (Portisch, vpeter, and others), the darkknight
  (`xpxp233333`), slimBOX, 4PDA, ZNDS, and Habr/Bastion researchers. Go to the originals.
