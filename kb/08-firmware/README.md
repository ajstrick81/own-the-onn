# 08 — Firmware

Partition layout, update/recovery flow, factory provisioning, A/B slots, and
image/container formats. Extraction method is the moria → mithril pipeline
(see `../../research/root-study.md`).

Record findings with `../_templates/finding.md`.

**Do not commit firmware images, vendor code, or extracted vendor binaries.**
The repo `.gitignore` blocks raw dumps; keep it that way. Record *what was
learned* from an image, with its build id, not the image.
