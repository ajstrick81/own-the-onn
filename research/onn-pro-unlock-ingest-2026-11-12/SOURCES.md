# Sources — onn 4K Pro unlock ingest (2026-11-12)

All fetched 2026-11-12 from the OpenEnsemble GitHub repos' `main` branch (mutable). GitHub pages pin no commit
here; reproducibility is via the **verbatim field dumps below** plus the quoted strings in
[`ONN-PRO-UNLOCK-MECHANISM.md`](ONN-PRO-UNLOCK-MECHANISM.md). If any of this is ever relied on beyond a lead, pin
the repo commit SHA at acquisition (track §1: a different URL is not independent confirmation).

## Pages read

**2026 Pro — `openensemble/onn-4k-pro-2026-unlock-root`**
- `README.md` · `docs/MANUAL.md` · `docs/RECOVERY.md` · `docs/BUILD.md`
- `docs/HOW_IT_WORKS.md` — **404 (absent)**; `openensemble.github.io/onn-4k-pro-2026-unlock-root/` not fetched
- Not fetched: `docs/RECOVERY.md` sub-refs, `firmware/` profile

**2024 Pro — `openensemble/onn-4k-pro-unlock-root`** (site: `openensemble.github.io/onn-4k-pro-unlock-root/`)
- `README.md` · `docs/MANUAL.md` · `docs/EXPERIMENTAL_UNLOCK.md` · `docs/RECOVERY.md` · `docs/HOW_IT_WORKS.md`
- `firmware/tested-profile.json` · `evidence/unlock-after-reset.json`
- Not fetched: `docs/FIRMWARE_UPDATE.md`, `docs/RESULTS.md`

> The repos also carry crypto tip-jar addresses in their READMEs; deliberately **not** reproduced.

## `firmware/tested-profile.json` (2024) — verbatim key fields

```
model                     "onn. Streaming Device 4K Pro"
hardware_generation       "Earlier model (pre-2026 hardware), jarvis / SNA"
excluded_models           ["onn. 4K Pro (new 2026 hardware model)"]
model_2026_supported      false
model_2026_tested         false
product                   "jarvis / SNA"
android_tv_os             "14"
build_id                  "URO4.260304.011.B1"
incremental               "15051976"
fingerprint               "onn/jarvis/SNA:14/URO4.260304.011.B1/15051976:user/release-keys"
security_patch            "2026-03-01"
bootloader                "01.01.260304.175641"
active_slot               "_b"
first_api_level           "31"
abi                       "armeabi-v7a"
tested_units              1
stock_boot_size           100663296        (96 MiB)
stock_boot_sha256         5c5a874dd2e3e5b2ad87903a3d53a6f8b3ebcebe2ad64a28fd837d1a07ceaad8
expected_patched_sha256   2447a78a0580a804b3997b3920e9198a437aedf7294ec2907952d2ef751d36a3
magisk_version            "30.7"  (code 30700)
magisk_apk_sha256         e0d32d2123532860f97123d927b1bb86c4e08e6fd8a48bfc6b5bee0afae9ebd5
boot_target               "/dev/block/by-name/boot_b"
boot_device               "/dev/block/mmcblk0p21"
stock_startup             "run storeboot_base;"
other_firmware_test_scope "A later 15051976/B to 16202347/A update retained root and setup on the same one
                           device. Fresh unlock on 16202347 remains untested."
```

## `evidence/unlock-after-reset.json` (2024) — verbatim key fields

```
saved_at_utc                          "2026-10-21T08:30:25.590844+00:00"
status                                "android_recovered_avb_unlock_persists_through_stock_reboot"
persistent_avb_unlock_observed        true
stock_startup                         "run storeboot_base;"
factory_reset_completed               true
properties.ro.build.fingerprint       "onn/jarvis/SNA:14/URO4.260304.011.B1/15051976:user/release-keys"
properties.ro.bootloader              "01.01.260304.175641"
properties.ro.boot.flash.locked       "0"
properties.ro.boot.vbmeta.device_state "unlocked"
properties.ro.boot.verifiedbootstate  "orange"
properties.ro.boot.veritymode         "enforcing"
root_proven                           false
custom_firmware_boot_proven           false
hardware_secure_boot_disabled_proven  false
independent_secure_getter_capture_after_cold_boot  false
```

## Mechanism strings (2024 `docs/HOW_IT_WORKS.md`) — the ones that matter

```
env var written    ubootenv.var.storeboot   (via vendor SystemControl)
stock startup      run storeboot_base;
boot carrier       one-use FAT USB gate -> unsigned legacy native payload, AArch64 EL2
AVB TA UUID        023f8f1a-292a-432b-8fc4-de8471358067
AVB TA call        command 3, one VALUE_INPUT (attribute 1, values 0/0/0)  -> secure state 1 -> 0
key/signature      "No manufacturer private key was recovered or signature forged." (payload unsigned)
scope statement    "persistent Android AVB lock-state change, not disablement of earlier hardware
                    secure boot or support for arbitrary first-stage bootloader replacement."
```

## 2026 Pro identity (from `README.md` / `docs/MANUAL.md`)

```
model/product    "2026 onn 4K Pro (jarvis2)"   SoC "AMLS905X5M / S7D"
build / incr     URO3.260203.035.A1 / 15640252     SPL 2026-06-01
bootloader       01.01.260525.135322               active slot _b
root target      init_boot_b (8 MiB), Magisk 30.7 (via single-use DSU root console)
unlock           onn26 unlock --accept-data-loss -> trusted state 0, flash lock 0, vbmeta unlocked, orange
unlock transport NOT NAMED (HOW_IT_WORKS.md absent); ships 2x ARM32 AVB helpers (NDK r28c, API 28)
host toolchain   NDK 28.2.13676358, erofs-utils 1.7.1, secilc; ~911 MB firmware download
```
