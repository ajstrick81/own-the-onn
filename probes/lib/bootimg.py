"""In-memory boot-image ramdisk extraction (vendor_boot v3/v4, boot/init_boot v3/v4), lz4-legacy/gzip, newc cpio.

Same logic as research/coffey-boot-dispatch-2026-11-04/scripts/{bootimg_split,rd_extract}.py, but returning data
instead of writing files, so probes never touch the disk.
"""
import gzip
import struct


def _al(n, page):
    return (n + page - 1) // page * page


def _cstr(b):
    return b.split(b"\0", 1)[0].decode(errors="replace")


def split(d):
    """Return {'kind', 'cmdline', 'bootconfig', 'ramdisks': [(name, type, bytes)]}."""
    if d[:8] == b"VNDRBOOT":
        ver, page, _, _, vrd_size = struct.unpack_from("<IIIII", d, 8)
        cmdline = _cstr(d[28:28 + 2048])
        o = 28 + 2048
        hdr_size, dtb_size = struct.unpack_from("<II", d, o + 20)
        o += 36
        tbl_size = tbl_n = tbl_esz = bc_size = 0
        if ver >= 4:
            tbl_size, tbl_n, tbl_esz, bc_size = struct.unpack_from("<IIII", d, o)
        rd_off = _al(hdr_size, page)
        dtb_off = rd_off + _al(vrd_size, page)
        tbl_off = dtb_off + _al(dtb_size, page)
        bc_off = tbl_off + _al(tbl_size, page)
        rds = []
        if ver >= 4 and tbl_n:
            for i in range(tbl_n):
                e = tbl_off + i * tbl_esz
                sz, off, typ = struct.unpack_from("<III", d, e)
                rds.append((_cstr(d[e + 12:e + 44]) or f"frag{i}", typ, d[rd_off + off:rd_off + off + sz]))
        else:
            rds.append(("vendor", 0, d[rd_off:rd_off + vrd_size]))
        bc = d[bc_off:bc_off + bc_size].decode(errors="replace") if bc_size else ""
        return {"kind": f"vendor_boot_v{ver}", "cmdline": cmdline, "bootconfig": bc, "ramdisks": rds}
    if d[:8] == b"ANDROID!":
        k_size, r_size = struct.unpack_from("<II", d, 8)
        ver, = struct.unpack_from("<I", d, 40)
        page = 4096
        rds = []
        if r_size:
            off = page + _al(k_size, page)
            rds.append(("ramdisk", 0, d[off:off + r_size]))
        return {"kind": f"boot_v{ver}", "cmdline": _cstr(d[44:44 + 1536]), "bootconfig": "", "ramdisks": rds}
    raise ValueError("unknown boot image type")


def _lz4_block(src):
    dst = bytearray()
    i, n = 0, len(src)
    while i < n:
        tok = src[i]
        i += 1
        lit = tok >> 4
        if lit == 15:
            while True:
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        dst += src[i:i + lit]
        i += lit
        if i >= n:
            break
        off = src[i] | (src[i + 1] << 8)
        i += 2
        ml = tok & 15
        if ml == 15:
            while True:
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        ml += 4
        start = len(dst) - off
        if off >= ml:
            dst += dst[start:start + ml]
        else:
            for k in range(ml):
                dst.append(dst[start + k])
    return bytes(dst)


def decompress(d):
    if d[:4] == b"\x02\x21\x4c\x18":
        out, i = bytearray(), 4
        while i + 4 <= len(d):
            sz, = struct.unpack_from("<I", d, i)
            i += 4
            if sz == 0x184C2102:
                continue
            if sz == 0 or i + sz > len(d):
                break
            out += _lz4_block(d[i:i + sz])
            i += sz
        return bytes(out)
    if d[:2] == b"\x1f\x8b":
        return gzip.decompress(d)
    return d


def cpio_files(data):
    """Return {path: bytes} for regular files in a newc cpio archive (symlinks/devices skipped)."""
    files, i = {}, 0
    while i + 110 <= len(data):
        h = data[i:i + 110]
        if h[:6] not in (b"070701", b"070702"):
            break
        f = [int(h[6 + 8 * k:14 + 8 * k], 16) for k in range(13)]
        mode, fsize, nsize = f[1], f[6], f[11]
        name = data[i + 110:i + 110 + nsize - 1].decode(errors="replace")
        i = (i + 110 + nsize + 3) & ~3
        body = data[i:i + fsize]
        i = (i + fsize + 3) & ~3
        if name == "TRAILER!!!":
            break
        if mode & 0o170000 == 0o100000:
            files[name.lstrip("/")] = body
    return files
