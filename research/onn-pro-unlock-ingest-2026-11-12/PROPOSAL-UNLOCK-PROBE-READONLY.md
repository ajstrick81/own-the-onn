# Proposal — read-only AVB lock-bit probe on coffey (boot-policy track §6)

> **Status: RUN 2026-11-20T03:53:33Z — TA present, reads locked.** Result:
> [`COFFEY-UNLOCK-PROBE-RESULT.md`](COFFEY-UNLOCK-PROBE-RESULT.md). Deviations: the unit was on `16202347`, not
> `15051976` (maintainer chose to proceed); binary built from source on a Windows host. Original text below.
>
> **Original status: proposed, not run.** A device experiment needs its own concrete proposal (track §6): exact binary,
> expected behaviour, persistent-side-effect assessment, recovery prerequisites. This is that proposal for running
> `kushmint/onn-unlock-probe` in its **default read-only mode** on the maintainer's coffey unit. It is the
> maintainer's step on his own machine. Background and code review:
> [`EXTERNAL-COFFEY-TOOLS-2026-11-19.md`](EXTERNAL-COFFEY-TOOLS-2026-11-19.md) §2.

## Question
Does coffey's TEE answer a session for AVB trusted app `023f8f1a-292a-432b-8fc4-de8471358067`? This settles the
"built-in service" half of check §2.1 that offline analysis can't reach (C13).

## Binary
- Source: `kushmint/onn-unlock-probe` at commit **`6439f22`**, `native/probe.c`.
- Preferred: build from that source with NDK r28c (API 28) for the device ABI and record its **SHA-256**. Fallback:
  the repo's prebuilt for the ABI `ro.product.cpu.abi` reports, with its SHA-256 recorded before use.
- The hash goes in this packet's evidence ledger with the capture; the binary itself stays out of git.

## Preconditions (check and record before running)
- `ro.product.device` = `coffey`, `ro.build.version.incremental` = `15051976`, slot `_b`; lock props as PF-4
  (`flash.locked=1`, `vbmeta.device_state=locked`, `verifiedbootstate=green`).
- Automatic system updates **off**.
- A clean boot: no temporary root session active (run this **before** any OnnDemand session).

## Procedure
Push and run the binary **directly, with no arguments** — do not use `run_probe.sh`'s interactive prompt, so the
toggle path can't be reached by a mistyped answer:
```
adb push probe /data/local/tmp/onn-unlock-probe
adb shell chmod 755 /data/local/tmp/onn-unlock-probe
adb shell /data/local/tmp/onn-unlock-probe > unlock-probe-readonly.jsonl
adb shell rm -f /data/local/tmp/onn-unlock-probe
```
**Never pass `--toggle-test`.**

## Expected behaviour
One TEE session open and, if it opens, one READ invoke (command 2, `VALUE_OUTPUT`); a JSON line per stage and a
final `{"stage":"finished",…,"rebooted":false}`. Interpretation table in the review doc §2. Most likely outcome
given the offline miss: `ta_not_present_or_session_refused` (14) — but jarvis on the same build train answered, so
both outcomes are live.

## Persistent side effects
- **None expected.** The read path issues no write command; the code has no reboot, `exec`, or `system` path.
- Opening a TA session is a normal TEE client operation (the same `/dev/tee0` interface stock clients like
  `tee-supplicant` use). A refused session changes nothing.
- The `alarm(8)` timeout in read-only mode can only kill the probe process; with no write issued, there is
  nothing to leave half-done.
- Transient: one file pushed to `/data/local/tmp`, removed after.

## Recovery prerequisites
None needed for a read. If the output is anything **other than** the outcomes listed in the review doc (any
`CRITICAL_…` string should be impossible in read-only mode), **do not reboot**; save the output and stop.

## Evidence handling
Save `unlock-probe-readonly.jsonl` off-repo, run `tools/privacy_scan.py` over a copy, then commit it (or a probe
summary) with its SHA-256 under this packet, update `COFFEY-APPLICABILITY.md` §2.1, `STATUS.md` C5/vector #3 and
`progress.json`. A later option is to wrap this as a read-only probe in the harness (`probes/collection/…`) so the
capture is append-only and fingerprinted like PF-4.
