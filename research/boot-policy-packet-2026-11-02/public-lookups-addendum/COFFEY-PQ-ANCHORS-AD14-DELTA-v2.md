# COFFEY-PQ-ANCHORS-AD14-DELTA v2

**Date:** 2026-11-03 UTC  
**Scope:** Public host-side research and offline static inspection only. No device access, firmware-script execution, hardware action, or import of donor offsets/keys/images into a coffey conclusion.

## Result

**Phase F donor-source negative is bounded for the three avenues specified below, with one explicit unfinished binary inspection.** No newer Android 12–14 `CPQControl` source was found in any branch or tag of `Amlogic-Lineage/android_vendor_amlogic_common_frameworks`; no matching methods or service implementation were found in the checked AOSP Yukawa/SEI610 trees or its pinned Android 14 vendor package; and no target-device ROM-dump mirror containing a `systemcontrol` ELF was found in the specifically enumerated GitHub repositories/search set.

The Xiaomi Box S 3rd Gen (`twilight`) Android 14 full OTA was acquired as a sibling S7D comparator. Its `vendor.img` and `system.img` were extracted from the OTA payload, but both are EROFS and the available host could neither mount nor userspace-extract them. Therefore the presence/absence of `systemcontrol` inside that OTA is **not determined**; this is not counted as a negative ELF result. No A14 source or ELF comparator result changes coffey authorization: **U — unresolved**.

### Status key

- **P** — directly inspected public source/artifact.
- **R** — author report not independently reproduced.
- **B** — inherited project baseline.
- **H** — inference or lead; not target-build proof.
- **U** — unresolved.

A source repository ref is pinned by full Git commit. SHA-256 values identify downloaded/local artifact bytes, not authenticity or applicability to coffey.

## Findings

### F1 — Same-repository branch and tag census: no newer source candidate

- **Claim/status:** P — the public repository exposes one branch and 67 tags; none is a newer Android 12–14 source ref.
- **Target:** `Amlogic-Lineage/android_vendor_amlogic_common_frameworks`.
- **Branch:** `khadas-vims-pie_64` → commit `9f87fb04e81e4d5577bea584aa098d42b06f16ab` (branch HEAD; commit subject merges `khadas-vims-pie`).
- **Refs examined:** All 67 advertised tags are listed in Appendix A with their resolved commit and commit date. The date span is 2016–2020; release-name families are V*, Vim3/Vims Pie, g12_9.0.0_*, and s922_9.0.0_*.
- **Method census across tags:** all 67 contain `permissionCheck`; 58 contain `factorySetParamsDefault`; 7 contain `getPQDatabaseInfo`. The latter hits are all from the 2019–2020-era tag set. The source locations in the checked branch include `SystemControlService.cpp` (`permissionCheck`, lines 118–138; reset wrapper around line 1411; database-info wrapper around line 2024) and `CPQControl.cpp` (`LoadPQSettings`, line 334; `FactorySetParamsDefault`, around line 3316; `GetDBVersionInfo`, around line 5284). None provides an Android 12–14 branch/tag.
- **Files at branch HEAD:**
  - `services/systemcontrol/PQ/CPQControl.cpp` — SHA-256 `c6b66c7509dc0e63e4a0b9de23451f5c2410b7f018653f28a675a66623de5558`.
  - `services/systemcontrol/SystemControlService.cpp` — SHA-256 `3a0d7683d6b865989ec3452724459f4d0ea316b5de9737f961dcd66378ed74bd`.
  - `services/systemcontrol/SystemControl.cpp` — SHA-256 `361056e4db33d213bb5062c49a8a4422bd081e0bbd407d2afb269a7aec376171`.
  - `services/systemcontrol/SystemControlHal.cpp` — SHA-256 `d2016efda1cad77312f7efa7c78c11b73c161cd5bf8ce9fe0c17c1dee80fb82e`.
  - `services/systemcontrol/SystemControlClient.cpp` — SHA-256 `174de439aca20662e0e15b981972b249174118f71db71cb09c85556b553ae5b3`.
