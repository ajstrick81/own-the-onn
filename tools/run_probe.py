#!/usr/bin/env python3
"""Run one probe against named inputs and write an append-only capture (probes/README.md §1, §5).

usage: python -I tools/run_probe.py <probe-id> [role=path ...] [--dry-run]
  <probe-id>   path under probes/ without .py, e.g. kernel/cve-2026-43499-rtmutex
  role=path    input for a role declared in the probe header. Roles not given here are looked up in
               probes/local-inputs.json (git-ignored; see probes/local-inputs.example.json).

Input types (from the probe header `# inputs:` line, `role:type`, `?` = optional):
  file  -> sha256 + size          dir -> manifest sha256 over (relpath, sha256) of regular files
  git   -> "<repo>@<rev>": resolved commit + tree id     adb -> device serial (not recorded)

The capture is results/<probe-id>/<UTC>-<body-sha12>.txt: a provenance header, then the probe's stdout
verbatim. Captures are never overwritten; each run appends a line to results/SHA256SUMS.
Local paths are never written into a capture, only roles and fingerprints.
"""
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBES = os.path.join(ROOT, "probes")
RESULTS = os.path.join(ROOT, "results")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def header(probe_path):
    meta = {}
    with open(probe_path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                if line.strip():
                    break
                continue
            if ":" in line and not line.startswith("#!"):
                k, v = line[1:].split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def roles(meta):
    out = []
    for item in meta.get("inputs", "").split(","):
        item = item.strip()
        if not item:
            continue
        name, typ = item.split(":", 1)
        opt = typ.endswith("?")
        out.append((name.strip(), typ.rstrip("?").strip(), opt))
    return out


def fingerprint(typ, value):
    if typ == "file":
        return f"sha256={sha256_file(value)} size={os.path.getsize(value)}"
    if typ == "dir":
        h, n, skipped = hashlib.sha256(), 0, 0
        for dp, dn, fn in os.walk(value):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                if os.path.islink(p) or not os.path.isfile(p):
                    continue
                rel = os.path.relpath(p, value).replace(os.sep, "/")
                try:
                    digest = sha256_file(p)
                except OSError:  # e.g. WSL symlinks that Windows can't open
                    skipped += 1
                    continue
                h.update(f"{rel}\0{digest}\n".encode())
                n += 1
        return f"manifest-sha256={h.hexdigest()} files={n} unreadable-skipped={skipped}"
    if typ == "git":
        repo, rev = value.rsplit("@", 1)
        commit = subprocess.check_output(["git", "-C", repo, "rev-parse", rev + "^{commit}"], text=True).strip()
        tree = subprocess.check_output(["git", "-C", repo, "rev-parse", commit + "^{tree}"], text=True).strip()
        return f"commit={commit} tree={tree}"
    if typ == "adb":
        return "device (serial not recorded; identity is in the probe output)"
    raise SystemExit(f"unknown input type {typ}")


def tool_versions(types):
    v = [f"python {platform.python_version()}", f"os {platform.system()}"]
    if "git" in types:
        v.append(subprocess.check_output(["git", "--version"], text=True).strip())
    return "; ".join(v)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        raise SystemExit(__doc__)
    pid = args[0].replace("\\", "/").removesuffix(".py")
    probe = os.path.join(PROBES, *pid.split("/")) + ".py"
    if not os.path.isfile(probe):
        raise SystemExit(f"no probe {probe}")
    meta = header(probe)
    given = dict(a.split("=", 1) for a in args[1:])
    local = {}
    lp = os.path.join(PROBES, "local-inputs.json")
    if os.path.isfile(lp):
        local = json.load(open(lp, encoding="utf-8"))
    inputs, prov = {}, []
    for name, typ, opt in roles(meta):
        val = given.get(name, local.get(name))
        if val is None:
            if opt:
                continue
            raise SystemExit(f"missing input role '{name}' ({typ}); pass {name}=<path> or set it in {lp}")
        inputs[name] = val
        prov.append(f"#   {name} ({typ}): {fingerprint(typ, val)}")
    if dry:
        print("\n".join(prov))
        return 0
    r = subprocess.run([sys.executable, "-I", probe, "--inputs", json.dumps(inputs)],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit(f"probe failed (exit {r.returncode}); no capture written")
    body = r.stdout
    json.loads(body)  # a probe must emit one JSON object
    body_sha = hashlib.sha256(body.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    head = [f"# probe: {pid} @ {sha256_file(probe)}",
            f"# class: {meta.get('class', '?')}",
            "# inputs:", *prov,
            f"# tools: {tool_versions({t for _, t, _ in roles(meta)})}",
            f"# run: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            f"# body-sha256: {body_sha}",
            "# ---"]
    outdir = os.path.join(RESULTS, *pid.split("/"))
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"{now.strftime('%Y%m%dT%H%M%SZ')}-{body_sha[:12]}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite existing capture {out}")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(head) + "\n" + body)
    rel = os.path.relpath(out, RESULTS).replace(os.sep, "/")
    with open(os.path.join(RESULTS, "SHA256SUMS"), "a", encoding="utf-8", newline="\n") as f:
        f.write(f"{sha256_file(out)}  {rel}\n")
    print(f"capture: results/{rel}")
    print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
