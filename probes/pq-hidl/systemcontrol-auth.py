# id: pq-hidl/systemcontrol-auth
# question: who does coffey's loaded SELinux policy let reach systemcontrol, and does the service check callers itself?
# class: host
# inputs: systemcontrol:file, systemcontrol_rc:file, vendor_lib:dir, plat_cil:file, plat_mapping:file, sysext_cil:file, sysext_mapping:file, product_cil:file, vendor_cil:file, plat_stamp:file, sysext_stamp:file, product_stamp:file, odm_selinux:dir
# emits: json {runs_as, policy_is_loaded, callers: {find_hwservice, binder_call}, untrusted_app_reachable, caller_identity_imports, ubootenv_prefix_check}
# grade: P for policy reachability and imports (when policy_is_loaded); in-process check absence stays H (an identity check could be done some other way)
# refs: research/coffey-systemcontrol-authz-2026-11-03/COFFEY-PQ-AUTHORIZATION.md (C15)
# tools: none (pure Python CIL resolver and ELF reader)
"""Policy- and import-level only: no method is invoked, no transaction codes or call details are produced."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib import elf  # noqa: E402
from lib.cil import Policy  # noqa: E402
from lib.probe import emit, inputs, sha256_bytes  # noqa: E402

IDENTITY = re.compile(r"getCalling(Uid|Pid|Sid)|getpidcon|getpeercon|selinux_check_access|checkPermission|"
                      r"checkCallingPermission")
APP_DOMAINS = ["untrusted_app", "untrusted_app_32", "untrusted_app_30", "untrusted_app_29", "untrusted_app_27",
               "untrusted_app_25", "isolated_app", "priv_app", "platform_app", "system_app", "shell", "adbd",
               "system_server"]


def read(p):
    return open(p, encoding="utf-8", errors="replace").read()


def main():
    inp = inputs()
    rc = read(inp["systemcontrol_rc"])
    user = re.search(r"^\s*user\s+(\S+)", rc, re.M)
    ifaces = re.findall(r"^\s*interface\s+(\S+)\s+(\S+)", rc, re.M)

    stamps = {}
    for role, odm_name in (("plat_stamp", "precompiled_sepolicy.plat_sepolicy_and_mapping.sha256"),
                           ("sysext_stamp", "precompiled_sepolicy.system_ext_sepolicy_and_mapping.sha256"),
                           ("product_stamp", "precompiled_sepolicy.product_sepolicy_and_mapping.sha256")):
        src = read(inp[role]).strip()
        odm = read(os.path.join(inp["odm_selinux"], odm_name)).strip()
        stamps[role] = {"partition": src, "odm_precompiled": odm, "match": src == odm}
    loaded = all(s["match"] for s in stamps.values())

    pol = Policy([read(inp[r]) for r in ("plat_cil", "plat_mapping", "sysext_cil", "sysext_mapping",
                                         "product_cil", "vendor_cil")])
    find = pol.who_can("hwservice_manager", "find", "systemcontrol_hwservice")
    call = pol.who_can("binder", "call", "system_control")
    probe_domains = {d: {"find": d in find, "call": d in call} for d in APP_DOMAINS if d in pol.types}
    untrusted = sorted(d for d, v in probe_domains.items() if d.startswith("untrusted_app") and v["find"] and v["call"])

    sc_bytes = open(inp["systemcontrol"], "rb").read()
    sc = elf.read(sc_bytes)
    binaries = {"systemcontrol": (sc_bytes, sc)}
    for lib in sc["needed"]:
        p = os.path.join(inp["vendor_lib"], lib)
        if os.path.isfile(p):
            b = open(p, "rb").read()
            binaries[lib] = (b, elf.read(b))
    imports = {name: {"sha256": sha256_bytes(b), "caller_identity_imports":
                      sorted(s for s in info["dynsym_undefined"] if IDENTITY.search(s))}
               for name, (b, info) in sorted(binaries.items())}
    any_identity = any(v["caller_identity_imports"] for v in imports.values())

    emit({
        "probe": "pq-hidl/systemcontrol-auth",
        "systemcontrol": {"sha256": sha256_bytes(sc_bytes), "class": sc["class"], "build_id": sc["build_id"]},
        "runs_as": user.group(1) if user else None,
        "registered_interfaces": [f"{a} {b}" for a, b in ifaces],
        "policy_stamps": stamps,
        "policy_is_loaded": loaded,
        "callers": {"find_systemcontrol_hwservice": sorted(find), "binder_call_system_control": sorted(call)},
        "granting_rules_untrusted": {d: {"find": find.get(d), "call": call.get(d)} for d in untrusted},
        "probe_domains": probe_domains,
        "untrusted_app_reachable": untrusted,
        "binaries_checked": len(imports),
        "caller_identity_imports": imports,
        "any_caller_identity_import": any_identity,
        "ubootenv_prefix_check": b"is not a ubootenv variable" in sc_bytes,
        "grade": {"policy_reachability": "P" if loaded else "H", "no_in_process_check": "H" if not any_identity else "n/a"},
    })


if __name__ == "__main__":
    main()
