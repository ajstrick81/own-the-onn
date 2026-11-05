#!/bin/bash
# Rebuild the donor DTBs and the normalized coffey DT used in COFFEY-DTB-COMPARISON-v2.md.
# Host: WSL Ubuntu with git, cpp, dtc 1.7.2, python3.
# Inputs: CoreELEC common_drivers (fetched below at pinned commits); dt-bindings from AOSP kernel/common at
# coffey's commit 3d26c188ef7e (local clone path in KCOMMON); coffey's carved base DT (COFFEY_DTB).
set -e
KCOMMON=${KCOMMON:-/mnt/e/Morphe/kernel/common}
COFFEY_DTB=${COFFEY_DTB:-/mnt/e/Morphe/device/coffey-ota/analysis/vbdt/01_dtbdump_s7d_s905x5m_bm202.dtb}
W=${W:-$HOME/ownonn-dt}
BOARDS="s7d_s905x5m_bm202 s7d_s905x5m_2g s7d_s905x5m_xiaomi_3rd_gen s7d_s905x5m_ugoos_x5m_pro s7d_s905x5m_odroid_c5 s7d_s905x5m_bm201"

rm -rf "$W"; mkdir -p "$W/out"; cd "$W"
git clone -q --filter=blob:none --no-checkout https://github.com/CoreELEC/common_drivers.git cd
git -C cd fetch -q --filter=blob:none origin 4dbe1c27ae176fde4c1cbef7506618fd7f62b976 8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734
git -C cd sparse-checkout set --no-cone '/arch/arm64/boot/dts/amlogic/' '/include/'
git -C cd worktree add -q --detach ../cd-4dbe1c27 4dbe1c27ae176fde4c1cbef7506618fd7f62b976
git -C cd worktree add -q --detach ../cd-8646fbd1 8646fbd1a8b0c77d7f73bbbc77b0a660bda4b734
mkdir -p kinc && git -C "$KCOMMON" archive 3d26c188ef7e include/dt-bindings | tar -x -C kinc

for c in 4dbe1c27 8646fbd1; do
  D=cd-$c/arch/arm64/boot/dts/amlogic
  for b in $BOARDS; do
    o=out/$c-$b
    cpp -nostdinc -undef -D__DTS__ -x assembler-with-cpp -I "$D" -I "cd-$c/include" -I kinc/include "$D/$b.dts" -o "$o.pp"
    dtc -q -I dts -O dtb -o "$o.dtb" "$o.pp"
    dtc -q -s -I dtb -O dts -o "$o.dts" "$o.dtb"
  done
done

# coffey: the dump is the FDT followed by unrelated bytes; keep exactly the header's totalsize
python3 -I - "$COFFEY_DTB" out/coffey.dtb <<'EOF'
import struct, sys
d = open(sys.argv[1], 'rb').read()
assert d[:4] == b'\xd0\x0d\xfe\xed', 'not an FDT'
n = struct.unpack('>I', d[4:8])[0]
open(sys.argv[2], 'wb').write(d[:n])
print('coffey FDT totalsize', n)
EOF
dtc -q -s -I dtb -O dts -o out/coffey.dts out/coffey.dtb
sha256sum out/coffey.dtb out/*.dtb | sort -u -k2
