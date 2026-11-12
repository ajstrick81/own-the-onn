#!/usr/bin/env python3
"""Offline, read-only scan for a TEE Trusted-Application UUID in firmware bytes.

Searches every file under the given paths for the UUID in five representations,
so a built-in/secure-world reference is caught even when no `<uuid>.ta` file ships:

  ascii-hyphen-lower   023f8f1a-292a-432b-8fc4-de8471358067
  ascii-hyphen-upper   (same, upper)
  ascii-compact-lower  023f8f1a292a432b8fc4de8471358067
  packed-be            canonical byte order: 02 3f 8f 1a 29 2a 43 2b 8f c4 ...
  packed-optee-mixed   OP-TEE in-memory TEE_UUID (timeLow/Mid/HiVer little-endian):
                       1a 8f 3f 02 2a 29 2b 43 8f c4 ...

Usage:  python -I scan_ta_uuid.py <uuid> <path> [<path> ...]
Paths may be files or directories (walked). Compressed containers that hold no
plaintext (payload.bin, *.zip) are skipped by name. Unreadable entries (Windows
cannot resolve Android symlinks -> os error 1920) are counted and skipped, never
fatal. Prints each hit as `HIT <path> <offset> <form>`; a summary goes to stderr.
Read-only: opens files for reading only; imports nothing from the scanned data.
"""
import mmap
import os
import sys

SKIP_NAMES = {"payload.bin"}
SKIP_EXT = {".zip"}


def uuid_forms(u):
    u = u.lower().strip()
    hexs = u.replace("-", "")
    b = bytes.fromhex(hexs)                       # canonical big-endian order
    tl, tm, th, node = b[0:4], b[4:6], b[6:8], b[8:16]
    mixed = tl[::-1] + tm[::-1] + th[::-1] + node  # OP-TEE in-memory layout
    return {
        "ascii-hyphen-lower": u.encode(),
        "ascii-hyphen-upper": u.upper().encode(),
        "ascii-compact-lower": hexs.encode(),
        "packed-be": b,
        "packed-optee-mixed": mixed,
    }


def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for dirpath, _dirs, files in os.walk(p):
                for f in files:
                    yield os.path.join(dirpath, f)
        else:
            yield p


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: python -I scan_ta_uuid.py <uuid> <path> [<path> ...]")
    uuid = sys.argv[1]
    forms = uuid_forms(uuid)
    scanned = skipped = named_skip = hits = 0
    for fp in walk(sys.argv[2:]):
        base = os.path.basename(fp).lower()
        if base in SKIP_NAMES or os.path.splitext(base)[1] in SKIP_EXT:
            named_skip += 1
            continue
        try:
            with open(fp, "rb") as fh:
                try:
                    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                except (ValueError, OSError):
                    skipped += 1
                    continue
                scanned += 1
                try:
                    for name, pat in forms.items():
                        i = mm.find(pat)
                        while i != -1:
                            print(f"HIT\t{fp}\t{i}\t{name}")
                            hits += 1
                            i = mm.find(pat, i + 1)
                finally:
                    mm.close()
        except OSError:
            skipped += 1
            continue
    sys.stderr.write(
        f"[scan] uuid={uuid} scanned={scanned} unreadable_skipped={skipped} "
        f"name_skipped={named_skip} hits={hits}\n"
    )
    for name, pat in forms.items():
        shown = pat.hex() if name.startswith("packed") else pat.decode()
        sys.stderr.write(f"[scan] form {name}: {shown}\n")


if __name__ == "__main__":
    main()
