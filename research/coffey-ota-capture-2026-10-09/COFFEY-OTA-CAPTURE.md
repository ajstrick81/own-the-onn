# COFFEY OTA capture — acquisition, identity, extraction

**Captured:** 2026-10-09 (UTC) by the maintainer, on their own machine. **Ingested to the repo:** 2026-11-03.
Host-side download of the public OTA package plus offline extraction; the device itself was not modified. No
firmware bytes are committed: the off-repo artifacts are hash-pinned in
[`COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt), and the original working notes are
copied byte-for-byte into [`source-notes/`](source-notes/) (ledger: [`source-notes/SHA256SUMS`](source-notes/SHA256SUMS)).

This closes the capture half of priority vector #1 and supersedes the "no bytes fetched" state of
[`../boot-policy-packet-round2-2026-11-03/COFFEY-R2-4-OTA-CAPTURE-PRESTAGE.md`](../boot-policy-packet-round2-2026-11-03/COFFEY-R2-4-OTA-CAPTURE-PRESTAGE.md).

## 1. Acquisition (grade **P**)

| Field | Value |
|---|---|
| Request URL | `https://android.googleapis.com/packages/ota-api/package/db1ba0cd0b332be68b0488095966feeb6b39305a.zip` |
| Redirect chain | `302` → `redirector.gvt1.com/packages/data/ota-api/package/db1ba0cd….zip` → `302` → `rr1---sn-….gvt1.com/…` (Google edge cache) → `200 OK` |
| Final response | `Content-Type: application/octet-stream`, `Content-Length: 906283326`, **`ETag: db1ba0cd0b332be68b0488095966feeb6b39305a`**, `Last-Modified: Fri, 20 Mar 2026 01:48:23 GMT` |
| Tool / window | curl 8.18.0 (WSL), exit 0, `2026-10-09T03:27:56Z` → `03:30:06Z` |
| Bytes on disk | **906,283,326** (= `Content-Length`) |
| **SHA-256 (ZIP)** | **`ec755bd03500da81b0f509b393fa26451050c9711c689749cec2ffa49395b1a7`** |
| Re-verified | 2026-11-03 on the maintainer's machine — hash and size unchanged |

The 40-hex URL token is an endpoint/ETag identifier, **not** a content digest (R2-4b caution stands). The raw
response-header capture is kept off-repo (hash-pinned) because its edge-cache redirect carries the client IP
and signed cache parameters; the fields above are the non-identifying subset.

## 2. Package identity vs. the expected build (grade **P**)

Read from the ZIP's own `META-INF/com/android/metadata` (verbatim copy:
[`source-notes/META-INF-com-android-metadata.txt`](source-notes/META-INF-com-android-metadata.txt)):

