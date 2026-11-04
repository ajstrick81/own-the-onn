"""Minimal CIL policy resolver: who-can queries with attribute expansion on both sides.

usage: python -I cilq.py <out.json> <cil> [<cil> ...]
Handles: type, typeattribute, typeattributeset (incl. and/or/not/all), allow with inline
(class (perms)) or a named classpermissionset, 'self' targets. Ignores neverallow/dontaudit/auditallow.
"""
import json
import re
import sys


def tokenize(s):
    s = re.sub(r";[^\n]*", "", s)
    return re.findall(r'\(|\)|"[^"]*"|[^\s()]+', s)


def parse(tokens):
    stack, cur = [], []
    for t in tokens:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t)
    return cur


types, attrs, attr_exprs, cps, allows = set(), set(), {}, {}, []
for path in sys.argv[2:]:
    for st in parse(tokenize(open(path, encoding="utf-8", errors="replace").read())):
        if not isinstance(st, list) or not st:
            continue
        k = st[0]
        if k == "type":
            types.add(st[1])
        elif k == "typeattribute":
            attrs.add(st[1])
        elif k == "typeattributeset":
            attr_exprs.setdefault(st[1], []).append(st[2])
        elif k == "classpermissionset":
            cps.setdefault(st[1], []).append(st[2])
        elif k == "allow":
            allows.append((st[1], st[2], st[3], path))

cache = {}


def expand(name, seen=()):
    if name in cache:
        return cache[name]
    if name in types and name not in attr_exprs:
        return {name}
    if name in seen:
        return set()
    out = set()
    for e in attr_exprs.get(name, []):
        out |= eval_expr(e, seen + (name,))
    cache[name] = out
    return out


def eval_expr(e, seen):
    if isinstance(e, str):
        return expand(e, seen)
    if e and e[0] == "and":
        a, b = eval_expr(e[1], seen), eval_expr(e[2], seen)
        return a & b
    if e and e[0] == "or":
        return eval_expr(e[1], seen) | eval_expr(e[2], seen)
    if e and e[0] == "not":
        return all_types() - eval_expr(e[1], seen)
    if e and e[0] == "all":
        return all_types()
    out = set()
    for x in e:
        out |= eval_expr(x, seen)
    return out


def all_types():
    return set(t for t in types if t not in attr_exprs)


def perms_of(cp):
    """cp is either [class, [perms]] or a classpermissionset name."""
    if isinstance(cp, str):
        res = []
        for v in cps.get(cp, []):
            res += perms_of(v)
        return res
    cls, ps = cp[0], cp[1]
    ps = ps if isinstance(ps, list) else [ps]
    flat = []
    for p in ps:
        flat += p if isinstance(p, list) else [p]
    return [(cls, flat)]


def who_can(cls, perm, target):
    srcs = {}
    for s, t, cp, path in allows:
        for c, ps in perms_of(cp):
            if c != cls or not (perm in ps or "all" in ps):
                continue
            if t == "self":
                hit = expand(s) & {target}
            else:
                hit = {target} if target in expand(t) else set()
            if not hit:
                continue
            for d in (expand(s) if t != "self" else hit):
                srcs.setdefault(d, set()).add(f"({s} {t}) [{path.split(chr(92))[-1].split('/')[-1]}]")
    return srcs


def what_can(src, cls, perm, targets):
    out = {}
    for s, t, cp, path in allows:
        if src not in expand(s):
            continue
        for c, ps in perms_of(cp):
            if c != cls or not (perm in ps or "all" in ps):
                continue
            tt = {src} if t == "self" else expand(t)
            for x in targets & tt:
                out.setdefault(x, set()).add(f"({s} {t} {c} {' '.join(ps)})")
    return out


domains = expand("domain")
Q = {
    "find_systemcontrol_hwservice": who_can("hwservice_manager", "find", "systemcontrol_hwservice"),
    "binder_call_system_control": who_can("binder", "call", "system_control"),
    "find_system_control_service": who_can("service_manager", "find", "system_control_service"),
}
blk = {"env_device", "param_block_device", "bootloader_device", "misc_block_device",
       "boot_block_device", "vbmeta_block_device", "super_block_device", "factory_block_device",
       "tee_block_device", "dtbo_block_device", "odm_block_device"}
W = {
    "system_control_blk_write": what_can("system_control", "blk_file", "write", blk),
    "system_control_file_write": what_can("system_control", "file", "write", {"param_tv_file"}),
    "system_control_chr_write": what_can("system_control", "chr_file", "write",
                                         {t for t in all_types() if t.endswith("_device")}),
}
res = {
    "counts": {"types": len(types), "attrs_with_sets": len(attr_exprs), "allow_rules": len(allows),
               "domains": len(domains)},
    "callers": {k: {d: sorted(v) for d, v in sorted(q.items()) if d in domains} for k, q in Q.items()},
    "writes": {k: {d: sorted(v) for d, v in sorted(q.items())} for k, q in W.items()},
}
probe = ["untrusted_app", "untrusted_app_32", "untrusted_app_30", "untrusted_app_29", "untrusted_app_27",
         "untrusted_app_25", "isolated_app", "shell", "adbd", "platform_app", "priv_app", "system_app",
         "system_server"]
res["probe"] = {p: {k: (p in res["callers"][k]) for k in Q} for p in probe if p in types}
json.dump(res, open(sys.argv[1], "w"), indent=1)
print(json.dumps(res["counts"]))
for k in Q:
    print(k, len(res["callers"][k]), sorted(res["callers"][k]))
print("probe", json.dumps(res["probe"]))
for k, v in res["writes"].items():
    print(k, sorted(v))
