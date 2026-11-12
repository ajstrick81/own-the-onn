# coffey — can `systemcontrol` set `ubootenv.var.storeboot`? (vector #3, check §2.2)

> **Offline, read-only** inspection of coffey's own `systemcontrol` ELF
> (`…/vendor-ex/bin/systemcontrol`, pinned in the Phase-F ledger) for the second 2024-Pro precondition: the
> unlock's first move is to redirect the U-Boot **startup** by writing `ubootenv.var.storeboot` through the
> vendor SystemControl interface (C19/R). Question: does coffey's env writer permit that key, or filter it?
> Run 2026-11-12. No device action. Builds on Phase F ([`../coffey-systemcontrol-authz-2026-11-03/`](../coffey-systemcontrol-authz-2026-11-03/), C15/PF-3).

## Answer — **yes, at the systemcontrol layer** (P); bootloader honoring stays **U** (C13)

coffey's env writer gates writes on **one thing only — the `ubootenv.var.` namespace prefix** — and keeps **no
protected-key list**. `storeboot` is not special-cased, so `ubootenv.var.storeboot` is writable exactly like any
other key.

## Evidence (from the `systemcontrol` ELF)

- The writer is Amlogic `Ubootenv.cpp`
  (`vendor/amlogic/common/frameworks/services/systemcontrol/ubootenv/Ubootenv.cpp`).
- The **sole key filter** is the namespace check:
  `[ubootenv] %s is not a ubootenv variable and need prefix:ubootenv.var.xxx`. A key under `ubootenv.var.` passes;
  nothing else is checked.
- **No protected/denied/allow key array.** Scanning the ELF's printable strings for bare protected-key tokens
  (`storeboot|lock|avb|recovery|upgrade_step|bootcmd|…`) returns only `bootcmd` — and that is the ordinary
  internal usage string `ubootenv.var.bootcmd`, not a filter list. `storeboot` itself: **0 occurrences** in the
  binary, i.e. the service neither references nor protects it — it is just data to the generic setter. This
  matches Phase F's independent finding: "No list of protected key names appears" (COFFEY-PQ-AUTHORIZATION.md).
- **Backend:** the writer operates on the **`env` MTD partition** directly (`Get MTD info`, `MEMERASE`,
  CRC-wrapped image, `Save ubootenv to %s succeed!`), not via `fw_setenv`. coffey's loaded policy **permits
  `system_control` to write `env_device`** (C15 / Phase F block-device table), so the write path is authorized.
- **Reachability (C15/PF-3, carried):** `systemcontrol` runs as root, imports **no caller-identity API**, and its
  HIDL service is findable+callable by `untrusted_app` / `untrusted_app_32`. So a third-party app, not just
  `shell`, can reach `setBootEnv`.

Putting it together: **the Android-side write of `ubootenv.var.storeboot` is unobstructed** at coffey's
systemcontrol/SELinux layer — the same primitive the 2024 Pro used for step 1.

## What this does **not** establish (the wall that remains)

- **Whether coffey's BL33 reads or honors a changed `storeboot`.** Phase B found **no plaintext dispatch logic**
  in `bootloader.img` (C13/C18, PF-2) — U-Boot's handling of `storeboot`/`bootcmd` is opaque. Setting the env
  var is not the same as the bootloader acting on it.
- **The USB-boot gate** the Pro chain depends on (boot an unsigned payload off the first USB disk) — that is
  check **§2.3**, still open and gated on the same C13 opacity.
- So §2.2 removes the *Android-write* obstacle only. The Pro unlock also needs the bootloader to (a) honor the
  redirected `storeboot` and (b) boot the USB payload — both **U** on coffey.

## Grade

- **P** — coffey's `systemcontrol` env writer permits `ubootenv.var.storeboot` with only the namespace-prefix
  gate, no per-key protection, writing to the authorized `env` partition; reachable by apps (C15).
  *Method caveat:* this is strings- + policy-level (not a full instruction-trace of the HIDL `setBootEnv`
  method); no in-method key allowlist is evident, and Phase F reached the same conclusion independently, but a
  hidden filter cannot be excluded with 100 % certainty from static strings alone.
- **U** — bootloader honoring of the change (C13); the USB-boot gate (§2.3).

## Vector #3 status after §2.1 + §2.2

| Check | Result |
|---|---|
| §2.1 AVB TA UUID present on coffey | **MISS** (P, bounded) — loadable-TA route absent; built-in service U behind C13 |
| §2.2 `storeboot` writable via systemcontrol | **YES** (P) — Android-side write unobstructed; bootloader honoring U |
| §2.3 USB-boot gate | **open** — gated on C13 / the UART lead (vector #5) |

The two offline-answerable preconditions now point opposite ways: coffey **can** be made to write the startup
redirect (§2.2), but it **lacks** the Pro's specific lock-writing TA as a loadable artifact (§2.1), and both the
"does the bootloader act on it" and "does it boot a USB payload" questions collapse onto coffey's **opaque BL32/
BL33** (C13) — which only a readable secure-world image or the serial-console/UART path (vector #5) can move.

## Reproduce

```
rg -a -o -N "[ -~]{6,}" E:/Morphe/device/coffey-ota/init-audit-images/vendor-ex/bin/systemcontrol \
  | rg -i "storeboot|bootcmd|ubootenv|not a ubootenv variable"
```
