"""Shared plumbing for probes: input parsing, deterministic JSON output, hashing.

A probe is run by tools/run_probe.py as:  python -I <probe.py> --inputs '<json {role: path-or-spec}>'
It must print exactly one JSON object on stdout (via emit) and read its inputs without modifying them.
"""
import argparse
import hashlib
import json
import sys


def inputs():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help="JSON object mapping role -> path/spec")
    return json.loads(ap.parse_args().inputs)


def emit(obj):
    """Print the probe's result; sorted keys so the same input always gives the same bytes."""
    sys.stdout.write(json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=True) + "\n")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
