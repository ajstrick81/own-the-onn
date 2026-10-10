---
finding_id: AML-F0022
title: "coffey system_control untrusted-callable surface reaches u-boot env writes (setBootEnv) and unifykeys secure-key writes (writeUnifyKey) — SELinux domain permits both; per-method/driver gates + live policy unverified"
component: security
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: probable
source_refs:
  - AML-S0005
  - AML-S0010
source_urls: []
source_revision: "systemcontrol sha256 aec8998d…c8c1a4 + @1.0/@1.1 interface libs (OTA URO4.260304.011.B1, AML-S0005); method surface from Bn-handler symbols; SELinux write grants via SETools 4.6.0 sesearch on shipped odm precompiled_sepolicy; device-type→path from shipped file_contexts; all re-derived in-house (Codex offline)"
related_findings:
  - AML-F0020
  - AML-F0021
status: reviewed
---

# coffey system_control high-value write surface: bootenv + unifykeys (in-house analysis)

## Observations
1. **Full method surface.** The shipped `@1.0`+`@1.1` interface libraries expose
   **287 unique HIDL methods** (from `BnHwSystemControl…_hidl_<name>` symbols).
   All are on the interface that AML-F0020 shows is untrusted-callable with no
   caller-identity check. Beyond display/PQ getters/setters, the surface includes
   **key/provisioning and firmware** methods: `writeProvisionKey(2)`,
   `writeProvisionKeyWithResult(2)`, `deleteProvisionKey(Ex)`, `checkProvisionKey`,
   `writeUnifyKey`/`readUnifyKey`, `refreshHdcpKey`, `writeHdcpRXImg`,
   `StartUpgradeFBC`/`UpdateFBCUpgradeStatus`, `sysSSMWriteNTypes`, `SSMRecovery`,
   `factorySSMRestore`, `setBootEnv`, `updataLogoBmp`.
2. **Endpoints referenced by the service.** `systemcontrol` strings + NEEDED libs
   show `/dev/block/by-name/env`, `/dev/block/by-name/ubootenv`, `/dev/nand_env`
   (u-boot env), `/dev/unifykeys` + `/sys/class/unifykeys/{write,secure,lock,read}`,
   `/dev/block/by-name/logo`; linked `libprovision.so` (keys) and `libfbc.so`
   (panel/FBC firmware). `Ubootenv.cpp` write logic is present (MEMERASE / write /
   CRC) over `ubootenv.var.*` keys including `bootcmd`, `boot_flag`, `firstboot`.
   `SysWrite::writeUnifyKey` / `writeUnifyKeyfs` present.
3. **SELinux domain permits the writes (candidate policy).** `sesearch` (SETools
   4.6.0) on the shipped ODM `precompiled_sepolicy`:
   - `allow system_control env_device:blk_file { getattr open read write }`
   - `allow system_control unify_device:chr_file { ioctl open read write }`
   - `allow system_control logo_device:blk_file { … write }`,
     `sda_block_device`, `cri_block_device` likewise.
   file_contexts map `/dev/block/by-name/env` + `/dev/nand_env` → `env_device`,
   `/dev/unifykeys` → `unify_device`, `/dev/block/by-name/logo` → `logo_device`.

   **Route correction (do not conflate):** `writeUnifyKey`/`writeUnifyKeyfs` use the
   **`/sys/class/unifykeys/*` sysfs** nodes (verified: only sysfs strings, **no
   `/dev/unifykeys`** in the writer) — label `sysfs_unifykey`, **not** the
   `unify_device` char node. So the `unify_device:blk/chr` grant above is **not**
   the `writeUnifyKey` route and must not be cited as its permission. The
   provisioning writers are a **third, separate** route (libprovision → libteec →
   TEE device). Three distinct lanes: (a) sysfs unifykeys, (b) `/dev/unifykeys`
   consumer(s), (c) TEE provisioning.

5. **setBootEnv writer chain confirmed in-house (direct, no TEE, no caller/lock
   check).** HIDL `_hidl_setBootEnv` handler at 0x77ff4 (symbol confirmed, 304 B)
   → impl 0x2c36c → service wrapper 0x32b10 → update body 0x26140. The body checks
   an init byte, null key/value, and the `ubootenv.var.` namespace, and
   **explicitly special-cases `ubootenv.var.bootcmd`**; serializer limits key ≤127
   / value <4096 (representation, not auth). Save (0x26f40): opens the selected
   path **O_RDWR** (`movs r1,#2`, verified in-house) and writes **two copies** —
   seek 0 then seek 0x10000 (verified: `movs r1/r2,#0` then `cmp r0,#0x10000`) —
   direct userspace I/O; the MTD branch uses `ioctl 0x80204d01/0x40084d02`.
   **No caller-identity or lock-state check** appears in the inspected wrapper or
   writer, and **no TEEC call** is on this path. Device candidates:
   `/dev/nand_env`, `/dev/block/env`, `/dev/block/by-name/{env,ubootenv}`.

