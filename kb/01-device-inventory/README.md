# 01 — Device Inventory

Exact models, SoCs, Android/kernel builds, bootloader state, and board
revisions for every device in scope. One file per device, using
`../_templates/device.md`.

**Rule:** every field carries its own confidence and source. The device's
*identity* (SoC, kernel version, bootloader state) must be settled against a
primary source — on-device `getprop`/kernel config, or the signed firmware —
not an aggregator or a spec-sheet guess.
