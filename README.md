# own-the-onn

> **Status: study in progress.** Findings below are from one device and one evening. They will change as the
> remaining scenarios finish. Nothing here is final.

What does an **onn Google TV streamer** (Walmart's house brand) collect and send by itself, meaning the OS and
the preinstalled apps, not the apps you install? This repo is a repeatable, local-only audit, modeled on the
LG smart-TV investigation by Gamers Nexus and Level1Techs (see [Credits](#credits)) (ACR audio fingerprinting,
home-network scanning, heavy phoning-home while "off").

**Ground rules.** Local-first, no decryption of anyone's traffic, no redistribution of vendor code, and no personal
data in this repo. *You own the glass.* That line and the philosophy behind it come from Rory Gallagher's project
(see [Credits](#credits)). This repo's name, **own-the-onn**, is a nod to it.

## Headline answers (onn 4K Plus "coffey", 2026-09)

| Question | Answer so far | Evidence |
|---|---|---|
| ACR / audio or HDMI fingerprinting on the onn? | **No evidence.** No ACR vendor packages; no app can capture the screen or TV input. | [findings](findings/coffey-2026-09.md#acr) |
| Background microphone use? | **No.** Voice is push-to-talk through the remote only; in a privacy-mode profile the Assistant refuses and capture never starts. | [findings](findings/coffey-2026-09.md#e-voice-button-press--5-min-silence) |
| Trackers dodging blocklists? | **Yes, in one app.** Angel TV's Kochava SDK called a rotating fallback domain (`int.dewrain.life`), not `kochava.com`. | [findings](findings/coffey-2026-09.md#rotating-tracker-domains-kochava-in-angel-tv) |
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

- `findings/`: per-device reports
- `method/`: how to reproduce (adb collection + WireGuard passthrough capture)
- `tools/`: scripts
- `recommendations.md`: settings you can change now, DNS rules, host-TV ACR guides
- `diagrams/`: interactive diagrams + JSON sources
- `blocklists/`: optional DNS rules for observed telemetry hosts *(pending)*

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

If we've credited something wrongly or missed someone, please open an issue.
