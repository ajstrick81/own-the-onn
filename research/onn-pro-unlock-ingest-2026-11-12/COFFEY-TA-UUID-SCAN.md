# coffey — AVB trusted-app UUID scan (vector #3, check §2.1)

> **Offline, read-only** scan of coffey's own captured artifacts for the AVB trusted-app UUID the 2024 onn 4K
> **Pro** unlock calls (`023f8f1a-292a-432b-8fc4-de8471358067`, C19/R). Run 2026-11-12 with
> [`scripts/scan_ta_uuid.py`](scripts/scan_ta_uuid.py) over the OTA-capture tree
> (`E:/Morphe/device/coffey-ota/`, artifacts pinned in
> [`../coffey-ota-capture-2026-10-09/COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](../coffey-ota-capture-2026-10-09/COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt)).
> No device action.

## Result — **no hit** (bounded negative on the loadable-TA path, P; built-in-service path stays U)

coffey does **not** ship the Pro's AVB trusted-app as a loadable TA, and the UUID appears in **no** readable
coffey boot/vendor binary, in any representation.

## What was searched

Five byte representations (so a reference is caught even without a `<uuid>.ta` file):

| form | bytes / text |
|---|---|
| `ascii-hyphen-lower` | `023f8f1a-292a-432b-8fc4-de8471358067` |
| `ascii-hyphen-upper` | `023F8F1A-292A-432B-8FC4-DE8471358067` |
| `ascii-compact-lower` | `023f8f1a292a432b8fc4de8471358067` |
| `packed-be` (GlobalPlatform canonical order) | `02 3f 8f 1a 29 2a 43 2b 8f c4 de 84 71 35 80 67` |
| `packed-optee-mixed` (OP-TEE in-memory `TEE_UUID`, time fields little-endian) | `1a 8f 3f 02 2a 29 2b 43 8f c4 de 84 71 35 80 67` |

Two passes:
1. **Whole tree** `E:/Morphe/device/coffey-ota/` — `scanned=2151`, `unreadable_skipped=464`, `name_skipped=4`
   (`payload.bin` + `*.zip`, compressed — no plaintext), **`hits=0`**. The 464 skips are Android symlinks
   Windows can't resolve (`os error 1920`); their targets are scanned under canonical paths.
2. **Explicit high-value set** — `scanned=25`, `skipped=1`, **`hits=0`**. The one skip is `vendor-ex/bin/tee`
   (a symlink to `toybox_vendor`, the `tee` coreutil — not a TEE binary). Set: `images/{bootloader,boot,
   vendor_boot,dtbo}.img`; all 11 `vendor-ex/lib/teetz/*.ta`; `vendor-ex/bin/{tee-supplicant,tee_attest,
   tee_hdcp,tee_key_inject,tee_preload_fw,tee_provision}`; `vendor-ex/lib/{libteec,libckteec,
   libtee_load_video_fw}.so`; `vendor-ex/bin/systemcontrol`.

## coffey's shipped loadable TAs (`vendor-ex/lib/teetz/`, 11 total)

```
00d1ca22-1764-4e35-90aa-5b8c12630764.ta   2088528d-102a-4716-b940-23fd9be04adf.ta
2c1a33c0-44cc-11e5-bc3b-0002a5d5c51b.ta   526fc4fc-7ee6-4a12-96e3-83da9565bce8.ta
5dc33b6a-216d-4641-a834-b3f3aa1accb8.ta   6c67ce8f-95c1-4826-b62e-1a857a1ced3d.ta
8efb1e1c-37e5-4326-a5d6-8c33726c7d57.ta   d83c3c4a-9e8d-4e4e-ad30-9d40e137f689.ta
e043cde0-61d0-11e5-9c26-0002a5d5c51b.ta   e92a43ab-b4c8-4450-aa12-b1516259613b.ta
ff2a4bea-ef6d-11e6-89cc-d4ae52a7b3b3.ta
```
None is `023f8f1a-…`. (These are Amlogic/OP-TEE secure-world apps — e.g. the `2c1a33c0-…`/`e043cde0-…` family is
the usual Widevine/PlayReady/keymaster/gatekeeper set — but their functions are not decoded here; only the UUID
match matters for this check.)

## Grading

- **P (bounded negative) — loadable-TA path.** The 2024 Pro's AVB trusted-app is **not present or referenced**
  in coffey's readable TEE TA set, boot images, TEE client binaries/libs, or `systemcontrol`. A payload that
  simply "opened the same TA" would have nothing to open on coffey.
- **U — built-in-service path.** coffey's **BL32 / TEE-OS lives inside the signed bootloader container whose
  stage bodies are opaque** (C13: encrypted/packed). AVB lock-state ownership is a core secure-world function and
  may be a **built-in** service rather than a loadable TA — such code would not appear in plaintext here, so this
  scan can neither confirm nor exclude it. The remaining uncertainty collapses onto the **same C13 opacity wall**.

## So what

- This **does not** make coffey unlockable or un-unlockable. It removes the *easy* transfer hypothesis (coffey
  shipping the identical callable TA) and shows coffey's equivalent AVB authority, if present, is behind its own
  opaque secure world.
- **The U half is testable on the device (2026-11-19):** a read-only TEE session open to this UUID from a normal
  adb shell (`kushmint/onn-unlock-probe`, default mode) distinguishes "built-in AVB TA present" from "absent" —
  see [`PROPOSAL-UNLOCK-PROBE-READONLY.md`](PROPOSAL-UNLOCK-PROBE-READONLY.md). Proposed, not run.
- Next discriminating moves stay as in [`COFFEY-APPLICABILITY.md`](COFFEY-APPLICABILITY.md) §2.2 (can coffey
  `systemcontrol` set `ubootenv.var.storeboot`) and §2.3 (USB-boot gate) — both independent of this TA question —
  plus the standing BL32/BL33 opacity wall (C13), which only a readable secure-world image or the UART lead
  (vector #5) can move.

## Reproduce

```
python -I research/onn-pro-unlock-ingest-2026-11-12/scripts/scan_ta_uuid.py \
  023f8f1a-292a-432b-8fc4-de8471358067  E:/Morphe/device/coffey-ota
```
(input paths are the maintainer's off-repo OTA capture; script is committed text.)
