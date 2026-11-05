# id: collection/device-baseline
# question: is the owner's unit on the analyzed build, what lock state does the bootloader report, and which Mainline modules are installed?
# class: device
# inputs: adb:file, serial:adb
# emits: json {props: {...}, apex: {module: versionCode}, selinux_mode, systemcontrol_label}
# grade: P (device-reported); read-only getprop / pm / getenforce / ps queries only
# refs: research/coffey-device-checks-2026-11-04/COFFEY-DEVICE-CHECKS.md
# tools: adb (platform-tools)
"""Read-only device probe. Runs only property, package-list, getenforce and process-label queries over adb.

It never writes settings, installs anything, reboots, or calls a service. Run it from the maintainer's own machine.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib.probe import emit, inputs  # noqa: E402

PROPS = ["ro.build.fingerprint", "ro.build.version.security_patch", "ro.vendor.build.security_patch",
         "ro.boot.verifiedbootstate", "ro.boot.flash.locked", "ro.boot.vbmeta.device_state", "ro.build.type",
         "ro.secure", "ro.adb.secure", "ro.debuggable", "ro.boot.slot_suffix", "ro.product.device",
         "ro.oem_unlock_supported", "sys.oem_unlock_allowed"]


def main():
    inp = inputs()
    base = [inp["adb"], "-s", inp["serial"], "shell"]

    def sh(cmd):
        return subprocess.run(base + [cmd], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=60).stdout.replace("\r", "").strip()

    props = {p: sh(f"getprop {p}") for p in PROPS}
    apex = {}
    for line in sh("pm list packages --apex-only --show-versioncode").splitlines():
        parts = dict(x.split(":", 1) for x in line.split() if ":" in x)
        if "package" in parts:
            apex[parts["package"]] = parts.get("versionCode")
    labels = sorted({l.split()[0] for l in sh("ps -A -o LABEL,NAME").splitlines()
                     if l.strip().endswith("systemcontrol") and l.split()})
    emit({
        "probe": "collection/device-baseline",
        "props": props,
        "apex": dict(sorted(apex.items())),
        "selinux_mode": sh("getenforce"),
        "systemcontrol_label": labels,
        "grade": "P",
    })


if __name__ == "__main__":
    main()
