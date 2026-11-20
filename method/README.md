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
3. Record scenario windows in `markers.txt` (`<start_epoch> <end_epoch|now> <label>`) with
   `python tools/mark.py <capture-dir> start <label>` / `stop`. For overnight runs,
   `python tools/sleep_watch.py <capture-dir>` keeps the PC awake (Windows) and opens the asleep window when the onn
   sleeps; stop it with Ctrl+C. (It replaces `tools/sleep_watch.sh`; adb path and serial come from
   `probes/local-inputs.json`.)
4. Right after a window, run the read-only device probe `python -I tools/run_probe.py telemetry/device-context`
   (wake state, uptime, recent microphone app-ops; needed for E). After an F reboot, save the boot log outside the
   repo (`adb logcat -d -b all > F_boot_logcat.txt`) and run `collection/factorytool-boot logcat=<that file>`.
5. Commit summaries through the probe, not by hand:
   `python -I tools/run_probe.py telemetry/window-summary capture=<study.jsonl> markers=<markers.txt>`.
   It masks per-device hostname tokens and drops IPs. `tools/summarize.py` remains for quick local looks.
   Run `python tools/privacy_scan.py` before every commit.

Why WireGuard rather than PCAPdroid: it's already used on the device, nothing extra needs installing, and Android
routes system-UID traffic through it too. Limitation (shared with PCAPdroid): it doesn't see LAN-local traffic such as
mDNS, SSDP or ARP. Capture those from the PC with Wireshark (`mdns || ssdp || arp`, filtered to the onn's IP).

### LAN-side capture (as run 2026-11-12)

1. Find the PC's Wi-Fi interface (`dumpcap -D`; the one holding the PC's LAN address) and start, outside the repo:
   `dumpcap -i <n> -a duration:720 -f "arp or (udp and (port 5353 or port 1900))" -w lan-scan.pcap`.
2. Right after it starts, run `python -I tools/lan_probe.py <PC's LAN IPv4>` once (standard SSDP M-SEARCH + mDNS PTR
   queries) so the capture records what the onn answers, not just what it volunteers.
3. Attribute the onn's frames by its MAC (so its IPv6 and ARP count too), drop the adb session (`tcp port 5555`),
   and commit only a masked summary (`findings/coffey-2026-11-lan.md` is the template). Note whether ADB over
   Wi-Fi is on: it makes the box advertise `_adb._tcp` with its serial.

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
