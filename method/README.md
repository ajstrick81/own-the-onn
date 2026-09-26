# Method

Everything runs from a PC on the same network over **ADB over Wi-Fi**. No root is needed, and nothing is decrypted.

## 1. Static collection (sections 1–4)

```bash
tools/collect.sh <onn-ip> <output-dir>
```

It collects identity and props, settings, package lists, `dumpsys package / appops / location / wifi / audio /
connectivity / hdmi_control / netstats / jobscheduler / alarm`, boot receivers and the socket table (readable
without root on Android 14). It then extracts sensitive granted permissions (from the `Packages:` section only).

Pull suspicious system APKs with `adb pull` into your output directory, **never into this repo**, and decode them
with apktool/jadx. Search for `AudioRecord`, `MediaProjection`, `TvInputManager`, `getScanResults`,
`getMacAddress`, `discoverServices`, `239.255.255.250`, and hardcoded URLs.

## 2. Network capture: WireGuard passthrough

1. On the PC, run mitmproxy in WireGuard mode with the passthrough logger:
   ```bash
   ONN_SCENARIO=study ONN_CAP_LOG=study.jsonl mitmdump --mode wireguard -s tools/passthrough_logger.py
   ```
   Import the printed client config into the official WireGuard app on the onn and switch it on.
2. The addon marks **every** TLS/QUIC handshake `ignore_connection`, so traffic passes through byte-for-byte. It logs
   only DNS questions, TLS SNI and destinations. Apps behave as if the tunnel weren't there.
3. Record scenario windows in `markers.txt` (`<start_epoch> <end_epoch|now> <label>`).
   `tools/sleep_watch.sh` closes the open window automatically when the onn goes to sleep.
4. Summarize with `python tools/summarize.py [label…]`.

Why WireGuard rather than PCAPdroid: it's already used on the device, nothing extra needs installing, and Android
routes system-UID traffic through it too. Limitation (shared with PCAPdroid): it doesn't see LAN-local traffic such as
mDNS, SSDP or ARP. Capture those from the PC with Wireshark (`mdns || ssdp || arp`, filtered to the onn's IP).

### Scenarios

| | Scenario | Length |
|---|---|---|
| A | Home screen, no input | 60 min (or until sleep) |
| Z | Screen off / asleep | as long as possible (overnight) |
| B | Screensaver | 30 min |
| C | Patched app playing | 15 min |
| D | Stock app playing | 15 min |
| E | Voice button once, then silence | 5 min |
| F | Reboot, capture from boot | 15 min |

## Privacy checklist

Before committing anything, remove Wi-Fi SSIDs and BSSIDs, MAC and Bluetooth addresses, IPv6 prefixes, serials,
Android and advertising IDs, account names, and your full installed-app list. Commit **summaries only**. Keep raw
dumps and captures outside the repo.
