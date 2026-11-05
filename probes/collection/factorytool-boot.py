# id: collection/factorytool-boot
# question: what does the preinstalled factory tool (com.gretzky.hwinfo) do at boot on a retail unit?
# class: host
# inputs: logcat:file
# emits: json {boot_markers, pattern_counts, factorytool_running_prop, process_starts, sample_lines (redacted)}
# grade: P for what the saved boot logcat shows; absence of a line is bounded by what logcat retained
# refs: findings/coffey-2026-09.md "Factory tool" (pending: boot-state log line, scenario F)
# tools: none
"""Reads a logcat saved by the maintainer after a reboot (`adb logcat -d -b all > F_boot_logcat.txt`).

Only lines mentioning the factory tool are kept, and identifiers are redacted (MAC addresses, IPv4/IPv6
addresses, serial-like tokens, emails) before anything is emitted.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib.probe import emit, inputs  # noqa: E402

PATTERNS = {
    "hwinfo_package": r"com\.gretzky\.hwinfo",
    "start_temp_service": r"StartTempService",
    "factorytool_prop": r"sys\.factorytool",
    "factory_tester_apk": r"FactoryTester",
    "otg_device_env": r"otg_device",
    "mes_upload": r"\bMES\b|mesUpload|uploadTest",
    "other_gretzky": r"com\.gretzky\.(?!hwinfo)",
}
BOOT = {"boot_completed": r"sys\.boot_completed|BOOT_COMPLETED|Boot is finished",
        "zygote_start": r"Zygote\s*:\s*begin preload|ZygoteInit"}
REDACT = [
    (re.compile(r"\b[0-9A-Fa-f]{2}([:-])[0-9A-Fa-f]{2}(\1[0-9A-Fa-f]{2}){4}\b"), "<mac>"),
    (re.compile(r"\b\d{1,3}(\.\d{1,3}){3}\b"), "<ipv4>"),
    (re.compile(r"\b[0-9a-f]{1,4}(:[0-9a-f]{0,4}){3,7}\b", re.I), "<ipv6>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<email>"),
    (re.compile(r"\b(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{10,}\b"), "<serial-like>"),
]
SAMPLE = 30


def redact(s):
    for rx, rep in REDACT:
        s = rx.sub(rep, s)
    return s


def main():
    inp = inputs()
    lines = open(inp["logcat"], encoding="utf-8", errors="replace").read().splitlines()
    counts = collections.Counter()
    boot = collections.Counter()
    hits, prop_lines, starts = [], [], []
    for line in lines:
        for k, rx in BOOT.items():
            if re.search(rx, line):
                boot[k] += 1
        matched = [k for k, rx in PATTERNS.items() if re.search(rx, line)]
        for k in matched:
            counts[k] += 1
        if matched:
            hits.append(redact(line.strip()))
            if "factorytool_prop" in matched:
                prop_lines.append(redact(line.strip()))
            if re.search(r"Start proc .*com\.gretzky\.hwinfo|startService.*StartTempService", line):
                starts.append(redact(line.strip()))
    emit({
        "probe": "collection/factorytool-boot",
        "lines_total": len(lines),
        "boot_markers": dict(sorted(boot.items())),
        "pattern_counts": {k: counts.get(k, 0) for k in PATTERNS},
        "factorytool_prop_lines": prop_lines[:10],
        "process_or_service_starts": starts[:15],
        "sample_lines": hits[:SAMPLE],
        "sample_truncated": len(hits) > SAMPLE,
        "grade": "P",
    })


if __name__ == "__main__":
    main()
