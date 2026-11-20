# coffey — read-only AVB lock-bit probe: **TA present, reads locked** (2026-11-20T03:53:33Z)

> First **on-device** boot-policy evidence for this study. The maintainer's coffey unit, run per
> [`PROPOSAL-UNLOCK-PROBE-READONLY.md`](PROPOSAL-UNLOCK-PROBE-READONLY.md): `kushmint/onn-unlock-probe` @ `6439f22`,
> **built from reviewed source** (NDK r28c), one invocation with **no arguments**, as uid 2000 / `u:r:shell:s0`.
> No write was issued; binary removed after; the box was not rebooted. Captures + hashes in
> [`evidence/`](evidence/) ([`SHA256SUMS.txt`](evidence/SHA256SUMS.txt)).

## Result

```
tee_version  impl_id=1 (OP-TEE)  gen_caps=13 (GP)
open         rc=0  tee_result=0x00000000  origin=4      session to 023f8f1a-292a-432b-8fc4-de8471358067 ACCEPTED
command 2    rc=0  tee_result=0x00000000  value=1       lock bit = 1 (agrees with ro.boot.flash.locked=1)
close        rc=0
finished     outcome=locked_read_only_rerun_with_toggle_test_to_probe_further  exit_code=0  rebooted=false
```

## Graded findings

| # | Finding | Grade |
|---|---|---|
| R1 | coffey's TEE is OP-TEE with the GlobalPlatform capability, and `/dev/tee0` is reachable from an **unprivileged adb shell** (`drm_device`; policy allows `shell` open/read/write/ioctl — checked in both builds' CIL) | P |
| R2 | A TEE session to the **jarvis/jarvis2 AVB trusted app UUID** opens on coffey (public login, `tee_result 0`, origin 4 = trusted app) | P |
| R3 | Its command 2 returns **1**, matching the device-reported locked state | P (value) / H (that cmd 2 is the same `secure_lock_state` read as on jarvis2 — consistent, not independently proven) |
| R4 | The TA is **built into the TEE**, not a loadable `.ta`: no file with this UUID under `/vendor/lib/teetz`, `/vendor/lib/optee_armtz`, `/system/lib/optee_armtz`, `/odm/lib/teetz` on the live unit, and none in the 15051976 OTA (offline scan) | P (absence of loadable file) → built-in strongly indicated |

**§2.1 is closed:** the offline "MISS" was right for the loadable path; the U half resolves to **present (built-in)**.

## What this changes

- **C5's "can't be flipped" baseline (B) no longer holds as an assumption.** coffey's AVB lock state is held behind a
  TEE trusted app with the same UUID and read command that the jarvis2 unlock path writes through (C19). The weld
  is therefore at least partly a **TEE-stored flag**, reachable from Linux userspace — not purely a ROM/BL2 fact.
  New grade: **H** (flippable in principle; untested on coffey).
- **Still unknown (and deliberately untested):** whether command 3 (write) is accepted from an adb-shell session on
  coffey, whether a written value persists, and whether coffey's BL33 honors it at boot (on jarvis2 an unlocked
  reboot behaved like a factory reset). `--toggle-test` was **not** run: it changes persistent secure boot state,
  has two code defects that can leave the box unlocked (see the review doc §2), and is excluded by track §6 /
  `CLAUDE.md`. A write is a one-way decision for the maintainer, not a probe.
- **Unchanged:** hardware secure boot (BL1/BL2 signature chain) and BL33 replacement — the alternate-OS wall (C13).
  An AVB unlock, if it ever happened, would allow re-flashing `boot`/`init_boot` (persistent root), not CoreELEC.
- **Disclosure note:** an adb-shell-reachable TA that (on a sibling) accepts a lock-state write is a
  security-relevant property of the retail device. The protocol is already public (openensemble, the probe repo);
  what this run adds is that **coffey exposes it**. Under the 2026-11-20 policy, publishing isn't gated on
  vendor disclosure; a courtesy notice to onn/Amlogic is optional.

## Run conditions (deviation from the proposal, recorded)

The proposal's precondition "build `15051976`, slot `_b`" **failed**: the unit had taken an OTA to
`onn/coffey/coffey:14/URO4.260304.092/16202347`, slot `_a`, SPL 2026-09-01, `ro.bootloader` `01.01.260305.112513`
(automatic updates were on). The maintainer chose to run on the new build. So this result is graded for
**16202347**. Notable for carry-over (all P, read 2026-11-19/20):
- Kernel `uname -r` unchanged: `5.15.196-android14-11-g3d26c188ef7e-ab14657224` (built Jan 3) — the September SPL
  OTA did not replace the GKI kernel, so C14's affected-code result very likely still applies (version string,
  not image hash).
- `plat_sepolicy.cil` and `vendor_sepolicy.cil` byte-identical to 15051976; live plat stamp matches the ODM
  precompiled policy → C15/C18 policy findings carry over.
- Same 11 loadable TAs by filename.
- Lock state unchanged (1 / locked / green); no `su`.

Binary: built on a Windows host from `probe.c` (`sha256 503dfae7…`) with r28c's clang and the repo's own flags
(`-std=c11 -D_GNU_SOURCE -O2 -Wall -Wextra -Werror -fPIE -pie`, target `armv7a-linux-androideabi28`) →
`999c3b57…`. It differs from the upstream prebuilt (`f4dde76e…`, not used) as expected for a different host
toolchain; dynamic imports are identical (libc only: `open`, `ioctl`, `__system_property_get`, `alarm`, stdio…; no
`exec`/`system`/`reboot`).

## Credits
OpenEnsemble (the AVB-TA protocol), kushmint (onn-unlock-probe). See the originals.
