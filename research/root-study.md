# Own the Onn — Root & Firmware Research (coffey)

> **Status: research in progress. Blueprint / notebook, not a how-to.**
> This document maps what an owner can learn about their own onn streamer's boot, factory, and kernel
> attack surface. It is **analysis and credits**, not a weaponized recipe. In keeping with this repo's
> ground rules: **local-first, on hardware we own, no redistribution of vendor code or firmware, no
> working exploits, no personal data.** *You own the glass* — this is about understanding the device you
> bought, and standing on the shoulders of the researchers credited at the end.

## Why this exists

The [privacy study](../README.md) answered *what the onn sends*. This track asks the ownership question:
*can the owner gain full control (root) of an onn 4K Plus ("coffey")?* Modern onn hardware ships a
**welded bootloader** (OEM-unlock disabled, AVB locked), so the usual unlock-and-Magisk path — which
worked on earlier onn models (see Credits: amit-raut, whitewolf101, bgondell) — does **not** apply. That
pushes the question toward *software* attack surface, which is where most of the learning happened.

The framing — *an updatable, networked device must expose some privileged, reachable path; find the set
of keys, door by door* — is borrowed from the PS5 "Relapse" research reframe ("indirection is the attack
surface").

## Device, in brief

| | |
|---|---|
| Model | onn 4K Plus ("coffey"), Amlogic **S905X5M** (platform s7d) |
| Kernel | **arm64** GKI `5.15.196-android14-11` (userland is 32-bit only — a 64-bit kernel with 32-bit apps) |
| OS | Android 14, security patch level 2026-03 |
| Bootloader | **welded**: OEM-unlock disabled, flash locked, verified-boot green |

A recurring lesson: **secondary sources lie about details.** Device arch, CVE version ranges, and
"affected" claims all had to be settled against the *primary* source (the kernel config, the source tree,
the researcher's own repo) — never an aggregator summary.

## Attack-surface map (what we looked at, door by door)

### A. Bootloader / OEM-unlock (the "weld")
The OEM-unlock state is an Amlogic **U-Boot environment variable** (`lock`, an 8-field bitfield), read and
written through the vendor **SystemControl** service's `get/setBootEnv`, stored on the `env` partition. A
system-context caller can reach that write path, and the env writer applies **no protected-variable
filter**. *(Update 2026-11-03, from coffey's own policy and binary —
[`coffey-systemcontrol-authz-2026-11-03/`](coffey-systemcontrol-authz-2026-11-03/INDEX.md): the shipped SELinux
policy also lets third-party `untrusted_app` domains reach the service, `shell`/adbd cannot; the writer checks
only the `ubootenv.var.` key prefix; no protected-key list is visible in its strings.)* *However*, Amlogic's production/secure boot either ignores the env unlock bits (non-DEV board
variants) or enforces a **"force locked"** consistency check that halts boot if the lock vars are tampered.
**Conclusion:** the weld is enforced in the signed bootloader, not merely in a software flag — so a naive
env flip is at best a no-op and at worst a soft-brick. Documented, **not attempted on-device.**

### B. Factory test tool (system-privileged)
A preinstalled ODM **factory test app runs with system privileges** and is reachable without special
permission. It contains a classic **Zip-Slip** (archive-extraction path traversal) that survives into
current builds. Its write, though, lands in a confined SELinux domain:

### C. SELinux "second door" analysis
Attribute-expanded policy analysis shows the factory tool's domain can write only a tiny privileged set
(cgroup, a misc data type) with **no executable target any more-privileged process runs** — so the
Zip-Slip file-write is *boxed*: it is system-UID, not root, and cannot cross into code execution by itself.
The one genuine cross-domain reach we confirmed is a **binder bridge into a vendor provisioning HAL**, but
that HAL is itself non-root (no capabilities, no raw block device, no arbitrary exec) — a secure-storage
*tamper* primitive, not a root primitive. **Conclusion:** userland-logic doors are real but walled; root
must come from a memory-safety bug.

### D. Kernel n-day lane (the live path)
The kernel config is hardened against the *easy* public LPE classes:
- **no unprivileged user namespaces** and **no nftables** → the most common 2022–2024 public LPE PoCs don't apply.

But real surface remains: **io_uring, userfaultfd, perf_events** are enabled, and `perf_event_paranoid=-1`
(perf wide open). Cross-referencing the Android Security Bulletins and the Linux CVE trackers against this
exact kernel (built early 2026, missing several bulletins) surfaced two confirmed-applicable epoll bugs:

- **CVE-2026-46242 "Bad Epoll"** — a use-after-free race in epoll's file-release path (see Credits:
  Jaeyoung Chung). Present in this kernel via the GKI backport of the introducing refactor; the fix
  post-dates the device's build. Core subsystem, reachable from an unprivileged app, has a public x86_64
  PoC.
