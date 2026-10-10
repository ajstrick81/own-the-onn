---
finding_id: AML-F0020
title: "coffey shipped system_control exposes HIDL to untrusted_app and contains no caller-identity enforcement primitive (no getCallingUid/checkPermission); reference permissionCheck() is a disabled stub"
component: security
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0005
  - AML-S0010
source_urls:
  - "https://github.com/khadas/android_vendor_amlogic_common/blob/992853c992d9206c3c0aedbb44415b0777155661/frameworks/services/systemcontrol/SystemControlService.cpp#L126"
  - "https://github.com/khadas/android_vendor_amlogic_common/blob/992853c992d9206c3c0aedbb44415b0777155661/frameworks/services/systemcontrol/SystemControlHal.cpp#L352"
  - "https://github.com/khadas/android_vendor_amlogic_common/blob/992853c992d9206c3c0aedbb44415b0777155661/interfaces/systemcontrol/1.0/ISystemControl.hal"
  - "https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/init/selinux.cpp"
source_revision: "systemcontrol sha256 aec8998d…c8c1a4 (stripped ARM32 PIE) + vendor.amlogic.hardware.systemcontrol@1.0.so sha256 e011923e…18da3 + @1.1.so sha256 df156fc0…c9095 + vendor sepolicy, from OTA URO4.260304.011.B1 (AML-S0005); re-verified in-image with arm-linux-gnueabihf-objdump 2.46: _hidl_readSysfs handler (transport checks + impl dispatch slot +0x78, no uid/perm), SysWrite::readSys open=__open_2(path,O_RDONLY)+__read_chk 4096 cap + no path allowlist; registration/1.1-delegation/surface/compiled-policy from Codex evidence JSONs (same hashes)"
related_findings:
  - AML-F0018
status: reviewed
---

# coffey system_control: untrusted_app reachable + no caller-identity check in shipped binary (Codex lead, re-verified in-image)

## Observations
All reproduced in-image from AML-S0005 artifacts:

1. **Reachability (shipped sepolicy).** `vendor` CIL grants untrusted apps both
   discovery and call:
   - `(allow untrusted_app_34_0 systemcontrol_hwservice (hwservice_manager (find)))`
   - `(allow untrusted_app_34_0 system_control (binder (call)))`
   - same for `untrusted_app_32_34_0` and `untrusted_app_29_34_0`.

2. **No caller-identity primitive in the shipped binary.** `vendor/bin/systemcontrol`
   (sha256 `aec8998d…c8c1a4`, stripped ARM32 PIE, Android 34) imports from
   `libbinder` **only** `IPCThreadState::self()` and
   `IPCThreadState::joinThreadPool(bool)` — both service-startup boilerplate. Its
   dynamic symbol table contains **no** `getCallingUid`, `getCallingPid`,
   `checkPermission`, `checkCallingPermission`, or `PermissionCache`, and **no**
   libc `getuid`/`geteuid`/`getgid`/`getpid`. The binary never obtains any
   uid/pid at the ABI level.

3. **Reference check is disabled.** Khadas `SystemControlService::permissionCheck()`
   (AML-S0010) has its UID/permission body inside a block comment and the active
   function returns `NO_ERROR`; HIDL read/write wrappers forward to the service
   without an independent gate.

4. **A reached read wrapper has no gate.** Codex `systemcontrol-bounded-read-wrapper-evidence.json`
   (same binary hash): the service read routine at 0x326a8 takes a pthread mutex
   and calls `SysWrite::readSysfs(const char*, char*)` at 0x58fd4 with no
   UID/permission decision before the read; the upstream HIDL wrapper at 0x2b6c8
   calls it with a result/string callback.

