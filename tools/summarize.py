"""Summarize study.jsonl between scenario markers in markers.txt.

markers.txt lines: <epoch_start> <epoch_end|now> <label>
Usage: python summarize.py [label ...]   (no args = all scenarios)
"""
import collections, json, sys, time

recs = [json.loads(l) for l in open("study.jsonl", encoding="utf-8") if l.strip()]
marks = []
for l in open("markers.txt", encoding="utf-8"):
    p = l.split(None, 2)
    if len(p) == 3:
        marks.append((float(p[0]), time.time() if p[1] == "now" else float(p[1]), p[2].strip()))

want = set(sys.argv[1:])
for a, b, lab in marks:
    if want and lab.split()[0] not in want:
        continue
    win = [r for r in recs if a <= r["t"] <= b]
    hrs = max((b - a) / 3600, 1e-9)
    hosts = collections.Counter()
    for r in win:
        h = r.get("sni") or r.get("q") or r.get("host")
        if r["k"] in ("tls", "http", "dns") and h:
            hosts[(r["k"], h)] += 1
    conns = sum(1 for r in win if r["k"] == "conn")
    uniq = {r.get("sni") or r.get("dst") for r in win if r["k"] in ("tls", "conn")}
    dnsq = {r["q"] for r in win if r["k"] == "dns"}
    print(f"\n=== {lab}  ({(b - a) / 60:.1f} min)  connections={conns} ({conns / hrs:.0f}/h)  "
          f"unique endpoints={len(uniq)}  unique DNS names={len(dnsq)}")
    agg = collections.Counter()
    for (k, h), n in hosts.items():
        agg[h] += n
    for h, n in agg.most_common(60):
        print(f"  {n:5d}  {h}")
