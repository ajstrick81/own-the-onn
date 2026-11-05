# odm_ext consumers — 2026-11-04 (boot-policy Phase E)

What coffey's `odm_ext` partition holds, what reads it, under which privilege, and who can change it.
Offline only. Reports and scripts verify against [`SHA256SUMS.txt`](SHA256SUMS.txt); the partition's files are
pinned in [`ODMEXT-CONTENTS-SHA256SUMS.txt`](ODMEXT-CONTENTS-SHA256SUMS.txt) and not committed.

| File | Content |
|---|---|
| [`COFFEY-ODMEXT-CONSUMERS.md`](COFFEY-ODMEXT-CONSUMERS.md) | Mount and integrity facts, per-file consumer table, writers by policy, consumer graph, answers |
| [`scripts/pathscan.py`](scripts/pathscan.py) | String scan for odm_ext/PQ paths across ELFs, configs, jars and APK contents |

## Bottom line

- `odm_ext` is mounted read-only and is the **only firmware partition with no AVB/dm-verity coverage** (no
  fstab `avb` flag, absent from both vbmeta images). The baseline moves from B to **P**.
- Its only privileged consumer is **root `systemcontrol`** (via `libpqcontrol`), which parses `pq.db`
  (SQLite), `pq_default.ini` and `UI_PQSetting.bin` from it. Checks are CRC/version only, not authentication.
  The audio HAL (non-root) references three INIs that aren't present on coffey.
- Only `init`, `update_engine`, `fsck` and `e2fs` may write the partition; apps, `shell` and `system_control`
  can't. No software path from shell or app bytes into `odm_ext` was found.
- Five TV config files have no consumer, and a stray `chmod_files.sh` is inert (nothing references it; no
  domain may execute that label).