- **Observed Pie call paths (P, donor only):** `factorySetParamsDefault` client → HAL → `SystemControlService::factorySetParamsDefault` → `CPQControl::FactorySetParamsDefault`; `getPQDatabaseInfo` client → HAL → service → `CPQControl::GetDBVersionInfo`. `SystemControlService::permissionCheck()` at lines 118–138 has its check body commented and returns `NO_ERROR` in this donor. This is not an A14 comparison.
- **Interpretation:** within this repository, the earlier negative can be upgraded from “only Pie branch searched” to “all current public branches and all 67 current public tags inspected; no Android 12–14 ref found.”
- **Competing explanations / limit:** a later vendor mirror, deleted/unadvertised ref, another organization’s fork, or non-public source may exist. Branch/tag names and content cannot establish target Android version beyond source evidence.
- **Next discriminating check:** compare coffey’s own `systemcontrol` ELF and effective Binder/HwBinder/SELinux policy when those artifacts become available; do not transfer this donor’s stubs or call paths as coffey facts.

### F2 — AOSP Amlogic reference-board tree: no matching `systemcontrol` implementation

- **Claim/status:** P — no `factorySetParamsDefault`, `getPQDatabaseInfo`, or `CPQControl` implementation was found in the checked AOSP Yukawa tree snapshots.
- **Repository:** `https://android.googlesource.com/device/amlogic/yukawa`.
- **Pinned refs:** `android12-release` `2f132d927bbad8b6b7cc57669dc34f2f7b71a78e`; `android13-release` `d8932e27a041a97a08fef02509202067acc5a00c`; `android14-release` `080626c8a069894390960818dfcf4776525a8ec7`; `main` `fc7e9e39b30dfed460fb4cb4dc6177aa52c267c7`.
- **Inspection:** tree-wide tracked-file search for the two method names, `CPQControl`, `systemcontrol`, and vendor references. `manifest.xml` does not declare the Amlogic systemcontrol implementation. `device/amlogic/yukawa` is the checked SEI610/Yukawa device tree; no separate SEI610 source repository was found in the queried AOSP project list.
- **AOSP vendor-package lead (P):** at `main` commit `fc7e9e39b30dfed460fb4cb4dc6177aa52c267c7`, `fetch-vendor-package.sh` pins public package `https://public.amlogic.binaries.baylibre.com/ci/vendor_packages/20241217/extract-yukawa_devices-20241217.tgz`, expected SHA-512 `220cdca0a6364e54c57cbc544eeec0ff5f88680763c1f15136f6e1412e35fc3bd8545db4a2ebde07127cb3cd49bfc33be770ef9736118febcfb0446a64a27a1c`. Retrieved bytes: 70,606,945; SHA-256 `cf6335df4824ba15678448f11fd1a687237ad9af8fcb95683eb2ad06116f3acc`; SHA-512 matches the pinned value. Its embedded tar inventory was inspected without running the self-extracting wrapper; it contains board firmware / U-Boot / GPU and related vendor files, but no `systemcontrol`, `CPQControl`, or Android service binary.
- **Package-pinning source files:** `fetch-vendor-package.sh` SHA-256 `7bcee60903fb883aa3ab1da992a5036c66271dd570fe37be5353db457982f621`; `vendor-package-ver.mk` SHA-256 `4b5fc70a54fc441b3c74c7a01c3f8589b1794bc63d21dd1cfff2e2d64442250e`; `manifest.xml` SHA-256 `609422e4ca33c8554500c8b134317cf6fbcd2b4b0d0b2a8602c9f69f7d5155e2`.
- **Interpretation:** this AOSP reference avenue did not supply a newer CPQ/systemcontrol source implementation or matching ELF.
- **Competing explanations / limit:** AOSP Yukawa is a reference-board tree and may omit proprietary Android TV service packages. The BayLibre package is not a complete Android system/vendor image.
- **Next discriminating check:** inspect a full matching AOSP reference-board system/vendor build or a public newer Amlogic vendor source tree if one is located.

