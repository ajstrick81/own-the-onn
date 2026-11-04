# coffey OTA capture — 2026-10-09 (ingested 2026-11-03)

The maintainer's capture of coffey's **own** OTA (`URO4.260304.011.B1`, SPL 2026-03-01) and the offline
analysis done on it in October, brought into the repo. This is priority vector #1 ("the one unlock"), now done.
Text only: firmware bytes stay on the maintainer's machine and are pinned by hash.

| File | What it is |
|---|---|
| [`COFFEY-OTA-CAPTURE.md`](COFFEY-OTA-CAPTURE.md) | Acquisition record (URL, redirects, ETag, size, **ZIP SHA-256 `ec755bd0…b1a7`**), package identity vs. the expected build (all fields match), kernel banner, extracted-partition table |
| [`COFFEY-OTA-FINDINGS.md`](COFFEY-OTA-FINDINGS.md) | Findings O1–O13 graded P/R/B/H/U, plus what they change in the CVE and boot-policy tracks |
| [`COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt) | Off-repo checksum list: ZIP, `payload.bin`, every extracted image, kernel, DTBs, `systemcontrol` ELF + libs (not committed, so CI skips them) |
| [`source-notes/`](source-notes/) | The maintainer's original notes and read-only captures, **byte-identical** to the originals ([`SHA256SUMS`](source-notes/SHA256SUMS); `.gitattributes` disables EOL conversion so CRLF captures stay exact) |
| [`SHA256SUMS.txt`](SHA256SUMS.txt) | Checksums for this packet's own reports |

### Source notes (original IDs kept)

| Note | Topic |
|---|---|
| `ACQUISITION-PROVENANCE.txt`, `EXTRACTION-PROVENANCE.txt` | Download and `payload_dumper` logs with hashes |
| `META-INF-com-android-metadata.txt`, `payload_properties.txt` | The package's own metadata |
| `ANALYSIS.txt`, `kernel-parse.txt`, `DT-CHARACTERIZE.txt` | First pass: DTs, kernel header, `otacert` |
| `BOOTLOADER-INVENTORY.txt`, `PHASE5-BOOT-CONTAINER.md`, `PHASE5-BL33-ENCRYPTION-FINDING.md` | Bootloader container layout; the BL33 note carries a 10-10 **partial withdrawal** banner (read it first) |
| `E0003-LINEAGE-MATRIX.md`, `E0005-ARCH-MAP.md` | S7D ↔ SC2 lineage; clock/reset/pinctrl/reserved-memory map |
| `E0006-DRIVER-MAP.md`, `E0006-PROBE-DIAGRAMS.md` | Vendor vs. mainline driver stacks, probe flows from public source |
| `E0006B-MODULE-INVENTORY.md`, `E0006C-FIRSTSTAGE-INVENTORY.md`, `*.load`, `vendorboot-ko-names.txt` | Module inventories and boot load order |
| `by-name.txt`, `lpdump-coffey-slot_b.txt`, `proc-partitions.txt`, `sysfs-mmc-geometry.txt` | Read-only captures from the owner's unit (partition map, dynamic-partition layout, a permission-denied bound) |

## Bottom line

The OTA is genuine and matches the expected build. coffey's kernel is GKI `5.15.196-android14-11-g3d26c188ef7e-ab14657224`,
built 2026-01-03. The kernel, DTB and `systemcontrol` ELF are all on hand. The bootloader's later stages are
opaque (encrypted or packed, unresolved), which keeps BL33 behaviour and the env question indeterminate.

**Next:** CVE applicability against this exact kernel build (vectors #2/#3), then `systemcontrol` and the
boot-policy phases.

### Deliberately not ingested

The maintainer's local store also holds kernel rebuilds, a `ghostlock/` workspace, and CVE trigger/repro code.
Under the repo's no-exploit rule none of that is committed, and none of it is summarized here.
