# id: telemetry/window-summary
# question: per scenario window, what does the box contact (rates, endpoints, DNS names, plaintext HTTP, direct-to-resolver DNS)?
# class: host
# inputs: capture:file, markers:file
# emits: json {windows: [{label, minutes, connections_per_h, unique_endpoints, unique_dns_names, top_hosts, http_plaintext, direct_dns, ports}]}
# grade: P for what the passthrough log recorded in each window (metadata only: DNS, SNI, destinations; nothing decrypted)
# refs: method/README.md §2; findings/coffey-2026-09.md; tools/passthrough_logger.py
# tools: none
"""Privacy-safe summary of a passthrough capture (study.jsonl) split by markers.txt windows.

Raw logs stay outside the repo. This output omits every IP address except well-known public DNS resolvers,
drops reverse lookups and anything mentioning a private address, collapses per-node CDN hostnames, and reports
plaintext HTTP as host + method only (never paths, which can carry device identifiers).
An open window (end "now") ends at the next window's start, or at the last record if it's the last window.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib.probe import emit, inputs  # noqa: E402

PUBLIC_RESOLVERS = {"8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1", "9.9.9.9", "149.112.112.112",
                    "208.67.222.222", "208.67.220.220", "94.140.14.14", "94.140.15.15"}
PRIVATE = re.compile(r"\b(10\.\d+|192\.168|172\.(1[6-9]|2\d|3[01])|127\.\d+|169\.254)\.\d+\.\d+\b")
TOP_N = 40


def norm_host(h):
    if not h:
        return None
    h = h.lower().rstrip(".")
    if h.endswith((".in-addr.arpa", ".ip6.arpa")) or PRIVATE.search(h) or re.fullmatch(r"[\d.]+|[0-9a-f:]+", h):
        return None
    h = re.sub(r"\brr\d+---sn-[a-z0-9-]+", "rr*---sn-*", h)  # per-node CDN names encode cache location
    # opaque per-device / per-session tokens (e.g. a 64-hex device hash in a telemetry hostname): any
    # hyphen/dot-separated token of 14+ characters mixing letters and digits becomes <id>
    h = re.sub(r"(?<![a-z0-9])(?=[a-z0-9]*\d)(?=[a-z0-9]*[a-z])[a-z0-9]{14,}(?![a-z0-9])", "<id>", h)
    return h


def windows(markers, last_t):
    rows = []
    for line in markers.splitlines():
        p = line.split(None, 2)
        if len(p) == 3:
            rows.append((float(p[0]), p[1], p[2].strip()))
    rows.sort(key=lambda r: r[0])
    out = []
    for i, (a, b, label) in enumerate(rows):
        inferred = b == "now"
        end = (rows[i + 1][0] if i + 1 < len(rows) else last_t) if inferred else float(b)
        out.append((a, end, label, inferred))
    return out


def main():
    inp = inputs()
    recs = [json.loads(l) for l in open(inp["capture"], encoding="utf-8") if l.strip()]
    last_t = max(r["t"] for r in recs) if recs else 0
    result = []
    for a, b, label, inferred in windows(open(inp["markers"], encoding="utf-8").read(), last_t):
        win = [r for r in recs if a <= r["t"] <= b]
        hrs = max((b - a) / 3600, 1e-9)
        conns = sum(1 for r in win if r["k"] == "conn")
        endpoints = {r.get("sni") or r.get("dst") for r in win if r["k"] in ("tls", "conn")}
        dnsq = {norm_host(r["q"]) for r in win if r["k"] == "dns"} - {None}
        hosts = collections.Counter()
        http = collections.Counter()
        direct = collections.Counter()
        ports = collections.Counter()
        for r in win:
            if r["k"] in ("tls", "dns", "http"):
                h = norm_host(r.get("sni") or r.get("q") or r.get("host"))
                if h:
                    hosts[h] += 1
            if r["k"] == "http":
                h = norm_host(r.get("host"))
                http[f"{h or '<ip-literal>'} {r.get('method', '?')}"] += 1
            dst = r.get("dst")
            if r["k"] == "conn" and dst:
                ip, _, port = dst.rpartition(":")
                if port != "443":
                    ports[port] += 1
                if port in ("53", "853"):
                    direct[f"{ip}:{port}" if ip in PUBLIC_RESOLVERS else f"<other>:{port}"] += 1
        top = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_N]
        result.append({
            "label": label,
            "scenario": label.split()[0],
            "minutes": round((b - a) / 60, 1),
            "end_inferred": inferred,
            "records": len(win),
            "connections": conns,
            "connections_per_h": round(conns / hrs),
            "unique_endpoints": len(endpoints - {None}),
            "unique_dns_names": len(dnsq),
            "top_hosts": [{"host": h, "count": n} for h, n in top],
            "http_plaintext": [{"host_method": k, "count": n} for k, n in sorted(http.items())],
            "direct_dns": [{"to": k, "count": n} for k, n in sorted(direct.items())],
            "non_443_ports": [{"port": p, "count": n} for p, n in sorted(ports.items(), key=lambda kv: int(kv[0]))],
        })
    emit({"probe": "telemetry/window-summary", "records_total": len(recs), "windows": result, "grade": "P"})


if __name__ == "__main__":
    main()
