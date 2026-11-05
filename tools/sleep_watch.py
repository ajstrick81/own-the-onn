#!/usr/bin/env python3
"""Keep the capture PC awake, and open an "asleep" window in markers.txt when the onn goes to sleep.

usage: python tools/sleep_watch.py <capture-dir> [label] [--exit-on-sleep]

- Polls `dumpsys power` once a minute over adb (read-only). adb path and serial come from
  probes/local-inputs.json ("adb", "serial").
- While running, asks Windows not to sleep (SetThreadExecutionState), so an overnight capture isn't lost to the
  PC sleeping, which is what invalidated the first overnight run. Stop with Ctrl+C in the morning.
- On sleep it closes the open window and opens `<label>` (default "Z2-asleep-overnight"). It keeps holding the
  PC awake afterwards unless --exit-on-sleep is given. Replaces tools/sleep_watch.sh.
"""
import ctypes
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mark  # noqa: E402

ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001


def hold_awake(on):
    if os.name == "nt":
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


def wakefulness(adb, serial):
    r = subprocess.run([adb, "-s", serial, "shell", "dumpsys power"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    for line in r.stdout.splitlines():
        if "mWakefulness=" in line:
            return line.split("=", 1)[1].strip()
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    capdir, label = args[0], (" ".join(args[1:]) or "Z2-asleep-overnight")
    local = json.load(open(os.path.join(ROOT, "probes", "local-inputs.json"), encoding="utf-8"))
    adb, serial = local["adb"], local["serial"]
    path = os.path.join(capdir, "markers.txt")
    hold_awake(True)
    print(f"holding PC awake; polling onn every 60 s (Ctrl+C to stop)")
    try:
        asleep = False
        while True:
            w = wakefulness(adb, serial)
            if w == "Asleep" and not asleep:
                ts = f"{time.time():.3f}"
                lines = mark.close_open(mark.load(path), ts) + [f"{ts} now {label}"]
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write("\n".join(lines) + "\n")
                print(f"onn asleep at {time.strftime('%Y-%m-%d %H:%M:%S')}; opened window '{label}'")
                asleep = True
                if "--exit-on-sleep" in sys.argv:
                    break
            elif w == "Awake" and asleep:
                print(f"onn awake at {time.strftime('%Y-%m-%d %H:%M:%S')} (window left open; close it with mark.py stop)")
                asleep = False
            time.sleep(60)
    except KeyboardInterrupt:
        print("stopped")
    finally:
        hold_awake(False)


if __name__ == "__main__":
    main()
