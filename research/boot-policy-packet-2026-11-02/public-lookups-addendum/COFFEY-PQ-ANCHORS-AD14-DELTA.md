# COFFEY PQ anchors — newer-public-source delta

Research date: 2026-11-02 (America/Chicago). Public-source, host-side research only.

## Result

The public `Amlogic-Lineage/android_vendor_amlogic_common_frameworks` source previously used for the PQ map is still the only source located in this search that exposes the relevant implementation. It is an Android Pie-era Khadas VIM branch (`khadas-vims-pie_64`, repository commit recorded in the existing anchor report as `9f87fb04e81e4d5577bea584aa098d42b06f16ab`). The repository catalog shows it was last updated in April 2022. Exact searches for `factorySetParamsDefault`, `getPQDatabaseInfo`, `CPQControl.cpp`, and `CFG_ALL_PQ_MOUDLE_ENABLE` did not locate a public Android 12/13/14 implementation or a newer equivalent call graph.

**Conclusion:** no A14-era source delta can be asserted. The prior call map remains a **lead-only Pie donor map**, not an authorization model for coffey. This is a bounded negative search result, not proof that newer vendor source is unavailable privately or under another name.

## Candidate inventory

| Candidate | What was inspected/found | Applicability |
|---|---|---|
| `Amlogic-Lineage/android_vendor_amlogic_common_frameworks`, `khadas-vims-pie_64` | Public tree and Java manager references; repository listing reports last update 2022-04-02. Prior report pins source commit `9f87fb04e81e4d5577bea584aa098d42b06f16ab`. | Android Pie donor only; no A14 authorization inference. |
| `UVCHAL/vendor/amlogic/frameworks/services/systemcontrol` | Public old systemcontrol tree; indexed source is ~2014 vintage. | Too old to close the A14 gap. |
| Vantiva UZW4030WNH OSS report | 2024 publication lists an Amlogic `frameworks/services/systemcontrol` component and module revision `e145027`, but the report is not the implementation source and is for another product/platform. | Acquisition lead only; not an A14/S7D match. |
| Amlogic interface / public logs | Search surfaced older HIDL interface material and service logs, but not matching newer `CPQControl` source with both target methods and caller checks. | Symbols/log text alone cannot establish control flow. |

## Delta against existing PQ anchors

| Anchor | Pie donor status | A14/public delta | Coffey status |
|---|---|---|---|
| `CFG_ALL_PQ_MOUDLE_ENABLE` | Present in older public configuration source. Preserve the misspelling. | No newer occurrence located in the searched public sources. | U — must match exact ELF/config. |
| `mPQConfigFile->GetString`, `mPQdb`, `mSSMAction->SSMReadDnlpMode` | Prior map records these in older CPQControl paths. | No newer call graph found. | U. |
| `CPQControl::LoadPQSettings`, `CPQControl::SetBacklight` | Older donor code exposes these anchors and calls. | No A14 implementation found to compare semantics. | U. |
| `factorySetParamsDefault` | Existing donor map records client → HAL/service → CPQControl reset/reseed path; donor permission routine differs from coffey’s unknown checks. | No newer public implementation found. | U — coffey ELF and caller policy required. |
| `getPQDatabaseInfo` | Existing donor map records client → HAL/service → CPQControl/database query path. | No newer public implementation found. | U — do not call “safe” from method name alone. |
| Authorization | Pie branch had a permissive/stubbed permission routine in the previously inspected source. | No Android 12+ body found; no generalization is justified. | U — service registration, transport permissions, caller checks, SELinux and callee behavior remain target-specific. |

## Next discriminating public/target check

Once coffey material is available, first pin the matching `systemcontrol` ELF by SHA-256 and GNU Build ID. Resolve the service descriptor/version and VINTF registration from the same build, then trace method handlers and every deeper caller/UID/PID/permission/SELinux gate. If an Android 12–14 source dump becomes available, pin its manifest/commit and compare exact symbols and bodies; do not accept a similarly named repo as a match without build provenance.

## Sources

- Amlogic-Lineage repository catalog: https://github.com/orgs/Amlogic-Lineage/repositories
- Pie donor Java wrapper: https://github.com/Amlogic-Lineage/android_vendor_amlogic_common_frameworks/tree/khadas-vims-pie_64
- Older public systemcontrol tree: https://github.com/ramalinga18680/UVCHAL/tree/master/vendor/amlogic/frameworks/services/systemcontrol
- Vantiva OSS publication (component/revision lead): https://www.vantiva.com/app/uploads/2024/10/UZW4030WNH-Version-2.2.14-OSS-Publication-1.pdf
- Existing donor call map: `COFFEY-PQ-ANCHORS.md` in the prior public-research packet.

