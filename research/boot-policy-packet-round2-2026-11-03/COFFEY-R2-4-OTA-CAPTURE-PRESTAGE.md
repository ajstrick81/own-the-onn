# COFFEY R2-4 — OTA endpoint and capture pre-stage

**Research date:** 2026-11-03. No coffey OTA package was downloaded. The public candidate URL below is metadata evidence only, not proof it is the unit's current or available update.

## Public target/build fingerprint

| ID · claim · classification | Target/build · artifact SHA-256 · source ref | Observation | Interpretation / competing explanation | Next discriminating check |
|---|---|---|---|---|
| R2-4a · coffey OTA target fingerprint · **R** | Catalog entry `OTAChecker #2594`; exact URL hash token `db1ba0cd0b332be68b0488095966feeb6b39305a`; OTA package not downloaded, so no local SHA-256 | [OTA record](https://otachecker.com/ota/2594) lists postcondition fingerprint `onn/coffey/coffey:14/URO4.260304.011.B1/15051976:user/release-keys`, build incremental `15051976`, device `coffey`, SDK 34, and `securityPatchLevel=2026-03-01`. Its precondition names device `coffey` but does not publish a source fingerprint. | Strong public metadata for an Android 14 coffey build. It does not prove that a specific physical unit is currently on that build. The 40-hex token embedded in the OTA URL is an endpoint identifier, **not** asserted to be a SHA-1 or SHA-256 digest. | Compare the captured device's full properties and OTA precondition to the catalog record and actual package metadata. |
| R2-4b · Google OTA URL pattern · **R/H** | Candidate package host: `android.googleapis.com`; redirect observed by the retrieval tool to `redirector.gvt1.com`; no package downloaded | Catalog URL: `https://android.googleapis.com/packages/ota-api/package/db1ba0cd0b332be68b0488095966feeb6b39305a.zip`. The tool observed redirect to `https://redirector.gvt1.com/packages/data/ota-api/package/db1ba0cd0b332be68b0488095966feeb6b39305a.zip`; the redirected body was not fetched. An independent OTA capture utility's README describes URLs of the same `/packages/ota-api/package/<HASH>.zip` form, but its GitHub branch head was not commit-pinned in this pass. | The endpoint path/host pattern is corroborated by an exact coffey catalog record. Do not assume all devices use one fixed update-check host or that the package URL remains live. | On the device, preserve the actual update-service request, full redirect chain, response headers, and returned package URL. |
| R2-4c · Google TV fingerprint shape · **P/R** | Exact catalog fingerprint above | Shape: `brand/product/device:release/id/incremental:type/tags`; actual coffey record is `onn/coffey/coffey:14/URO4.260304.011.B1/15051976:user/release-keys`. | The generic Android shape is not sufficient to synthesize an unknown future build. The published example is a real catalogued target, not a promised current fingerprint. | Capture the full on-device value rather than reconstructing it from the product model. |
| R2-4d · onn OTA host notes from update-blocker repo · **H / source commit pending** | `bgondell/onn-update-blocker`, `master` page read 2026-11-03; branch tip SHA unavailable via the indexed GitHub page; no file hash | README names `gvt1.com`, `gvt2.com`, and `update.googleapis.com` for downloads, and `android.googleapis.com`, `play.googleapis.com`, and `dl.google.com` during update checking/setup. The guide is for the 2023 YOC device and warns that those Google hosts serve other functions too. | Host strings are a same-vendor lead only; because no commit pin was retrievable and the described device/build is YOC rather than coffey, this is not coffey endpoint proof. | Re-open the repo at a full commit SHA or observe coffey's own request log. |

## OTA capture fields to preserve

Capture a read-only transcript around the update check and package retrieval. Retain exact raw values and timestamps; redact account/device secrets only in the share copy, never in the preserved original.

1. `ro.build.fingerprint` (full string), `ro.build.id`, `ro.build.version.incremental`, Android release/API level, `ro.build.version.security_patch`, and device/product/model properties.
2. Update-service request: service/component and action, request URL/host, method, query/body parameters, headers, timestamps, and the originating log lines. Record any request nonce/token separately and protect it as a secret.
3. Response: status, headers (`Content-Length`, `Content-Type`, `ETag`, `Last-Modified`, `Content-Disposition` if present), every redirect status and `Location`, final package URL, and advertised package size/hash fields. Record any advertised digest algorithm explicitly; do not infer it from digest length.
4. Package file: preserve unmodified bytes, exact byte count, and local `sha256sum`; record download tool/version and timestamp. Keep the OTA URL hash token separate from the locally computed SHA-256.
5. OTA metadata after acquisition: source/precondition and target/postcondition fingerprints, incremental/build ID, security patch, device/SDK level, payload size, and partition metadata. Hash the original ZIP before extraction or transformation.

## Source search scope and limits

- Checked `bgondell/onn-update-blocker` README on the `master` page and noted its YOC-only scope; current full commit SHA not exposed, so host claims remain H.
- Checked XDA-indexed query `site:xdaforums.com onn firmware "ro.build.fingerprint"`; no coffey fingerprint lead found there.
- Checked the exact Google OTA path on the coffey OTA catalog entry and an independent GitHub OTA-capture README. The latter was read on `main` but not commit-pinned; its role is pattern corroboration only.
- Checked exact-device search `"onn" "coffey" "ro.build.fingerprint" OR OTA`; found OTAChecker entry #2594 above.

**Relay:** an expected concrete target fingerprint and package URL pattern are now available to compare against Adam's capture. The catalog entry gives Android 14 build `URO4.260304.011.B1`, incremental `15051976`, SPL `2026-03-01`, and an OTA URL token; it is not a downloaded image and does not replace the live capture. The single next step is to capture coffey's own current fingerprint plus its update-service response and preserve the original package bytes for SHA-256.

**SHA note:** no OTA package was downloaded. The endpoint's 40-character token is not a local content hash. Report-file SHA-256 is in `SHA256SUMS.txt`.
