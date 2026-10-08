# 05 — Security

TrustZone, TEE, fuses, signature formats, rollback protection, verified-boot
policy, and SELinux posture. Where a security operation lives (normal world
vs. secure firmware vs. hardware controller) is the key cross-generation
question.

Record findings with `../_templates/finding.md`.

**Scope of this repo (unchanged):** analysis of an owner's own device.
No working exploits, no weaponized primitives, no firmware or vendor code
redistribution. Memory-safety research is documented as attack-*surface*
analysis and reproduction/patch-validation, and is done in an emulator, not
against a device.
