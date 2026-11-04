# coffey boot-policy & alternate-OS track

> **Status: scaffold / agenda, not a result.** This file frames the "can coffey boot an alternate OS
> (CoreELEC / custom ROM), and what does the bootloader actually verify" question and holds the plan to
> answer it. **No boot bypass, bootloader unlock, AVB bypass, or working CoreELEC port is established.** The
> decisive evidence is coffey's own bootloader/firmware artifact set plus an exact CoreELEC recovery image,
> inspected offline. Both are now in hand: the CoreELEC audit (Phase C) and coffey's OTA capture (Phase A,
> 2026-11-03). The remaining phases are being filled from them.
>
> This track is the companion to [`root-study.md`](root-study.md): that file concludes flashing a custom ROM
> requires breaking the welded bootloader (section A + the runtime-root-vs-unlock table). This file is the
> disciplined attempt to *map* that weld rather than assume it.

Origin: external research handoff by Codex (`ONN-COFFEY-CLAUDE-HANDOFF-2026-11-02`, rev 2), reviewed and
reframed here. Source IDs `S*`/`F*`/`N*` below refer to that handoff's source map (reproduced in §Sources).

> **Progress — 2026-11-02 public-artifact pass (Codex).** First results are committed under
> [`boot-policy-packet-2026-11-02/`](boot-policy-packet-2026-11-02/) (text reports only; firmware blobs kept
> out of git, re-fetchable via the hash-pinned manifest). Headline: **Phase C answered** — the stock CoreELEC
> recovery is *state-changing* (writes the persistent boot env via `fw_setenv`, 11 assignments, no rollback),
> so it **fails the read-only boundary**; do not boot it on coffey. Public comparators (CoreELEC release +
> nightly, donor DTBs, upstream S7D, PQ donor source, slimBOX unlock = standard `fastboot flashing unlock`)
> are pinned. **Still nothing established about coffey itself** — no acceptance, root, parser-input control, or
> authorization gap; darkknight OTA and coffey's own artifact set remain missing.

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

> Status (2026-11-02): a **provenance-backed darkknight OTA was not obtained** — N1/N2 don't supply a verified
> one, and no donor was relabeled as darkknight. The CoreELEC *Xiaomi Box S 3rd Gen* DT is a comparator but is
> **not** darkknight stock firmware. Public searches found no provenance-backed darkknight stock image, so this
> artifact stays **U — unresolved**; do not substitute a comparator for it.
>
> Treat the Xiaomi owner guide (N1/N2) as a **device-specific documentation source, not the firmware itself**.
> Its "no OTA" statement may be **stale** — a later owner report mentions build **OS3.0.2.0**, so a normal
> darkknight update flow likely does serve an OTA. The highest-value darkknight input is therefore the **exact
> OTA package captured from darkknight's normal update flow**, with URL, request/response headers, date,
> SHA-256, and source/target build metadata. Only after **matching build identity** should it be compared
> offline against coffey, and no darkknight offsets/keys/DTB/images transfer into a coffey conclusion.
>
> OTA recon (2026-11-02,
> [`…/public-lookups-addendum/COFFEY-DARKKNIGHT-OTA-RECON.md`](boot-policy-packet-2026-11-02/public-lookups-addendum/COFFEY-DARKKNIGHT-OTA-RECON.md)):
> Xiaomi/Google OTA endpoint *families* are documented as leads but **no darkknight endpoint or package is
> confirmed** (status `U`). Important caveat: the **OS3.0.2.0** report is for a device labelled **Box 5 *MAX*
> (`MOB1MB-5M`)**, whereas the darkknight comparator here is **Box 5 (`MOB2MB-5P`)** — same codename and
> `MiTV-AZFU0`, but a product-code mismatch, so OS3.0.2.0 is **not** confirmed for the exact MOB2MB-5P
> hardware. Do not synthesize a URL from the build string; capture it from the device's real update check.

## 3a. Next evidence priority (2026-11-02)

The public-artifact pass is largely spent; further general web searching is low-yield. The two inputs that
actually close the biggest gaps are:

1. **coffey's own artifacts** (the keystone, device-side — Adam's step): the matching `systemcontrol` ELF and
   the coffey DTB, each with **SHA-256 + build ID/fingerprint**, plus the coffey OTA/bootloader container.
   These turn every `B`/`U` cell in §2–§3 and Phases A/B/D/E/F into build-specific results.
2. **A provenance-backed darkknight OTA** captured from its normal update flow, with full metadata (see §3) —
   compared offline against coffey *only after* build-identity match.

Everything else (more donor comparators, more forum reports) is secondary until these land. Keep the
P/R/B/H/U labels on every new item, and do not transfer donor offsets, keys, DTBs, or images into coffey
conclusions.

