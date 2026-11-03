# Research & search methodology

> Reusable playbook for the coffey investigation (and future devices). It captures **how** to search so we
> don't gloss over high-value resources, and **which** resource classes to hit for each kind of question.
> Distilled from the boot-policy / root rounds (the PQ v2 sweep, the public-lookup addendum, the Codex task
> blocks). Keep it current as new resource classes prove useful.

This is about *finding and grading evidence*. For device collection + capture mechanics see
[`../method/README.md`](../method/README.md); for the live investigation state see
[`boot-policy-track.md`](boot-policy-track.md) and [`root-study.md`](root-study.md).

## 1. Search discipline (apply to every lookup)

1. **Enumerate the search space explicitly.** Name every repo, branch, tag, forum, database, filing, and query
   string checked — *including the ones that returned nothing*. "I searched" is not evidence; "I checked refs
   X, Y, Z and queries A, B, C" is. The PQ sweep only became trustworthy once it listed *all 1 branch + 67
   tags*, dated.
2. **Pin everything.** Source refs by full Git commit / release tag / filing ID / archived URL + date;
   artifacts by SHA-256. A bare URL without a pin or hash is a lead, not a finding.
3. **Make negatives bounded, not provisional.** Don't stop at "none found." State exactly what was searched so
   "not found" is defensible. Distinguish *"exhausted this enumerated set"* from *"nothing exists anywhere."*
4. **Separate mechanism from inference.** A string/symbol/log match is a lead, not proof of control flow or a
   target fact. A same-SoC / same-vendor / same-brand hit is a **comparator** unless the exact board+build
   matches.
5. **Primary source wins.** Settle every "affected / present / enforced" claim against the primary artifact
   (the config, the source tree, the DTB, the ELF, the filing) — not a blog, a forum post, or a README that
   merely *cites* one. A different URL is not independent confirmation; the same author's blog + forum post can
   be one experiment.
6. **Grade with P/R/B/H/U, and never transfer donor data into a target conclusion.** Donor offsets, keys,
   DTBs, and images stay donor evidence; the target's cells stay `U`/`B` until the target's own artifacts
   exist. (`P` primary inspected · `R` first-hand report, not reproduced · `B` inherited baseline ·
   `H` hypothesis/lead · `U` unresolved.)
7. **Record the next discriminating check** for each finding — the specific artifact or test that would move it
   from `H`/`U` toward `P`.
8. **Identity is fingerprint, not marketing.** Analyze by `ro.build.fingerprint` + build ID + board/codename +
   SoC + active slot + artifact SHA-256. A marketing name ("Box 5" vs "Box 5 MAX"), generation, or purchase
   year is not an identity — model-code and codename conflicts are common (see the darkknight/`MiTV-AZFU0`
   case).

**Per-finding record:** `ID · claim · P/R/B/H/U · target/build · artifact SHA-256 · source ref ·
file+locator · observation · interpretation + competing explanation · next discriminating check.`
Deliver text reports + a SHA-256 list; keep firmware blobs out of git, hash-pinned and re-fetchable.

## 2. Resource catalogue (where to look, by class)

Don't stop at a web search. Sweep the relevant classes below. Entries marked ★ have already paid off here.

### Firmware & vendor source
- ★ **AOSP / Google source** — `android.googlesource.com` (device trees e.g. `device/amlogic/yukawa`,
  `external/u-boot`, `external/avb`, `system/update_engine`, kernel `kernel/arm64`). Pin by branch tag
  (`android12/13/14-release`).
- ★ **Vendor-lineage mirrors** — e.g. `Amlogic-Lineage/*` on GitHub. **Enumerate *all* branches and tags**, not
  the default branch; the useful ref is often an obscure tag.
- ★ **SoC vendor open-source** — Amlogic U-Boot GPL drops, BayLibre vendor packages
  (`public.amlogic.binaries.baylibre.com`), ODM/board vendors (Hardkernel, Khadas, SEI Robotics).
- ★ **CoreELEC / LibreELEC** — `CoreELEC/CoreELEC`, `CoreELEC/common_drivers` (build recipes, device DTs,
  recovery initramfs). Pin the exact release/nightly commit; the current branch ≠ the shipped artifact.
- **OEM OSS compliance publications** — vendors (e.g. Vantiva) publish source/BOM PDFs listing component
  revisions; useful acquisition leads even when the source itself isn't attached.
- **ROM-dump mirrors** — dumpyara-style GitHub dumps carry compiled `system`/`vendor`/`product` partitions and
  service ELFs for build-ID/symbol comparators. Enumerate candidate repos by SoC + codename.

