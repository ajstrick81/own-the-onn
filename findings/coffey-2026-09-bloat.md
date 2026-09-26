# onn 4K Plus "coffey": bloatware study (DRAFT, 2026-09-26)

Read-only measurements (nothing disabled). Sources: `dumpsys diskstats`, `procstats --hours 24`, `meminfo`, `cpuinfo`,
`usagestats`, `jobscheduler`, `alarm`, `deviceidle`. Raw data is kept outside the repo.

## Context: the constraint is RAM, not storage

- **RAM: 1.97 GB total**, about 1.72 GB used, **~611 MB already swapped to compressed ZRAM**. Every always-resident app competes with
  what you're watching.
- System partitions are read-only and 100% full **by design**. Disabling a preinstalled app does **not** free system space; it
  frees its `/data` footprint (updates, data, cache), RAM, background CPU and network. `/data`: 6.0 of 11 GB used.
- CPU at idle is dominated by system_server, surfaceflinger, the audio HAL and the launcher (~5%, animated previews). No app was a CPU hog.

> procstats "% resident" includes cached time. We report the **state** (Top = you were using it; Imp Bg / Service = kept
> alive in the background) so that foreground use isn't mistaken for bloat.

## Findings

### 1. Preinstalled Netflix: heaviest, but REQUIRED if you use a patched Netflix
`com.netflix.ninja` (system app): **36 seconds of recorded use**, yet **resident 50% of the day in "important background"**
(avg 93 MB, peak 144 MB, about 5% of all RAM), 127 MB of data, 3 scheduled jobs. It is on the **firmware's idle-exemption
list** (`system-excidle`), so the firmware deliberately keeps it out of Android's power management. It is also the app that logs while
the screen is off, boots itself on wake over plain HTTP, and holds LAN listeners (see the traffic findings). The companion
`com.netflix.tokenmanager` runs as the system UID.

**Keep it anyway** if you run a patched or cloned Netflix: the clone's security check depends on the original preinstalled
APK being present. For stock-only users it remains the strongest candidate. *(Possible future experiment: restrict its
background running without disabling it, then check the clone still works.)*

### 2. Always-resident vendor services (small, but never stop)
| Package | Resident | Avg RAM | What it does |
|---|---|---|---|
| `com.gretzky.hwinfo` | 100% (service) | 5 MB | Factory test tool; in retail, mirrors the USB-debug toggle and checks remote pairing |
| `com.onn.updatenotification` | 100% | 8 MB | onn OTA-update notices (keep for security) |
| `com.onn.bluetoothconnect` | 100% | 8 MB | Remote-pairing wizard (needed if the remote is re-paired) |
| `com.droidlogic.*` (4) | 100% | 5–20 MB | Amlogic platform glue: settings, mic toggle, connected devices (keep) |

### 3. Google components you may not use
| Package | Cost | Note |
|---|---|---|
| `com.google.android.apps.mediashell` (Chromecast built-in) | 100% resident, 31 MB, LAN listeners 8008/8009/8443 | Needed only if you cast |
| `com.google.android.tungsten.setupwraith` (setup wizard) | 35% resident (19% stuck in a receiver), 14–22 MB | Setup finished long ago; also used when adding accounts |
| `com.google.android.apps.tv.dreamx` (ambient/screensaver) | 21%, 18 MB | Only if you want Google's ambient mode |
| `com.google.android.play.games` | 20 MB data, never used | No function on this device |
| `com.google.android.syncadapters.calendar` | 11 MB, 1 job | No calendar UI on TV |
| `com.android.printspooler` | holds location permission | Nothing to print from |
| AdServices / OnDevicePersonalization / Health Connect | APEX modules, idle | Privacy Sandbox ad APIs on a TV; usually not user-removable |

### 4. User-installed apps with no recorded use
Several installed apps show **no recorded use** in the usage-stats history while holding 60–430 MB of data each
(a browser, a streaming app, the Apple TV app, and a few utilities). Only the owner can judge these; the data is in the raw table.

### Not bloat (checked)
- Tubi's high residency was **foreground viewing** (Top 47%), not background.
- The Netflix clone and Prime: foreground use plus normal playback services.
- WireGuard: resident because the capture tunnel was active.

## Removal methods (all reversible, none applied)

| Method | Command | Undo |
|---|---|---|
| Disable (preferred) | `adb shell pm disable-user --user 0 <pkg>` | `adb shell pm enable <pkg>` |
| Uninstall for user 0 (keeps the system copy) | `adb shell pm uninstall -k --user 0 <pkg>` | `adb shell cmd package install-existing <pkg>` |
| Restrict background only | `adb shell cmd appops set <pkg> RUN_ANY_IN_BACKGROUND ignore` | `… allow` |

Factory reset restores everything. **Never** remove platform packages (`com.droidlogic*`, `com.android.*` core, GMS, launcher, Gboard).

## Trial on the test unit (2026-09-26)

Disabled with `pm disable-user --user 0`, one at a time, checking for crashes and ANRs after each and confirming the launcher still works:

| Package | Result |
|---|---|
| `com.google.android.play.games` | disabled, no errors |
| `com.google.android.syncadapters.calendar` | disabled, no errors |
| `com.android.printspooler` | disabled, no errors; its location grant is now inert (the app can't run) |

- **RAM:** no measurable change, as expected: all three showed 0% residency beforehand. Free RAM moved within normal noise.
- **`/data`:** free space rose from 4.99 GB to 5.11 GB (+~117 MB; includes cache clean-up by the Play Store and search indexer).
- **Kept by choice:** preinstalled Netflix (the clone depends on it) and Chromecast built-in.
- Undo any of them: `adb shell pm enable <pkg>`.
