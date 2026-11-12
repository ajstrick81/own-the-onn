# What the onn 4K Pro unlock means for coffey — applicability + discriminating checks

> **Nothing here is a coffey result.** It maps the sibling mechanism
> ([`ONN-PRO-UNLOCK-MECHANISM.md`](ONN-PRO-UNLOCK-MECHANISM.md), grade **R**) onto coffey's **own** confirmed
> findings (C13/C15/C18) and lists the offline checks that would raise or kill each transfer. Per the repo rule:
> **no donor datum becomes a coffey conclusion** — every coffey cell stays `U`/`B`/`H` until coffey's own
> artifacts say otherwise. All proposed checks are **host-side, read-only** on the already-captured OTA
> ([`../coffey-ota-capture-2026-10-09/`](../coffey-ota-capture-2026-10-09/)); none is a device action.

## 1. It lands exactly on our existing map

The 2024 Pro chain is, step for step, built from primitives we already documented on coffey:

| Pro primitive (R) | coffey finding | Match? |
|---|---|---|
| Set `ubootenv.var.storeboot` via **SystemControl** | **C15/C18** — root `systemcontrol` writes `ubootenv.var.*` (prefix-only check), reachable by `untrusted_app`; boot steered through the U-Boot env | **Yes, by construction** — coffey's systemcontrol is the same kind of env writer. `storeboot` specifically: not yet confirmed writable (prefix check suggests yes; **H**) |
| First-USB-disk boot gate | **C13/Phase B** — `bootloader.img` has no plaintext dispatch; U-Boot's USB-boot behaviour is **U** (opaque container) | **Unknown** — the decisive, bootloader-specific unknown |
| Unsigned EL2 payload, fixed addresses | — | **Will not transfer as-is** — "specific to the tested bootloader"; needs coffey's own BL33 (blocked offline, C13) |
| AVB trusted-service TA `023f8f1a-…`, cmd 3 → state 0 | coffey TEE/TA set not yet enumerated | **Checkable offline** — see §2.1 |
| Flashable `boot_b`/`init_boot_b` once AVB-unlocked | **C18** — `fastbootd` is lock-gated on `ro.boot.verifiedbootstate`; unlock would ungate it | Consistent |

Phase B's own grep token list already includes `storeboot`, `bootcmd`, `aml_autoscript`, `usb_burning` — the Pro
mechanism is a concrete instance of exactly what Phase B was looking for. This is corroboration that our
boot-policy map named the right primitives, now with a sibling showing one way they compose into an unlock.

## 2. Discriminating checks (offline, on coffey's captured artifacts)

Ranked by value ÷ cost. Each is a grep/parse over bytes already in hand; results stay graded.

### 2.1 — **Highest value:** is the AVB trusted-app present on coffey?
Search coffey's extracted `vendor`/`odm`/`vendor_boot`/TEE images for the TA **UUID**
`023f8f1a-292a-432b-8fc4-de8471358067` (and its byte-order permutations), plus any `*.ta`/trusted-app blobs and
the strings that invoke them. 
- **Hit** → the same AVB lock-state TA ships on coffey; the *interface* that flips the lock exists here too
  (the write would still need a way to call it — §2.3). Raises the unlock lead to a real **H** on coffey.
- **Miss** (bounded) → coffey uses a different secure-world AVB path; the 2024 TA route does not transfer. A
  genuine, useful negative.

### 2.2 — Can coffey's systemcontrol set `storeboot` specifically?
We know (C15) the env writer checks only the `ubootenv.var.` prefix and imports no caller-identity API. Confirm
from the **coffey systemcontrol ELF** that `storeboot` is not on any internal deny/allow list distinct from
`lock`, and that `set`-path for arbitrary `ubootenv.var.*` reaches the env partition. Output: upgrade the
`storeboot`-writable cell from **H** to **P/U**.

### 2.3 — Does coffey boot from a first USB disk at all?
The hardest and most decisive unknown (C13). Offline, bound it as far as the plaintext allows: re-grep the OTA's
plaintext env defaults and `vendor_boot` for `usb`, `storeboot`, `bootcmd`, `aml_autoscript`, `usb_burning`
handling (Phase B found none in `bootloader.img`; re-confirm nothing in env defaults contradicts). This likely
stays **U** until the serial-console/UART lead (STATUS vector #4) or a readable BL33 lands — record it as the
gating unknown, don't manufacture an answer.

### 2.4 — Bootloader-build correspondence
Record precisely how coffey's bootloader identity (`ro.bootloader` on the owner unit; container tag
`S7D-s905x5m-26030511BBST`, C13) relates to jarvis's `01.01.260304.175641`. Same platform + near-identical date
stamp (`260304`/`260305`), **different build** → the fixed-address EL2 payload is non-transferable even if every
other precondition holds. This is why "same build train" does **not** mean "same unlock binary."

## 3. What this does — and does **not** — change for the project goals

- **Runtime-root → persistent root (the big shift).** Our standing conclusion was "runtime root ≠ custom ROM,
  and per-boot root leaves the lock intact" — persistence needed a bootloader unlock we treated as a hard wall
  (B). The Pro evidence shows, on sibling S905X5M/S7D silicon, that the **AVB lock is writable** (R) by a TEE
  path, which would turn a one-boot root into a **flashed, persistent** root (patch `boot_b`/`init_boot_b`). If
  §2.1–§2.3 come back favourable on coffey, "no persistent root" moves from *hard wall* to *open lead*.
- **Alternate-OS / CoreELEC (unchanged).** The Pro authors are explicit: this is "not disablement of earlier
  hardware secure boot or support for arbitrary first-stage bootloader replacement." Hardware secure boot and
  BL33 stay welded (our C13). **CoreELEC/custom ROM remains blocked by the same wall** — this evidence does not
  touch it.
- **Grade discipline.** C5's "can't be flipped" was graded **B** (inherited baseline). It now has a **direct
  sibling-silicon counterexample at the AVB layer (R)**. That doesn't make coffey unlockable; it means the
  baseline assumption is no longer safe to inherit, and the question is now **empirical for coffey**, answerable
  (in part) by §2.

## 4. Boundaries (unchanged)
Everything above is offline artifact analysis. **Do not** run either Pro installer, set `storeboot`, mount a
boot USB, invoke a TEE command, or flash anything on coffey. A device experiment would be a separate, explicit,
maintainer-approved proposal with image hashes, expected behaviour, persistent-side-effect assessment, and
recovery prerequisites (track §6) — and note the Pro projects themselves proved **no independent unbrick path**.