- **CVE-2026-43074** — the companion epoll free-vs-use race in the same code (found by Anthropic's Mythos;
  fixed by Nicholas Carlini / Christian Brauner). Source-verified present-and-unpatched on this build;
  has a public 1-day.

> **Correction (2026-11-03, from the R3 CVE sweep —
> [`boot-policy-packet-round3-cve-2026-11-03/`](boot-policy-packet-round3-cve-2026-11-03/INDEX.md)):** the
> "confirmed-applicable" label above is **downgraded to `H`, pending coffey's own kernel.** Upstream
> version-range analysis puts Bad Epoll's vulnerable interval at `5.15.209`–`<5.15.222` — which the nominal
> base `5.15.196` **predates** — and places CVE-2026-43074 in later-6.x code. On *nominal upstream* grounds
> neither is an automatic match at `5.15.196`; they are real only if coffey's **GKI vendor fork** backported
> the affected code (plausible — GKI trees cherry-pick independently — which is why they stay comparators, not
> closed). Resolve by diffing coffey's extracted kernel history for the epoll functions, not by the version
> string alone.

> **Resolved (2026-11-03, R4 —
> [`coffey-cve-applicability-r4-2026-11-03/`](coffey-cve-applicability-r4-2026-11-03/INDEX.md)): neither epoll
> CVE applies to coffey's shipped kernel (`P`).** coffey runs GKI `ab14657224` = `kernel/common` commit
> `3d26c188ef7e` (branch point of `android14-5.15-2026-01`, 5.15.196). Its `fs/eventpoll.c` lacks the refcount
> refactor that introduced both bugs on 5.15 (stable `f2451def…`, 5.15.209). The `android14-5.15` branch tip
> (5.15.216) has it, which is the likely source of the "present" claim above. Keep watching: a newer coffey
> OTA on a later GKI release would change this.

**Honest blockers.** The public exploits are **x86_64** and built on **libxdk** (Google kernelCTF's
exploitation library), whose post-exploitation primitives (KASLR leak, cross-cache, ROP) are x86-only. The
*trigger* is generic and portable; the *post-exploitation* is from-scratch **arm64** work. The CVE-2026-43074
public exploit's technique additionally relies on `/proc/kmsg`, `/proc/iomem`, and a writable `core_pattern`
— all locked down on the device — so its leak and finish would need replacing. Bad Epoll's `/proc/self/fdinfo`
arbitrary-read is the more Android-viable primitive.

### D-bis. Related external work: GhostLock / CVE-2026-43499 (sibling device)
A public write-up (see Credits: Acheron) documents a per-boot kernel root on the **onn 4K Pro** (board
`jarvis2`), a *sibling* of coffey, not the same device. It is a useful external data point for this study:

- **Bug:** CVE-2026-43499, a use-after-free in the **futex PI requeue** path of the `android14-5.15` GKI
  kernel (a walked waiter references a task that is freed under controlled PI churn). It is a **port of a
  public bug** to a specific build, not a new discovery — the same shape as our "kernel memory-safety bug is
  the live lane" thesis, just a different subsystem than the two epoll CVEs above.
- **Why it matters for coffey (dated 2026-11-03):** coffey runs the **same GKI branch** (`5.15.196-android14-11`)
  and sits at an **older security patch level** (2026-03 vs the Pro's 2026-06). The fix is now dated (see
  [`boot-policy-packet-round2-2026-11-03/COFFEY-R2-1-CVE-TIMELINE.md`](boot-policy-packet-round2-2026-11-03/COFFEY-R2-1-CVE-TIMELINE.md)):
  upstream Linux `3bfdc639…`, Android common cherry-pick `74b647b4` (2026-07-23), **first GKI release tag
  `android14-5.15-2025-07_r5` (released 2026-08-05)**, stable 5.15.212, and **first Android Security Bulletin
  listing in November 2026** (A-496407345). Both coffey (2026-03-01) and the sibling Pro (2026-06-01) **predate
  the first ASB that lists the fix** — so on patch-level grounds coffey is **likely affected (`H` — patch-level
  inference)**, a third candidate n-day alongside the epoll pair. Not a vulnerable-code proof: an OEM could
  backport ahead of the ASB, and SPL does not prove the `vmlinux` contents — confirm against coffey's own
  extracted kernel (`rtmutex.c` control flow / build ID) before calling it affected.
  **Resolved (2026-11-03, R4): affected code present in coffey's kernel (`P`).** coffey's `rtmutex.c` at
  `3d26c188ef7e` is blob `be1042f31…`, exactly the pre-image of the published fix (`74b647b4` / GKI
  `8d140868`): `remove_waiter()` still uses `current` instead of `waiter->task`. This is an applicability
  result only; reachability under coffey's SELinux/seccomp policy and exploitability were not assessed.
