# darkknight OTA reconnaissance — public endpoint and build-ID leads

Research date: 2026-11-02 (America/Chicago). No OTA was downloaded or fabricated in this research. Every endpoint family below is a public comparator unless explicitly marked darkknight-confirmed.

## Result

The public evidence identifies **at least two Xiaomi TV update-service patterns**, plus a separate Google OTA package URL form used by Xiaomi Google TV devices. It does **not** identify which pattern darkknight uses. The exact OS3.0.2.0 build string appears in a public owner comment, but not beside a downloadable package or captured update log.

Do not synthesize a darkknight URL from its build string. The most reliable capture discriminator remains the actual package URL and metadata emitted during darkknight's ordinary update check, correlated to the device's reported build/fingerprint.

## Public endpoint families

| Family / example | Observed use | Relation to darkknight |
|---|---|---|
| `https://ota-mitv.cdn.pandora.xiaomi.com/translator/...` | Xiaomi TV forum posts show full-package paths and `packageUrl` / `packageUrl2` entries in updater logs. A second mirror family is `https://cdn.cnbj3-fusion.fds.api.mi-img.com/translator/...`. | H only. Those are other Xiaomi TV models/older update-service generations. No darkknight request was found. |
| `https://<region>.tv.global.mi.com/tvservice/getdevicestatus?...` | A 4PDA owner log shows a 2026 Xiaomi TV updater querying `ua.tv.global.mi.com`, with `server_region`, `ptf`, `mitv_sw_ver`, `mitv_hw_ver`, `os_type`, and device type fields. | H only. It is the status/check API in that report, not the firmware payload URL; device is not proven darkknight. |
| `https://android.googleapis.com/packages/ota-api/package/<opaque-hash>.zip` | A public Xiaomi TV Box S 3rd Gen guide lists working full OTA URLs in this form. | H for Xiaomi Google TV service products; not demonstrated for darkknight. Opaque hash does not encode the build string in a predictable way. |

## Build identity and naming ambiguity

The Xiaomi Box 5 owner guide associates `MOB2MB-5P` with codename `darkknight`, system model `MiTV-AZFU0`, Android 14, and factory build `UD2A.240505.001.W1.OS2.0.7.0.UZFAABX`. It describes the device as Xiaomi Box 5. A later public owner comment (2026-10-30) reports a device as “Xiaomi Box 5 MAX” with `MiTV-AZFU0`, `device=darkknight`, S7D, Android 14, and `OS3.0.2.0.UZFAABX`. Separately, a public model catalog maps `MOB2MB-5P` to Box 5 and `MOB1MB-5M` to Box 5 MAX.

This is a **naming/model identity conflict**, not enough evidence to declare OS3.0.2.0 as an OTA for the exact MOB2MB-5P hardware. The build-ID shape itself is plausible for the same software family, but the public report does not provide a fingerprint, package, payload metadata, or verified model label.

## Capture-ready verification fields

When an owner-authorized OTA URL becomes available, record the following before extraction:

1. Device model label, product/model properties, codename, full `ro.build.fingerprint`, incremental/build ID, Android release, and security patch.
2. Update-service log lines showing request parameters and the returned package URL, advertised size/hash, source build and target build.
3. HTTP response headers, redirect chain, final hostname, byte count, and locally computed SHA-256 of the unmodified package.
4. OTA metadata (`payload_properties.txt` / payload manifest, if present), payload partition list, and package-signature verification result. Keep these package facts separate from an image extracted from a different model.

**Expected pattern status:**

- Darkknight endpoint/host: **U**.
- OTA API class: **H**; observed only on other Xiaomi TV devices.
- `OS3.0.2.0.UZFAABX` association: **R** owner report, product identity needs corroboration.
- Downloadable stock image and SHA-256: **U — not found**.

## Sources

- Xiaomi Box 5 owner guide / hardware identity: https://github.com/xpxp233333/xiaomi-mibox5-guides and https://xpxp233333.github.io/xiaomi-mibox5-guides/hardware.html
- Public OS3.0.2.0 owner report (Aerial TV issue #901, comment 10): https://github.com/pengchujin/aerial-tv/issues/901
- Public Xiaomi TV updater and endpoint logs (4PDA Xiaomi TV S Pro 2026): https://4pda.to/forum/index.php?showtopic=1115060&st=240
- Public Xiaomi TV OTA package URL patterns (4PDA; other TV model): https://4pda.to/forum/index.php?showtopic=1050344&st=580
- Xiaomi TV Box S 3rd Gen full OTA hash-URL examples: https://gist.github.com/imSp4rky/75ca403530780feeb3182d5d269ee421
- Product-code mapping `MOB2MB-5P` vs `MOB1MB-5M`: https://github.com/KHwang9883/MobileModels/blob/master/brands/mitv_cn.md
- Generic Android update-engine request/response model: https://android.googlesource.com/platform/system/update_engine/

