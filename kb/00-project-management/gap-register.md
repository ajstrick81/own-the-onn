# Architecture gap register

Living list of unresolved items and their blockers. Updated 2026-10-09 (after
Phase 5 boot-container analysis). `offline` = resolvable without the device;
`device` = needs on-device access; `gated` = needs Director authorization and/or
a capability (e.g. root) we do not have.

| # | Gap | Status | Blocker / path to close |
|---|---|---|---|
| G1 | Physical GPT partition **start-LBAs** | ADVANCED (template) | bootloader-tail embeds a **CRC-valid GPT provisioning template** (AML-F0017): package-declared start-LBAs for all 31 partitions (names match device p1–p31). **LIVE absolute offsets still unmeasured** (UINT64_MAX placeholders; needs device read / factory image). |
| G2 | Physical **PCB revision** (independent of DT `bm202`) | OPEN | `device` — needs a physical/label or hardware read; DT only declares `bm202`. |
| G3 | **AO-domain pinctrl** pin-maps | PARTLY RESOLVED | coffey DTB declares ONLY `pinctrl@4000` periphs — no separate AO-pinctrl node present (AML-F0012). If AO pinmux is needed, it is not exposed in this DTB. |
| G4 | SCMI PWM clock indices | RESOLVED (static) | Shipped DT provider 0x18: PWM G/H/I/J use 19/20/21/22, matching pinned s7d-scmi-clkc.h. Runtime rates/enables remain G8. |
| G5 | Later boot **stages** SCP/BL31/BL32/BL33 identification | ADVANCED | DEVF = TF-A FIP; ToC identifies SCP/BL30/BL31/BL32/BL33 (+vendor BL40?) by UUID, no keys (AML-F0016, Codex+re-verified). Payload impl stays opaque. |
| G6 | Exact Coffey DDR firmware location | OPEN (narrowed) | S7D source merges 8192-byte ACS + 212992-byte DDR data, passes merged csinit-params to BL2 boot-blob creation; separate DDR input commented out. Exact Coffey range/build flags unresolved. |
| G7 | **TrustZone enforcement** (vs DT secure-region declarations) | OPEN | secure-world attestation / EL3 inspection — out of offline scope; DT `secmon`/secure pools are intent, not proof. |
| G8 | Runtime clock/reset/PLL **state** (vs DT-wired indices) | OPEN | `device` — on-device clk/reset tree dump; current claims are DT-wiring only. |
| G9 | S7D↔SC2 reset-**index** reindex delta | RESOLVED | AML-F0015: 57 shared resets at IDENTICAL slots (0 reindexed), 35 S7D-added / 30 SC2-dropped; in-place edit of the same 192-bit map. |
| G10 | Vendor I²C/MMC/USB probe tracing | RESOLVED (source) | Existing probe diagrams and G16 cover source flows/defer/failure paths. Runtime sequence remains unobserved. |
| G11 | Coffey CPU-ID path and runtime identity | NARROWED | Artifact-backed CPU-ID candidate is first-stage amlogic-cpuinfo → secmon: SMC 0x82000044 mode 2, version 2 + 16 ID bytes. Vendor major 0x47 agrees with mainline. amlogic-socinfo is separate socdata/NOCS. Returned IDs/runtime bind unobserved. |
| G13 | Full coffey **vendor-module** config (beyond GKI base) | OPEN | `gated` — GKI base config lacks CONFIG_AMLOGIC_*; vendor module config would need the vendor kernel build or on-device module enumeration. |
| G14 | SCMI **clock provider** for DTB `scmi_clk` (PWM G–J) | RESOLVED | `clk-scmi.ko` present + in vendor_boot first-stage modules.load (AML-F0014). Provider shipped despite GKI COMMON_CLK_SCMI unset. (Runtime bind still device-gated.) |
| G15 | vendor_boot module inventory and configured lists | RESOLVED (inventory) | 52 boot-fragment modules; 50-entry modules.load. List order is configured metadata, not actual execution order. Init consumer audit remains separate. |
| G12 | Which exact ATF/BL31 secure-monitor impl runs | OPEN | BL31 now UUID-identified in DEVF FIP (AML-F0016) but payload opaque (~8-bit entropy); impl/version needs keys/decode or UART trace. |
| G17 | Vendor FIP entry, prefix and image tail | PARTLY RESOLVED | Tail decoded as CRC-valid GPT provisioning template (not live geometry). BL40 probable from S7D template UUID/size and packing inputs; no symbolic UUID mapping located. DEVF prefix unresolved. |
| G18 | Pin TF-A UUID identification reference | RESOLVED | TF-A v2.10 commit b6c0948400594e3cc4dbb5a4ef04b815d2675808 matches four standard component UUIDs; does not identify Coffey ATF version. |

| G16 | First-stage OF-alias confirmation + deferred-probe/failure paths | RESOLVED | UART/I²C/MMC/WDT/SARADC/USB OF-alias-confirmed to first-stage modules; clk/reset/pinctrl/scmi are OF_DECLARE providers (no alias). Defer/fail paths documented (MMC/I²C defer on clkc; USB hard-fails). analysis/E0006-PROBE-DIAGRAMS.md. |

## Recently CLOSED
- Physical GPT **template** (package-declared 31-partition start-LBAs) → ADVANCED (G1, AML-F0017); live offsets still open.
- SCMI clock provider → RESOLVED (clk-scmi first-stage, AML-F0014).
- vendor_boot first-stage inventory → RESOLVED (52 .ko, AML-F0014).
- First-stage OF-aliases + probe defer/fail paths → RESOLVED (G16, AML-F0014 refinement).
- S7D↔SC2 reset-index delta → RESOLVED (G9, AML-F0015).
- Logical **super LP grouping** → RESOLVED (AML-F0008, on-device lpdump, 8 dyn + 8 cow).
- Upstream **commit SHA** → RESOLVED (`8646fbd1…`, files byte-identical; AML-S0006).
- Clock/reset **index tables** (clkc + reset) → RESOLVED, device-confirmed (AML-F0009).
- DT lineage S7D↔SC2 → AML-F0007; hardware architecture map → AML-E0005.
- Bootloader container internal map → AML-F0010 (this phase).
