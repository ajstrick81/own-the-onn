#!/usr/bin/env python3
"""Offline evidence check for CI and local use (probes/README.md §6).

usage: python -I tools/verify_offline.py [root] [--rerun]

1. Runs tools/verify_hashes.py over every SHA256SUMS ledger (committed text vs ledger).
2. For every capture under results/:
   - it must be listed in results/SHA256SUMS (verify_hashes checks the hash itself);
   - its `body-sha256` header must match the body below `# ---`;
   - its probe file must exist; if the probe changed since the capture, that is reported as STALE (not a failure).
3. --rerun (local only): for the newest capture of each host probe whose probe is unchanged and whose inputs are
   available (probes/local-inputs.json) with identical fingerprints, re-run the probe and require byte-identical
   output. Device captures are never re-run.

Exit 1 on any failure.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("--")), "."))
RERUN = "--rerun" in sys.argv[1:]
TOOLS = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_capture(path):
    text = open(path, encoding="utf-8").read()
    head, sep, body = text.partition("# ---\n")
    if not sep:
        return None, None
    meta, inputs = {}, {}
    for line in head.splitlines():
        s = line[1:].strip() if line.startswith("#") else ""
        if line.startswith("#   ") and "(" in s:
            role = s.split(" ", 1)[0]
            inputs[role] = s.split("): ", 1)[1]
        elif ":" in s:
            k, v = s.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["inputs"] = inputs
    return meta, body


def main():
    fails, notes = [], []
    sys.argv = [sys.argv[0], ROOT]
    if load("verify_hashes").main() != 0:
        fails.append("verify_hashes reported mismatches")

    results = os.path.join(ROOT, "results")
    ledger = os.path.join(results, "SHA256SUMS")
    listed = set()
    if os.path.isfile(ledger):
        for line in open(ledger, encoding="utf-8"):
            parts = line.split()
            if len(parts) >= 2:
                listed.add(parts[1])
    run_probe = load("run_probe")
    newest = {}
    n = 0
    for dp, dn, fn in os.walk(results):
        for f in sorted(fn):
            if not f.endswith(".txt"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, results).replace(os.sep, "/")
            n += 1
            if rel not in listed:
                fails.append(f"capture not in results/SHA256SUMS: {rel}")
            meta, body = parse_capture(p)
            if meta is None:
                fails.append(f"capture has no header separator: {rel}")
                continue
            if hashlib.sha256(body.encode()).hexdigest() != meta.get("body-sha256"):
                fails.append(f"body hash mismatch: {rel}")
            pid, _, psha = meta.get("probe", "").partition(" @ ")
            probe = os.path.join(ROOT, "probes", *pid.split("/")) + ".py"
            if not os.path.isfile(probe):
                fails.append(f"probe missing for {rel}: {pid}")
                continue
            stale = run_probe.sha256_file(probe) != psha
            if stale:
                notes.append(f"STALE (probe changed since capture): {rel}")
            if meta.get("class") == "host" and not stale and rel > newest.get(pid, ("", None))[0]:
                newest[pid] = (rel, meta, body, probe)

    if RERUN:
        local = {}
        lp = os.path.join(ROOT, "probes", "local-inputs.json")
        if os.path.isfile(lp):
            local = json.load(open(lp, encoding="utf-8"))
        for pid, (rel, meta, body, probe) in sorted(newest.items()):
            roles = run_probe.roles(run_probe.header(probe))
            inputs, ok = {}, True
            for name, typ, opt in roles:
                if name not in meta["inputs"]:
                    continue
                val = local.get(name)
                if val is None or run_probe.fingerprint(typ, val) != meta["inputs"][name]:
                    notes.append(f"rerun skipped for {pid}: input '{name}' unavailable or changed")
                    ok = False
                    break
                inputs[name] = val
            if not ok:
                continue
            r = subprocess.run([sys.executable, "-I", probe, "--inputs", json.dumps(inputs)],
                               capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0 or r.stdout != body:
                fails.append(f"rerun does not reproduce {rel}")
            else:
                notes.append(f"rerun reproduced {rel}")

    print(f"captures: {n} | host probes eligible for rerun: {len(newest)}")
    for x in notes:
        print("  " + x)
    for x in fails:
        print("  FAIL " + x)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
