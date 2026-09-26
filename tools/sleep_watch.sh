#!/usr/bin/env bash
# Poll the onn once a minute; on sleep, close the open "now" window in markers.txt
# and open a new "asleep" window. Usage: tools/sleep_watch.sh <onn-ip> <capture-dir> [label]
export MSYS_NO_PATHCONV=1
IP="${1:?onn ip}"; DIR="${2:?capture dir}"; LABEL="${3:-Z-asleep}"
cd "$DIR" || exit 1
while true; do
  w=$(adb -s "$IP:5555" shell "dumpsys power | grep -m1 mWakefulness=" 2>/dev/null | tr -d '\r' | sed 's/.*=//')
  if [ "$w" = "Asleep" ]; then
    ts=$(python -c "import time;print(time.time())")
    python - "$ts" "$LABEL" <<'EOF'
import sys
ts, label = sys.argv[1], sys.argv[2]
L = open("markers.txt").read().splitlines()
L = [l.replace(" now ", f" {ts} ", 1) if " now " in l else l for l in L]
L.append(f"{ts} now {label}")
open("markers.txt", "w").write("\n".join(L) + "\n")
EOF
    echo "asleep at $(date)"; cat markers.txt; exit 0
  fi
  sleep 60
done
