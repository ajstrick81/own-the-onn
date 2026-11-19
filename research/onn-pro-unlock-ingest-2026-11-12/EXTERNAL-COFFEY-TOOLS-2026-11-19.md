# External coffey tools — OnnDemand-4kplus and onn-unlock-probe (2026-11-19, grade R)

> Two public repos that target the onn 4K **Plus** (or claim to), both downstream of the OpenEnsemble 4K Pro work
> ingested in this packet (C19). Read at source on 2026-11-19 (README, docs, and for the probe, `native/probe.c`
> and `tools/run_probe.sh` in full). **Grade R** — third-party reports; **nothing here has been run on our unit**.
> Per the repo rules they are **cited, never vendored**: the probe has no license, and OnnDemand's inherited jarvis2
> material carries no license grant. Running either is the maintainer's step on his own machine; the read-only
> probe run is written up as a track-§6 proposal in
> [`PROPOSAL-UNLOCK-PROBE-READONLY.md`](PROPOSAL-UNLOCK-PROBE-READONLY.md).

## 1. ShaneBreazeale/OnnDemand-4kplus — temporary root + root SSH on coffey

**Identity:** `https://github.com/ShaneBreazeale/OnnDemand-4kplus` · 15 commits on `main`, oldest `b7cdef7`
(2026-11-11, by openensemble: "2026 onn 4K Pro unlock and permanent root"), latest `3c454d0` (2026-11-17).

| Claim (verbatim where quoted) | Our reading |
|---|---|
| "**Tested device:** onn. 4K Plus, Android 14, firmware build **15051976** (`URO4.260304.011.B1`)"; topics include `coffey` | **Exact match** to our unit's build (C10, PF-4) |
| "Live SSH tests on one coffey unit verified root UID 0 …" | One unit; confirmation is `id -u` → `0` |
| Same sentence: "These tests **reused an existing root loop** over USB ADB forwarding. They did **not validate a new exploit attempt**, direct LAN access, or every firmware version." | The *root acquisition* itself is not validated by these tests — only the SSH layer on top of an already-rooted session |
| "Based on openensemble/onn-4k-pro-2026-unlock-root, which retargets the 2026 onn 4K Pro unlock/root work to the 4K Plus"; ships "the coffey root payload, and its loader" under `vendor/coffey` | A coffey-specific port of the jarvis2 temp-root path is **claimed** (`vendor/coffey` not read) |
| **No mention of GhostLock or CVE-2026-43499** in README, `docs/COFFEY.md`, `docs/ROOT_PATH.md`, `docs/HOST_TOOLS.md`, `LICENSE_SCOPE.md` | The bug used is **not stated** by this repo. Do not record it as a GhostLock confirmation |
| "A reboot clears temporary root and stops SSH"; "does not unlock the bootloader, flash replacement boot images, or require a factory reset" | Per-boot only — the same ceiling as root-study §D-bis / section A |
| `ROOT_PATH.md`: "relaxes SELinux enforcement and kernel module verification for the rooted boot" | Security is reduced until reboot (README says so too). Tension with "keeps the existing boot configuration" unresolved from the docs |
| "SSH defaults to device loopback through authorized ADB forwarding. Direct LAN access is an explicit option." | Keep the default |
| "Permanent root and bootloader unlocking on the 4K Plus are outside the supported workflow." | Consistent with the weld (C5/C13) |
| License: own code Apache-2.0; "The inherited upstream material carries no open-source license grant and is not relicensed here." Inherited list includes `bin/armeabi-v7a/read_state`, `bin/armeabi-v7a/unlock_once`, `native/unlock_once.c`, `root_workflow.py`, `profile.json` | Cite only. Note the jarvis2 **AVB-TA reader/writer** (`read_state`, `unlock_once`) rides along, though unlock is out of scope for the Plus |

Not read: `vendor/coffey`, `native/rootssh`, SSH/RESTORE/RESULTS docs, tests, binary contents. The README's
"private repo" clone note conflicts with the repo being public.

**What it means for the study (graded):**
- **Runtime root (track 2):** a second public coffey temp-root claim (after `chaitan3/ghostlock-coffey`, 2026-11-04,
  not opened), on our **exact build** — **R**. It does not raise our CVE-2026-43499 applicability, which is already
  **P** from coffey's own kernel source (C14/PF-1) and stronger than any R report. The mechanism is unstated, so it
  is not GhostLock evidence.
