# COFFEY-R2-5-FCC-PHOTO-REVIEW

**Review date:** 2026-11-03  
**Scope:** Visual, host-side review of the named FCC internal-photo and label/location exhibits and EDN teardown images. No device interaction or electrical testing was performed. This is a public-photo comparator only.

## Finding

**R2-5-01 · Candidate exposed four-pad row visible in FCC photos · H — photo lead, unverified · target/build: FCC filings for Luxshare CS116K4Y / CS116K4O; coffey retail identity and board revision unresolved.**

In page 3 of FCC internal-photo exhibit 7952340 (CS116K4Y), the pictured PCB has four small exposed pads in a row near the upper-left edge in the photographed orientation, beside a legible silk-screen legend that appears to read “GND / TX / RX / GND.” The corresponding area is also visible in page 3 (Configuration 2) of exhibit 7952199 (CS116K4O), with similar pad/legend presentation. The pad row is a **candidate test/serial interface from the photo**. The apparent legend is transcribed as visual text only; this report does **not** assert that it accurately identifies electrical functions or pad order.

The photos do not establish that either suffix/filing PCB is the same revision as the user's retail onn 4K Plus (“coffey”) unit. No FCC suffix-to-retail-unit match has been verified from the user's unit label. The EDN teardown photos are consistent contextual board images for onn 4K Plus, but they do not resolve this exact board-revision identity.

- **Artifact hashes:** see COFFEY-R2-5-SHA256SUMS.txt. FCCID.io reports SHA-256 for the two internal-photo PDFs and label/location PDF. EDN serves the four selected images through resized image URLs; their original-file hashes were not obtained, so no image-byte hash is claimed.
- **Source refs:** FCCID.io exhibit records for docs 7952340, 7952339, 7952199; EDN article by Brian Dipert, published 2025-10-13.
- **File + locator:** 7952340, p. 3/4; 7952199, p. 3/5 (“Configuration 2”); 7952339, p. 1/1. EDN figures/image links 79, 80, 89, 103.
- **Observation:** the FCC p. 3 images show a four-pad exposed row and adjacent silk-screen lettering that visually appears to read GND/TX/RX/GND. The EDN figures 79/80 show the standalone PCB sides; 89 and 103 show the opened shield regions, including eMMC/DRAM and the S905X5M area. No similarly clear, labeled four-pad row is visible in the four EDN images reviewed.
- **Interpretation:** a photo-backed candidate now exists in the enumerated FCC filing images. It is not a verified UART, not a pinout, and not evidence about coffey's exact production board.
- **Competing explanations:** the pads may be factory test points, an unused/debug interface, or another purpose; silk-screen text may be incomplete or not correspond to actual electrical behavior; the user's retail SKU may use a different PCB revision; visually similar photos may represent a related filing variant rather than the user's device.
- **Next discriminating check:** read the FCC ID/model information from the physical unit label and compare the exact board revision/markings to the filing photos. Any electrical characterization must be performed on the actual unit with appropriate continuity and scope measurements before connection. This sheet is not a wiring instruction.

## Exact image-review inventory

| Source / artifact | Pages or image IDs visually reviewed | Visual result |
|---|---|---|
| FCC ID 2AYYS-CS116K4Y, internal photos, exhibit 7952340 | All pages 1–4; p. 3 examined at increased display zoom | Four-pad candidate and apparent silk-screen legend on p. 3. Other pages provide enclosure, PCB, and remote views. |
| FCC ID 2AYYS-CS116K4Y, label/location, exhibit 7952339 | Page 1 | Label drawing and laser-engraving location; no board/test-point view. Filing identifies product code CS116K4Y and FCC ID 2AYYS-CS116K4Y. |
| FCC ID 2AYYS-CS116K4O, internal photos, exhibit 7952199 | All pages 1–5; p. 3 examined at increased display zoom | Similar candidate pad row/legend visible on p. 3, Configuration 2. Other pages show enclosure/board configurations and associated components. |
| EDN, “Inside Walmart’s onn. 4K Plus” | Article images 79 (PCB bottom), 80 (PCB top), 89 (bottom-side cage interior), 103 (top-side cage interior) | Reviewed each actual image. No comparably clear labeled four-pad group in these four images; small pads elsewhere cannot be excluded solely from these views. |

### EDN image pins

All are image links from the article dated 2025-10-13; the figure numbers below are the article's link/image IDs. The web-rendered image endpoints were served at 950 px width.

- **79:** https://www.edn.com/wp-content/uploads/pcb-overview_bottom.jpg?resize=950%2C1011&w=950
- **80:** https://www.edn.com/wp-content/uploads/pcb-overview_top.jpg?resize=950%2C985&w=950
- **89:** https://www.edn.com/wp-content/uploads/pcb_bottom_cage-inside-1.jpg?resize=950%2C812&w=950
- **103:** https://www.edn.com/wp-content/uploads/pcb_top_cage-inside-1.jpg?resize=950%2C789&w=950

## Search-discipline record

- **Enumerated and reviewed:** FCCID.io document pages and PDF content for 7952340 (4 pages), 7952339 (1 page), and 7952199 (5 pages); the four specified EDN images 79/80/89/103.
- **Not reviewed:** additional FCC exhibits, other EDN teardown images, user-generated board photographs, or any physical retail unit.
- **Bounded statement:** a candidate is visible in the named FCC exhibit photos. The EDN images reviewed do not independently show a comparably clear, labeled candidate. This is not a claim that no other test points exist, or that the pictured pads serve UART.
- **No transfer:** no FCC/EDN observation is treated as a confirmed coffey fact. No pin functions, pad order, voltage, or electrical hookup are inferred.

## Sources

1. FCCID.io, [CS116K4Y internal photos, doc 7952340](https://fccid.io/2AYYS-CS116K4Y/Internal-Photos/Internal-Photos-7952340) — four-page PDF; SHA-256 recorded by page as 79911efe04eb89a04a28806ec83b18bdbac4be47537ea2c653bb99caf6a1a485; available 2025-07-05.
2. FCCID.io, [CS116K4Y label and location, doc 7952339](https://fccid.io/2AYYS-CS116K4Y/Label/Label-and-Location-7952339) — one-page PDF; SHA-256 recorded by page as 633249258371b990447a394c888dc058722e946b06acb8340fd9eff9d97d821f; available 2025-01-06.
3. FCCID.io, [CS116K4O internal photos, doc 7952199](https://fccid.io/2AYYS-CS116K4O/Internal-Photos/Internal-Photos-7952199.pdf) — five-page PDF; SHA-256 recorded by page as 0d359c42d7db6b31572123e767885b95c7ab3f401797581270616d46baf12ed6.
4. Brian Dipert, EDN, [Inside Walmart’s onn. 4K Plus: A streaming device with a hidden bonus](https://www.edn.com/inside-walmarts-onn-4k-plus-a-streaming-device-with-a-hidden-bonus/), 2025-10-13; article image IDs 79, 80, 89, 103.