4. **Provisioning-key writers are TEE-mediated (secure-world gate present).**
   Re-verified in-house: `libprovision.so` → NEEDED `libteec.so`, imports the full
   `TEEC_*` set (`InitializeContext`/`OpenSession`/`InvokeCommand`/shared-mem) and
   exports `key_provision_{store,query,delete,calc_checksum,checksum,get_dac,get_pfid}`;
   `libteec` opens `/dev/tee%zu` and issues `TEE_IOC_OPEN_SESSION`/`INVOKE`. Per
   Codex O2 traces, the 9 provisioning handlers route to these exports (store
   0x53d38, delete 0x5447c, …). So `writeProvisionKey`/`deleteProvisionKey*` etc.
   **invoke a secure-world Trusted Application** — the TA is the authorization
   boundary for an actual key change (store/delete also touch a factory-partition
   helper, so not TEE-exclusive). `refreshHdcpKey` instead runs `system()` on the
   fixed `/vendor/bin/tee_hdcp` (verified: string + `system@` import). Guard note:
   `deleteProvisionKeyEx` compares key-name length against 0x3f with unsigned-HI
   rejection → lengths **≤63 pass**, >63 fail (a length check, not auth).

6. **TEE route is SELinux-accessible, PUBLIC-login, and the TA is opaque
   (verified in-house).** The 5 provisioning exports all call `TEEC_OpenSession`
   with login class **`TEE_IOCTL_LOGIN_PUBLIC` (r3=0)** — the original Binder
   caller identity is **not** passed to the TA (so the session layer does not
   authenticate the app). The client uses **`/dev/tee0`**, which shipped
   file_contexts label **`drm_device`** (not `tee_device`), and `system_control`
   is granted `drm_device:chr_file {ioctl open read write}` (sesearch, verified) —
   so the TEE device is reachable. All 5 target UUID `e92a43ab-…-613b`; the
   packaged TA `/vendor/lib/teetz/e92a43ab-…-613b.ta` (sha256 `53e3cc55…`, 138528 B)
   begins magic **`HSTO`** (Amlogic wrapped format, not ELF) with ~8 bits/byte
   entropy ⇒ **opaque/undecoded** (high entropy is opacity, *not* demonstrated
   encryption). So key-provisioning security rests **entirely on this opaque TA's
   internal per-command authorization** — the one gate left, a secure-world wall.

7. **Factory-provisioning helpers are normal-world vfat file ops, further gated
   (in-house-verified policy barrier).** `libprovision`'s factory helpers operate
   on `/mnt/vendor/factory` (fstab: `/dev/block/by-name/factory`, **vfat**;
   file_contexts → `vfat`) with ordinary `fopen(wb)`/write/fsync/read-back — **not**
   block-partition writes. Gate structure (Codex traces): `key_provision_delete`
   calls `factory_provision_delete` **only after the TEE command returns zero**
   (success-gated); `key_provision_store`'s error path triggers a
   `remove_same_type_keybox` cleanup. `factory_provision_store` checks keybox
   magic/version≥5/size 0xa5..0x2800/type==0 (representation checks; TA semantics
   undecoded); the systemcontrol wrappers pass the first two store args as **0**
   (optional filename not caller-controlled via these wrappers).
   **Candidate-policy barrier (sesearch, verified in-house):** `system_control`
   has `vfat:file {create getattr open read write}` and `vfat:dir {add_name open
   read search write}` — but **no `vfat:file unlink` and no `vfat:dir remove_name`**
   (explicit queries empty; domain not permissive). So the delete/cleanup path is
   **blocked under the candidate policy**, while keybox create/write is permitted.
   Route permissions (sesearch on compiled candidate policy, hash `535dc363…`,
   re-verified in-house): `sysfs_unifykey:file {open read write}` (the
   `writeUnifyKey` route), `drm_device:chr_file …` (the `/dev/tee0` route),
   `unify_device:chr_file …` (a *separate* `/dev/unifykeys` route); `tee_device`
   (`/dev/otz_client`) returned no allow — but that is not the route used.

