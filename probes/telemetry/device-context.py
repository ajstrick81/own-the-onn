# id: telemetry/device-context
# question: right after a capture window, what state is the box in, and which apps recently used the microphone?
# class: device
# inputs: adb:file, serial:adb
# emits: json {wakefulness, screen_state, uptime_s, boot_completed, record_audio: [{package, accesses}]}
# grade: P (device-reported); read-only dumpsys / getprop / /proc queries only
# refs: method/README.md scenarios; findings/coffey-2026-09.md "Microphone" (scenario E)
# tools: adb (platform-tools)
"""Read-only. Run immediately after a scenario window (especially E, the voice press). Never changes state."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib.probe import emit, inputs  # noqa: E402


def main():
    inp = inputs()
    base = [inp["adb"], "-s", inp["serial"], "shell"]

    def sh(cmd):
        return subprocess.run(base + [cmd], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=90).stdout.replace("\r", "")

    power = sh("dumpsys power")
    wake = re.search(r"mWakefulness=(\w+)", power)
    disp = re.search(r"Display Power: state=(\w+)", power)
    uptime = sh("cat /proc/uptime").split()
    # RECORD_AUDIO access history per package: keep package names and access lines only
    rec, pkg = {}, None
    for line in sh("dumpsys appops --op RECORD_AUDIO").splitlines():
        m = re.match(r"\s*Package (\S+):", line)
        if m:
            pkg = m.group(1).rstrip(":")
            continue
        if pkg and re.search(r"\b(Access|Reject):", line):
            rec.setdefault(pkg, []).append(line.strip())
    emit({
        "probe": "telemetry/device-context",
        "wakefulness": wake.group(1) if wake else None,
        "display_power": disp.group(1) if disp else None,
        "uptime_s": round(float(uptime[0])) if uptime else None,
        "boot_completed": sh("getprop sys.boot_completed").strip(),
        "record_audio": [{"package": p, "accesses": v} for p, v in sorted(rec.items())],
        "grade": "P",
    })


if __name__ == "__main__":
    main()