> **Round-2 public lookups done (2026-11-03)** —
> [`boot-policy-packet-round2-2026-11-03/`](boot-policy-packet-round2-2026-11-03/). The public surface is now
> worked and bounded:
> - **R2-1** dated the GhostLock futex-PI fix (first GKI tag 2026-08-05, first ASB Nov 2026) → coffey's 2026-03
>   SPL is likely pre-fix (`H`); folded into [`root-study.md`](root-study.md) D-bis.
> - **R2-2 + R2-5** found FCC IDs `2AYYS-CS116K4Y`/`…K4O` (Luxshare), the FORESEE 16 GB eMMC + S905X5M board,
>   and — on inspecting the exhibit photos (R2-5) — a **candidate 4-pad `GND/TX/RX/GND` header** on p.3 of
>   internal-photo exhibit 7952340 (`H`, photo lead). First concrete lead on the serial-console path to the
>   `env`/`misc`/`param` blocker; needs a board-revision match to the owner's retail unit, then physical
>   probing. No pin order/voltage inferred from the photo.
> - **R2-3** bounded negative: no prior coffey-specific root/CoreELEC/unlock work exists (only user-space ADB
>   debloat).
> - **R2-4** pinned a public coffey OTA catalog fingerprint `onn/coffey/coffey:14/URO4.260304.011.B1/15051976`
>   (SPL 2026-03-01) + the capture-fields checklist — a metadata comparator, not a captured package.
>
> Remaining public item: the queued **twilight EROFS** read (Phase F comparator). Everything else waits on the
> coffey OTA/ELF/DTB capture.

> **Progress — coffey's own artifacts (captured 2026-10-09, ingested 2026-11-03):**
> [`coffey-ota-capture-2026-10-09/`](coffey-ota-capture-2026-10-09/). The exact-build OTA
> (`URO4.260304.011.B1`, ZIP SHA-256 `ec755bd0…b1a7`) is captured and matches the expected fingerprint field by
> field. The kernel (GKI `5.15.196-android14-11-g3d26c188ef7e-ab14657224`), base DT `s7d_s905x5m_bm202`, module
> inventories, bootloader container, and the **`systemcontrol` ELF** are extracted and hash-pinned off-repo.
> Bootloader: signed `@ML`/`@AMLBOOT` container (build `S7D-s905x5m-26030511BBST`); every stage body after the
> headers is **opaque** (encrypted or packed; transform/key unresolved), so BL33 can't be grepped offline.
> Phase A is done; B/D/E/F can now use coffey's own data (see each phase).

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

