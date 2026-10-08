#!/usr/bin/env python3
"""Test cases for the KB validator (stdlib unittest; no pytest needed).

Run:
    python kb/tools/test_validate.py            # verbose
    python -m unittest -v kb.tools.test_validate # (from repo root, if preferred)

Each test builds a throwaway record tree in a temp dir and asserts the
validator's error/warning output, so the checks are demonstrable and
reproducible.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate  # noqa: E402


DEVICE = "onn 4K Plus (coffey)"

SOURCE_DEVICE = f"""---
source_id: AML-S0001
title: "device readout"
type: observation
device_model: "{DEVICE}"
credibility: primary
scope: exact-device
---
body
"""

SOURCE_DEVICE_NODM = """---
source_id: AML-S0003
title: "device readout, no model declared"
type: observation
credibility: primary
scope: exact-device
---
body
"""

SOURCE_DEVICE_OTHER = """---
source_id: AML-S0004
title: "a different device"
type: observation
device_model: "Some Other Streamer"
credibility: primary
scope: exact-device
---
body
"""

SOURCE_FAMILY = """---
source_id: AML-S0002
title: "family tree"
type: source-code
credibility: primary
scope: related-family
---
body
"""


def _run(files: dict[str, str]):
    """Write {relpath: text} into a temp tree, validate it, return (errors, warnings)."""
    with tempfile.TemporaryDirectory() as d:
        for rel, text in files.items():
            full = os.path.join(d, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(text)
        rep = validate.Report()
        validate.validate_tree(d, rep)
        return rep.errors, rep.warnings


def _finding(**over):
    f = {
        "finding_id": "AML-F0001",
        "title": "t",
        "component": "c",
        "device_model": "onn 4K Plus (coffey)",
        "soc": "S905X5M",
        "evidence_scope": "exact-device",
        "confidence": "confirmed",
        "source_refs": "[AML-S0001]",
    }
    f.update(over)
    lines = ["---"]
    for k, v in f.items():
        if v is None:
            continue
        lines.append(f"{k}: {v}")
    lines.append("---\nbody\n")
    return "\n".join(lines)


class ValidatorTests(unittest.TestCase):
    def test_good_record_passes(self):
        errs, warns = _run({"s.md": SOURCE_DEVICE, "f.md": _finding()})
        self.assertEqual(errs, [])
        self.assertEqual(warns, [])

    def test_bad_id_format(self):
        errs, _ = _run({"s.md": SOURCE_DEVICE, "f.md": _finding(finding_id="AML-FXXX")})
        self.assertTrue(any("does not match" in e for e in errs))

    def test_bad_vocab_scope(self):
        errs, _ = _run({"s.md": SOURCE_DEVICE, "f.md": _finding(evidence_scope="planet-scale")})
        self.assertTrue(any("not in" in e for e in errs))

    def test_missing_required_field(self):
        errs, _ = _run({"s.md": SOURCE_DEVICE, "f.md": _finding(soc=None)})
        self.assertTrue(any("missing required field 'soc'" in e for e in errs))

    def test_duplicate_id(self):
        errs, _ = _run({"a.md": _finding(), "b.md": _finding()})
        self.assertTrue(any("duplicate id" in e for e in errs))

    def test_dangling_reference(self):
        errs, _ = _run({"f.md": _finding(source_refs="[AML-S9999]")})
        self.assertTrue(any("unknown id 'AML-S9999'" in e for e in errs))

    def test_confirmed_needs_source(self):
        errs, _ = _run({"f.md": _finding(evidence_scope="general", source_refs="[]")})
        self.assertTrue(any("confidence=confirmed but no source" in e for e in errs))

    def test_exact_device_requires_device_model(self):
        errs, _ = _run({"s.md": SOURCE_DEVICE, "f.md": _finding(device_model="")})
        self.assertTrue(any("device_model is empty" in e for e in errs))

    def test_exact_device_requires_device_scoped_source(self):
        # confirmed exact-device finding backed ONLY by a related-family source -> error
        errs, _ = _run({"s.md": SOURCE_FAMILY, "f.md": _finding(source_refs="[AML-S0002]")})
        self.assertTrue(any("not backed by any exact-device source" in e for e in errs))

    def test_exact_device_inferred_only_warns(self):
        # same mismatch but inferred confidence -> warning, not error
        errs, warns = _run({"s.md": SOURCE_FAMILY,
                            "f.md": _finding(confidence="inferred", source_refs="[AML-S0002]")})
        self.assertFalse(any("not backed by any exact-device source" in e for e in errs))
        self.assertTrue(any("not backed by any exact-device source" in w for w in warns))

    def test_confirmed_non_device_scope_warns(self):
        errs, warns = _run({"s.md": SOURCE_FAMILY,
                            "f.md": _finding(evidence_scope="related-family", source_refs="[AML-S0002]")})
        self.assertTrue(any("non-device scope" in w for w in warns))

    def test_device_model_mismatch_errors(self):
        # exact-device finding backed only by a source for a DIFFERENT device
        errs, _ = _run({"s.md": SOURCE_DEVICE_OTHER, "f.md": _finding(source_refs="[AML-S0004]")})
        self.assertTrue(any("different device_model" in e for e in errs))

    def test_multiple_sources_one_device_matches_passes(self):
        # cites a family source AND the matching device source -> clean
        errs, warns = _run({
            "s1.md": SOURCE_FAMILY,
            "s2.md": SOURCE_DEVICE,
            "f.md": _finding(source_refs="[AML-S0002, AML-S0001]"),
        })
        self.assertEqual(errs, [])
        self.assertEqual(warns, [])

    def test_multiple_sources_only_other_device_errors(self):
        # cites a family source AND an exact-device source for the WRONG device
        errs, _ = _run({
            "s1.md": SOURCE_FAMILY,
            "s2.md": SOURCE_DEVICE_OTHER,
            "f.md": _finding(source_refs="[AML-S0002, AML-S0004]"),
        })
        self.assertTrue(any("different device_model" in e for e in errs))

    def test_exact_device_source_without_model_warns(self):
        # exact-device source that declares no device_model -> cannot confirm -> warn
        errs, warns = _run({"s.md": SOURCE_DEVICE_NODM, "f.md": _finding(source_refs="[AML-S0003]")})
        self.assertFalse(any("device_model" in e for e in errs))
        self.assertTrue(any("cannot confirm the device identity" in w for w in warns))

    def test_flow_mapping_fails_clearly(self):
        errs, _ = _run({"f.md": "---\nfinding_id: AML-F0001\nmeta: {a: b}\n---\nbody\n"})
        self.assertTrue(any("flow mappings" in e for e in errs))

    def test_duplicate_key_fails_clearly(self):
        errs, _ = _run({"f.md": "---\nfinding_id: AML-F0001\ntitle: a\ntitle: b\n---\nbody\n"})
        self.assertTrue(any("duplicate key" in e for e in errs))

    def test_block_scalar_fails_clearly(self):
        errs, _ = _run({"f.md": "---\nfinding_id: AML-F0001\nnote: |\n  multi\n  line\n---\nbody\n"})
        self.assertTrue(any("block scalars" in e for e in errs))

    def test_malformed_frontmatter(self):
        errs, _ = _run({"bad.md": "no frontmatter here\njust text\n"})
        # a file without an opening '---' is simply not treated as a record;
        # one with an unterminated block is an error.
        errs2, _ = _run({"bad.md": "---\nfinding_id: AML-F0001\nbody without close\n"})
        self.assertTrue(any("not closed" in e for e in errs2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
