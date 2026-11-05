"""Split Android boot-image ramdisks out (vendor_boot v3/v4, boot/init_boot v3/v4) and print header fields.

usage: python3 -I bootimg_split.py <image> <outdir>
Writes <outdir>/<name>.ramdisk (still compressed) per ramdisk, plus cmdline.txt / bootconfig.txt when present.
"""
import os
import struct
import sys

img, out = sys.argv[1], sys.argv[2]
d = open(img, "rb").read()
os.makedirs(out, exist_ok=True)


def al(n, page):
    return (n + page - 1) // page * page


def cstr(b):
    return b.split(b"\0", 1)[0].decode(errors="replace")


if d[:8] == b"VNDRBOOT":
    ver, page, _, _, vrd_size = struct.unpack_from("<IIIII", d, 8)
    cmdline = cstr(d[28:28 + 2048])
    o = 28 + 2048
    tags, = struct.unpack_from("<I", d, o)
    name = cstr(d[o + 4:o + 20])
    hdr_size, dtb_size = struct.unpack_from("<II", d, o + 20)
    o += 28 + 8  # header_size, dtb_size, dtb_addr(u64)
    tbl_size = tbl_n = tbl_esz = bc_size = 0
    if ver >= 4:
        tbl_size, tbl_n, tbl_esz, bc_size = struct.unpack_from("<IIII", d, o)
    print(f"vendor_boot v{ver} page={page} name={name!r} vendor_ramdisk_size={vrd_size} dtb_size={dtb_size} "
          f"table_entries={tbl_n} bootconfig_size={bc_size}")
    open(os.path.join(out, "cmdline.txt"), "w").write(cmdline + "\n")
    print("cmdline:", cmdline)
    rd_off = al(hdr_size, page)
    dtb_off = rd_off + al(vrd_size, page)
    tbl_off = dtb_off + al(dtb_size, page)
    bc_off = tbl_off + al(tbl_size, page)
    if ver >= 4 and tbl_n:
        for i in range(tbl_n):
            e = tbl_off + i * tbl_esz
            sz, off, typ = struct.unpack_from("<III", d, e)
            nm = cstr(d[e + 12:e + 44]) or f"frag{i}"
            p = os.path.join(out, f"{i}-{nm}-type{typ}.ramdisk")
            open(p, "wb").write(d[rd_off + off:rd_off + off + sz])
            print(f"ramdisk[{i}] name={nm!r} type={typ} size={sz} -> {os.path.basename(p)}")
    else:
        open(os.path.join(out, "vendor.ramdisk"), "wb").write(d[rd_off:rd_off + vrd_size])
    if bc_size:
        bc = d[bc_off:bc_off + bc_size].decode(errors="replace")
        open(os.path.join(out, "bootconfig.txt"), "w").write(bc)
        print("bootconfig:\n" + bc)
elif d[:8] == b"ANDROID!":
    k_size, r_size, os_ver, hdr_size = struct.unpack_from("<IIII", d, 8)
    ver, = struct.unpack_from("<I", d, 40)
    page = 4096
    cmdline = cstr(d[44:44 + 1536])
    print(f"boot v{ver} kernel_size={k_size} ramdisk_size={r_size} os_version=0x{os_ver:x}")
    print("cmdline:", cmdline)
    open(os.path.join(out, "cmdline.txt"), "w").write(cmdline + "\n")
    if r_size:
        off = page + al(k_size, page)
        open(os.path.join(out, "boot.ramdisk"), "wb").write(d[off:off + r_size])
        print("ramdisk -> boot.ramdisk")
else:
    sys.exit("unknown image type")