### Phase A — Ground & preserve existing evidence  _(status: DONE — 2026-11-03, see [`coffey-ota-capture-2026-10-09/`](coffey-ota-capture-2026-10-09/))_
Manifest = [`COFFEY-OTA-CAPTURE.md`](coffey-ota-capture-2026-10-09/COFFEY-OTA-CAPTURE.md) +
[`COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](coffey-ota-capture-2026-10-09/COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt).
Still missing: VINTF manifests and SELinux artifacts not yet pulled out of the extracted images; AVB/`vbmeta`
and the OTA signature not verified.
Locate the latest collection report, matching OTA, bootloader container, DTB/DTBO, boot/vendor_boot, AVB
reports, `systemcontrol` ELF+libs, init files, VINTF manifests, SELinux artifacts. Record for each: path,
size, SHA-256, build/fingerprint, extraction tool+version, relation to the live collection. Preserve
originals; never silently merge across OTA builds.
**Acceptance:** `COFFEY-ARTIFACT-MANIFEST.md` + an explicit missing-prerequisite list.

### Phase B — Reconstruct boot dispatch offline  _(donor scaffold done 2026-11-02; S7D specifics U, coffey half blocked on A)_
A public stage/signature/rollback **scaffold** exists:
[`boot-policy-packet-2026-11-02/public-lookups-addendum/COFFEY-BOOT-CHAIN-MODEL.md`](boot-policy-packet-2026-11-02/public-lookups-addendum/COFFEY-BOOT-CHAIN-MODEL.md).
It names the boot objects (`BL2`, `BL2E`, `BL2X`, `DDRFIP`/`DEVFIP`/FIP, `BL31/32/33`) and keeps **Amlogic
boot-firmware anti-rollback (BL2 CVN/eFuse) separate from Android AVB rollback indexes**, but **no public S7D
source states which stage authenticates the next or where the rollback counter lives** — those stay `U` until
coffey's own bootloader container is extracted. **Update 2026-11-03:** it is extracted
([`…/COFFEY-OTA-FINDINGS.md`](coffey-ota-capture-2026-10-09/COFFEY-OTA-FINDINGS.md) O7–O9). BL2E/BL2X are
named in a plaintext `@AMLBOOT` table but their bodies, and the later stages, are opaque, so the token grep
below can't run on BL2/BL33. Tokens may still turn up in plaintext places (`vendor_boot` ramdisk, env defaults
in the OTA).
Grep extracted images for: `update`, `switch_bootmode`, `get_rebootmode`, `bootcmd`, `storeboot`;
`recovery_from_udisk/sdcard/flash`; `aml_autoscript`, `recovery.img`, `autoscr`, `source`;
`usb_burning`, `*_burningcfg`, `aml_sdc_burn.ini`; `imgread`, `bootm`, `get_avb_mode`, `get_valid_slot`;
`saveenv`, `fw_setenv`, env import/export; verification/rollback diagnostics.
For each hit classify: active default · persisted env value · help string · dead code · handler. Follow
cross-refs into callers + verification routines. Separate OTA-packaged defaults from the live persisted env.
**Table:** Path · Entry condition · Media/source · Handler · Verification · Slot dependence · Persistent side
effects · Evidence offset · Confidence. **Acceptance:** `COFFEY-BOOT-POLICY-MAP.md`.

### Phase C — Audit the exact CoreELEC recovery image  _(status: DONE — 2026-11-02)_
Done for CoreELEC `22.0-Piers_rc1` Generic + the Nov-3 nightly. See
[`boot-policy-packet-2026-11-02/COFFEY-CE-RECOVERY-AUDIT.md`](boot-policy-packet-2026-11-02/COFFEY-CE-RECOVERY-AUDIT.md).
**Verdict: the stock recovery setup does not fit a read-only boundary** — `init` translates the bundled
`aml_autoscript` `setenv` lines into individual `fw_setenv` calls (11 assignments incl. `bootfromnand`,
`upgrade_step`, `bootcmd`) against the internal env backend (`/dev/env`, `fw_env.config`), then reboots with
no transaction/rollback. Release `init` matches its pinned CoreELEC recipe byte-for-byte after documented
substitutions; the nightly only fixes a `UPDATE_SYSTEM.md5` source-name mix-up. **Whether coffey accepts or
can execute this image is entirely unresolved**, and the FAT USB being mounted read-only does *not* stop the
internal env writes — so it must not be booted on coffey as a substitute for the Phase-A artifact work.

### Phase D — Compare board descriptions without transplanting  _(donor half done 2026-11-02; coffey half unblocked 2026-11-03 — coffey base DT `s7d_s905x5m_bm202` in hand, lineage/arch/driver maps in `coffey-ota-capture-2026-10-09/source-notes/E0003–E0006C`)_
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

### Phase F — Finish PQ/HIDL caller authorization  _(status: DONE offline — 2026-11-03, [`coffey-systemcontrol-authz-2026-11-03/COFFEY-PQ-AUTHORIZATION.md`](coffey-systemcontrol-authz-2026-11-03/COFFEY-PQ-AUTHORIZATION.md); end-to-end app reachability `U`, device-gated)_
> **Result (P unless noted):** `systemcontrol` runs as root and registers HIDL `ISystemControl` @1.0/@1.1
> (290/306 methods, incl. `setBootEnv`, `writeSysfs`, `writeUnifyKey`, `setProperty`). coffey's loaded policy
> (CIL stamps match `odm` `precompiled_sepolicy`) lets **`untrusted_app` / `untrusted_app_32` find and call
> it**, via explicit vendor rules. `shell`/adbd can't. The binary imports no caller-identity API (no in-process
> check evident, `H`); the env writer checks only the `ubootenv.var.` prefix. The service's own policy denies
> writes to bootloader/boot/vbmeta/super/misc/param/frp/factory and gives it no `CAP_SYS_ADMIN` or mount.
> Inherited offset `0x80cd8` is outside this ELF. Disclosure is advisable before publishing.

_Original agenda, kept for reference:_
A search for a newer public `systemcontrol`/`CPQControl` closer to Android 14 found **none**, and the negative
is now **bounded** (v2 re-sweep,
[`…/COFFEY-PQ-ANCHORS-AD14-DELTA-v2.md`](boot-policy-packet-2026-11-02/public-lookups-addendum/COFFEY-PQ-ANCHORS-AD14-DELTA-v2.md)):
**all 1 branch + 67 tags** of `Amlogic-Lineage/android_vendor_amlogic_common_frameworks` are 2016–2020 / Pie-era;
AOSP `yukawa` (android12/13/14/main) + its BayLibre vendor package carry no such service; and an enumerated
GitHub ROM-dump set yielded no qualifying `systemcontrol` ELF. The only public implementation remains the
**Android-Pie** `khadas-vims-pie_64` donor, whose stubbed/permissive permission routine says nothing about
coffey. **New comparator lead:** the `twilight` (Xiaomi Box S 3rd Gen) **Android-14 full OTA** is now pinned and
its `system`/`vendor` extracted — but both are **EROFS** and were unreadable on the author's host, so whether a
`systemcontrol` ELF is present is `U`. Enumerating that EROFS (read-only `dump.erofs`/`fsck.erofs`) is the one
open public step; it would at best yield an **H** build-ID/symbol comparator, never a coffey fact. The
authorization model still genuinely waits on coffey's own `systemcontrol` ELF (pin by SHA-256 + GNU Build ID
first). The trace steps below are unchanged.
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
