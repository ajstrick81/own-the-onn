# Coffey round-2 relay summary

**Research date:** 2026-11-03 · **Scope:** public host-side research only; no device access, firmware execution, flashing, or booting.

## Resolved

- **R2-1:** the futex PI waiter-task correction is pinned to upstream and Android common commits; the earliest confirmed Android 14 GKI release tag containing it is `android14-5.15-2025-07_r5` (official release date 2026-08-05; annotated tag creation 2026-08-10). Android's first public ASB listing is November 2026. Coffey's recorded 2026-03 SPL and the sibling's 2026-06 SPL are therefore **H — likely pre-ASB-fix by patch-level inference only**. Vendor backport remains a competing explanation. Coffey is not declared vulnerable.
- **R2-2:** FCC model filings and an exact-product teardown identify the product family, S905X5M, and FORESEE 16-GB eMMC. No source found here establishes UART pad locations, pinout, or console log. Match the actual FCC suffix/board before using filing photos.
- **R2-3:** no coffey-specific root, CoreELEC, unlock, or alternate-boot work was found in the enumerated forum/query set. GitHub has exact-device user-space ADB customization, which does not change the boot-policy assessment.
- **R2-4:** a public OTA catalog record provides an Android 14 coffey target fingerprint, incremental, SPL, and Google-hosted OTA URL token. This is a metadata comparator only; no OTA bytes were downloaded and no current-unit state is claimed.

## What remains unknown

The decisive artifacts are still coffey's own OTA and kernel, bootloader/environment/partition records, DTB, and `systemcontrol` ELF. Public comparators cannot settle OEM backport status, locked-device boot policy, UART accessibility, exact DT compatibility, or any bootability claim.

## Single most informative next step

Capture coffey's own current fingerprint and update-service response, preserve the unmodified OTA package, and record its local SHA-256. That one capture anchors the build-specific kernel, DTB, and `systemcontrol` analysis without transferring donor data into coffey conclusions.
