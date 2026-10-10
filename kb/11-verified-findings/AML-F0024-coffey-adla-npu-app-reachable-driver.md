---
finding_id: AML-F0024
title: "coffey /dev/adla0 (Amlogic ADLA NPU driver) is DIRECTLY reachable from untrusted_app — DAC 0666 + SELinux appdomain/untrusted_app chr_file {open ioctl read write}; an UNWALLED app->kernel-driver surface (unlike F0020). Attack-surface, not a proven vuln. Plus eBPF-lane CLOSED."
component: security-policy
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: probable
source_refs:
  - AML-S0005
source_urls: []
source_revision: "shipped odm precompiled_sepolicy + vendor_file_contexts + ueventd device-perms from OTA URO4.260304.011.B1; sesearch (SETools 4.6.0)"
related_findings:
  - AML-F0020
status: promoted
---

# coffey ADLA NPU app-reachable driver surface (Phase-2, offline/static)

Hunt: a vendor service/driver with the same app-reachability as system_control
(AML-F0020) but a LESS-walled effect. Found one at the driver layer.

## Observation — both access gates are open for untrusted_app
- **DAC:** shipped ueventd device-perms set `/dev/adla0` to mode **0666** (world
  read/write), owner/group `system`.
- **MAC (SELinux):** shipped odm policy grants, via sesearch:
  - `allow appdomain adla_device:chr_file { getattr ioctl open read write }`
  - `allow untrusted_app adla_device:chr_file { getattr ioctl open read write }`
  - `vendor_file_contexts`: `/dev/adla0  u:object_r:adla_device:s0`
- Context: AIDL NN service `hal_neuralnetworks_adla` (exec
  `android.hardware.neuralnetworks-service-aidl-driver`); init makes
  `/data/vendor/nn 0777`. ADLA = Amlogic Deep-Learning Accelerator (on-SoC NPU).

## Interpretation
An unprivileged app can `open("/dev/adla0")` and `ioctl()` the custom Amlogic ADLA
kernel driver **directly** — no HAL intermediary, and the terminal effect is a
kernel driver, **not** gated by a TEE / BL33 / AVB / secondary-policy wall (the
barriers that capped every F0020/F0022 effect). This is a materially LESS-WALLED
app->kernel attack surface. If the ADLA ioctl handler carries any of the common
custom-NPU-driver bug classes (dma-buf/ion import, user-pointer handling, mmap,
weak size/bounds validation on command buffers), it would be a **direct kernel LPE
-> root** with no further wall.

## Discipline / what this is NOT
- **Attack-SURFACE identification, not a proven vulnerability.** No ADLA driver
  ioctl handler has been audited here; no bug is claimed.
- **Device presence on coffey is unconfirmed** — `/dev/adla0` is created only if the
  ADLA block/driver is probed on this unit. S905X5M carries an NPU, so presence is
  likely, but confirm `/dev/adla0` exists when a passive device read is authorized.
- Candidate-ODM-policy ELIGIBLE caveat applies as for the lane (live selection
  unproven); the DAC 0666 is from the shipped ueventd config (strong, build-time).

## Sibling enumeration (P2) — for contrast
untrusted_app `binder:call` reaches: credstore, gpuservice, keystore,
system_control, and HAL servers allocator/cas/codec2/configstore/drm/
graphics_allocator/neuralnetworks(adla+server)/omx. Direct app chr_file ioctl
grants: **adla_device** (this finding) stands out as direct + unwalled; gpu_device/
ion/dma_heap are app-accessible by Android design; CAS (`aml_dsm_device`,
`dvb_device`), DRM (`tee_device`) and media (`ion_device`) paths are HAL-mediated
and TEE/secure-adjacent (more walled).

## Related negative — eBPF lane CLOSED
`/proc/config.gz`: `CONFIG_BPF_SYSCALL=y`, `BPF_JIT_ALWAYS_ON=y`,
`# CONFIG_BPF_UNPRIV_DEFAULT_OFF is not set`. BUT `sesearch -s untrusted_app -c bpf`
returns nothing -> SELinux grants apps no `bpf` class, so `bpf()` is denied to
untrusted_app regardless of the sysctl. Unprivileged-eBPF LPE is CLOSED by SELinux
bpf-class denial (recorded with its gate, like USER_NS / PREEMPT_RT elsewhere).

## Next (offline)
Locate the ADLA kernel driver (module `adla`/`npu` in coffey vendor_dlkm / GKI
modules) and statically audit its ioctl handler(s) for the NPU bug classes above.
A real driver to audit — unlike the walled system_control effects. GhostLock
(separate lane) stays the primary root path; ADLA is a parallel candidate
contingent on a driver bug. CFI/SCS mitigations (AML-M3) apply to any such exploit.
