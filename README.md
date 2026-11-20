# own-the-onn

> **Status: study in progress, nothing final.** An owner's investigation of a streaming box they bought —
> what it does by itself, and how locked-down it really is. Findings are evidence-graded and change as work
> lands. For the current state at a glance, read **[`STATUS.md`](STATUS.md)**.

What does an **onn Google TV streamer** (Walmart's house brand) collect and send by itself — the OS and the
preinstalled apps, not the apps you install? And, separately: **how locked is the device you supposedly own?**
This repo answers both for one unit, the onn 4K Plus Streaming (`coffey`, Amlogic S905X5M), with a repeatable,
local-only method. The telemetry half is modeled on the LG smart-TV investigation by Gamers Nexus and
Level1Techs (see [Credits](#credits)): ACR audio fingerprinting, home-network scanning, phoning home while
"off".

**Scope & ground rules.** This is **owner-authorized research on the maintainer's own hardware**, documented
for the next owner-researcher. It is **not** an attack kit:

- **Documentation, published openly — not an attack kit.** We record CVE *identities and applicability*,
  mechanism details and on-device results, enforcement *boundaries*, and honest dead ends; public third-party
  tools are linked and credited, not vendored. A documented boundary is a valid result;
  "we could not" is written as plainly as "we did."
- **Local-first.** No decryption of anyone's traffic, no network probing of third parties, no redistribution
  of vendor firmware (large blobs stay out of the repo; their hashes don't).
- **No personal data in the repo** (enforced by the privacy checklist below).
- **Evidence-graded.** Every claim carries **P** (inspected primary) / **R** (first-hand report) / **B**
  (inherited baseline) / **H** (hypothesis) / **U** (unresolved); a sibling device's result never becomes a
  `coffey` fact without `coffey`'s own evidence.

*You own the glass.* That line and the philosophy behind it come from Rory Gallagher's project (see
[Credits](#credits)); this repo's name is a nod to it.

## Two studies in one repo

1. **Telemetry audit** — what the box sends by itself. Largely done for `coffey` (headline answers below);
   `findings/`, `method/`, `tools/`.
2. **Root & boot-policy research** — the bootloader "weld", the runtime-root ceiling, and whether `coffey`
   could boot an alternate OS. **Honest state: no root, no bootloader unlock, no alternate-OS boot, and no
   bypass has been achieved or published** — the work maps *what enforces the lock*, now using coffey's own
   captured OTA ([`research/coffey-ota-capture-2026-10-09/`](research/coffey-ota-capture-2026-10-09/)). See
   [`research/`](research/) and the
   [`boot-policy-track.md`](research/boot-policy-track.md) agenda.

The dashboard [`STATUS.md`](STATUS.md) carries the live picture: confirmed findings, the hard walls, ranked
open leads, and bounded dead ends.

## Headline answers — telemetry audit (onn 4K Plus "coffey", 2026-09)

| Question | Answer so far | Evidence |
|---|---|---|
| ACR / audio or HDMI fingerprinting on the onn? | **No evidence.** No ACR vendor packages; no app can capture the screen or TV input. | [findings](findings/coffey-2026-09.md#acr) |
| Background microphone use? | **No.** Every mic use is a ~5 s foreground voice-button press. | [findings](findings/coffey-2026-09.md#microphone) |
| Phones home while idle / asleep? | **Yes, mostly Google plus your installed apps.** About 72 conn/h awake-idle, about 173 conn/h screen-off. The preinstalled Netflix keeps logging while asleep. | [findings](findings/coffey-2026-09.md#traffic) |
| Contacts Walmart / onn / chipset vendor / ACR companies? | **Not observed** so far. | [findings](findings/coffey-2026-09.md#traffic) |
| Leftover factory software? | **Yes.** A factory test tool runs with system privileges; its upload flow is dormant on retail units. | [findings](findings/coffey-2026-09.md#factory-tool) |
| Host-TV ACR? | Depends on your TV. The onn can't see or stop it. | [recommendations](recommendations.md#host-tv) |

### Compared with LG (AdGuard's write-up)

| | LG G3 as a monitor | onn coffey (this study) |
|---|---|---|
| ACR | Yes (Alphonso / LG Ad Solutions) | Not found |
| Idle connections / hour | 107 | ~72 awake-idle · ~173 screen-off |
| Endpoints / hour | 29 | 33 in 20 min awake · 81 in 33 min asleep |
| LAN scanning | 38 devices found | SSDP discovery seen on wake; scope *pending* |
| While "off" | 4,615 requests / 12 h | *rerun pending* (first overnight attempt invalid) |

## Diagrams

Interactive HTML (pan, zoom, guided views, light/dark), built with archify. Sources are in `diagrams/src/`.

- [What the onn talks to](diagrams/onn-traffic-map.html): OS, preinstalled Netflix, installed apps and the factory tool, and where each one sends data
- [Power states vs. network activity](diagrams/power-states.html): screen-off isn't offline
- [Capture method](diagrams/capture-method.html): WireGuard passthrough, see who but never what

## Layout

- [`STATUS.md`](STATUS.md): single status dashboard — confirmed findings, hard walls, ranked leads, dead ends
  (machine-readable mirror in [`progress.json`](progress.json))
- `findings/`: per-device reports
- `method/`: how to reproduce (adb collection + WireGuard passthrough capture)
- `research/`: root & boot-policy study ([`root-study.md`](research/root-study.md),
  [`boot-policy-track.md`](research/boot-policy-track.md), evidence packets) and the
  [search methodology](research/search-methodology.md)
- `tools/`: scripts (incl. `verify_hashes.py`, run in CI to re-verify every `SHA256SUMS`)
- `recommendations.md`: settings you can change now, DNS rules, host-TV ACR guides
- `diagrams/`: interactive diagrams + JSON sources
- `blocklists/`: optional DNS rules for observed telemetry hosts *(pending)*

Agent sessions: start from [`CLAUDE.md`](CLAUDE.md) for orientation and working rules.

## Contributing a device

Run `tools/collect.sh` and the capture method on your onn (4K Plus, 4K Pro, 2026 stick "wayne", …) and open a
findings file. **Strip personal data first** (see `method/README.md#privacy-checklist`).

## Credits

This study exists because of other people's work. Please go to the originals.

- **The LG investigation that inspired this.** Steve Burke (**Gamers Nexus**) and Wendell Wilson (**Level1Techs**), with
  independent researchers **MrBruh** and **uturn**:
  ["216,000,000 Spy TVs: The LG Smart TV Problem"](https://www.youtube.com/watch?v=6IFVTcM28KA) (2026). They documented ACR on
  HDMI inputs, home-network scanning, standby audio and phoning home while "off". Our scenarios and comparison table follow their
  method.
- **The summary we worked from.** Ekaterina Kachalova, **AdGuard DNS**:
  ["LG smart TVs and the surveillance behind the screen"](https://adguard-dns.io/en/blog/lg-smart-tv-spying-privacy.html)
  (Sept 24, 2026), including the AdGuard Home idle-request evidence we compare against.
- **"Own the glass."** **Rory Gallagher**,
  [lg-webos-dashboard / Glasshouse](https://github.com/rorygallagher2024/lg-webos-dashboard): a privacy, debloat and telemetry-blocking
  dashboard for rooted LG webOS TVs. Its idea that ownership should include meaningful control of the device is the posture of this
  repo. We borrowed the phrase (and riffed on it for this repo's name), not the code.
- **Tools:** [mitmproxy](https://mitmproxy.org) (WireGuard mode), [archify](https://github.com/tt-a1i/archify) (diagrams),
  apktool, and Android's own `dumpsys`.

**Root & boot-policy track** builds on others' published work, cited inline in `research/` and its packets:
the Amlogic U-Boot / AVB / ARM Trusted Firmware documentation; the CoreELEC project; the Acheron GhostLock
(CVE-2026-43499) write-up on the sibling onn 4K Pro; the public epoll / futex kernel-CVE records and Android
Security Bulletins; and the firmware-analysis tooling (moria/mithril, payload_dumper, jadx, dtc). These are
referenced as **comparators and primary records**, never reproduced as exploits. We do not publish firmware,
vendor code, or working exploits. (Some supporting research sweeps were run with AI assistants under the
discipline in [`research/search-methodology.md`](research/search-methodology.md); every result is primary-source
pinned and evidence-graded.)

If we've credited something wrongly or missed someone, please open an issue.
