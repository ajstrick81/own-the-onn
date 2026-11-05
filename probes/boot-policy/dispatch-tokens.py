# id: boot-policy/dispatch-tokens
# question: which boot-dispatch tokens appear in the plaintext parts of coffey's bootloader and boot ramdisks?
# class: host
# inputs: bootloader:file, vendor_boot:file, init_boot:file
# emits: json {sources: {name: {files_scanned, hits: {token: [files]}}}, bootconfig, bootloader_hits}
# grade: P for presence/absence in the scanned plaintext; absence in bootloader.img is a bounded negative (its later stages are opaque)
# refs: research/coffey-boot-dispatch-2026-11-04/COFFEY-BOOT-POLICY-MAP.md; research/boot-policy-track.md Phase B
# tools: none (pure Python lz4-legacy + cpio)
"""Read-only string scan. Ramdisks are decompressed in memory; nothing is written to disk."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib import bootimg  # noqa: E402
from lib.probe import emit, inputs, sha256_bytes  # noqa: E402

TOKENS = ["switch_bootmode", "get_rebootmode", "reboot_mode", "bootcmd", "storeboot", "recovery_from_udisk",
          "recovery_from_sdcard", "recovery_from_flash", "aml_autoscript", "autoscr", "usb_burning", "burningcfg",
          "aml_sdc_burn", "imgread", "bootm", "get_avb_mode", "avb_mode", "get_valid_slot", "saveenv", "fw_setenv",
          "fw_printenv", "setbootenv", "ubootenv.var.", "bootloader_message", "upgrade_step", "bootfromnand",
          "factory_update_param", "boot-recovery", "sideload", "ubootenv.var.lock", "flashing unlock",
          "verifiedbootstate", "otacerts"]


def scan(files):
    hits = {}
    for name in sorted(files):
        low = files[name].lower()
        for t in TOKENS:
            if t.lower().encode() in low:
                hits.setdefault(t, []).append(name)
    return hits


def main():
    inp = inputs()
    out = {"probe": "boot-policy/dispatch-tokens", "tokens": TOKENS, "sources": {}}
    bl = open(inp["bootloader"], "rb").read()
    out["sources"]["bootloader.img"] = {"files_scanned": 1, "hits": scan({"bootloader.img": bl})}
    for role in ("vendor_boot", "init_boot"):
        img = bootimg.split(open(inp[role], "rb").read())
        if role == "vendor_boot":
            out["vendor_boot_cmdline"] = img["cmdline"]
            out["vendor_boot_bootconfig"] = sorted(l for l in img["bootconfig"].splitlines() if l.strip())
        for name, typ, raw in img["ramdisks"]:
            files = bootimg.cpio_files(bootimg.decompress(raw))
            out["sources"][f"{role}:{name}"] = {"ramdisk_type": typ, "ramdisk_sha256": sha256_bytes(raw),
                                                "files_scanned": len(files), "hits": scan(files)}
    out["bootloader_hits"] = sum(len(v) for v in out["sources"]["bootloader.img"]["hits"].values())
    out["grade"] = "P"
    out["reading"] = ("bootloader.img plaintext has no dispatch tokens; U-Boot decisions stay U"
                      if out["bootloader_hits"] == 0 else "bootloader.img has plaintext dispatch tokens: inspect")
    emit(out)


if __name__ == "__main__":
    main()
