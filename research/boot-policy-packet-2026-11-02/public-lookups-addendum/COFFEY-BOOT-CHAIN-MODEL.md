# COFFEY boot-chain model — public architectural comparator

Research date: 2026-11-02 (America/Chicago). This is a stage model assembled from public artifacts and reports. It is **H — architectural/donor lead**, not a verified coffey chain reconstruction. No signing keys, donor images, or device-specific addresses are transferred.

## Model and confidence boundary

Public material supports an Amlogic-style chain with an on-chip BootROM, vendor BL2, later vendor stages, and a FIP carrying trusted-firmware/U-Boot components. Linux Amlogic storage definitions name boot areas `1STBLOB`, `BL2E`, `BL2X`, `DDRFIP`, and `DEVFIP`. A public S7D-specific source that states exactly which S7D stage authenticates each following stage, which anti-rollback counter is consulted, and where the counter is stored was not located.

The table therefore distinguishes **observed component names**, **generic architectural expectation**, and **coffey unknowns**. A secure-boot tool or config for another SoC does not establish the S7D fuse state or verification policy.

## Stage-to-control map

| Stage / object | Publicly supported statement | Signature / rollback conclusion | Coffey status |
|---|---|---|---|
| BootROM / BL1 | Amlogic BootROM is the first on-chip stage. Odd Solutions documents a BootROM exploit on the older S905D3G Chromecast; the jarvis2 report states its Amlogic ROM enforces the lock. | Hardware-rooted authentication is the expected secure-boot role, but no S7D ROM specification or coffey fuse dump was found. Do not infer a bypass or a particular key slot. | B: project baseline reports locked/green verified boot. Exact S7D ROM/fuse details U. |
| BL2 | Vendor U-Boot tooling and older configs expose BL2 signing/encryption options. A G12B config describes BL2 as restricted by ROM boot; a TL1 signer script accepts an anti-rollback configuration and sets a BL2 ARB CVN. | These sources show mechanisms in other families. They do not prove the S7D BL2 format, signing mode, verification path, or CVN policy. | U pending exact bootloader package, build match, and target evidence. |
| BL2E / BL2X | Amlogic kernel storage header names dedicated BL2E and BL2X boot areas. A S4 report provides a UART load message for BL2E, but is a different platform. | Naming/loading does not itself prove an independent signature check or rollback check at either stage. | The prior coffey baseline reports BL2E/BL2X present in OTA; hashes and authenticated relationships U. |
| DDRFIP / DEVFIP / FIP | The same storage header names DDRFIP and DEVFIP. Generic TF-A FIP documentation describes a container for firmware images; it is not Amlogic S7D policy documentation. | Container membership is not a signature verdict. S7D component manifests, certificates and stage policy remain unknown. | U. Need exact package plus offline structure/signature inspection. |
| BL31 / BL32 / BL33 | Generic ARM Trusted Firmware convention uses BL31 for EL3 runtime, optional BL32 secure payload/TEE, and BL33 as non-secure payload/U-Boot. Public SC2 boot-flow description reports this sequence on SC2. | The SC2 report and generic TF-A docs are architecture comparators only. They do not prove coffey's exact binaries or validation boundary. | Baseline indicates TEE and U-Boot-related components, but exact S7D build mapping U. |
| U-Boot → Android boot images | Amlogic G12B config includes AVB-related boot flow; AOSP AVB describes signed vbmeta/rollback indexes in Android Verified Boot. | Android AVB rollback protection is distinct from Amlogic BL2/ROM anti-rollback. `verifiedbootstate=green` is a high-level result, not a stage-by-stage trace of which firmware objects were checked. | B: coffey green/locked reported. Exact chain descriptors, vbmeta chain and rollback index state U. |
| External recovery / USB image | CoreELEC recovery can write environment variables on the host-audited image path. | Environment writes alone do not show that ROM/BL2/U-Boot accepts an alternate kernel or image. Acceptance may depend on earlier chain policy and boot path. | U. Need target-specific policy and exact recovery path evidence. |

## Anti-rollback: keep mechanisms separate

