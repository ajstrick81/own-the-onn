# COFFEY donor prerequisites

Date: 2026-11-02 (America/Chicago). Public artifact retrieval and host-side static analysis only. No device connection, firmware script execution, flashing, live boot, HIDL invocation or repository commit occurred. Host extraction/decompression utilities and researcher-written parsers were used; recovered firmware scripts and binaries were treated as data.

Classification: **P** inspected public source/artifact; **R** author report, not reproduced; **B** inherited project baseline; **H** inference/lead; **U** unresolved. A donor observation is not a coffey observation. Artifact hashes identify bytes, not trustworthiness or device compatibility.

Paths are relative to the evidence package root. `artifacts/` contains retrieved sources; `release/` and `nightly-new/` contain extracted files. Full image archives are separate deliverables, with URLs and hashes in the manifest.

## Matrix

“Yes” means explicitly shown/required. “U” means not established; “not stated” is not equivalent to “not required.” None of these sources demonstrates a locked-coffey bypass.

| Report | Root-capable adbd | Unlocked bootloader | Working external boot | Debug/userdebug build | What the evidence actually establishes |
|---|---|---|---|---|---|
| N3 X88 4PDA root/remount transcript | Yes, root restart reported | U | Not used in transcript | U; root-capable adbd alone does not prove exact build type | Already-privileged overlayfs workflow, not unprivileged odm_ext access |
| N4 X88 full-dump suggestion | Not required by proposed CE SSH path | U | Yes, assumed | U | Dump proposal starts after alternate OS boot; no initial-access result |
| N6 slimBOX Unlock_Bootloader.cmd | No adb command in inspected script | Not necessarily beforehand; standard unlock requested | Not required by script | U | Bootloader-fastboot response required; device must accept standard unlock. No exploit payload in script |
| S7 twilight dual boot | Root explicitly required; root-adbd specifically U | Yes, author states unlocked/orange | Existing alternate-boot route discussed | Debug-signed app mentioned, not proof of debug OS build | Rooted/unlocked-device storage and environment modification |
| N2 darkknight DSU backup | Root inside GSI; root-adbd specifically U | Yes, explicit prerequisite | DSU guest boot required, not USB boot | userdebug donor used to construct rooted GSI | Backup after unlocking and guest root; no locked-device bypass |

N3/N4 remain indexed-report evidence from the prior multilingual pass, not freshly downloaded forum attachments. URLs:
- N3: https://4pda.to/forum/index.php?showtopic=1104876&st=1540
- N4: https://4pda.to/forum/index.php?showtopic=1104876&st=7520
- N6 distribution: https://slimboxtv.ru/x96-m200/
- S7 pinned report: https://github.com/samtheruby/coreelec-android-dualboot-twilight/blob/e4bc9f0361e6d834d67cdedba58c678803e79fe2/research.md
- N2: https://xpxp233333.github.io/xiaomi-mibox5-guides/backup.html

## N6 script inspection, not execution

Member: Unlock_Bootloader/Unlock_Bootloader.cmd inside sbx_x96_m200_atv_14_26.zip, reached through the slimBOX-linked public Yandex folder. Local member SHA-256: `1309eccc93d7ce6f4a9bbd9b28bfcef17d729b18040a4f1f3f77752ba4bcf7ab`. It matches the pre-pause result. ZIP entry CRC was checked by Python zipfile during range extraction. Full-archive SHA was advertised by the host, not independently computed.

Observed commands, quoted as evidence only:

```bat
@( fastboot getvar is-userspace 2>&1 ) | find "is-userspace: no" > nul
@if not %errorlevel% == 0 (
  ...
  goto l
)
fastboot flashing unlock
fastboot reboot
```

The complete 22-line member is preserved as data. It contains no flashing image command, custom unlock payload or alternate cryptographic operation. It relies on a fastboot executable found by Windows command resolution and a connected device that permits the standard request. The bundled executable was not executed or certified.

The error branch targets label `l`, but the only label in the file is `:quit`. The script also does not check the unlock command's return code before issuing reboot. These are host-script control-flow defects/limitations; no runtime behavior was tested. The script does not establish OEM-unlock settings, confirmation UI, wipe behavior or the exact device firmware's authorization logic.

The distribution instructions require unlocking before the separate USB Burning Tool flashing workflow. A Verify Bootloader checkbox in that tool is not evidence that ROM verification is disabled. Do not flatten this case into “already unlocked required”: the script requests an ordinary permitted unlock. Equally, do not label it a demonstrated locked-device security bypass.

### PR-01 — slimBOX uses standard fastboot unlock request

- Target build: slimBOX X96 M200 unlock helper; target firmware version U
- Artifact SHA-256: `1309eccc93d7ce6f4a9bbd9b28bfcef17d729b18040a4f1f3f77752ba4bcf7ab`
- Source revision: `archive member; version 14_26`
- File + locator: `artifacts/Unlock_Bootloader.cmd` — lines 7–16
- Observation: P: checks is-userspace:no then flashing unlock and reboot.
- Interpretation: No custom bypass mechanism in this member.
- Competing explanations / limits: Acceptance depends on target bootloader; whole archive and executable not audited.
- Next discriminating check: Keep as donor prerequisite evidence; reconstruct coffey policy offline.
