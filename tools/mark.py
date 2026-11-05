#!/usr/bin/env python3
"""Open and close scenario windows in a capture directory's markers.txt (method/README.md §2).

usage: python tools/mark.py <capture-dir> start <label ...>   close any open window, open a new one now
       python tools/mark.py <capture-dir> stop                close the open window now
       python tools/mark.py <capture-dir> show

markers.txt lines: <start_epoch> <end_epoch|now> <label>
"""
import os
import sys
import time


def load(path):
    return open(path, encoding="utf-8").read().splitlines() if os.path.exists(path) else []


def close_open(lines, ts):
    return [l.replace(" now ", f" {ts} ", 1) if l.split(None, 2)[1:2] == ["now"] else l for l in lines]


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    path = os.path.join(sys.argv[1], "markers.txt")
    cmd, ts = sys.argv[2], f"{time.time():.3f}"
    lines = load(path)
    if cmd == "start":
        label = " ".join(sys.argv[3:]).strip()
        if not label:
            raise SystemExit("start needs a label, e.g. E-voice weather-question")
        lines = close_open(lines, ts) + [f"{ts} now {label}"]
    elif cmd == "stop":
        lines = close_open(lines, ts)
    elif cmd != "show":
        raise SystemExit(__doc__)
    if cmd != "show":
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines[-6:]))


if __name__ == "__main__":
    main()