## Interpretation
The untrusted-callable, caller-check-free `system_control` surface (AML-F0020)
reaches high-value **writers** and the `system_control` SELinux domain is granted
write to their device types — i.e. the SELinux layer that could have blocked them
is open. But the operations split by how strongly they are *otherwise* gated:
- **Provisioning keys** (`writeProvisionKey*`, `deleteProvisionKey*`): go through
  **libteec → `/dev/tee0` → TA**. The two gates *before* the TA are now shown
  **open**: SELinux permits `system_control` on the tee device (`drm_device`), and
  the session is **public-login** (no caller identity). So the key-change security
  rests **entirely on the opaque TA** (`e92a43ab…`, `HSTO`) — a secure-world wall.
  This neither tempers nor confirms the concern: it *localizes* it precisely to one
  undecoded component. The adjacent **factory** file lane (obs. 7) is further gated:
  create/write is policy-allowed but the delete/cleanup path lacks `vfat`
  `unlink`/`remove_name` in the candidate policy, and the store/delete TEE commands
  must succeed first.
- **u-boot env** (`setBootEnv`): a **confirmed direct** O_RDWR write (obs. 5) to
  the env device at offsets 0 and 0x10000, **no TEE, no caller/lock check**, with
  `bootcmd` explicitly accepted. This is the cleanest direct-write lead. But the
  **writer is only half the chain**: impact depends entirely on the **consumer**
  (BL33), which is unresolved — see below.
- **FBC firmware** (`StartUpgradeFBC` via `libfbc.so`) and **SSM/factory** writers
  are additional surfaces not yet traced.

**The impact gate (consumer side) is INDETERMINATE.** A confirmed env *write* does
not establish boot influence. coffey's BL33 (range [0x1aa000,0x32a260) in
bootloader.img sha256 `389daa99…`, BL33 sha256 `693afa5b…`) is **opaque** — not
decoded — so whether a locked/AVB bootloader imports and honors `bootcmd`/`boot_flag`
from this env, and whether AVB would reject any resulting unverified boot, is
**unknown** from the acquired artifacts. (BL33 is opaque **normal-world bootloader**
code — distinct from the secure-world TA above; both are undecoded but of different
class.) A boot variable affecting selection ≠ acceptance of an unverified payload.
Net: the F0020 ceiling *reaches a confirmed direct env writer*, but its real-world
effect is gated by unresolved BL33/AVB behavior; the key paths are separately
TEE-TA / sysfs-driver / vfat-policy gated. Every high-value lane terminates at an
undecoded component (BL33 bootloader, or the HSTO TA) or a candidate-policy barrier.

## Alternative explanations / open caveats (critical)
This is a **surface + policy-permission** result, **not** a demonstrated
exploit. Unproven, in order of importance:
- **Live policy** is still the *candidate* ODM policy (AML-F0020 P1: eligible,
  not proven selected). If a different policy is live, grants may differ.
- **Writer traced for `setBootEnv`** (obs. 5): no caller/lock check, but the
  **consumer (BL33) is unresolved** — this, not the writer, is the impact gate.
  `writeUnifyKey`/provisioning writers' per-method+TA/driver guards remain only
  partly traced.
- **Route attributions corrected.** `writeUnifyKey` = `/sys/class/unifykeys` sysfs
  (`sysfs_unifykey`), **not** the `unify_device` grant; provisioning = TEE. Do not
  cite the `unify_device` write grant as the `writeUnifyKey` permission.
- **Driver / hardware gates unverified.** unifykeys exposes `secure`/`lock`
  sysfs — keys may be locked/efuse-protected; the TEE TA decision is secure-world;
  a u-boot env write may or may not be honored by a locked/verified-boot
  bootloader. Whether any write produces a useful effect is not established.
- **No runtime, no invocation, no device.** Reachability of dispatch at runtime,
  object init, and actual effect remain unproven.
No key, env value, or firmware was read, written, or extracted.

## Validation needed
Priority now narrowed: since the key paths are TEE-gated, the cleanest lead is
**`setBootEnv`** (direct, non-TEE block write). Static (offline, next): (1)
disasm `setBootEnv` impl for any guard beyond the `ubootenv.var.` prefix + the
exact write primitive (MEMERASE/ioctl vs raw write) — does any `ubootenv.var.*`
write produce a boot-relevant change, and does a **locked/AVB bootloader consume
`bootcmd`/`boot_flag` from this env** (the real impact gate)? (2) Characterize
the TEE TA for `key_provision_store`/`delete` only as far as offline allows
(command IDs, any client-side auth) — the TA decision is secure-world, so expect
a ceiling here. (3) Resolve live policy selection (AML-F0020 P1). Device-gated
(separate Director-approved plan): **none** — any write test is out of scope and
potentially destructive (brick / boot / key loss). Treat as a HIGH-VALUE LEAD,
security-sensitive, Director-gated (cf. AML-D0002); relay coordination-only.
