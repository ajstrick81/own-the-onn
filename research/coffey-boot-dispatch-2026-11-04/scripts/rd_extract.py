"""Extract an Android ramdisk (lz4-legacy or gzip, newc cpio) without external tools.

Regular files and directories only; symlinks are recorded in SYMLINKS.txt, device nodes skipped, and paths are
confined to <outdir>.
usage: python -I rd_extract.py <ramdisk> <outdir>
"""
import gzip
import os
import struct
import sys


def lz4_block(src, out_cap):
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
    if d[:4] == b"\x02\x21\x4c\x18":  # lz4 legacy
        out, i = bytearray(), 4
        while i + 4 <= len(d):
            sz, = struct.unpack_from("<I", d, i)
            if sz == 0x184C2102:  # concatenated frame
                i += 4
                continue
            i += 4
            if sz == 0 or i + sz > len(d):
                break
            out += lz4_block(d[i:i + sz], 8 << 20)
            i += sz
        return bytes(out)
    if d[:2] == b"\x1f\x8b":
        return gzip.decompress(d)
    return d


def cpio(data, outdir):
    i, nfiles, links = 0, 0, []
    root = os.path.realpath(outdir)
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
        dest = os.path.realpath(os.path.join(outdir, name.lstrip("/")))
        if not dest.startswith(root):
            continue
        kind = mode & 0o170000
        if kind == 0o040000:
            os.makedirs(dest, exist_ok=True)
        elif kind == 0o100000:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "wb").write(body)
            nfiles += 1
        elif kind == 0o120000:
            links.append(f"{name} -> {body.decode(errors='replace')}")
    open(os.path.join(outdir, "SYMLINKS.txt"), "w").write("\n".join(links) + "\n")
    return nfiles, len(links)


if __name__ == "__main__":
    raw = open(sys.argv[1], "rb").read()
    os.makedirs(sys.argv[2], exist_ok=True)
    n, l = cpio(decompress(raw), sys.argv[2])
    print(f"{sys.argv[1]}: {n} files, {l} symlinks")