### F3 — GitHub ROM/dump mirror search: no qualifying dump found in enumerated candidates

- **Claim/status:** P for inspected repositories; H for the search-space boundary. No matching `systemcontrol` ELF was obtained from the candidates below.
- **Inspected repositories and pins:**
  1. `xpxp233333/xiaomi-mibox5-guides` `main` → `56eae90381979a74040949790079e722e8903df0`. Repository is guides/source, not a system/vendor dump. `docs/backup.md` links the `twilight` OTA listed under F4. Relevant docs’ hashes: README `bf5593eafcbe03aaefb8a265d8eb0fb98a44065608ee853493327675bad683da`; `docs/backup.md` `eddf17bd71d679189dd6360d6debc19c8b98d0a07d28194a520416d19e056a68`; `docs/root.md` `bb000fa522b5103e69cd6f867a6b20b42ad1faf6ef2c6daee2fa9e9f11d8673e`.
  2. `samtheruby/coreelec-android-dualboot-twilight` `main` → `e4bc9f0361e6d834d67cdedba58c678803e79fe2`. CoreELEC dual-boot research/build repo; no Android `system.img`, `vendor.img`, `super.img`, `systemcontrol`, or `CPQControl` in tracked tree. Its checked-in GPT edge snippets and CE installer/release assets are not a stock Android dump. Hashes: `research.md` `fac761a0df71030fb12514e254e7e2a6e70ade60bc6ed388cd2850baa0470311`; `README.md` `cc4155562f2bbced61388497e8b10c945acc65c6c13749ba1b00bfa92675b23c`; `stock_gpt_first2m.bin` `5fa43f9282959980715f0d6ecbb7665a05250e742b95c0c5ecf76b2f05e9d5e1`; `stock_gpt_last2m.bin` `42a1eb665533d653c9013705b6c3750b4d0efc32e3fe2e3ab50d9e412d2a4fe3`.
  3. `dangerouslaser/ugoos-am9-pro-coreelec-emmc` `main` → `581ca4f7a441461b957d814cc9beb1a1cca6cfe5` (repo tree previously inspected; docs/CE material, no Android systemcontrol ELF; this is AM9 Pro, not S905X5M).
  4. `RodrigoDeveloperX/xiaomi-mi-tv-stick-4k-mdz-27-aa-recovery` `main` → `95a440273808b4568500e0fd4de1c5df33952a6c` (older MDZ-27-AA recovery project; not S905X5M/S7D; no local full dump).
  5. `yuliitezarygml/xiaomi-fimware` `main` → `00fae81b0f65e50e910a18361a0dca403a88e771` (older modified Mi TV Stick 4K archive project; not S905X5M/S7D).
- **Search set:** GitHub repository searches / web queries for `S905X5M`, `darkknight Xiaomi firmware`, `twilight Xiaomi firmware`, `Ugoos X5M firmware`, `Vontar X5 S905X5M`, `onn coffey`, and `systemcontrol S905X5M`. No qualifying public GitHub full ROM/dump mirror for darkknight, twilight, Ugoos X5M, Vontar X5, or onn/coffey was identified in these queries.
- **Interpretation:** bounded negative for the enumerated GitHub candidates and query set, not a claim that no dump exists anywhere on the internet.
- **Competing explanations / limit:** private, delisted, unindexed, non-GitHub, forum-hosted, or externally linked archives could exist. A guide or installer repository is not evidence that the stock Android partitions are present.
- **Next discriminating check:** if a specific public full-dump URL/repository appears, pin its commit/release and hash the ELF before using it as a build-ID/symbol comparator.

### F4 — `twilight` Android 14 OTA: acquired sibling artifact; internal ELF remains U