### Primary-source documentation
- ★ **U-Boot docs** (`docs.u-boot.org`, and the `doc/*.rst` source when HTML fails), **AOSP AVB / verified-boot
  design**, **ARM Trusted Firmware** (FIP/boot-stage), kernel.org docs. Settle semantics here, not on forums.

### Community / first-hand reports
- ★ **CoreELEC Discourse**, **4PDA** (Russian — strong Amlogic TV-box coverage), **XDA-Developers**,
  **freaktab**, **Reddit** (r/Onn, r/AndroidTV, r/GoogleTV), **ZNDS / Right.com.cn** (Chinese). Owner teardown
  posts, UART logs, firmware archives. Treat as `R`; search the *exact device/codename* first, then the SoC.
- Search multilingual — Russian/Chinese forums often hold the only owner documentation for a given box.

### Hardware documentation
- **FCC OET database / FCCID.io** — internal photos, board shots, UART/test-point locations, user manuals, and
  occasionally boot logs. The applicant is usually the **ODM**, not the retail brand.
- Teardowns (YouTube, iFixit-style posts) for eMMC package, UART pads, serial-console pinout.

### Vulnerability & security data
- ★ **CVE records** (NVD, `CVEProject/cvelistv5`, kernel.org CNA, linuxcvetracker, Red Hat CVE DB), **Android
  Security Bulletins** (map a fix → first patch level that shipped it), **GKI branch commit/tag history** (find
  the fixing commit and the first release tag containing it), **kernelCTF / linux-kernel-exploitation**
  references. Cross-reference the *exact* kernel build + patch level against the fix date.

### OTA / update mechanics
- Vendor update servers (Xiaomi `*.pandora.xiaomi.com`, `*.tv.global.mi.com`, `mi-img.com`), Google-TV
  `android.googleapis.com/packages/ota-api/...`, onn/Google `SystemUpdateService` + `fes.google.com`. Capture
  the **request params + returned package URL + advertised size/hash**, don't synthesize a URL from a build
  string. `bgondell/onn-update-blocker` lists onn OTA domains.

### Tooling (host-side, read-only)
- **moria/mithril** (identify/extract + SBOM/CVE/boot-posture), **payload_dumper / payload-dumper-go** (OTA
  payload → partition images), **erofs-utils** `dump.erofs`/`fsck.erofs` (read EROFS without mounting),
  **jadx/apktool** (APK/jadx), **dtc** (DTB↔DTS), **pahole** + QEMU (offsets, emulated kernel), **OTACaptor**
  (read-only OTA-URL capture).

## 3. Playbook by question type

| Question | Primary classes to sweep | Bounded-negative looks like |
|---|---|---|
| Is a vulnerability/CVE applicable? | CVE records + Android Security Bulletins + GKI branch history, vs the exact build+patch level | "Fix in commit `<sha>` / release `<tag>` / patch `<YYYY-MM>`; target at `<date>` is before/after" |
| Does a source/implementation exist (e.g. a service, a driver)? | Vendor-lineage mirrors (all branches+tags), AOSP device trees, ROM dumps, OSS compliance PDFs | "All N branches + M tags of repo X (dated), AOSP trees Y, dump set Z — none carries it" |
| What does the boot chain verify? | U-Boot GPL + AVB + TF-A docs, SoC board configs, signer tools, UART logs | Stage/signature/rollback model with per-stage `U` where no primary S-series source states the check |
| Can this board boot an alternate OS? | CoreELEC/LibreELEC repos + Discourse, device DTs, forum boot reports | Barrier matrix (DT-match / boot-entry / acceptance / decode / secure-media), each target cell `U` |
| Hardware access (UART/eMMC/bootloader)? | FCC filings + teardowns | FCC ID pinned + photo'd pads/parts, vs inferred-only |
| How to verify an OTA capture? | Vendor update servers + Google OTA pattern + prior fingerprints | Expected endpoint + fingerprint shape (`H`), + exact on-device fields to record |

## 4. Anti-patterns (seen and corrected here)

- Stopping at "only the obvious branch searched" → always enumerate *all* refs before calling a negative.
- Treating a marketing-name match as device identity → use codename + model-code + fingerprint.
- Reading a config string / compatible string / declared method as proof of a reachable, checked, or enforced
  path → it's a lead until the control flow / policy is traced.
- Conflating layers (Amlogic BL2 anti-rollback vs Android AVB rollback; mount-ro vs partition-writable;
  declared-vs-registered-vs-callable service) → keep them separate columns.
- Promising unbrickability or a bypass to show progress → a documented enforcement boundary is a valid result.