1. **Amlogic boot-firmware rollback** may be implemented in early boot stages and/or OTP/eFuse-backed state. Public TL1 signing tooling shows an ARB-CVN input; older-family configs expose an anti-rollback build option. Neither establishes S7D behavior.
2. **Android AVB rollback indexes** protect verified OS metadata/partitions and use trusted storage according to the platform's AVB integration. This is a separate layer and should not be conflated with BL2 CVNs.
3. **Observed green/locked state** establishes the reported high-level Android verified-boot state, not the exact list of Amlogic firmware objects authenticated or their rollback counters.

## Evidence ledger

| ID | Claim | Source / revision | Observation | Interpretation and competing explanation | Next discriminating check |
|---|---|---|---|---|---|
| BC-P1 | Amlogic boot areas include BL2E/BL2X and DDRFIP/DEVFIP labels. | Amlogic kernel `drivers/amlogic/mtd/nand_bootpart.h`, commit `f5269100977385d1fd4a5ef68e49631892cf4fe4`. | Header defines sizes/names for the listed boot areas. | P for source definitions; not evidence every S7D device uses same layout. | Match partition metadata in the exact S7D/coffey artifact. |
| BC-P2 | A vendor U-Boot signer can accept a BL2 firmware anti-rollback config. | Android external U-Boot commit `85456d35639a7a126d820f7db5801b1f837502bb`, `fip/stool/amlogic-sign-tl1.sh`. | Script exposes `-b <firmware-antirollback-config>` and a BL2 CVN variable. | P for TL1 tool behavior only; family/build transfer is H. | Locate S7D-matched tool/config or binary metadata. |
| BC-P3 | Amlogic G12B code documents ROM-restricted BL2 and AVB switches. | G12B U-Boot config commit `a8fd56bc97e2f7713e8dbcc24eeda292e62104f4`. | Comments and config flags are present in G12B board config. | Comparator only; G12B is not S7D. | Obtain S7D board config or firmware build manifest. |
| BC-R1 | jarvis2 owner reports locked/green state and ROM-enforced lock on an onn 4K Pro. | https://hack.ec/posts/2026-10-27-adb-to-root-on-a-locked-android-tv/ ; owner report. | Article describes a different onn board/build and its owner's observation. | R; useful same-vendor/brand context, not proof for coffey. | Compare exact SoC/board and bootloader generation before applying any implication. |
| BC-R2 | Sabrina (S905D3G) secure-boot work documents older Amlogic chain and rollback hazards. | https://oddsolutions.github.io/Chromecast-with-Google-TV-4K-Secure-Boot-Bypass-v2/ ; https://fredericb.info/2021/11/booting-ubuntu-on-google-chromecast-with-google-tv.html | Authors describe BL1 exploit history and older/newer bootloader rollback mismatch. | R on another SoC; strong warning not to transfer old bootloader behavior to S7D. | Keep only as method/architecture comparator. |

## Public sources

- Amlogic kernel storage header: https://android.googlesource.com/kernel/arm64/+/f5269100977385d1fd4a5ef68e49631892cf4fe4/drivers/amlogic/mtd/nand_bootpart.h
- Android external U-Boot TL1 signer: https://android.googlesource.com/platform/external/u-boot/+/85456d35639a7a126d820f7db5801b1f837502bb/fip/stool/amlogic-sign-tl1.sh
- G12B U-Boot config: https://nest-open-source.googlesource.com/manifest_repos/u-boot/+/a8fd56bc97e2f7713e8dbcc24eeda292e62104f4/board/amlogic/configs/g12b_w411_v1.h
- S4 report with BL2E USB load log (different chip): https://github.com/MarcinWad/Amlogic_s905W2_S4
- Generic TF-A FIP/boot-stage documentation: https://trustedfirmware-a.readthedocs.io/en/latest/
- AOSP AVB: https://android.googlesource.com/platform/external/avb/+/master/README.md
- jarvis2 report: https://hack.ec/posts/2026-10-27-adb-to-root-on-a-locked-android-tv/
- Odd Solutions Sabrina report: https://oddsolutions.github.io/Chromecast-with-Google-TV-4K-Secure-Boot-Bypass-v2/

