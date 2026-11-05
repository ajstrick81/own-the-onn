"""Minimal SELinux CIL resolver for probes: who-can / what-can with attribute expansion on both sides.

Same logic as research/coffey-systemcontrol-authz-2026-11-03/scripts/cilq.py, packaged as a class.
Handles type, typeattribute, typeattributeset (and/or/not/all), allow with inline (class (perms)) or a named
classpermissionset, and 'self'. Ignores neverallow/dontaudit/auditallow.
"""
import re


def _tokenize(s):
    s = re.sub(r";[^\n]*", "", s)
    return re.findall(r'\(|\)|"[^"]*"|[^\s()]+', s)


def _parse(tokens):
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


class Policy:
    def __init__(self, texts):
        self.types, self.attr_exprs, self.cps, self.allows = set(), {}, {}, []
        for text in texts:
            for st in _parse(_tokenize(text)):
                if not isinstance(st, list) or not st:
                    continue
                k = st[0]
                if k == "type":
                    self.types.add(st[1])
                elif k == "typeattributeset":
                    self.attr_exprs.setdefault(st[1], []).append(st[2])
                elif k == "classpermissionset":
                    self.cps.setdefault(st[1], []).append(st[2])
                elif k == "allow":
                    self.allows.append((st[1], st[2], st[3]))
        self._cache = {}

    def all_types(self):
        return {t for t in self.types if t not in self.attr_exprs}

    def expand(self, name, seen=()):
        if name in self._cache:
            return self._cache[name]
        if name in self.types and name not in self.attr_exprs:
            return {name}
        if name in seen:
            return set()
        out = set()
        for e in self.attr_exprs.get(name, []):
            out |= self._eval(e, seen + (name,))
        self._cache[name] = out
        return out

    def _eval(self, e, seen):
        if isinstance(e, str):
            return self.expand(e, seen)
        if e and e[0] == "and":
            return self._eval(e[1], seen) & self._eval(e[2], seen)
        if e and e[0] == "or":
            return self._eval(e[1], seen) | self._eval(e[2], seen)
        if e and e[0] == "not":
            return self.all_types() - self._eval(e[1], seen)
        if e and e[0] == "all":
            return self.all_types()
        out = set()
        for x in e:
            out |= self._eval(x, seen)
        return out

    def _perms(self, cp):
        if isinstance(cp, str):
            res = []
            for v in self.cps.get(cp, []):
                res += self._perms(v)
            return res
        cls, ps = cp[0], cp[1]
        ps = ps if isinstance(ps, list) else [ps]
        flat = []
        for p in ps:
            flat += p if isinstance(p, list) else [p]
        return [(cls, flat)]

    def who_can(self, cls, perm, target):
        """Domains (types in attribute 'domain') allowed cls:perm on target, with the granting rules."""
        domains = self.expand("domain")
        out = {}
        for s, t, cp in self.allows:
            for c, ps in self._perms(cp):
                if c != cls or not (perm in ps or "all" in ps):
                    continue
                if t == "self":
                    srcs = self.expand(s) & {target}
                elif target in self.expand(t):
                    srcs = self.expand(s)
                else:
                    continue
                for d in srcs & domains:
                    out.setdefault(d, set()).add(f"allow {s} {t}")
        return {d: sorted(v) for d, v in sorted(out.items())}

    def what_can(self, src, cls, perm, targets):
        out = {}
        for s, t, cp in self.allows:
            if src not in self.expand(s):
                continue
            for c, ps in self._perms(cp):
                if c != cls or not (perm in ps or "all" in ps):
                    continue
                tt = {src} if t == "self" else self.expand(t)
                for x in targets & tt:
                    out.setdefault(x, set()).add(f"allow {s} {t}")
        return {d: sorted(v) for d, v in sorted(out.items())}
