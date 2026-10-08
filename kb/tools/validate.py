#!/usr/bin/env python3
"""Lightweight validator for the Amlogic KB.

Checks record ID format and uniqueness, required fields, controlled
vocabularies (confidence / evidence_scope / risk_level / result /
credibility), and that cross-references resolve to real records. Pure
stdlib; no PyYAML required.

Usage:
    python kb/tools/validate.py            # validate the whole kb/ tree
    python kb/tools/validate.py <dir>      # validate a subtree

Exit code 0 = clean, 1 = one or more errors. Warnings never fail the run.
"""
from __future__ import annotations

import os
import re
import sys

import kbrecord

ID_PATTERNS = {
    "finding_id": re.compile(r"^AML-F\d{4}$"),
    "experiment_id": re.compile(r"^AML-E\d{4}$"),
    "decision_id": re.compile(r"^AML-D\d{4}$"),
    "source_id": re.compile(r"^AML-S\d{4}$"),
}

CONFIDENCE = {"confirmed", "probable", "inferred", "unknown"}
SCOPE = {"exact-device", "exact-soc", "related-family", "general"}
RISK = {"read-only", "low", "invasive"}
RESULT = {"not-started", "in-progress", "done", "inconclusive"}
CREDIBILITY = {"primary", "secondary", "tertiary"}

# required top-level fields per record kind (keyed by the id field present)
REQUIRED = {
    "finding_id": ["title", "component", "device_model", "soc", "evidence_scope", "confidence"],
    "experiment_id": ["title", "research_question", "hypothesis", "target_device", "risk_level", "result"],
    "decision_id": ["title", "question", "status"],
    "source_id": ["title", "type", "credibility", "scope"],
}

# list-typed fields that hold references to other record IDs
REF_FIELDS = ["source_refs", "related_findings", "supporting_evidence"]


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path, msg):
        self.errors.append(f"ERROR  {_rel(path)}: {msg}")

    def warn(self, path, msg):
        self.warnings.append(f"WARN   {_rel(path)}: {msg}")


def _rel(path):
    try:
        return os.path.relpath(path)
    except ValueError:
        return path


def _kind(rec: kbrecord.Record):
    for id_field in ID_PATTERNS:
        if id_field in rec.fields:
            return id_field
    return None


def _as_list(v):
    if v == "" or v is None:
        return []
    return v if isinstance(v, list) else [v]


def validate_tree(root: str, rep: Report):
    records = []
    for path in kbrecord.iter_record_files(root):
        try:
            records.append(kbrecord.load(path))
        except kbrecord.FrontmatterError as exc:
            rep.error(path, str(exc))

    seen_ids: dict[str, str] = {}
    all_ids: set[str] = set()

    for rec in records:
        id_field = _kind(rec)
        if id_field is None:
            rep.error(rec.path, "no recognized ID field (finding_id/experiment_id/decision_id/source_id)")
            continue

        rec_id = rec.get(id_field, "")
        if not isinstance(rec_id, str) or not rec_id:
            rep.error(rec.path, f"{id_field} is empty")
        else:
            if not ID_PATTERNS[id_field].match(rec_id):
                rep.error(rec.path, f"{id_field}='{rec_id}' does not match {ID_PATTERNS[id_field].pattern}")
            if rec_id in seen_ids:
                rep.error(rec.path, f"duplicate id '{rec_id}' (also in {_rel(seen_ids[rec_id])})")
            else:
                seen_ids[rec_id] = rec.path
                all_ids.add(rec_id)

        for req in REQUIRED.get(id_field, []):
            val = rec.fields.get(req, None)
            if val is None or val == "" or val == []:
                rep.error(rec.path, f"missing required field '{req}'")

        # controlled vocabularies
        _check_vocab(rec, "confidence", CONFIDENCE, rep)
        _check_vocab(rec, "evidence_scope", SCOPE, rep)
        _check_vocab(rec, "scope", SCOPE, rep)
        _check_vocab(rec, "risk_level", RISK, rep)
        _check_vocab(rec, "result", RESULT, rep)
        _check_vocab(rec, "credibility", CREDIBILITY, rep)

        # evidence discipline: a 'confirmed' finding must cite at least one source
        if rec.get("confidence") == "confirmed":
            if not _as_list(rec.get("source_refs")) and not _as_list(rec.get("source_urls")):
                rep.error(rec.path, "confidence=confirmed but no source_refs or source_urls cited")
            if rec.get("evidence_scope") in {"related-family", "general"}:
                rep.warn(rec.path, "confidence=confirmed at a non-device scope — confirm it is confirmed FOR this scope, "
                                   "not upgraded from another device")

    # second pass: cross-reference resolution
    for rec in records:
        for fld in REF_FIELDS:
            for ref in _as_list(rec.fields.get(fld)):
                if ref not in all_ids:
                    rep.error(rec.path, f"{fld} references unknown id '{ref}'")

    return len(records)


def _check_vocab(rec, field_name, allowed, rep):
    if field_name in rec.fields:
        val = rec.fields[field_name]
        if val not in allowed and val != "":
            rep.error(rec.path, f"{field_name}='{val}' not in {sorted(allowed)}")


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
    root = os.path.abspath(root)
    rep = Report()
    n = validate_tree(root, rep)

    for w in rep.warnings:
        print(w)
    for e in rep.errors:
        print(e)

    print(f"\n{n} record(s) checked — {len(rep.errors)} error(s), {len(rep.warnings)} warning(s).")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
