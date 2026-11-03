# COFFEY R2-2 — FCC filing and teardown hardware-access sheet

**Research date:** 2026-11-03. Public documentation only. No device was opened or tested in this task.

## Findings

| ID · claim · classification | Target/build · artifact SHA-256 · source ref | Locator · observation | Interpretation / competing explanation | Next discriminating check |
|---|---|---|---|---|
| R2-2a · product identity · **P/R** | onn. 4K Plus / `CS116K4`, also listed as `DV6116N / coffey`; no device artifact hash | [Android TV Guide device entry](https://www.androidtv-guide.com/streaming-gaming/onn-walmart-4k-plus-streaming-box-google-tv/) identifies code name `DV6116N / coffey / CS116K4` and S905X5M. | Strong model-level identity cross-reference; it does not identify which FCC suffix is printed on a particular retail unit. | Match the retail unit's regulatory label to the FCC ID before applying a specific FCC photo set. |
| R2-2b · FCC exhibits `2AYYS-CS116K4Y` · **P/R** | FCC OET application/grant indexed under [FCC ID 2AYYS-CS116K4Y](https://fccid.io/2AYYS-CS116K4Y); internal-photo document ID 7952340, label/location document ID 7952339; internal-photo PDF SHA-256 as listed by index: `79911efe04eb89a04a28806ec83b18bdbac4be47537ea2c653bb99caf6a1a485` | [Internal photos](https://fccid.io/2AYYS-CS116K4Y/Internal-Photos/Internal-Photos-7952340), [label/location exhibit](https://fccid.io/2AYYS-CS116K4Y/Label/Label-and-Location-7952339), [FCC filing index](https://fccid.io/2AYYS-CS116K4Y). Grant/index identifies Luxshare and CS116K4 family. | Official filing photos are model-level reference images. The FCC page is an index/mirror of OET exhibit documents; the FCC OET portal itself was not directly retrievable in this pass. No UART pad/pin assignment is established by the filing metadata. | Compare the unit's printed FCC ID and board revision to the label and internal-photo exhibits; inspect the actual exhibit image before asserting pads. |
| R2-2c · FCC exhibits `2AYYS-CS116K4O` · **P/R** | [FCC ID 2AYYS-CS116K4O](https://fccid.io/2AYYS-CS116K4O); internal-photo document ID 7952199; label/location exhibit linked from filing record | FCC ID search result identifies the same CS116K4 family under a second suffix and separate internal photo exhibit. | The two filings may represent color/variant or certification differences; suffix-to-retail-unit mapping remains unverified. Do not merge photos into one assumed PCB revision. | Read the regulatory label on the exact unit and select its matching filing. |
| R2-2d · board memory and SoC · **R** | EDN/Brian Dipert teardown of onn. 4K Plus, published 2025-10-13; source article (not downloaded); no artifact SHA-256 | [EDN teardown](https://www.edn.com/inside-walmarts-onn-4k-plus-a-streaming-device-with-a-hidden-bonus/), board images linked as article images 79/80/89/103; text identifies a FORESEE `FEMDNN016G` 16-GB eMMC, two Micron 8-Gbit DDR4 packages, and Amlogic S905X5M. | Direct editorial teardown of this product model supports component identification. It does not prove the same BOM on every production lot or FCC suffix. | Check package markings and board revision on the actual unit/filing photo. |
| R2-2e · UART / test-point location · **U** | Exact coffey retail unit and board revision unknown; no photo-backed pin map or boot log located | EDN page text search for `UART`, `serial`, and `test point` returned no match. FCC exhibit metadata names internal photos but no UART finding. | **No public UART pad, console pinout, or boot log is established by this search.** Absence from article text is not evidence pads are absent; pads may be unpopulated, shielded, or visible only in a close-up. | If a board photo or teardown is later obtained, identify pads only from a clear board-side photo and independent electrical documentation. Do not infer pin order or voltage. |

## Photo index

- `2AYYS-CS116K4Y`: [FCC internal photos, exhibit 7952340](https://fccid.io/2AYYS-CS116K4Y/Internal-Photos/Internal-Photos-7952340); [label and location, exhibit 7952339](https://fccid.io/2AYYS-CS116K4Y/Label/Label-and-Location-7952339).
- `2AYYS-CS116K4O`: [FCC filing index](https://fccid.io/2AYYS-CS116K4O) and internal photo exhibit 7952199.
- Exact-product teardown: [EDN article and board/chip photographs](https://www.edn.com/inside-walmarts-onn-4k-plus-a-streaming-device-with-a-hidden-bonus/).

## Relay

The useful non-root hardware avenue remains physically gated: these public sources help identify the board and its storage component, but do not reveal a confirmed UART pinout. Before relying on a filing photo, match the exact unit's FCC ID and board revision. No electrical assumptions or console access claims are transferred to coffey without a clear photo-backed pin map.

**SHA note:** the FCC index reports the internal-photo exhibit digest above; the PDF was not locally downloaded in this task. No other binary was downloaded. Report-file SHA-256 is in `SHA256SUMS.txt`.