- **Walls:** a temp-root shell is exactly what the "`env`/`misc`/`param` unreadable without root" wall lacks, and
  it would let the maintainer read those partitions and capture kernel/DTB/`systemcontrol` live — **if** it
  reproduces on our unit (then P). Weld, AVB/dm-verity and alternate-OS are unchanged.
- **Hygiene if run:** auto-updates off first (an update likely closes it); keep telemetry captures on clean,
  non-root boots so root-session traffic can't contaminate scenarios.

## 2. kushmint/onn-unlock-probe — read-only AVB lock-bit check

**Identity:** `https://github.com/kushmint/onn-unlock-probe` · 1 commit `6439f22` (2026-11-18) · no license ·
prebuilt `bin/arm64-v8a/` and `bin/armeabi-v7a/` (NDK r28c, API 28; contents not verified) · credits
openensemble for the AVB-TA protocol.

**Targets:** README names "the **onn Plus** and the **onn 4K Pro (2024)**"; it never says `coffey` or "4K Plus".
Ambiguous — treat coffey as an untested target. `run_probe.sh` prints but **does not check** the model.

**What `native/probe.c` does (read in full):**
- Requires `getuid() == 2000 && geteuid() == 2000` — **normal adb shell, no root**.
- Opens `/dev/tee0`; `TEE_IOC_VERSION` must report OP-TEE with the GP capability, else `not_optee_gp`.
- Opens a session to UUID `023f8f1a-292a-432b-8fc4-de8471358067` — the C19 AVB trusted app.
- `PROBE_TA_CMD_READ 2u` (`VALUE_OUTPUT`) reads `secure_lock_state` (0 unlocked, 1 locked);
  `PROBE_TA_CMD_WRITE 3u` (`VALUE_INPUT`) writes it.
- **Default: one READ, then exit. No write.** If already 0: `already_unlocked_no_write_attempted`.
- `--toggle-test` (only if initial = 1): WRITE 0 → READ → WRITE 1 → READ. Never reboots.
- Output: newline-delimited JSON, final `{"stage":"finished","outcome":…,"exit_code":N,"rebooted":false}`.

Outcomes (code): `no_tee_device` (10) · `tee_version_ioctl_failed` (11) · `not_optee_gp` (12) ·
`allocation_failed` (13) · **`ta_not_present_or_session_refused` (14)** · `initial_read_failed` (20) ·
`initial_value_unexpected` (21) · `already_unlocked_no_write_attempted` (0) ·
**`locked_read_only_rerun_with_toggle_test_to_probe_further` (0)** · plus toggle-only outcomes 30–43 and
`toggle_test_passed_state_fully_restored` (0).

**Two defects in `--toggle-test` (from the code) — never run it:**
1. `alarm(toggle_test ? 20 : 8)` with **no SIGALRM handler** — a hang after the unlock write kills the process
   before the relock (inference from the missing handler).
2. If the mid-state READ fails it exits (`CRITICAL_midstate_read_failed…`) **without attempting the relock**.

Either leaves the box at lock state 0, and openensemble reports an unlocked reboot behaving like a factory reset.
The write also changes persistent secure boot state, which track §6 and `CLAUDE.md` rule out. The read alone
answers the study's question.

**Why it fits — it closes our §2.1 "U":** the offline scan
([`COFFEY-TA-UUID-SCAN.md`](COFFEY-TA-UUID-SCAN.md)) found this UUID in **none** of coffey's 11 loadable TAs, so
the only way it could exist on coffey is **built into** the opaque TEE OS (C13). The probe's read-only session open
tests exactly that, from userspace:

| Read-only outcome on coffey | Meaning | Effect |
|---|---|---|
| `ta_not_present_or_session_refused` (14) | No AVB TA under this UUID, loadable or built-in | §2.1 fully closed (P, bounded); supports C5; the jarvis/jarvis2 AVB route doesn't exist on coffey |
| `locked_read_only_…` (reads 1) | Built-in AVB TA present and answering | §2.1 flips; the jarvis2 unlock *interface* exists on coffey — the weld's lock state is a TEE-stored flag, C5 drops to H, new top vector |
| `already_unlocked_…` (reads 0) | Contradicts PF-4 (`flash.locked=1`) | Stop and investigate |
| 10–13 | Environment error (no TEE node, not OP-TEE, …) | Inconclusive; record as such |

## Credits
OpenEnsemble (the AVB-TA method both build on), ShaneBreazeale (OnnDemand-4kplus), kushmint (onn-unlock-probe).
Go to the originals.
