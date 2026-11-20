# systemcontrol caller authorization — 2026-11-03 (boot-policy Phase F)

Offline, read-only analysis of coffey's own `vendor/bin/systemcontrol` and the SELinux policy coffey loads.
Nothing was invoked on a device. Reports and scripts verify against [`SHA256SUMS.txt`](SHA256SUMS.txt); the policy
inputs are hash-pinned in [`POLICY-INPUTS-SHA256SUMS.txt`](POLICY-INPUTS-SHA256SUMS.txt) and not committed.

| File | Content |
|---|---|
| [`COFFEY-PQ-AUTHORIZATION.md`](COFFEY-PQ-AUTHORIZATION.md) | Service shape, effective caller policy, in-process checks, the service's own SELinux limits, the Phase F acceptance table, reconciliations |
| [`scripts/cilq.py`](scripts/cilq.py) | Minimal CIL resolver (who-can / what-can with attribute expansion) |
| [`scripts/elfsyms.py`](scripts/elfsyms.py) | Minimal ELF reader (build-id, NEEDED, dynamic-symbol filter) |

## Bottom line

- `systemcontrol` runs **as root** and registers HIDL `ISystemControl` @1.0/@1.1 with ~300 methods, including
  boot-env, sysfs, key-storage, property and logo writes.
- **The shipped policy lets ordinary third-party apps reach it** (`untrusted_app`, `untrusted_app_32`: find +
  binder call, from explicit `vendor_sepolicy.cil` rules). `shell`/adbd can't.
- The binary imports **no caller-identity API**, so SELinux appears to be the only gate (`H`). The boot-env
  writer only checks the `ubootenv.var.` key prefix.
- The service's **own** policy stops it from writing bootloader, boot, vbmeta, super, misc, param, frp and
  factory partitions, and gives it no `CAP_SYS_ADMIN` or mount. It may write `env`, `logo`, `cri_data`, generic
  sysfs, key-storage nodes and vendor properties.
- End-to-end reachability from an app is **untested** (`U`). A vendor notice is optional — publishing isn't gated on it (policy
  2026-11-20; see the report's note).
- The inherited `0x80cd8` handler offset is outside this ELF's mapped range.
