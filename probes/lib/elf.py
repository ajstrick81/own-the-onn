"""Minimal ELF reader for probes: class, build-id, NEEDED, dynamic symbols. Read-only; no external tools."""
import struct


def read(d):
    assert d[:4] == b"\x7fELF", "not an ELF"
    is64 = d[4] == 2
    if is64:
        f = struct.unpack_from("<HHIQQQIHHHHHH", d, 16)
    else:
        f = struct.unpack_from("<HHIIIIIHHHHHH", d, 16)
    e_shoff, e_shentsize, e_shnum, e_shstrndx = f[5], f[10], f[11], f[12]
    secs = []
    for i in range(e_shnum):
        o = e_shoff + i * e_shentsize
        if is64:
            name, typ, _, addr, off, size, link, info, _, ent = struct.unpack_from("<IIQQQQIIQQ", d, o)
        else:
            name, typ, _, addr, off, size, link, info, _, ent = struct.unpack_from("<IIIIIIIIII", d, o)
        secs.append({"name": name, "off": off, "size": size})

    def cstr(off):
        return d[off:d.index(b"\0", off)].decode(errors="replace")

    strtab = secs[e_shstrndx]["off"]
    by = {cstr(strtab + s["name"]): s for s in secs}
    out = {"class": "ELF64" if is64 else "ELF32", "build_id": None, "needed": [], "dynsym_defined": [],
           "dynsym_undefined": []}
    note = by.get(".note.gnu.build-id")
    if note:
        namesz, descsz, _ = struct.unpack_from("<III", d, note["off"])
        s = note["off"] + 12 + ((namesz + 3) & ~3)
        out["build_id"] = d[s:s + descsz].hex()
    dyn, dynstr = by.get(".dynamic"), by.get(".dynstr")
    if dyn and dynstr:
        ent = 16 if is64 else 8
        for i in range(dyn["size"] // ent):
            tag, val = struct.unpack_from("<qQ" if is64 else "<iI", d, dyn["off"] + i * ent)
            if tag == 1:
                out["needed"].append(cstr(dynstr["off"] + val))
    st = by.get(".dynsym")
    if st and dynstr:
        ent = 24 if is64 else 16
        for i in range(st["size"] // ent):
            o = st["off"] + i * ent
            if is64:
                nm, _, _, shndx, _, _ = struct.unpack_from("<IBBHQQ", d, o)
            else:
                nm, _, _, _, _, shndx = struct.unpack_from("<IIIBBH", d, o)
            name = cstr(dynstr["off"] + nm)
            if name:
                out["dynsym_undefined" if shndx == 0 else "dynsym_defined"].append(name)
    return out
