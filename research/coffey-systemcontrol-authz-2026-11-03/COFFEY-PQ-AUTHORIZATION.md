# COFFEY systemcontrol / PQ caller authorization (boot-policy Phase F)

**Date:** 2026-11-03. **Scope:** offline, read-only analysis of coffey's own `systemcontrol` service and the
SELinux policy it ships with (OTA `URO4.260304.011.B1`; artifacts pinned in
[`../coffey-ota-capture-2026-10-09/COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt`](../coffey-ota-capture-2026-10-09/COFFEY-OTA-ARTIFACTS-SHA256SUMS.txt)).
Nothing was invoked on a device; no HIDL method was called. This report records **who the shipped policy lets
reach the service and what the service is permitted to touch**. It contains no transaction codes, call
sequences, handler addresses, or invocation recipe, and none should be added.

> **Disclosure note.** §3 documents that the shipped policy lets ordinary third-party apps reach a root vendor
> service whose interface includes boot-environment, sysfs, key-storage and property writes. That is a
> security-relevant platform finding, not just a coffey curiosity: the same Amlogic `systemcontrol` and policy
> are likely shared by other devices. Consider reporting it (Amlogic / onn / Google's Android partner channel)
> before this repo is public. End-to-end reachability from an app was **not** tested (§6).

## 1. Artifacts

| Artifact | Identity |
|---|---|
| `vendor/bin/systemcontrol` | SHA-256 `aec8998d…c1a4`, 350,020 B, **ELF32 ARM**, stripped (no `.symtab`), GNU build-id `c980ec27b1cd3ab6fa576214e48d46df` |
| `vendor/lib/libsystemcontrolservice.so` | `3899004f…60f1`, build-id `978487bf45ebb7b67644d53b155086d5` |
| `vendor/lib/vendor.amlogic.hardware.systemcontrol@1.0.so` / `@1.1.so` | `e011923e…8da3` / `df156fc0…9095` (HIDL stubs) |
| `vendor/etc/init/systemcontrol.rc` | `d08e5637…ee83` |
| SELinux policy | `system` `plat_sepolicy.cil` + `mapping/34.0.cil`, `system_ext_sepolicy.cil` (+ its `mapping/34.0.cil`), `product_sepolicy.cil`, `vendor_sepolicy.cil`; no `odm` CIL. **These are the policy coffey loads:** `odm/etc/selinux/precompiled_sepolicy`'s three stamps equal the plat (`1037b574…`), system_ext (`84d84a9e…`) and product (`69ccccaf…`) `*_and_mapping.sha256` values |

The `system_ext`, `product` and `odm` EROFS images were unpacked read-only (`fsck.erofs --extract`) for this.

## 2. Service shape (grade **P**)

- **Runs as root.** `service system_control /vendor/bin/systemcontrol` · `user root` · `group system root media audio`,
  started `on early-boot`. SELinux domain `system_control` (via `system_control_exec`).
- **Registered:** HIDL `vendor.amlogic.hardware.systemcontrol@1.0::ISystemControl/default` and `@1.1` (init
  `interface` lines; VINTF `manifest.xml` declares `@1.1::ISystemControl/default`, hwbinder). Also a
  vndbinder service `system_control` (`system_control_service`).
- **Declared surface:** **290** methods in `@1.0`, **306** in `@1.1` (from the HIDL stubs' instrumentation
  strings). Besides picture-quality getters/setters, the interface **declares**: `setBootEnv`/`getBootEnv`,
  `writeSysfs`/`writeSysfsBin`/`readSysfs`, `writeUnifyKey`/`readUnifyKey`, `writeProvisionKey*` /
  `deleteProvisionKey*` / `checkProvisionKey`, `setProperty`, `loopMountUnmount`, `updataLogoBmp`,
  `StartUpgradeFBC`, `writeHdcpRXImg`, `refreshHdcpKey`, `sysSSMWriteNTypes`, `factorySetParamsDefault`,
  `factoryReset*`, `SSMRecovery`, `getPQDatabaseInfo` (spellings as shipped).

## 3. Who can reach it — effective SELinux policy (grade **P**)

Resolved with attribute expansion on both source and target (script: [`scripts/cilq.py`](scripts/cilq.py)).

| Gate | Domains allowed |
|---|---|
| `hwservice_manager find` on `systemcontrol_hwservice` (19) | `untrusted_app`, `untrusted_app_32`, `priv_app`, `platform_app`, `system_app`, `bootanim`, `mediaserver`, `mediacodec`, `droidaudio`, `dtvkitserver`, `tvserver`, `hal_bootctl_default`, `hal_camera_default`, `hal_graphics_composer_default`, `hal_hidlimw`, `hal_oemlock_default`, `hal_power_default`, `hal_tv_tuner_default`, `system_control` |
| `binder call` on `system_control` (21) | the above (minus `system_control`) plus `untrusted_app_29`, `bootvideo`, `hwservicemanager` |
| `service_manager find` on `system_control_service` (vndbinder, 8) | `shell`, `system_app`, `surfaceflinger`, `bluetooth`, `droidaudio`, `dumpstate`, `atrace`, `traceur_app` |

- **Third-party apps:** the `untrusted_app` grants come from explicit rules in **`vendor_sepolicy.cil`**
  (`untrusted_app_34_0` / `untrusted_app_32_34_0` → `systemcontrol_hwservice` find and `system_control`
  binder call). The platform policy supplies the remaining HIDL prerequisites for these domains:
  `/dev/hwbinder` open/ioctl and `binder call` to `hwservicemanager` (via `halclientdomain`). **All SELinux
  gates are open for apps whose domain is `untrusted_app` (current targetSdk) or `untrusted_app_32`
  (targetSdk 32–33).** `untrusted_app_30/27/25` and `isolated_app` have neither grant; `untrusted_app_29` can
  call but not discover.
- **Not reachable by:** `shell`/`adbd` (shell can *find* the vndbinder service but has no `binder call` to
  `system_control`), `system_server`, `isolated_app`.

## 4. In-process caller checks (grade **P** for imports / **H** for "none")

- `systemcontrol` imports **no caller-identity API**: no `android::hardware::IPCThreadState::getCallingUid/
  getCallingPid/getCallingSid`, no libbinder `getCalling*`, no `getpidcon`/`getpeercon`/
  `selinux_check_access`, no `checkPermission`. Its only `IPCThreadState` imports are `self()` and
  `joinThreadPool`.
- The same holds for every vendor library it links (`libpqcontrol`, `libfbc`, `libprovision`,
  `libmeson_display_adapter_remote`, `libvideotunnel`, `libsystemcontrolservice`, the two HIDL stubs,
  `droidvold@1.0`). No caller-related strings (`permission`, `denied`, `uid`) appear in the binary.
- **Reading:** without an imported identity API the service can't tell callers apart, so SELinux (§3) is the
  only gate. That is consistent with the donor source's stubbed `permissionCheck` (PQ-02), now as a coffey
  observation. Kept at **H** because an identity check could in principle be done some other way; none is
  evident.
- **Boot-env key filter:** strings `[ubootenv] %s is not a ubootenv variable.` and `ubootenv.var.` show a
  **namespace check** (keys must be under `ubootenv.var.`). No list of protected key names appears in the
  strings. Whether specific keys are refused was not traced (no disassembly done).

## 5. What the service may touch — its own SELinux limits (grade **P**)

| Class | Allowed for `system_control` |
|---|---|
| Block-device **write** | `env_device` (`env`, p2), `cri_block_device` (`cri_data`, p14), `logo_device`, `sda_block_device` (USB storage) |
| File **write** | generic `sysfs` and 15 vendor sysfs types (incl. `sysfs_tee`, `sysfs_unifykey`, `sysfs_power`, `sysfs_display`), `param_tv_file` (`/mnt/vendor/param`, `odm_ext`), `mnt_vendor_file`, `cgroup`/`cgroup_v2`, `vfat`, `debugfs_trace_marker` |
| Property **set** | `vendor_persist_prop`, `vendor_platform_prop`, `vendor_tv_prop`, `vendor_media_prop`, `vendor_netflix_prop`, `hwservicemanager_prop`, `logpersistd_logging_prop`, `dumpstate_options_prop`, `ctl_dhcp_pan_prop`, **`ctl_default_prop`** (`ctl.*` start/stop of default-labelled services) |
| Char devices (write) | 24, incl. `unify_device`, `hdmitx_device`, `display_device`, `amvecm_device`, `drm_device` |
| **Denied by policy** | any write to `bootloader`, `boot`, `vbmeta`, `super`, `misc`, `param` (block), `frp`, `factory`, `tee`, `dtbo`, `odm` block devices; **no** `CAP_SYS_ADMIN`, **no** `CAP_DAC_OVERRIDE`, **no** `mount`/`mounton` (so `loopMountUnmount` can't mount under this policy) |

## 6. Phase F acceptance table

Per declared capability class. "Reaches" = the SELinux sink the method's name implies is **permitted**; the
method→sink link is by name and policy, not traced through code (**H**), unless noted.

| Capability (declared methods) | Declared | Registered | Discoverable by apps | Callable by apps (SELinux) | Reaches a sensitive op |
|---|---|---|---|---|---|
| Boot env (`setBootEnv`) | P | P | P | P | **H — `env` block write permitted**; `ubootenv.var.` prefix enforced (P); whether bootloader honors env changes stays U (BL33 opaque, C13) |
| Sysfs (`writeSysfs`, `writeSysfsBin`) | P | P | P | P | **H — generic `sysfs` write permitted, as root** |
| Keys (`writeUnifyKey`, `*ProvisionKey*`, `refreshHdcpKey`, `writeHdcpRXImg`) | P | P | P | P | H — `unify_device`/`sysfs_unifykey`/`sysfs_tee` writes permitted |
| Properties (`setProperty`) | P | P | P | P | H — vendor persist/platform props and `ctl_default_prop` permitted |
| Logo (`updataLogoBmp`) | P | P | P | P | H — `logo` block write permitted |
| PQ persistence (`factorySetParamsDefault`, `factoryReset*`, `save*`, `sysSSMWriteNTypes`, `SSMRecovery`) | P | P | P | P | H — `param_tv_file` writes permitted (PQ DB / SSM). **Do not invoke** (track §6) |
| Mount (`loopMountUnmount`) | P | P | P | P | **P — blocked**: no mount permission in policy |
| `getPQDatabaseInfo` | P | P | P | P | **U** — prerequisites/side effects not traced; not assumed safe |
| Bootloader / boot / vbmeta / super / misc / param partitions | — | — | — | — | **P — no write permission** for `system_control` |

**End-to-end reachability (U).** Every policy gate is open, and no in-process check is evident. But no app was
run and no call was made, so whether an app actually completes a transaction (e.g. HIDL client availability in
an app process) is untested. That test is a device experiment and needs its own proposal under track §6.

## 7. Reconciliations

- **Inherited handler offset `0x80cd8`:** **not from this ELF.** coffey's `systemcontrol` mapped range ends at
  `0x7f9dc` (last `PT_LOAD` vaddr `0x7f4b4` + memsz `0x528`); file size `0x55744`. The offset belongs to some
  other build and should not be reused.
- **`root-study.md` §A** said "a system-context caller can reach that write path". Coffey's policy is wider:
  third-party `untrusted_app` domains are also allowed (§3). The §A conclusion about the weld is unchanged:
  reaching the env writer doesn't establish that a locked production bootloader honors the change.
- **Donor PQ anchors** (`COFFEY-PQ-ANCHORS*.md`): PQ-02's stubbed permission check is now matched at the
  coffey level (no identity imports). Donor addresses and struct layouts remain unused.

## 8. Limits

- No disassembly or control-flow tracing of handlers was done; method→sink links are by name + policy.
- MAC policy only: DAC/file modes on individual sysfs nodes and devices weren't enumerated (the service runs as
  uid 0, so DAC mostly doesn't constrain it).
- `odm_ext`/`oem` contents and runtime property state (e.g. which services are `ctl_default`-labelled) not
  enumerated.
- Policy analysis by a purpose-written CIL resolver ([`scripts/cilq.py`](scripts/cilq.py)), not `secilc`/
  `sesearch`; its output was spot-checked against the raw `vendor_sepolicy.cil` rules quoted in §3.
