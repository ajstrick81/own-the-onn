---
finding_id: AML-F0001
title: "Device inventory — onn 4K Plus (coffey)"
component: device-inventory
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0001
source_urls: []
source_revision: "SPL 2026-03"
related_findings: []
status: promoted
---

# Device inventory — onn 4K Plus (coffey)

| Field | Value | Confidence | Source |
|---|---|---|---|
| Marketing name | Walmart onn 4K Plus | confirmed | AML-S0001 |
| Codename / platform | coffey / s7d | confirmed | AML-S0001 |
| SoC | Amlogic S905X5M | confirmed | AML-S0001 |
| SoC family / generation | S7D | confirmed | AML-S0001 |
| CPU / arch | arm64 kernel, 32-bit userland | confirmed | AML-S0001 |
| Android version | 14 | confirmed | AML-S0001 |
| Security patch level | 2026-03 | confirmed | AML-S0001 |
| Kernel version | GKI 5.15.196-android14-11 | confirmed | AML-S0001 |
| Bootloader state | welded: OEM-unlock disabled, flash locked, AVB green | confirmed | AML-S0001 |
| Board revision | not recorded | unknown | — |
| Firmware build id | not recorded here | unknown | — |

## Notes
All `confirmed` fields are read from the device's own build properties and
`/proc/config.gz` (AML-S0001), not from a retail listing or spec aggregator —
per this repo's rule that device identity is settled against primary sources.
A fuller device/attack-surface narrative is in `../../research/root-study.md`.

Board revision and exact firmware build id are left `unknown` rather than
guessed; fill them from a device read before marking confirmed.
