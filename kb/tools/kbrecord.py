#!/usr/bin/env python3
"""Shared record parser for the Amlogic KB.

Dependency-free. Records are Markdown files with a restricted-YAML
frontmatter block delimited by `---` ... `---`. The parser supports only
the subset the KB templates use:

    key: scalar
    key: "quoted scalar"
    key:                      # empty -> ""
    key: []                   # empty list
    key: [a, b, c]            # inline (flow) list
    key:
      - item one              # block list
      - item two

Top-level keys only (no nested maps). This keeps validation possible on a
stock Python 3 install with no PyYAML. If you need richer structure, add a
field, don't nest.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Record:
    path: str
    fields: dict = field(default_factory=dict)
    body: str = ""

    def get(self, key, default=None):
        return self.fields.get(key, default)


class FrontmatterError(ValueError):
    pass


def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw == "":
        return ""
    if raw == "[]":
        return []
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if inner == "":
            return []
        return [_unquote(p.strip()) for p in inner.split(",") if p.strip() != ""]
    return _unquote(raw)


def _unquote(s: str):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _strip_comment(s: str) -> str:
    """Remove an unquoted trailing '# ...' comment (whitespace-preceded)."""
    in_q = None
    for i, ch in enumerate(s):
        if in_q:
            if ch == in_q:
                in_q = None
        elif ch in "\"'":
            in_q = ch
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i].rstrip()
    return s


def parse_frontmatter(text: str, path: str = "<string>") -> Record:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError(f"{path}: file must start with a '---' frontmatter block")
    # find closing delimiter
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise FrontmatterError(f"{path}: frontmatter block is not closed with '---'")

    fields: dict = {}
    i = 1
    while i < end:
        line = lines[i]
        if line.strip() == "" or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            raise FrontmatterError(f"{path}: line {i+1}: unexpected indentation (keys must be top-level)")
        if ":" not in line:
            raise FrontmatterError(f"{path}: line {i+1}: expected 'key: value'")
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = _strip_comment(rest.strip())
        if key in fields:
            raise FrontmatterError(f"{path}: line {i+1}: duplicate key '{key}' (ambiguous)")
        if rest[:1] == "{":
            raise FrontmatterError(f"{path}: line {i+1}: flow mappings ({{...}}) are not supported; "
                                   "use flat top-level keys")
        if rest in ("|", ">", "|-", "|+", ">-", ">+"):
            raise FrontmatterError(f"{path}: line {i+1}: block scalars ('|','>') are not supported; "
                                   "put the value on one line or move prose to the body")
        if rest[:1] in ("&", "*", "!"):
            raise FrontmatterError(f"{path}: line {i+1}: YAML anchors/aliases/tags are not supported")
        if rest == "":
            # could be an empty scalar or the start of a block list
            block: list = []
            j = i + 1
            while j < end:
                nxt = lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                stripped = nxt.lstrip()
                if nxt[0] in " \t" and stripped.startswith("- "):
                    block.append(_unquote(_strip_comment(stripped[2:].strip())))
                    j += 1
                    continue
                break
            fields[key] = block if block else ""
            i = j
        else:
            fields[key] = _parse_scalar(rest)
            i += 1

    body = "\n".join(lines[end + 1:]).strip()
    return Record(path=path, fields=fields, body=body)


def load(path: str) -> Record:
    with open(path, "r", encoding="utf-8") as fh:
        return parse_frontmatter(fh.read(), path=path)


def iter_record_files(root: str):
    """Yield every .md file under root that opens with a frontmatter block,
    skipping README.md, template files (_*.md), and dotfiles."""
    for dirpath, dirnames, filenames in os.walk(root):
        # prune dotdirs and underscore dirs (e.g. _templates — not real records)
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and not d.startswith("_")]
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            if name == "README.md" or name.startswith("_"):
                continue
            full = os.path.join(dirpath, name)
            try:
                with open(full, "r", encoding="utf-8") as fh:
                    first = fh.readline()
            except OSError:
                continue
            if first.strip() == "---":
                yield full
