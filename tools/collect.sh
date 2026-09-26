#!/usr/bin/env bash
# Read-only device collection for the onn privacy audit (sections 1-4).
# Usage: tools/collect.sh <onn-ip> <output-dir>
# Output stays in <output-dir>. Keep it OUTSIDE this repo (it contains personal data).
set -u
IP="${1:?onn ip}"; OUT="${2:?output dir}"
export MSYS_NO_PATHCONV=1   # Git Bash on Windows: don't mangle /system/... paths
S="$IP:5555"
adb connect "$S" >/dev/null
A() { adb -s "$S" shell "$@"; }
mkdir -p "$OUT"; cd "$OUT" || exit 1

# 1. identity + settings
for p in ro.product.model ro.product.manufacturer ro.product.device ro.build.fingerprint \
         ro.build.version.release ro.build.version.security_patch ro.soc.manufacturer ro.soc.model; do
  echo "$p=$(A getprop $p | tr -d '\r')"
done > identity.txt
A 'su -c id' > root_check.txt 2>&1
for ns in global secure system; do A settings list $ns > settings_$ns.txt; done

# 2. packages
A pm list packages -f -s > pkgs_system.txt
A pm list packages -f -3 > pkgs_user.txt
A pm list packages -d    > pkgs_disabled.txt
A pm list packages -U    > pkgs_uid.txt

# 3. permissions / usage
A dumpsys package > dumpsys_package.txt
A dumpsys appops  > appops.txt
A dumpsys location > location.txt
A dumpsys wifi > wifi_full.txt
A dumpsys media.audio_policy > audio_policy.txt
A dumpsys audio > audio_full.txt
A dumpsys connectivity > connectivity.txt
A dumpsys hdmi_control > hdmi_control.txt

# 4. background activity
A dumpsys activity services > services.txt
A dumpsys jobscheduler > jobs.txt
A dumpsys alarm > alarms.txt
A dumpsys netstats detail > netstats.txt
A cmd package query-receivers --components -a android.intent.action.BOOT_COMPLETED > boot_receivers.txt
A cat /proc/net/tcp /proc/net/tcp6 /proc/net/udp /proc/net/udp6 > sockets.txt 2>&1

# sensitive granted permissions, parsed from the Packages: section ONLY
# (the later "Shared users:" section would otherwise be attributed to the last package)
awk '/^Packages:/{on=1} /^Hidden system packages:/{on=0}
     on && /^  Package \[/{pkg=$2; gsub(/[\[\]]/,"",pkg)}
     on && /granted=true/{p=$1; sub(/:.*/,"",p); print pkg"\t"p}' dumpsys_package.txt | sort -u > granted.tsv
for perm in RECORD_AUDIO CAPTURE_AUDIO_OUTPUT CAPTURE_VIDEO_OUTPUT CAPTURE_SECURE_VIDEO_OUTPUT READ_FRAME_BUFFER \
            CAPTURE_TV_INPUT CAPTURE_AUDIO_HOTWORD ACCESS_FINE_LOCATION ACCESS_COARSE_LOCATION \
            ACCESS_BACKGROUND_LOCATION NEARBY_WIFI_DEVICES BLUETOOTH_SCAN LOCAL_MAC_ADDRESS \
            CHANGE_WIFI_MULTICAST_STATE QUERY_ALL_PACKAGES PACKAGE_USAGE_STATS; do
  echo "$perm: $(grep "\.$perm\$" granted.tsv | cut -f1 | tr '\n' ' ')"
done > granted_summary.txt

# system-UID packages (full OS privilege)
grep -B1 -A1 'sharedUser=SharedUserSetting{[^}]*android.uid.system' dumpsys_package.txt \
  | grep -oE 'Package \[[^]]+\]' | sort -u > system_uid_packages.txt

echo "done -> $OUT"; cat identity.txt; cat granted_summary.txt
