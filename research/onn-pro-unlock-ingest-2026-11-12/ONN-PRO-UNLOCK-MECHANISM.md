# onn 4K **Pro** unlock/root mechanism — external sibling evidence (R)

> **Grade: R (first-hand report, not reproduced here).** This records what two third-party OpenEnsemble
> projects claim for the onn 4K **Pro** (`jarvis` / `jarvis2`). **Our device is the 4K _Plus_ (`coffey`).**
> Nothing here is coffey-tested; see [`COFFEY-APPLICABILITY.md`](COFFEY-APPLICABILITY.md) for what transfers and
> what does not. Mechanism **identity and enforcement boundary** are recorded per the repo rule; no working
> payload, offset, or key is reproduced (the sources publish none either). Both projects are single-unit,
> self-described experimental, and warn that bricking is possible and that no independent unbrick path was
> proven. Ingested 2026-11-12; sources + verbatim field dumps in [`SOURCES.md`](SOURCES.md). **The mechanism,
> the hardware testing, and the evidence discipline below are OpenEnsemble's original work** — see
> [`INDEX.md` → Credits](INDEX.md#credits).

## 0. Why this is relevant at all

The two Pro projects matter to the coffey study because of **two exact overlaps**, not the shared "4K Pro"
marketing name (the Pro is a different board from our Plus):

| Axis | coffey (4K **Plus**) | 2024 4K **Pro** (`jarvis`/`SNA`) | 2026 4K **Pro** (`jarvis2`) |
|---|---|---|---|
| Build ID / incremental | `URO4.260304.011.B1` / `15051976` | **`URO4.260304.011.B1` / `15051976`** (identical) | `URO3.260203.035.A1` / `15640252` |
| SoC / platform | **S905X5M / S7D** | not named in the pages | **`AMLS905X5M` / `S7D`** (identical platform) |
| Android | 14 | 14 | 14 |
| Active slot | A/B, `_b` live | `_b` | `_b` |
| `ro.bootloader` / container tag | container `S7D-s905x5m-26030511BBST` (C13) | `01.01.260304.175641` | `01.01.260525.135322` |

So coffey shares the **release train** with the 2024 Pro (same build number + incremental; the fingerprints
differ only in product: `onn/coffey/coffey` vs `onn/jarvis/SNA`) and shares the **silicon** with the 2026 Pro.
onn evidently cuts these on one shared platform build. **Same-SoC ≠ same keys/OTP/bootloader policy** (track §4
correction 1) — the overlap is a lead to test against coffey's own artifacts, not a conclusion.

## 1. What the Pro unlock actually does (2024 `jarvis`, the detailed one)

The 2024 project's `docs/HOW_IT_WORKS.md` is the only page that names the path. In its own words it is scoped to
"the earlier onn. 4K Pro (jarvis / SNA), firmware `URO4.260304.011.B1` / `15051976` only," and "fixed addresses,
code prefixes, and memory layout make it specific to the tested bootloader."

Chain, as the page describes it:

1. **Startup redirect.** A diagnostic APK "reads/changes `ubootenv.var.storeboot` through the vendor
   **SystemControl** interface." `storeboot` is the U-Boot **startup path**; stock value is
   `run storeboot_base;` (confirmed in `tested-profile.json` and the `unlock-after-reset.json` capture).
2. **Boot a payload.** "Temporary startup consumes a one-use FAT USB gate before loading an **unsigned legacy
   native payload**. The payload runs in the measured **AArch64 EL2** context, guarded by register state and
   stock code prefixes." The bootloader "always uses its first USB disk" as the boot source.
3. **Write the AVB secure state via a TEE trusted app.** The payload "requires state 1, opens **AVB trusted
   service UUID `023f8f1a-292a-432b-8fc4-de8471358067`**, and issues **command 3** with one `VALUE_INPUT`
   parameter (attribute 1, values 0/0/0)," then re-reads the state. The capture "recorded exactly one write,
   transport and TA success, and **state 0**."
4. **Restore startup.** `restore-startup --kit unlock` puts `ubootenv.var.storeboot` back to `run storeboot_base;`
   and verifies through "a fresh vendor service."

Result properties (from `evidence/unlock-after-reset.json`, 2026-10-21, verbatim): `ro.boot.flash.locked=0`,
`ro.boot.vbmeta.device_state=unlocked`, `ro.boot.verifiedbootstate=orange`, `ro.boot.veritymode=enforcing`;
"these properties survived a further ordinary reboot with normal startup and no mounted USB" and a factory reset.

### What the authors explicitly say it is **not**
- "**No manufacturer private key was recovered or signature forged.**" The payload is "unsigned." No CVE, debug
  door, unsigned-AVB-region, or rollback is named as the reason the write is accepted.
- "This proves a persistent **Android AVB lock-state change**, not **disablement of earlier hardware secure
  boot** or **support for arbitrary first-stage bootloader replacement**."
- `hardware_secure_boot_disabled_proven: false`, `custom_firmware_boot_proven: false`, `root_proven: false` (in
  that Oct-21 capture; root was reported separately, later).

**Reading (inference, H):** the TEE's AVB trusted app accepts a "set lock state" call (cmd 3 → 0) from code
running in the secure/hypervisor context, without a signed token — i.e. the weld is defeated at the **AVB
layer inside the TEE**, reached from an unsigned EL2 payload that the bootloader is coaxed into running via the
`storeboot` env + first-USB-disk boot. The **hardware secure-boot chain (BL1/BL2 signatures) is untouched**, so
BL33 replacement / custom first-stage is still not possible by this method. The page states the boundary; the
"no signed token" part is our inference from the absence of any token in the description.

## 2. The 2026 `jarvis2` unlock (same silicon as coffey, less detail)

- Command `onn26 unlock --accept-data-loss`; expected `trusted state 0, flash lock 0, vbmeta unlocked, verified
  boot orange` — the **same AVB-unlock outcome** as 2024.
- **The transport of the unlock write is not named on any 2026 page** (`docs/HOW_IT_WORKS.md` 404s). The repo
  ships "two ARM32 AVB helpers built with Android NDK r28c, API 28" implementing "native AVB protocol scenarios,"
  and `RECOVERY.md` states the flow "does not change saved `bootcmd`/`storeboot`, alter bootloader firmware,
  install a boot receiver, or leave an experimental startup script. No temporary-root exploit is used," and that
  "USB autoscript experiments did not establish a usable installation route and are not included."
- So 2026 reaches the **same AVB-lock write** but **without** the USB/`storeboot` transport of 2024 (no USB drive
  is required); the exact carrier is undocumented. DSU is used only for the **init_boot_b** root write afterward,
  not for the unlock.

## 3. Root, post-unlock (both, for completeness)

Unlock only flips the lock. Persistent root is a **separate** step that the unlock enables:
- 2024: patch stock `boot_b` (at `/dev/block/mmcblk0p21`, 96 MiB) with Magisk 30.7 on the device, write it once
  with full readback, leaving `boot_a`/`vbmeta_b`/`vendor_boot_b` unchanged.
- 2026: write a Magisk-patched **`init_boot_b`** (8 MiB) via a single-use DSU root console; no vbmeta/bootloader
  write.

Both target the Android boot image an unlocked AVB state now permits re-flashing — **a persistence path for
root, not an alternate-OS path.**

## 4. Caveats that bound this evidence
- One tested unit each; "not hardware-tested end to end"; bricking warned; **no proven independent unbrick**
  (2024 `restore-stock` needs a still-working Android/root; fastboot/cable/full-brick recovery "untested").
- The 2024 chain is explicitly "specific to the tested bootloader" by **fixed addresses / code prefixes /
  memory layout** — the one part guaranteed **not** to port as-is to a different bootloader build.
- No SoC name, no "Amlogic," and no named TEE OS (BL32/OP-TEE/Trusty) appears in any page; the TA **UUID** is the
  only secure-world identifier given.
- These are third-party reports. Grade stays **R**. They become coffey-relevant only through the discriminating
  checks in [`COFFEY-APPLICABILITY.md`](COFFEY-APPLICABILITY.md), run against coffey's **own** captured artifacts.
