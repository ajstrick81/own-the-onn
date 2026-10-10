---
finding_id: AML-F0024
title: "coffey adla_device (NPU) policy is app-open (DAC 0666 + SELinux untrusted_app chr_file {open ioctl read write}) BUT the ADLA kernel driver AND NN HAL are ABSENT from every shipped partition → surface is DORMANT/latent on this build (/dev/adla0 almost certainly not created). Latent-boilerplate risk, not a live lead. Plus eBPF-lane CLOSED."
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

## ★ DEVICE PRESENCE — DORMANT on coffey (decisive downgrade, 2026-10-10)
The ADLA **kernel driver and NN HAL are ABSENT from every shipped partition**:
- No `adla` symbol in the GKI `vmlinux-5.15.196-coffey-gki` System.map (not built-in).
- No adla/npu `.ko` in **vendor_dlkm** (112 modules, all "hits" false — antenna /
  `nna_pll` / stream_in**pu**t) nor in **system_dlkm**.
- vendor.img (`/vendor`) has NO `/lib/modules` and no adla `.ko`; the ONLY `adla`
  references in vendor are boilerplate: `etc/ueventd.rc` (the 0666 rule),
  `etc/selinux/*` (the type + grant), `etc/init/fs.rc` (`mkdir /data/vendor/nn`),
  and a false string in `libGLES_mali.so`.
- The NN AIDL HAL service binary (`android.hardware.neuralnetworks-service-aidl-driver`,
  `hal_neuralnetworks_adla`) is **not present** in vendor.img.
⇒ With no driver, `/dev/adla0` is **not created**, so there is **nothing for an app
to open**. The SELinux grant + world-writable ueventd rule are **Amlogic reference-
BSP leftovers**, not a live surface on this unit. **This is a LATENT surface, not an
exploitable lead on coffey.** (100% confirmation = one on-device `ls -l /dev/adla0`,
device-read-gated; all offline evidence says absent.)

**Residual value (latent-boilerplate risk):** the policy pre-authorizes untrusted_app
to a world-writable NPU node. If a FUTURE coffey build (or a sibling S7D device that
DOES ship the ADLA driver + HAL) populates `/dev/adla0`, this surface becomes live
with no further policy change — worth re-checking on any build that ships the driver.

## Discipline / what this is NOT
- **Attack-SURFACE (now shown DORMANT), not a proven vulnerability.** No ADLA driver
  is present to audit on coffey; no bug is claimed.
- Candidate-ODM-policy ELIGIBLE caveat applies as for the lane (live selection
  unproven); the DAC 0666 is from the shipped ueventd config (real but moot without
  the node).

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

## Next
Driver-audit path is CLOSED on coffey (no driver shipped). Options: (1) one
device-read `ls -l /dev/adla0` to confirm dormancy on-device (gated); (2) re-check
on any S7D sibling/build that actually ships the ADLA driver+HAL (then the ioctl
audit becomes live). GhostLock stays the primary root path; this lane is parked as
latent. Lesson: policy-level app-reachability (F0020-style enumeration) must be
paired with a device-presence check before treating a surface as live.