- **Claim/status:** P — OTA and payload partitions acquired and hashed; **U** — internal `systemcontrol` ELF not yet enumerated.
- **Source:** OTA URL linked by `xpxp233333/xiaomi-mibox5-guides` commit `56eae90381979a74040949790079e722e8903df0`: `https://android.googleapis.com/packages/ota-api/package/fbc6a620d9d88823fa3b4b4257e7c765eb471cb1.zip`.
- **OTA artifact:** 1,143,553,247 bytes; SHA-256 `a8770042cb04c0bfecd3079d94e9f8366102e721940aaa756f63ff00356eb61c`.
- **OTA metadata:** AB package; `pre-device=twilight`; `post-build=Xiaomi/twilight/twilight:14/UKG3.250107.001/V816.0.25.7.22.UZFAABX:user/release-keys`; incremental `V816.0.25.7.22.UZFAABX`; SDK 34; security patch `2025-06-01`; timestamp `1753131656`.
- **Extracted partitions:** `vendor.img` EROFS, 120,999,936 bytes, SHA-256 `80ac782390c9c700ab9b25438535d9fb7b2c453602a4c5d610734ac0dd5082ba`; `system.img` EROFS, 802,906,112 bytes, SHA-256 `57c782747a04949ef0664eaebad76c91bd5be528dbc437cd85acd6868da1daed`. The source OTA contains payload metadata/properties and signed package metadata. The extracted partitions were generated with `payload-dumper-go` 2.1.0; dumper release archive SHA-256 `bbbb53a71955c69272afdef7bc7e83a1bb1770f453d0c21dcaf61a3ba0463c11`.
- **Inspection boundary:** image format confirmed using `file`; EROFS mount attempt was denied by the host; `fsck.erofs`/`dump.erofs` were unavailable and package installation failed. No extracted OTA binary was executed. No ELF/string/build-ID scan of these EROFS contents is claimed.
- **Interpretation:** this is a pinned Android 14 sibling S7D build and a concrete lead for future build-ID/symbol comparison only; it does not yet establish any `systemcontrol` binary or call chain.
- **Competing explanations / limit:** service may reside in vendor, system, product, or system_ext; package itself may omit it or split it across partitions. The OTA is `twilight` sibling firmware, not darkknight or coffey.
- **Next discriminating check:** enumerate the OTA EROFS partitions with a compatible read-only userspace extractor, hash any `systemcontrol` ELF, record GNU build ID/exported symbols/strings and service registration/SELinux context. Keep every resulting row H for coffey until matched to coffey’s ELF.

### F5 — Coffey applicability and authorization

- **Claim/status:** U — coffey authorization and exact A14 call chain remain unresolved.
- **Observation:** no coffey ELF, service manifest, effective SELinux policy, or device-specific Binder access trace was part of this public-source sweep.
- **Interpretation:** neither the Pie stubbed `permissionCheck` nor the sibling OTA’s Android version determines whether coffey exposes or authorizes either method.
- **Competing explanations:** coffey may differ in service implementation, registration, transport, policy, caller identity checks, or build configuration.
- **Next discriminating check:** obtain the coffey `systemcontrol` ELF plus matching VINTF/init/SELinux artifacts; identify target methods and authorization at service, transport, and policy layers. No bypass claim is supported.

## Relay summary for Claude

Resolved: the earlier “only Pie branch searched” caveat is closed for the current public branch/tag inventory of `Amlogic-Lineage/android_vendor_amlogic_common_frameworks`; all 67 tags and the sole branch were checked. The AOSP Yukawa Android 12/13/14/main trees and their pinned Amlogic/BayLibre vendor package did not supply the methods or service binary. The named GitHub dump-search set produced no qualifying full Android dump. Comparator improved: a 2025 Android 14 `twilight` full OTA is now pinned and its `system`/`vendor` partitions are extracted, but EROFS internals remain uninspected. Single most informative next step: extract and fingerprint `systemcontrol` from that sibling OTA (if present), then match control flow and policy against coffey’s own ELF/artifacts when available. Coffey authorization remains U.

