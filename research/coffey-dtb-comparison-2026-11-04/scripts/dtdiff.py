"""Semantic device-tree diff over `dtc -s -I dtb -O dts` output.

Trees built separately number their phandles differently. `summary` compares properties pairwise: two cells
match if they are equal, or if each is a phandle in its own tree and both point to the same node path. Only
properties that still differ after that are reported. (`axes` uses a looser display-only rewrite.)

usage: python3 dtdiff.py summary <a.dts> <b.dts>        node/property differences
       python3 dtdiff.py axes <name=x.dts> [...]         Phase-D axis table as JSON
"""
import json
import re
import sys

PH_PROPS = re.compile(r"^(clocks|resets|interrupt-parent|power-domains|phys|memory-region|pinctrl-\d+|"
                      r"iommus|dmas|mboxes|nvmem-cells|thermal-sensors|cooling-device|operating-points-v2|"
                      r"cpu-idle-states|next-level-cache|.*-supply|.*-gpios?|gpio-ranges|interrupts-extended|"
                      r"remote-endpoint|sound-dai|.*-handle|ports?|regulator|vbus-supply|phy-handle)$")


def parse(path):
    nodes, stack = {}, []
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or line.startswith("/dts-v1/") or line.startswith("/memreserve/"):
            continue
        m = re.match(r"^([^=]*?)\s*\{$", line)
        if m:
            name = m.group(1).split(":")[-1].strip()
            stack.append("" if name == "/" else name)
            nodes.setdefault("/" + "/".join(s for s in stack if s), {})
            continue
        if line == "};":
            stack.pop()
            continue
        m = re.match(r"^([^=;]+?)\s*(?:=\s*(.*))?;$", line)
        if m and stack is not None:
            cur = "/" + "/".join(s for s in stack if s)
            nodes.setdefault(cur, {})[m.group(1).strip()] = (m.group(2) or "").strip()
    return nodes


def resolve(nodes):
    ph = {}
    for p, props in nodes.items():
        v = props.get("phandle")
        if v:
            ph[v.strip("<> ")] = p
    out = {}
    for p, props in nodes.items():
        q = {}
        for k, v in props.items():
            if k in ("phandle", "linux,phandle"):
                continue
            if PH_PROPS.match(k) and v.startswith("<"):
                v = re.sub(r"0x[0-9a-f]+", lambda m: "&" + ph[m.group(0)] if m.group(0) in ph else m.group(0), v)
            q[k] = v
        out[p] = q
    return out


def load(path):
    return resolve(parse(path))


def phmap(nodes):
    return {v.strip("<> "): p for p, props in nodes.items() for k, v in props.items()
            if k in ("phandle", "linux,phandle")}


def cells(v):
    return re.findall(r"0x[0-9a-f]+", v) if v and v.startswith("<") and '"' not in v else None


SPEC = [(re.compile(r"^(clocks|assigned-clocks|assigned-clock-parents)$"), "#clock-cells"),
        (re.compile(r"^resets$"), "#reset-cells"), (re.compile(r"^power-domains$"), "#power-domain-cells"),
        (re.compile(r"^mboxes$"), "#mbox-cells"), (re.compile(r"^pwms$"), "#pwm-cells"),
        (re.compile(r"(^|-|_)gpios?$|-gpios-"), "#gpio-cells"), (re.compile(r"^cooling-device$"), "#cooling-cells"),
        (re.compile(r"^phys$"), "#phy-cells"), (re.compile(r"^dmas$"), "#dma-cells"),
        (re.compile(r"^thermal-sensors$"), "#thermal-sensor-cells"), (re.compile(r"^iommus$"), "#iommu-cells"),
        (re.compile(r"^interrupts-extended$"), "#interrupt-cells"), (re.compile(r"^io-channels$"), "#io-channel-cells"),
        (re.compile(r"^sound-dai$"), "#sound-dai-cells")]


# fixed-stride vendor/legacy layouts: property -> (stride, phandle offset within each tuple)
STRIDE = {"gpio-ranges": (4, 0), "in_links": (2, 1), "out_links": (2, 1)}


def ph_positions(key, cs, ph, nodes):
    """Indexes of cells that are phandles, walking specifiers by the provider's #*-cells; None if unknown.

    For properties with no known layout, an all-phandle value is returned as a 'soft' match (see same())."""
    if key in STRIDE:
        st, off = STRIDE[key]
        return {i for i in range(off, len(cs), st)}
    for rx, cname in SPEC:
        if rx.search(key):
            pos, i = set(), 0
            while i < len(cs):
                c = cs[i]
                if c == "0x00":
                    i += 1
                    continue
                if c not in ph:
                    return None
                pos.add(i)
                n = nodes[ph[c]].get(cname, "<0x00>")
                i += 1 + int(n.strip("<> ") or "0", 16)
            return pos
    return "soft"