| Field | Package says | Expected (R2-4 catalog / unit) | Match |
|---|---|---|---|
| `post-build` | `onn/coffey/coffey:14/URO4.260304.011.B1/15051976:user/release-keys` | same (OTAChecker #2594) | ✅ |
| `post-build-incremental` | `15051976` | `15051976` | ✅ |
| `post-security-patch-level` | `2026-03-01` | `2026-03-01` | ✅ |
| `post-sdk-level` | `34` | 34 (Android 14) | ✅ |
| `pre-device` | `coffey` | coffey | ✅ |
| `ota-type` | `AB` — **full** package (no `pre-build` precondition) | — | — |
| build ID vs. unit | `URO4.260304.011.B1` | `findings/coffey-2026-09.md` records the unit on `URO4.260304.011.B1` | ✅ |

ZIP members: `payload.bin`, `payload_properties.txt`, `apex_info.pb`, `care_map.pb`,
`META-INF/com/android/{metadata,metadata.pb,otacert}`.

**Payload integrity:** `payload.bin` = 906,274,586 B, SHA-256 `ad8b7611…6122c`. The package's own
`payload_properties.txt` `FILE_HASH` (base64) decodes to exactly that digest, and `FILE_SIZE` matches.
**Signature:** the embedded `otacert` is `CN=Android, O=Google Inc.` (2022-10-20 → 2052); this is the package's
own cert, **self-referential**, not an independent trust anchor. The ZIP's whole-file signature was not
verified against an external key.

## 3. Kernel identity — from coffey's own `boot.img` (grade **P**)

`boot.img` is header v4; its kernel is LZ4-legacy (magic `02 21 4c 18`; the 10-09 parser labelled it only
"not gzip"). The decompressed Image's banner:

```
Linux version 5.15.196-android14-11-g3d26c188ef7e-ab14657224 (build-user@build-host)
  (Android (10087095, +pgo, +bolt, +lto, -mlgo, based on r487747c) clang version 17.0.2 …, LLD 17.0.2)
  #1 SMP PREEMPT Sat Jan 3 21:52:40 UTC 2026
```

- GKI build **`ab14657224`**, git `g3d26c188ef7e`, built **2026-01-03**. `system_dlkm` modules carry the same
  vermagic (15/15), so the running-kernel string and the shipped kernel agree.
- Vendor modules (`vendor_boot` first stage 52/52, `vendor_dlkm` 109/112) are built against a **different**
  kernel build (`g10bd23fd47b5`); two `vendor_dlkm` modules are an older `5.15.192` base. The ABI is bridged by
  GKI KMI/modversions, not vermagic equality.

This is the input the CVE-applicability work (priority vectors #2/#3) was waiting on; that analysis is the
next step and is **not** done in this packet.

## 4. Extracted partitions (off-repo, hash-pinned)

`payload_dumper` (exit 0) on 2026-10-09; later re-extractions on 10-09/10-10/10-18 for audits. Same-named images
in different audit folders are byte-identical.

| Partition | Bytes | SHA-256 (prefix) | Notes |
|---|---|---|---|
| `boot` | 67,108,864 | `e9a02f96…` | GKI kernel (above) |
| `vendor_boot` | 67,108,864 | `3db861f2…` | base DT `s7d_s905x5m_bm202` + 52 first-stage `.ko`; 2 ramdisk fragments (boot, recovery) |
| `dtbo` | 2,097,152 | `4a9d07e1…` | one overlay: dummy battery/charger only |
| `bootloader` | 4,100,096 | `389daa99…` | Amlogic signed container, build `S7D-s905x5m-26030511BBST` |
| `init_boot` | 8,388,608 | `bc2112c2…` | |
| `vendor` | 83,812,352 | `78836a53…` | unpacked to `init-audit-images/vendor-ex/`: **`bin/systemcontrol` ELF (350,020 B, `aec8998d…`)** + `libsystemcontrolservice.so`, HIDL `systemcontrol@1.0/1.1`, `systemcontrol.rc` — **not yet analyzed** |
| `system` / `system_ext` / `product` | 473 M / 96 M / 544 M | `25f04a5d…` / `00a3019b…` / `35f3d682…` | |
| `vendor_dlkm` / `system_dlkm` | 22 M / 0.76 M | `42606eff…` / `7f6f41c8…` | EROFS/LZ4; 112 + 15 modules |
| `odm` / `odm_dlkm` / `odm_ext` / `oem` | | see ledger | |
| `vbmeta` / `vbmeta_system` | 12,288 / 4,096 | `4fb53c43…` / `595f6cbe…` | AVB descriptors not yet parsed |

Full digests: [`COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt).

## 5. Limits

- Package = expected build, and the unit's recorded build ID matches; the unit's **full live fingerprint** was
  not re-read on 2026-11-03 (it would only matter if the unit has since updated).
- The OTA ZIP signature and AVB/vbmeta chains are **not** verified here.
- No exploit, offset, or bypass material is in this packet. Kernel builds and trigger code elsewhere in the
  maintainer's local store are deliberately not ingested.
