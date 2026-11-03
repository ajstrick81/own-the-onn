# COFFEY PQ source anchors

Date: 2026-11-02 (America/Chicago). Public artifact retrieval and host-side static analysis only. No device connection, firmware script execution, flashing, live boot, HIDL invocation or repository commit occurred. Host extraction/decompression utilities and researcher-written parsers were used; recovered firmware scripts and binaries were treated as data.

Classification: **P** inspected public source/artifact; **R** author report, not reproduced; **B** inherited project baseline; **H** inference/lead; **U** unresolved. A donor observation is not a coffey observation. Artifact hashes identify bytes, not trustworthiness or device compatibility.

Paths are relative to the evidence package root. `artifacts/` contains retrieved sources; `release/` and `nightly-new/` contain extracted files. Full image archives are separate deliverables, with URLs and hashes in the manifest.

## Reference and limits

Public repository: https://github.com/Amlogic-Lineage/android_vendor_amlogic_common_frameworks/tree/9f87fb04e81e4d5577bea584aa098d42b06f16ab
Branch resolved: khadas-vims-pie_64. Commit: `9f87fb04e81e4d5577bea584aa098d42b06f16ab`. This is older Amlogic donor source, not Android 14 coffey source. Every call relationship below is **P in this source, H / lead only for coffey**. Coffey ELF offset is pending for every row; the inherited 0x80cd8 address is not assigned to a donor function without the matching ELF/hash.

| Anchor | Public function / call relationship | Source locator under services/systemcontrol | Coffey ELF offset |
|---|---|---|---|
| CFG_ALL_PQ_MOUDLE_ENABLE | Macro → literal pq.AllPQMoudle.en; section PQ | PQ/include/CConfigFile.h:17–19 | Pending |
| mPQConfigFile->GetString | LoadPQSettings → CConfigFile::GetString(section,key,default) | PQ/CPQControl.cpp:334–342; PQ/CConfigFile.cpp:219 | Pending |
| CPQControl::LoadPQSettings | disable branch → VPPDeviceIOCtl(AMVECM_IOC_S_PQ_STATUE); enabled branch → DIModule, PQMode, gamma/color, DNLP and display helpers | PQ/CPQControl.cpp:334–396 | Pending |
| mPQdb | CPQControlInit → new CPQdb → copy default if persistent path missing → openPqDB | PQ/CPQControl.cpp:50–75; PQ/include/CPQControl.h:25–30 | Pending |
| mSSMAction->SSMReadDnlpMode | GetDnlpMode → SSMReadDnlpMode → SSMReadNTypes | PQ/CPQControl.cpp:3743; PQ/SSMAction.cpp (symbol match) | Pending |
| CPQControl::SetBacklight | Local-dimming branch → Cpq_SetBackLight; is_save==1 → SaveBacklight → SSMSaveBackLightVal | PQ/CPQControl.cpp:2525–2570 | Pending |
| factorySetParamsDefault | Client → HIDL HAL → SystemControlService → CPQControl::FactorySetParamsDefault | SystemControlClient.cpp:946; SystemControlHal.cpp:994; SystemControlService.cpp:1411; PQ/CPQControl.cpp:3316 | Pending |
| FactorySetParamsDefault | FactoryResetPQMode, FactoryResetNonlinear, FactoryResetColorTemp, then overscan reset in one of two DB objects | PQ/CPQControl.cpp:3316–3328 | Pending |
| getPQDatabaseInfo | Client callback → HAL → service → GetDBVersionInfo | SystemControlClient.cpp:1178; SystemControlHal.cpp:1226; SystemControlService.cpp:2024; PQ/CPQControl.cpp:5284 | Pending |
| GetDBVersionInfo | DB selector → PQ_GetPqVersion or GetOverScanDbVersion; default selector falls back to PQ DB | PQ/CPQControl.cpp:5284–5310 | Pending |
| PQ_GetPqVersion | getSqlParams → SELECT ToolVersion,ProjectVersion,GenerateTime FROM PQ_VersionTable → select/cursor | PQ/CPQdb.cpp:2089 | Pending |

## Findings that constrain interpretation

- The fetched LoadPQSettings has **no argument**, whereas the 4PDA excerpt takes source_input_param_t. The shared name and typo do not establish identical revisions.
- Donor paths use /vendor/etc/tvconfig/pq/pq.db and /mnt/vendor/param/pq/pq.db. The initializer copies the former when the latter is missing. This is not proof that coffey chooses those paths or uses odm_ext the same way.
- The reset method reaches database-reset helpers; it is not a harmless getter. Do not invoke it.
- The database-info donor path reads a version table, but also chooses objects and copies returned strings. This is a code-navigation lead, not certification that coffey's method is side-effect-free or safely callable for every selector.
- SystemControlService::permissionCheck at lines 118–138 has its permission-check body commented out and returns NO_ERROR in this donor. The inspected reset/query wrappers do not introduce checks. This does not resolve service-manager access, SELinux Binder/HwBinder policy, transport checks or coffey's implementation. A service being declared or visible is not proof an unprivileged caller can reach it.
- The HAL query wrapper returns Result::OK after filling fields; that return value alone is not proof of an underlying database operation's success.

## Matching procedure for Claude

Search literal configuration strings first, identify function boundaries and callers in the matching coffey ELF, then compare control flow and object layout. Trace database selection, reset helpers and authorization separately. Record negative matches and version differences. Preserve MOUDLE/Moudle exactly. Do not import donor addresses, struct sizes or trust assumptions.

### PQ-01 — Reset/query wrapper chain is now concrete donor evidence

- Target build: khadas-vims-pie_64 donor source
- Artifact SHA-256: `d2016efda1cad77312f7efa7c78c11b73c161cd5bf8ce9fe0c17c1dee80fb82e`
- Source revision: `9f87fb04e81e4d5577bea584aa098d42b06f16ab`
- File + locator: `artifacts/pq-SystemControlHal.cpp` — lines 994 and 1226
- Observation: P: wrappers call service methods; query fills callback fields.
- Interpretation: Useful function-chain landmarks, lead only for coffey.
- Competing explanations / limits: Older branch; generated transport and target policy not matched.
- Next discriminating check: Cross-reference strings and calls in the exact coffey ELF.

### PQ-02 — Donor permission helper is stubbed

- Target build: khadas-vims-pie_64 donor source
- Artifact SHA-256: `3a0d7683d6b865989ec3452724459f4d0ea316b5de9737f961dcd66378ed74bd`
- Source revision: `9f87fb04e81e4d5577bea584aa098d42b06f16ab`
- File + locator: `artifacts/pq-SystemControlService.cpp` — lines 118–138
- Observation: P: permission-check code is commented out; function returns NO_ERROR.
- Interpretation: Prioritize caller-policy reconstruction; no coffey vulnerability conclusion.
- Competing explanations / limits: Other transport/SELinux gates may prevent access; coffey code may differ.
- Next discriminating check: Trace matching target wrappers and effective SELinux policy.
