# onn 4K Plus "coffey" — LAN-side scan (captured 2026-11-12, analyzed 2026-11-20)

The LAN-local half of the telemetry audit: what the box puts on the **home network itself** (mDNS, SSDP, ARP),
which the WireGuard passthrough capture can't see. Nothing here leaves the house; it's what any other device on the
same Wi-Fi can observe or ask for. Identifiers are masked (`<cast-uuid>`, `<serial>`, `<bt-mac>`, `<host-hash>`,
`<device name>`); the raw pcap stays off-repo.

| | |
|---|---|
| Build | `URO4.260304.011.B1` / `15051976` (the unit later OTA'd to `16202347` — STATUS C22) |
| Window | 712 s, one window; device state not recorded (believed idle on the home screen) |
| Method | PC-side `dumpcap` on the Wi-Fi adapter, capture filter `arp or (udp and (port 5353 or port 1900))`; at the start the PC sent SSDP M-SEARCH (`ssdp:all`, DIAL `urn:dial-multiscreen-org:service:dial:1`, `MediaRenderer:1`) and mDNS PTR queries (`_googlecast`, `_airplay`, `_http`, `_androidtvremote2`, `_services._dns-sd`) — [`tools/lan_probe.py`](../tools/lan_probe.py) |
| Scope | 1,512 frames from 12 LAN devices; the onn's frames attributed by its MAC (covers its IPv6 and ARP too) |
| Limits | The PC only sees multicast/broadcast and traffic to itself, not the onn's unicast to other LAN hosts; one state, one window |

## Findings (all **P** for this window)

### L1 — No UPnP / SSDP / DIAL at all
The onn sent **0 SSDP frames** — no NOTIFY, no M-SEARCH — and **did not answer** any of the three M-SEARCHes,
including DIAL. It also didn't answer the `_airplay` or `_http` mDNS queries. (The Sept report lists Netflix as
listening on UDP 1900 for DIAL; nothing answered in this window. Whether the Netflix process was running wasn't
recorded, so "Netflix DIAL never answers" is not established.)

### L2 — What it advertises over mDNS
| Service | Port | What's in it |
|---|---|---|
| `_googlecast._tcp` — Cast receiver | 8009 | instance `onn.-4K-Plus-Streami-<cast-uuid>`, host `<cast-uuid>.local`; TXT: `id` (Cast ID), `cd`, `rm`, `bs`, `ct`, `fn=<device name>`, `md=onn. 4K Plus Streaming`, `ve=05`, `ca=268805`, `ic=/setup/icon.png`, `nf=1`, `st=0`, `rs=` (empty) |
| `_androidtvremote2._tcp` — Android TV Remote v2 | 6466 | instance `<device name>`; TXT includes **`bt=<bt-mac>` — the Bluetooth MAC** |
| `_adb._tcp` — ADB over Wi-Fi | 5555 | instance **`adb-<serial>`** (the hardware serial), host `Android.local` — present **only because ADB over Wi-Fi was enabled for this study** |
| Host records | — | `Android_<host-hash>.local`, `Android.local`: A + AAAA, publishing the LAN IPv4, IPv6 link-local, ULA **and global (ISP-prefix) IPv6** addresses |

The Remote and ADB answers here came after our queries; any LAN device can make the same queries.

### L3 — It's chatty because the network asks, not on its own
- 228 mDNS frames in 712 s (~1,150/h): **12 queries, 216 responses**; 113 over IPv4, 115 over IPv6 (link-local source).
- ~97% of the responses answer **other devices**: one LAN device sent **149** `_googlecast` queries in the window,
  two others 42 and 7. The minute with the biggest spike (75 answers) coincides with a 71 + 35 query burst from two
  devices. 213 answers went to the multicast groups, 3 straight to the PC.
- The onn's **own** discovery: **8** `_googlecast._tcp` PTR queries (~40/h — it looks for other Cast devices) and
  4 A queries for **its own** Cast hostname (standard mDNS conflict probing).

### L4 — No LAN scanning
**1 ARP request in 12 minutes** (to a single LAN host); other devices ARP'd for the onn 45 times. No SSDP
M-SEARCH, no mDNS sweep beyond `_googlecast`. Contrast: the LG G3 baseline in the README found 38 devices.

### L5 — Cast status while idle
`st=0` (idle) and `rs=` empty throughout. `rs` is the Cast receiver-status field and is designed to carry the
running app/status during casting; whether it exposes what's playing on coffey is **untested (U)** — needs a
capture during playback.

## What this means for a household

- Every device on your Wi-Fi can learn the box's **Cast ID**, its **name**, its **Bluetooth MAC** (via the TV Remote
  service) and all of its IP addresses, just by asking. That's standard Chromecast / Android TV behaviour, not
  onn-specific telemetry, but the Bluetooth MAC is a stable hardware identifier.
- With **ADB over Wi-Fi on**, it also broadcasts its **hardware serial**. Turn wireless debugging off when not needed.
- It doesn't sweep or fingerprint the LAN (L4) and runs no UPnP/DIAL responder in this state (L1).

## Open
- `rs` during active casting / playback (L5).
- The Sept report's "SSDP right after wake" (DNS window, `coffey-2026-09.md` On wake) — this window had no wake, so
  that SSDP's sender and scope are still open; a LAN capture across a wake would settle it.
- Repeat on the current build (`16202347`).
