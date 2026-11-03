#!/usr/bin/env python3
"""Verify every committed text artifact against its SHA256SUMS ledger.

Hardware-free integrity check (inspired by the PS5-14.10-Research repo's offline
verification). For each `SHA256SUMS*` file in the repo, each entry is checked IF
the referenced file is actually committed here; entries whose file is absent are
SKIPPED, not failed — the research packets intentionally keep large firmware
blobs out of git while still listing their hashes in the ledger.

Exit status: 0 if no committed file mismatches its recorded hash; 1 on any
mismatch (or a malformed ledger line). Designed to run in CI with no console or
device in the loop.

Line formats handled:
  <64-hex>  <path>
  <64-hex>  <path>  <NNNN> bytes       (trailing size annotation, tolerated)
  # comment / blank                    (ignored)
Paths resolve relative to the ledger's directory; if that misses, the basename
in the same directory is tried (covers ledgers that list files under a prefix).
"""
import hashlib
import os
import re
import sys

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_ledgers(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for name in filenames:
            if "SHA256SUMS" in name:
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def parse_line(line):
    """Return (want_hash, filename) or None for blank/comment/non-entry lines."""
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    parts = s.split()
    if len(parts) < 2 or not HEX64.match(parts[0]):
        return None  # header/prose line in a ledger, ignore
    want = parts[0].lower()
    rest = parts[1:]
    # tolerate a trailing "  <int> bytes" annotation
    if len(rest) >= 3 and rest[-1].lower() == "bytes" and rest[-2].isdigit():
        rest = rest[:-2]
    name = " ".join(rest)
    return want, name


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    ledgers = find_ledgers(root)
    if not ledgers:
        print("no SHA256SUMS ledgers found")
        return 0

    ok = skip = fail = bad = 0
    failures = []
    for ledger in ledgers:
        base = os.path.dirname(ledger)
        rel_ledger = os.path.relpath(ledger, root)
        with open(ledger, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                parsed = parse_line(line)
                if parsed is None:
                    continue
                want, name = parsed
                cand = [os.path.join(base, name),
                        os.path.join(base, os.path.basename(name))]
                target = next((p for p in cand if os.path.isfile(p)), None)
                if target is None:
                    skip += 1
                    continue
                got = sha256(target)
                if got == want:
                    ok += 1
                else:
                    fail += 1
                    failures.append(
                        f"  MISMATCH {os.path.relpath(target, root)}\n"
                        f"    ledger {rel_ledger}:{lineno}\n"
                        f"    want {want}\n    got  {got}")

    print(f"ledgers: {len(ledgers)} | verified: {ok} | "
          f"skipped (not committed): {skip} | mismatches: {fail}")
    if failures:
        print("\n".join(failures))
    return 1 if fail or bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
