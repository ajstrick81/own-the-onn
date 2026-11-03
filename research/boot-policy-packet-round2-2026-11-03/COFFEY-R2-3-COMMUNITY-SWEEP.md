# COFFEY R2-3 — exact-device community-report sweep

**Research date:** 2026-11-03. **Method:** bounded indexed web search with venue-qualified query strings. A zero-result response means no indexed match in the enumerated queries, not that a venue contains no such post anywhere.

## Bounded search inventory

| Venue | Queries checked | Result |
|---|---|---|
| CoreELEC Discourse (`forum.coreelec.org`) | `site:forum.coreelec.org "onn coffey"`; `site:forum.coreelec.org "onn 4K Plus S905X5M"`; combined `site:forum.coreelec.org "onn coffey" OR "onn 4K Plus" OR "coffey" S905X5M` | No results returned. No exact-device CoreELEC boot/report lead found. |
| 4PDA (`4pda.to/forum`) | `site:4pda.to/forum "onn coffey"`; `site:4pda.to/forum "coffey" Amlogic`; combined `site:4pda.to/forum "onn coffey" OR "onn 4K Plus" S905X5M OR "coffey" Amlogic` | No results returned. Search-engine indexing is not a direct search of private/login-only or unindexed thread content. |
| XDA (`xdaforums.com`) | `site:xdaforums.com "onn coffey"`; `site:xdaforums.com "onn S905X5M root"`; combined `site:xdaforums.com "onn coffey" OR "onn 4K Plus" S905X5M root OR "coffey" Amlogic` | No results returned. |
| FreakTab (`freaktab.com`) | `site:freaktab.com "onn coffey"`; `site:freaktab.com "onn 4K Plus S905X5M"`; combined `site:freaktab.com "onn coffey" OR "onn 4K Plus" S905X5M OR "coffey" Amlogic` | No results returned. |
| Reddit — `r/Onn` | `site:reddit.com/r/Onn "onn coffey"`; broader `site:reddit.com/r/Onn "coffey" OR "S905X5M" OR "4K Plus" root` | No exact root/alternate-boot lead returned. |
| Reddit — `r/AndroidTV` | `site:reddit.com/r/AndroidTV "onn 4K Plus S905X5M"`; broader exact-product search | Product and SoC discussion returned, including [“onn 4K Plus listed”](https://www.reddit.com/r/AndroidTV/comments/1g19u65/) and [“onn Google TV”](https://www.reddit.com/r/AndroidTV/comments/1pxyugs/). These are consumer/product reports, not root, CoreELEC, unlock, or alternate-boot work. |
| Reddit — `r/GoogleTV` | `site:reddit.com/r/GoogleTV "coffey" Amlogic`; `site:reddit.com/r/GoogleTV "onn coffey" OR "onn 4K Plus" S905X5M` | No exact-device root/alternate-boot lead returned. |
| GitHub | `site:github.com "onn coffey CoreELEC" OR "onn S905X5M root"`; `"onn coffey" OR "onn 4K Plus S905X5M" root CoreELEC`; `"coffey" Amlogic` | No pinned coffey root/CoreELEC/alternate-boot project found. A pinned ADB customization profile exists (below); it is not root or alternate boot. |

## Exact-device hits that do not change the boot-policy result

| ID · claim · classification | Target/build · artifact SHA-256 · source ref | Observation | Interpretation / competing explanation | Next discriminating check |
|---|---|---|---|---|
| R2-3a · device-profile / ADB debloat lead · **R** | GitHub `Gathin23/cleanyourtv`, pinned source snapshot `2dcd4a81e240eefb57cf2c50263226651c665476`; no binary | [Pinned profile snapshot](https://github.com/Gathin23/cleanyourtv/tree/2dcd4a81e240eefb57cf2c50263226651c665476/examples/onn-4k-plus-2025) names onn 4K Plus (2025), device `coffey`, S905X5M, Google TV 14. Its scope is app disabling/launcher configuration through ADB. | This is prior exact-device software customization, not bootloader unlock, root, CoreELEC, or alternate boot. | Inspect the pinned commit's files if device-software cleanup becomes relevant; do not infer access to boot partitions from ADB customization. |
| R2-3b · device-specific launcher fork · **H / unpinned lead** | `picajoso/tv-vibehack-javipas`, observed `main` branch on 2026-11-03; full branch commit SHA not available in the indexed page | Public README describes an onn 4K Plus `coffey` Android 14 ADB debloat/launcher fork. | Same class of user-space customization; branch not commit-pinned here and not evidence for boot-policy access. Excluded from confirmed repo findings. | Capture the branch commit SHA before citing it as a pinned artifact. |

## Bounded verdict

**No prior public coffey-specific root, CoreELEC boot, bootloader-unlock, or alternate-boot project was found across the enumerated indexed venues and queries.** This is a bounded negative, not a universal non-existence claim. Results include product discussion and user-space ADB customization; neither constitutes a locked-device bypass or alternate OS boot report. Exact search set and date are listed above. No donor offsets, keys, DTBs, or images were used.

**SHA note:** no device images or binary artifacts were downloaded. The only pinned code reference used above is the full Git commit in the source URL; report-file SHA-256 is in `SHA256SUMS.txt`.