5. **Named HIDL read dispatch confirmed (interface lib).** The shipped
   `vendor/lib/vendor.amlogic.hardware.systemcontrol@1.0.so` (sha256
   `e011923e…18da3`) exports `BnHwSystemControl::_hidl_readSysfs` at **0x76e8c**,
   size **332 B** (reproduced in-image). Per Codex's annotated handler disasm
   (`hidl-read-dispatch-binary-evidence.json`, same lib hash), `onTransact`
   subtracts 1 from the txn code and uses a halfword jump table at 0x89766;
   **transaction code 18** routes (entry `0x030e` → case 0x89d82, PLT 0xaae30) to
   this handler. The handler calls `Parcel::enforceInterface`, `Parcel::readBuffer`,
   and `readEmbeddedFromParcel` (all three **confirmed imported** in-image),
   branches on their results, then loads the implementation vtable slot **+0x78**
   and `blx`es it — **no caller-UID/permission lookup or path allowlist** before
   the implementation call. The @1.0 lib imports **zero** caller-identity APIs;
   the @1.1 lib (which also carries `readSysfs` Bn/Bp symbols) likewise imports
   **zero**. So no binary in the dispatch chain (interface @1.0, @1.1, executable)
   contains a caller-identity primitive. (The handler body was independently
   re-disassembled in-image with `arm-linux-gnueabihf-objdump` and matches the
   annotation: transport checks → `ldr r7,[r0,#0x78]` → `blx r7`, no uid/perm call.)

6. **Registered implementation = the ungated vtable (static close).** Per Codex
   `systemcontrol-registration-evidence.json`: the executable's constructor at
   0x29ffc stores primary vptr **0x6e068** at object offset 0; slot **+0x78**
   (0x6e0e0) holds Thumb pointer **0x2b6c9** — the exact read wrapper traced in
   obs. 4. The same object is passed at 0x25c30 to the imported
   **`V1_1::ISystemControl::registerAsService`** with inline string `default`.
   (Corrects the earlier note that the executable registers @1.0: the
   reloc-resolved call is the **@1.1** registerAsService; the @1.0 debug string
   does not override it.) Registration *success* / running instance stay runtime
   facts.

7. **@1.1 delegates the inherited op to the @1.0 handler.** The shipped @1.1
   dispatcher handles transaction 18 via jump-table case 0x4d0c8 → PLT 0x685f0
   (0x4d0da), whose ELF relocation resolves to `V1_0::BnHwSystemControl::_hidl_readSysfs`
   — the same handler in obs. 5, not an alternate read impl.

8. **Helper read path re-disassembled in-image.** `SysWrite::readSysfs` (0x58fd4)
   wraps `SysWrite::readSys` (0x5904c) with a 4096-byte stack buffer. In-image
   (`arm-linux-gnueabihf-objdump`), `readSys` opens via **`__open_2(path, r1=0)`
   = O_RDONLY** (flag `movs r1,#0` at 0x5906a) and reads via **`__read_chk`**
   bounded to the 4096 buffer. Its other calls are `property_get`/`atoi`/
   `__strrchr_chk` (path/version parsing), `__android_log_print`, `__errno`/
   `strerror`, `close`. **No `strcmp`/`strncmp`/`strstr`/`access` against the
   caller-supplied path** — no path allowlist on the input.

9. **Surface is not read-only (mutate methods declared).** Codex interface-surface
   inventory: **297 named handlers (281 V1_0 + 16 V1_1)** — name-categorized as
   ~106 query/read, **~136 state-change**, **14 security/provisioning**, 41 other.
   State-changing declarations exist on the same interface; per-method
   implementation guards, argument checks, and subordinate service/kernel perms
   are **unverified**.

10. **Compiled-policy read scope (SETools on shipped policy).** Query of the
    shipped *precompiled* policy confirms `allow untrusted_app system_control:binder
    call` (and _32/_29), `systemcontrol_hwservice find` for untrusted_app/_32, and
    the `system_control` domain holding `param_tv_file` + `oemfs` file open/read +
    dir search (plus broader grants). Confirms the read-disclosure ceiling is the
    `system_control` **domain's** read reach.

## Interpretation
The static mechanism is now confirmed end-to-end in shipped binaries: the
startup code constructs and (via `V1_1::registerAsService("default")`) registers
the implementation whose vtable slot +0x78 is the ungated read wrapper (obs. 6);
both the @1.1 and @1.0 dispatchers route transaction 18 to the same
`_hidl_readSysfs` handler (obs. 5, 7); that handler performs transport
validation only — no caller-identity or path decision — before the impl call;
and the impl's helper opens the **caller-supplied path** `O_RDONLY` with **no
allowlist** and reads it capped at 4096 bytes (obs. 8). No binary in the chain
holds any caller-identity primitive. **This is a confirmed missing app→system
caller-authorization check on the read path.**

