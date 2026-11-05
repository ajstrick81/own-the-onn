"""Pre-commit privacy scan: fail if tracked text looks like personal identifiers.

Usage: python tools/privacy_scan.py [extra-literal ...]
Pass your own SSID, device serial and so on as extra literals to check for them too.
"""
import pathlib, re, subprocess, sys

PATTERNS = {
    # exactly six hex pairs: not part of a longer colon-hex chain such as a certificate fingerprint
    "MAC address": r"(?<![0-9A-Fa-f][:-])\b[0-9A-Fa-f]{2}([:-])[0-9A-Fa-f]{2}(\1[0-9A-Fa-f]{2}){4}\b(?![:-][0-9A-Fa-f])",
    "global IPv6": r"\b2[0-9a-f]{3}:[0-9a-f]{1,4}:[0-9a-f]{1,4}:[0-9a-f]{1,4}:",
    "private IPv4": r"\b(192\.168|10\.\d{1,3}|172\.(1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b",
    "SSID/BSSID field": r"\b(B?SSID)[\"']?\s*[:=]\s*\"?[^\s\",<]+",
    "android_id/adid value": r"\b(android_id|advertising_id|adid)\s*[=:]\s*[0-9a-f-]{8,}",
    # domain must start with a letter: skips HIDL versions (foo@1.0.so) and DT node names (fragment@0.dtb)
    "email": r"[\w.+-]+@[A-Za-z][\w-]*\.[A-Za-z][\w.-]*",
}
ALLOW = [r"example\.com", r"noreply@", r"10\.0\.0\.(1|53)\b"]  # documented tunnel addresses

files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                       capture_output=True, text=True).stdout.split()
extra = [re.escape(x) for x in sys.argv[1:]]
bad = 0
for f in files:
    p = pathlib.Path(f)
    if p.suffix.lower() not in {".md", ".txt", ".py", ".sh", ".json", ".csv", ".yml", ".yaml", ".html", ""}:
        continue
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if any(re.search(a, line) for a in ALLOW):
            continue
        for name, pat in list(PATTERNS.items()) + [("literal", x) for x in extra]:
            if re.search(pat, line):
                print(f"{f}:{n}: {name}: {line.strip()[:120]}")
                bad += 1
print("privacy scan:", "CLEAN" if not bad else f"{bad} hit(s)")
sys.exit(1 if bad else 0)