## Appendix A — Complete public tag inventory

The table lists all 67 tags from the repository’s current public tag refs, resolved to commit IDs. Dates are commit dates, not tag publication dates.

| Tag | Resolved commit | Commit date |
|---|---|---|
| `V160919` | `b6c4bd98bfee85ff8fa51b8cad69eb91db2c311c` | 2016-08-19 |
| `V161211` | `479dcc0e6fc34e8d96879475890eb321aa05d4d5` | 2016-09-23 |
| `V170421` | `c1257b29f622eac1de2dd3e24518f10087dce94b` | 2017-03-26 |
| `V170603` | `d8f59dc8365f54e44a4038909333315bde9ef4d5` | 2016-11-15 |
| `V170901` | `0ad9c018e5f9fa14e71b566fd2ba42fd464cb1f3` | 2017-08-09 |
| `V171027` | `6c83a2a6a9829f31cc703be1b6c40180280cc962` | 2017-10-25 |
| `V180206` | `7d7f5a49b7266bd8d9efbbd662f7bf48aa79de28` | 2017-09-28 |
| `V180622` | `063f7623e57789b16a0f00f0f00e8cac29563468` | 2018-05-21 |
| `V190327` | `063f7623e57789b16a0f00f0f00e8cac29563468` | 2018-05-21 |
| `Vim3-pie-V190704` | `701bb759bede9133e5b2bacd76b1bc029da9c9f5` | 2019-06-18 |
| `Vims-Pie-V190823` | `55fda43ba514b588b351a40a96b3e784449d4113` | 2019-07-10 |
| `Vims-Pie-V191202` | `4670740686b53c68f09ade0e881fa945795d14dd` | 2019-12-02 |
| `Vims-Pie-V200103` | `e59da77244504690783c2b21291dca752acb3537` | 2020-01-04 |
| `Vims-Pie-V200320` | `e59da77244504690783c2b21291dca752acb3537` | 2020-01-04 |
| `Vims-Pie-V200617` | `da3650f48dd0afd628293d52e7124bfb6c432296` | 2020-05-30 |
| `g12_9.0.0_20200401` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `g12_9.0.0_20200413` | `fc1470a0a6e4c079b693bda96761dff5c20164c5` | 2020-01-15 |
| `g12_9.0.0_20200422` | `3e584f4b5a4493be901afa56685ffd3784890019` | 2020-02-05 |
| `g12_9.0.0_20200507` | `3e584f4b5a4493be901afa56685ffd3784890019` | 2020-02-05 |
| `g12_9.0.0_20200520` | `ad09ce0260a947adb73ec3d5e08032956cc27d0b` | 2020-05-19 |
| `g12_9.0.0_64_20200401` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `g12_9.0.0_64_20200422` | `3e584f4b5a4493be901afa56685ffd3784890019` | 2020-02-05 |
| `g12_9.0.0_64_20200520` | `ad09ce0260a947adb73ec3d5e08032956cc27d0b` | 2020-05-19 |
| `s922_9.0.0_20190214` | `ca3a42a319a2534d18870f02e424274b47be72fd` | 2019-02-12 |
| `s922_9.0.0_20190222` | `db56071707bda5ed56db11d2721708192d4087e6` | 2019-02-21 |
| `s922_9.0.0_20190228` | `db56071707bda5ed56db11d2721708192d4087e6` | 2019-02-21 |
| `s922_9.0.0_20190308` | `c89922d6e84431027e89db7cf844aa1864973da5` | 2017-07-21 |
| `s922_9.0.0_20190319` | `35c9e586acb7b166f529e1656f45f10164e89a5d` | 2019-03-19 |
| `s922_9.0.0_20190320` | `35c9e586acb7b166f529e1656f45f10164e89a5d` | 2019-03-19 |
| `s922_9.0.0_20190321` | `35c9e586acb7b166f529e1656f45f10164e89a5d` | 2019-03-19 |
| `s922_9.0.0_20190404` | `23e3dc23cd41345d227feb94d292bcdf10634500` | 2019-03-26 |
| `s922_9.0.0_20190418` | `23e3dc23cd41345d227feb94d292bcdf10634500` | 2019-03-26 |
| `s922_9.0.0_20190425` | `23e3dc23cd41345d227feb94d292bcdf10634500` | 2019-03-26 |
| `s922_9.0.0_20190509` | `ac24f9aac7e60f1106b20943deaa526b0d340a66` | 2019-04-16 |
| `s922_9.0.0_20190516` | `ac24f9aac7e60f1106b20943deaa526b0d340a66` | 2019-04-16 |
| `s922_9.0.0_20190523` | `decf8a9294c84978ecd1823d2671aa3e88497279` | 2019-05-22 |
| `s922_9.0.0_20190531` | `decf8a9294c84978ecd1823d2671aa3e88497279` | 2019-05-22 |
| `s922_9.0.0_20190603` | `decf8a9294c84978ecd1823d2671aa3e88497279` | 2019-05-22 |
| `s922_9.0.0_20190612` | `aaeb8791250ae4d4bbfe9dac0febe1bf8c34a929` | 2019-06-03 |
| `s922_9.0.0_20190619` | `aaeb8791250ae4d4bbfe9dac0febe1bf8c34a929` | 2019-06-03 |
| `s922_9.0.0_20190719` | `416f78c4c737b5587550a11fb5910d5b30240651` | 2019-06-10 |
| `s922_9.0.0_20190726` | `416f78c4c737b5587550a11fb5910d5b30240651` | 2019-06-10 |
| `s922_9.0.0_20190801` | `416f78c4c737b5587550a11fb5910d5b30240651` | 2019-06-10 |
| `s922_9.0.0_20190812` | `416f78c4c737b5587550a11fb5910d5b30240651` | 2019-06-10 |
| `s922_9.0.0_20190820` | `416f78c4c737b5587550a11fb5910d5b30240651` | 2019-06-10 |
| `s922_9.0.0_20191028` | `4fb9c4e3bb665e5f1bb82073dde156e57b33a87e` | 2019-09-04 |
| `s922_9.0.0_20191118` | `7f54f80391bf0ca06a4bcfc8efc9b9fde158e4c9` | 2019-11-13 |
| `s922_9.0.0_20191119` | `7f54f80391bf0ca06a4bcfc8efc9b9fde158e4c9` | 2019-11-13 |
| `s922_9.0.0_20191121` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20191205` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20191213` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20191223` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20200110` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20200130` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20200305` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_20200318` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20190927` | `e6930f448456fb715e7556480261d7e2cf70d6a5` | 2019-09-09 |
| `s922_9.0.0_64_20191018` | `e6930f448456fb715e7556480261d7e2cf70d6a5` | 2019-09-09 |
| `s922_9.0.0_64_20191025` | `e6930f448456fb715e7556480261d7e2cf70d6a5` | 2019-09-09 |
| `s922_9.0.0_64_20191118` | `7f54f80391bf0ca06a4bcfc8efc9b9fde158e4c9` | 2019-11-13 |
| `s922_9.0.0_64_20191121` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20191205` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20191213` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20191223` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20200110` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20200130` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |
| `s922_9.0.0_64_20200318` | `7574e20525000df5519fbba1cdcb2cf65e972099` | 2019-11-20 |

## Appendix B — Integrity manifest

The companion `COFFEY-PQ-ANCHORS-AD14-DELTA-v2-SHA256SUMS.txt` contains SHA-256 for this report and the public OTA/payload extraction artifacts available locally. Source files and package contents are individually hashed above where relevant. The 1.14 GB OTA itself is not included in the handoff package; its URL and SHA-256 are recorded here.
