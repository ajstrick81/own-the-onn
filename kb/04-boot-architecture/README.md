# 04 — Boot Architecture

Power-on through handoff to the kernel: Boot ROM, BL2, DDR training, BL31,
U-Boot, boot-image containers, and Android Verified Boot.

Record findings with `../_templates/finding.md`. This is a high-value
cross-generation comparison area (containers, init stages, firmware
packaging). Document *where execution stops* on a failed cross-gen boot — a
failed experiment that localizes the incompatibility is a result.
