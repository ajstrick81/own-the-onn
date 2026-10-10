---
finding_id: AML-F0015
title: "S7D↔SC2 reset-index delta: 57 shared resets at IDENTICAL slots (0 reindexed), 35 S7D-added / 30 SC2-dropped — in-place edit of the same 192-bit reset map"
component: soc-generations
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-soc
confidence: confirmed
source_refs:
  - AML-S0006
source_urls: []
source_revision: "dt-bindings reset headers at CoreELEC common_drivers commit 8646fbd1"
related_findings:
  - AML-F0007
  - AML-F0009
status: promoted
---

# S7D ↔ SC2 reset-index delta (quantified lineage)

Compares the reset binding-header namespaces `amlogic,meson-s7d-reset.h` (92
`RESET_*`) and `amlogic,meson-sc2-reset.h` (87), both at commit `8646fbd1`.

## Observations
- **57 reset names shared** between S7D and SC2, and **every one is at the SAME
  index (0 reindexed).** Shared examples incl. `RESET_SD_EMMC_A`=152,
  `RESET_SD_EMMC_B`=153 (identical both gens).
- **35 S7D-only** (new signals): `RESET_USB1/USB0/USB1_COMB/USB0_COMB`(4–7),
  `RESET_USBCC`(10), `RESET_HDMI20_AES`(15), `RESET_GPU_TS`(39), `RESET_AM2AXI`(64),
  `RESET_SAR_ANA`(83), `RESET_SD_EMMC_C`(154)…
- **30 SC2-only** (dropped in S7D): `RESET_USBCTRL`(4), `RESET_DSPA`(43),
  `RESET_PCIE_CTRL/PHY/APB`(44/45/46), `RESET_SPICC1`(74), `RESET_RSA`(75),
  `RESET_SPIFC`(81)…
- Both namespaces span the same bit range **[0..191]** (6× RESET0–RESET5 words).
- **Slot repurposing:** freed SC2 slots are reused for new S7D signals at the same
  numeric position (e.g. slot 4 = SC2 `RESET_USBCTRL` → S7D `RESET_USB1`).

## Interpretation
S7D did **not renumber** the reset controller — it performed an **in-place edit
of SC2's 192-bit reset map**: shared signals keep their exact SC2 slots, SC2-only
signals (notably PCIe + DSP audio) are removed, and S7D signals (expanded USB,
GPU thermal, extra eMMC/SARADC) occupy new or freed slots. This quantifies the
"SC2-inherited reset IP" claim (AML-F0007): the inheritance is both at the
*binding* level (compatible `meson-sc2-reset`) and the *index-map* level (57
slot-stable signals), with a bounded S7D-specific diff (35 added / 30 removed).
Consistent with coffey's used reset indices (AML-F0009): SD_EMMC_A/B shared-same,
SAR_ANA(83)/SD_EMMC_C(154) S7D-only.

## Alternative explanations / discipline
Header namespaces are the DT-binding reset index contract; this is a DT/BSP-level
lineage measurement, not a silicon reset-tree netlist. The removed SC2 signals
(PCIe/DSPA) indicate feature-set differences, not proof those blocks are absent
from the die (a compatible node could still exist via another controller).

## Validation needed / ceiling
A register-level reset tree (addresses per word) would need the reset controller
driver's register map; this finding is index-namespace level only.