def same(k, va, vb, A, B, pa, pb):
    if va == vb:
        return True
    ca, cb = cells(va), cells(vb)
    if ca is None or cb is None or len(ca) != len(cb):
        return False
    xa, xb = ph_positions(k, ca, pa, A), ph_positions(k, cb, pb, B)
    if xa == "soft" or xb == "soft":
        # unknown layout: equal only if every cell is a phandle on both sides and they resolve identically
        return all(x in pa and y in pb and pa[x] == pb[y] for x, y in zip(ca, cb))
    if xa is None or xb is None or xa != xb:
        return False
    return all((pa.get(x) == pb.get(y)) if i in xa else (x == y) for i, (x, y) in enumerate(zip(ca, cb)))


def show(k, v, ph, nodes):
    c = cells(v)
    if c is None:
        return v
    pos = ph_positions(k, c, ph, nodes)
    if not isinstance(pos, set):
        return v
    return "<" + " ".join("&" + ph[x] if i in pos and x in ph else x for i, x in enumerate(c)) + ">"


def summary(a, b):
    A, B = parse(a), parse(b)
    pa, pb = phmap(A), phmap(B)
    only_a, only_b = sorted(set(A) - set(B)), sorted(set(B) - set(A))
    diff = []
    for p in sorted(set(A) & set(B)):
        for k in sorted((set(A[p]) | set(B[p])) - {"phandle", "linux,phandle"}):
            va, vb = A[p].get(k), B[p].get(k)
            if not same(k, va, vb, A, B, pa, pb):
                diff.append((p, k, va and show(k, va, pa, A), vb and show(k, vb, pb, B)))
    return {"nodes_a": len(A), "nodes_b": len(B), "only_a": only_a, "only_b": only_b, "prop_diffs": diff}


def first(nodes, pred):
    return sorted(p for p in nodes if pred(p, nodes[p]))


def axes(name, path):
    N = load(path)
    root = N.get("/", {})
    rm = {p.split("/")[-1]: {k: N[p].get(k) for k in ("reg", "size", "alloc-ranges", "compatible", "no-map", "reusable")
                             if k in N[p]} for p in first(N, lambda p, n: p.startswith("/reserved-memory/"))}
    ser = {p: {k: N[p].get(k) for k in ("compatible", "status", "clock-names", "interrupts")}
           for p in first(N, lambda p, n: re.search(r"/serial@[0-9a-f]+$", p) is not None)}
    mmc = {p: {k: N[p].get(k) for k in ("compatible", "status", "bus-width", "non-removable")}
           for p in first(N, lambda p, n: re.search(r"/(mmc|sd|sdio|emmc)@[0-9a-f]+$", p) is not None)}
    usb = {p: {k: N[p].get(k) for k in ("compatible", "status", "controller-type", "portnum", "dr_mode")}
           for p in first(N, lambda p, n: re.search(r"/(usb\w*|crg\w*|usbphy\w*)@?[0-9a-f]*$", p.split("/")[-1] and p) is not None
                            and re.search(r"(usb|crg)", p.split("/")[-1]) is not None)}
    gpu = {p: {k: N[p].get(k) for k in ("compatible", "status")}
           for p in first(N, lambda p, n: "mali" in n.get("compatible", "") or "gpu" in p.split("/")[-1])}
    eth = {p: {k: N[p].get(k) for k in ("compatible", "status", "phy-mode", "internal_phy")}
           for p in first(N, lambda p, n: re.search(r"/ethernet@[0-9a-f]+$", p) is not None)}
    psci = N.get("/psci", {})
    mem = {p: N[p] for p in first(N, lambda p, n: re.match(r"^/memory(@[0-9a-f]+)?$", p) is not None)}
    chosen = N.get("/chosen", {})
    parts = first(N, lambda p, n: "/partitions" in p and p.count("/") <= 4)
    return {"name": name, "nodes": len(N),
            "root": {k: root.get(k) for k in ("model", "compatible", "amlogic-dt-id", "#address-cells")},
            "memory": mem, "reserved_memory": rm, "psci": psci, "serial": ser, "mmc": mmc, "usb": usb,
            "gpu": gpu, "ethernet": eth, "chosen": chosen, "partition_nodes": parts}


if __name__ == "__main__":
    if sys.argv[1] == "summary":
        r = summary(sys.argv[2], sys.argv[3])
        print(json.dumps({k: (v if k != "prop_diffs" else [list(x) for x in v]) for k, v in r.items()}, indent=1))
    else:
        out = [axes(*a.split("=", 1)) for a in sys.argv[2:]]
        print(json.dumps(out, indent=1))