Impact ceiling for the read path: disclosure of files the `system_control`
**SELinux domain** can open/read (shipped policy confirms `param_tv_file` +
`oemfs` + broader grants, obs. 10), bounded to ~4096 bytes per call — i.e.
domain-scoped information disclosure, **not** arbitrary-root-file read and
**not** a write/root capability. The interface also declares ~136 state-change
and 14 security/provisioning methods on the same untrusted-callable surface
(obs. 9), so the *potential* exceeds disclosure — but no mutate method has been
shown to actually succeed from an untrusted caller.

## Alternative explanations / open caveats
- **Live policy selection: now shown *eligible*, not *proven*.** The SETools
  grants are from the shipped **candidate** (ODM precompiled) policy. Re-verified
  in-image (policy-selection-artifact-inventory + shipped `system/bin/init` sha256
  `44b3d043…`, 2,044,260 B): `system/etc/selinux/apex` is **absent** and none of
  the 31 system APEX archives is `com.android.sepolicy`; the init binary contains
  the selection strings (`/system/etc/selinux/apex/`, `/dev/selinux/apex_sepolicy.sha256`,
  `/odm/` + `/vendor/etc/selinux/precompiled_sepolicy`, `/metadata/sepolicy`); and
  the `plat_sepolicy_and_mapping` digest matches between system and the ODM
  companion (`1037b574…`). Under the Android-14 reference flow a missing APEX
  policy ZIP → non-APEX baseline → **eligibility for ODM precompiled** — i.e. the
  policy we queried. This is still an **inference about live selection**: init
  control flow, `/metadata/sepolicy/SEPolicy.zip`, live tmpfs labels, DAC mode,
  and boot logs remain unresolved/runtime.
- **Registration success is runtime.** Obs. 6 proves the ungated vtable is the
  instance the startup code *attempts* to register; that it wins and serves is a
  runtime fact.
- **Mutate reach is unproven.** Read-path authorization absence does **not**
  generalize to setters/provisioning (obs. 9): those may have their own guards,
  argument checks, or subordinate service/kernel permissions.
- Handler/helper bodies were re-disassembled in-image; the remaining
  source-correspondence to the Khadas tree stays `related-family`, not
  byte-exact.

## Follow-on static results (P2–P5, re-verified where noted)
- **P2 path semantics (in-image):** `readSys` passes the caller path to
  `__open_2` **unchanged** — no prefix construction, canonicalization, or
  allowlist (`property_get`/`strrchr` run after open, for logging). So an
  absolute caller path reaches the open on the non-null-buffer branch, bounded by
  SELinux/DAC. Disclosure breadth = the domain's read reach, not a sysfs subtree.
- **P3 domain read surface (SETools):** `system_control` has file `open`+`read`
  on **568 distinct types** in the candidate policy (Codex `P3-*`); patterns not
  resolved to live paths; sensitivity triage flags security/identity/persistent
  types for review — none extracted. The concrete benign baseline remains
  `/odm_ext/.../pq.db`.
- **P4 one setter (Codex):** `setBrightness` → impl → `CPQControl::SetBrightness`
  → `VPPDeviceIOCtl` `ioctl`; guards are transport/object/feature/argument
  (rejects ≥101), **no caller-identity check** (consistent with the binary-wide
  absence). One guarded setter does not characterize the other ~135.
- **P5 integrity lead → promoted to [[AML-F0021]]:** `factorySetParamsDefault`
  unlinks + recreates the writable PQ DB; re-verified in-image.

## Validation needed
Static (offline, remaining): the live **policy-selection** outcome is now shown
*eligible* but not *proven* (init control flow / `/metadata/sepolicy` /
tmpfs / boot logs). Device-gated (separate Director-approved read-only plan):
from an ordinary app context, confirm the service is bindable and a bounded read
returns; nothing mutating. Keep this a LEAD — the read-path authorization gap is
confirmed statically, but a real runtime disclosure, any reachable mutation
(see AML-F0021), and root capability are **not** shown. Relay stays
coordination-only; security-sensitive, pending Director review (cf. AML-D0002).