- **Why it does not drop in:** the exploit is **build-, offset-, and RAM-specific**. The Pro has a different
  SoC and ~3 GB RAM (vs coffey's S905X5M); the published binary is built for the Pro's kernel hash and would
  need rebuilding from the family sources with new offsets, plus re-derived spray/reclaim geometry for
  coffey. The author notes a **miss panics the kernel**, and repeated panics wedged the Pro's f2fs into a
  factory-reset boot loop — which is exactly why our kernel work stays in the emulator (section Method).
- **Scope confirms ours:** their root is **per-boot only** (verified boot stays green, no persistence, an
  accepted OTA closes it permanently) — the same ceiling section A/Status describes for coffey.
- **coffey-targeted follow-ons (R, 2026-11-19, STATUS C20):** `ShaneBreazeale/OnnDemand-4kplus` claims a
  temporary root + root SSH on one coffey unit on our exact build (`URO4.260304.011.B1/15051976`), retargeted from
  the jarvis2 temp-root work. It does **not** name the bug (so it is not GhostLock evidence), and its tests reused
  an existing root session rather than validating a fresh exploit. Same per-boot ceiling; unlock is out of its
  scope. Our applicability result above stays the stronger evidence (P vs R). Cited only — see
  [`onn-pro-unlock-ingest-2026-11-12/EXTERNAL-COFFEY-TOOLS-2026-11-19.md`](onn-pro-unlock-ingest-2026-11-12/EXTERNAL-COFFEY-TOOLS-2026-11-19.md).

**Runtime root is not a path to a custom ROM.** This is the key ceiling to understand, because it is easy to
assume uid 0 means "flash whatever you want." It does not. Runtime root and bootloader unlock are **two
separate locks**, and GhostLock only defeats one:

- **Runtime root** is control over the *already-running kernel in RAM*, per boot — it sits *downstream* of
  boot, after the system has verified and loaded.
- **Flashing a ROM/kernel/recovery** means writing new partition images that must be *loaded and verified at
  the next boot* — gated *upstream* by the signed Amlogic bootloader and the verified-boot chain, which run
  before any of your code does. Runtime root is on the wrong side of that line.

So even as uid 0, writing a custom image to `boot`/`system`/`vendor` does not boot it: **dm-verity/AVB** hash
those partitions against a hardware-anchored signature at the next boot, and on a **locked** device
(`verifiedbootstate=green`, `flash.locked=1`, no OEM-unlock token) a verification failure is a **brick / boot
loop, not a root** — the write "fails verification at the next boot, which is a brick, not a miss." To flash
anything you would first have to **unlock the bootloader** (flip the OEM-unlock state so it accepts other
images and relaxes verified boot) — which on this device is the welded, bootloader-enforced lock from
**section A**, not a software flag runtime root can flip. GhostLock is a ceiling, not a stepping stone to a
custom ROM. The separate question of whether coffey exposes *any* authenticated maintenance path to an
alternate OS (CoreELEC / custom ROM), and what the weld actually verifies, is tracked in
[`boot-policy-track.md`](boot-policy-track.md) — agenda only, no bypass established.

| Capability | GhostLock runtime root | Needs bootloader unlock |
|---|---|---|
| Read partitions, `kallsyms`, ptrace live procs, full network egress, Alpine chroot | ✅ (per boot) | — |
| Modify files on `/data` | ✅ | — |
| Persist root across reboot | ❌ | ✅ |
| Flash custom ROM / kernel / recovery | ❌ | ✅ |
| Write `boot` / `system` / `vendor` | ❌ (bricks) | ✅ |

We have **not** run any of this against a device. This entry records the CVE identity and applicability for
the next owner-researcher; we do not reproduce or host the exploit.

### D-ter. KernelPatch / APatch (assessed 2026-11-05)
[`bmax121/KernelPatch`](https://github.com/bmax121/KernelPatch), the engine behind APatch, patches and hooks a
stripped arm64 kernel image (code injection, inline and syscall-table hooks, an `su` feature). Its README lists
**static patching of the kernel image** or **runtime dynamic loading**, and requires arm64, Linux 3.18–6.6 and
`CONFIG_KALLSYMS=y`.

- **On paper coffey fits (P):** arm64, GKI 5.15.196, and its embedded config has `CONFIG_KALLSYMS=y` and
  `CONFIG_KALLSYMS_ALL=y`.
- **Static patching needs a modified `boot.img` to boot:** blocked on coffey. The unit reports
  `flash.locked=1` / `green`, `boot` is covered by `vbmeta`, and `fastbootd` refuses flashing while locked
  ([`coffey-boot-dispatch-2026-11-04/`](coffey-boot-dispatch-2026-11-04/INDEX.md),
  [`coffey-device-checks-2026-11-04/`](coffey-device-checks-2026-11-04/INDEX.md)). Same wall as a custom ROM:
  needs the bootloader unlock first.
- **Runtime loading needs kernel write access first:** it's post-exploitation tooling, so it would sit
  *behind* a kernel bug such as GhostLock (C14), and stay per-boot like the rest of this section.
- **Hardening to account for:** coffey has `CONFIG_CFI_CLANG=y` and `CONFIG_ARM64_PTR_AUTH_KERNEL=y`
  (`CONFIG_ARM64_BTI_KERNEL` unset; `CONFIG_MODULE_SIG=y` without `_FORCE`). How KernelPatch handles CFI/PAC
  wasn't checked.

**Verdict:** not a new route. It's what you'd use *after* an unlock or a kernel compromise, not a way to
either. Recorded as a bounded comparator; nothing was downloaded, built or run.

## Method & toolchain (reusable)

- **Firmware pipeline:** [moria](https://github.com/nmatt0/moria) (identify + extract partition images,
  no root) → [mithril](https://github.com/nmatt0/mithril) (SBOM, offline CVE match, secrets, boot-security
  posture). Built and driven in a WSL Ubuntu environment.
- **Firmware-sibling method:** where we couldn't get coffey's own signed images, we analyzed *sibling*
  onn firmware from the same ODM/SoC family to recover un-obfuscated versions of the same system
  components for comparison (same factory tool, identical SELinux model). A newer build is often an
  obfuscated version of an older one — the older one is the Rosetta Stone.
- **Decompile diff:** jadx on the factory APKs, diffing an un-obfuscated older build against the current
  obfuscated one to locate logic.
- **Kernel sandbox:** a matching **arm64 GKI 5.15 kernel built from source** and booted under
  `qemu-system-aarch64`, so bug-reproduction and exploit-development happen **off the real device** (a
  crash is a VM restart). Offsets via `pahole`, gadgets from the built `vmlinux`.
- **OTA capture (read-only):** [OTACaptor](https://github.com/honeybugserial/OTACaptor) logs the OTA
  package URL from logcat; paired with a selective DNS sinkhole (see Credits: bgondell) so the device
  never downloads/applies the update, then [payload_dumper](https://github.com/vm03/payload_dumper)
  extracts the images on a PC.
- **Safety:** the `env`/`misc`/`param` partitions are unreadable without root, so there is **no way to
  back them up first** — which is exactly why the bootloader/env experiments stay documented-but-untried,
  and why kernel work is done in the emulator. Factory reset recovers only `/data`; it does **not** undo
  env or vendor-partition writes.

## Status & honest conclusions

- The **bootloader is genuinely welded** (bootloader-enforced, not a flippable software flag).
- The **userland factory-tool doors are real but SELinux-boxed** (system-UID, not root).
- The **live path to root is a kernel memory-safety bug**. Against coffey's own kernel (R4, 2026-11-03) the
  GhostLock futex-PI bug CVE-2026-43499 is **present** (`P`), as is the lower-impact futex-keying bug
  CVE-2026-99169. The two epoll CVEs are **not** present in this build. Turning them into a working **arm64**
  root on this device is substantial, un-finished exploit-development — and will be done in the emulator
  first. Nothing here has been run against a device to gain root.
- This is a **learning project on owned hardware**, published so the next owner-researcher starts further
  along. We do not publish firmware, vendor code, or working exploits.

---

## Credits

This research stands entirely on other people's work. Please go to the originals and support them.

### Firmware analysis tooling
- **moria** and **mithril** — [@nmatt0](https://github.com/nmatt0/moria) /
  [mithril](https://github.com/nmatt0/mithril). Firmware identification/extraction and
  SBOM/CVE/secrets/boot-posture analysis. The backbone of our firmware pipeline. (MIT)
- **payload_dumper** — [@vm03](https://github.com/vm03/payload_dumper). Android OTA payload extraction.
- **jadx** — [@skylot](https://github.com/skylot/jadx), plus apktool, `pahole`, QEMU, and the Android SDK
  build-tools.

### onn rooting lineage (earlier, unlockable models)
- **amit-raut** — the original
  [Onn 4K Streaming Box rooting + remote-remap](https://github.com/amit-raut/Onn.-4k-Streaming-Box-Rooting-and-Remote-Button-Remapping)
  work that the whole lineage descends from.
- **whitewolf101** — the
  [2023 onn 4K (YOC) fork/adaptation](https://github.com/whitewolf101/Onn.-4k-2023-Streaming-Box-Rooting-and-Remote-Button-Remapping).
- **bgondell** — [onn-update-blocker](https://github.com/bgondell/onn-update-blocker): the forced-update
  blocking method and the vetted OTA-sinkhole domain list, plus a YOC Magisk/`vendor_boot` method.
- **"Functioner"** and the contributors of the XDA onn / SDMC bootloader threads.

### OTA capture
- **OTACaptor** — [@honeybugserial](https://github.com/honeybugserial/OTACaptor). Read-only OTA-URL capture over adb.

### Kernel vulnerability & exploitation research
- **Jaeyoung Chung** ([@J-jaeyoung](https://github.com/J-jaeyoung/bad-epoll)) — discovered and exploited
  **CVE-2026-46242 "Bad Epoll"** (Google kernelCTF 0-day); the writeup and PoC are the core of the kernel
  track here.
- **Anthropic's Mythos** — found the companion epoll race **CVE-2026-43074**.
- **Nicholas Carlini** — reported/authored the CVE-2026-43074 fix.
- **Christian Brauner** — the kernel maintainer who authored/committed the epoll UAF fixes.
- **2045castor** — the public 1-day exploit for CVE-2026-43074.
- **Acheron** ([acheronsec.com](https://acheronsec.com/research/adb-to-root-on-a-locked-android-tv/)) — the
  GhostLock / **CVE-2026-43499** (futex-PI UAF) per-boot root write-up on the sibling onn 4K Pro (`jarvis2`);
  the external reference for section D-bis. (Device/offset-specific; not reproduced here.)
- **ShaneBreazeale** ([OnnDemand-4kplus](https://github.com/ShaneBreazeale/OnnDemand-4kplus)) — the coffey
  temporary-root + root-SSH port cited in D-bis; and **kushmint**
  ([onn-unlock-probe](https://github.com/kushmint/onn-unlock-probe)) — the read-only AVB lock-bit check proposed
  for coffey's §2.1. Both build on OpenEnsemble's 4K Pro work. Cited only.
- **Google kernelCTF / [google/kernel-research](https://github.com/google/kernel-research)** — `libxdk`,
  the exploitation framework the PoCs build on.
- **[@xairy](https://github.com/xairy/linux-kernel-exploitation)** — the linux-kernel-exploitation
  reference collection.
- The **"Bad" lineage** these build on: **Project Zero** (Bad Binder),
  **[@Markakd](https://github.com/Markakd/bad_io_uring)** (Bad io_uring),
  **[@0xkol](https://github.com/0xkol/badspin)** (Bad Spin).

### Amlogic / bootloader reference
- The **Amlogic U-Boot** GPL sources (the `lock`/AVB/oemlock mechanism), and the **oddsolutions**
  Chromecast-with-Google-TV secure-boot write-up as an Amlogic secure-boot reference.

### Vulnerability data
- **[CVEProject/cvelistv5](https://github.com/CVEProject/cvelistv5)**, **linuxcvetracker.com**, the
  **Red Hat CVE database**, the **Android Security Bulletins**, and the feeds **mithril** mirrors
  (OSV.dev, NVD, CISA KEV, FIRST EPSS, kernel.org CNA).

### Posture
- **Rory Gallagher** — *"you own the glass."* The ethos of the whole repo (see the privacy study's Credits).
- The **PS5 "Relapse"** research reframe — *indirection is the attack surface* — the methodology lens.

> If we've credited something wrongly or missed someone, please open an issue — correcting attribution is
> a priority, not an afterthought.
