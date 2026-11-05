# Findings index — probe-backed evidence

Each row binds a finding to the probe that produced it and the exact capture (append-only, hash-pinned in
[`SHA256SUMS`](SHA256SUMS)). Rerun locally with `python -I tools/run_probe.py <probe-id>`; check everything
with `python -I tools/verify_offline.py . [--rerun]`. See [`../probes/README.md`](../probes/README.md).

| Finding | STATUS | Probe | Capture | Result | Grade |
|---|---|---|---|---|---|
| PF-1 | C14 | `kernel/cve-2026-43499-rtmutex` | [`kernel/cve-2026-43499-rtmutex/20261105T174827Z-46906e21148e.txt`](kernel/cve-2026-43499-rtmutex/20261105T174827Z-46906e21148e.txt) | `affected-code-present`: `rtmutex.c` blob `be1042f31…` equals the fix's pre-image; `remove_waiter()` locks `current->pi_lock`; source commit `3d26c188ef7e` bound to the shipped Image by its banner. Negative control on the fixed `android14-5.15` tip returns `fixed` (not captured) | P |
| PF-2 | C18 | `boot-policy/dispatch-tokens` | [`boot-policy/dispatch-tokens/20261105T174918Z-0b3a28d0297a.txt`](boot-policy/dispatch-tokens/20261105T174918Z-0b3a28d0297a.txt) | `bootloader.img`: 0 hits for 33 dispatch tokens. Recovery ramdisk hits for `bootcmd`/`setbootenv` (boot HAL, `systemcontrol_static`, recovery UI), `boot-recovery`, `factory_update_param`, `otacerts` | P (bounded negative for the bootloader) |
| PF-3 | C15 | `pq-hidl/systemcontrol-auth` | [`pq-hidl/systemcontrol-auth/20261105T174942Z-a8a4481f560e.txt`](pq-hidl/systemcontrol-auth/20261105T174942Z-a8a4481f560e.txt) | policy is the loaded one (all three odm stamps match); `untrusted_app` and `untrusted_app_32` can find + call `system_control`; runs as root; 0 caller-identity imports across `systemcontrol` + 8 linked vendor libs; `ubootenv.var.` prefix check present | P (reachability) / H (no in-process check) |
| PF-4 | C5, device checks | `collection/device-baseline` | [`collection/device-baseline/20261105T175650Z-04907e40888a.txt`](collection/device-baseline/20261105T175650Z-04907e40888a.txt) | Owner's unit: fingerprint = analyzed build; `flash.locked=1`, `vbmeta.device_state=locked`, `verifiedbootstate=green`; `sys.oem_unlock_allowed=0`, `ro.oem_unlock_supported` unset; slot `_b`; SELinux `Enforcing`; `systemcontrol` runs as `u:r:system_control:s0`; `adbd`/ART at shipped `340090000` | P (device-reported; run by the maintainer, read-only) |

Rerun status (2026-11-05, local): PF-1, PF-2 and PF-3 reproduce byte-for-byte. PF-4 is a device capture and is
not re-run by the verifier.
