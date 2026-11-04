"""Minimal ELF reader: class/machine, build-id, NEEDED, dynamic symbols (defined/undefined), sections.

usage: python -I elfsyms.py <elf> [regex-filter]
"""
import re
import struct
import sys

p = sys.argv[1]
flt = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
d = open(p, "rb").read()
assert d[:4] == b"\x7fELF"
is64 = d[4] == 2
E = "<"
if is64:
    (e_type, e_mach, _, _, _, e_shoff, _, _, _, _, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(E + "HHIQQQIHHHHHH", d, 16)
else:
    (e_type, e_mach, _, _, _, e_shoff, _, _, _, _, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(E + "HHIIIIIHHHHHH", d, 16)
secs = []
for i in range(e_shnum):
    o = e_shoff + i * e_shentsize
    if is64:
        name, typ, flags, addr, off, size, link, info, align, entsize = struct.unpack_from(E + "IIQQQQIIQQ", d, o)
    else:
        name, typ, flags, addr, off, size, link, info, align, entsize = struct.unpack_from(E + "IIIIIIIIII", d, o)
    secs.append(dict(name=name, type=typ, addr=addr, off=off, size=size, link=link, entsize=entsize))
shstr = secs[e_shstrndx]


def cstr(off):
    return d[off:d.index(b"\0", off)].decode(errors="replace")


for s in secs:
    s["n"] = cstr(shstr["off"] + s["name"])
by = {s["n"]: s for s in secs}
print(f"class={'ELF64' if is64 else 'ELF32'} machine={e_mach} sections={len(secs)} "
      f"symtab={'yes' if '.symtab' in by else 'no'}")
if ".note.gnu.build-id" in by:
    s = by[".note.gnu.build-id"]
    namesz, descsz, _ = struct.unpack_from("<III", d, s["off"])
    print("build-id", d[s["off"] + 12 + ((namesz + 3) & ~3): s["off"] + 12 + ((namesz + 3) & ~3) + descsz].hex())
dyn, dynstr = by.get(".dynamic"), by.get(".dynstr")
if dyn:
    ent = 16 if is64 else 8
    for i in range(dyn["size"] // ent):
        tag, val = struct.unpack_from("<qQ" if is64 else "<iI", d, dyn["off"] + i * ent)
        if tag == 1:
            print("NEEDED", cstr(dynstr["off"] + val))
for tabname, strname in ((".dynsym", ".dynstr"), (".symtab", ".strtab")):
    if tabname not in by:
        continue
    st, ss = by[tabname], by[strname]
    ent = 24 if is64 else 16
    n_def = n_und = 0
    for i in range(st["size"] // ent):
        o = st["off"] + i * ent
        if is64:
            nm, info, other, shndx, value, size = struct.unpack_from("<IBBHQQ", d, o)
        else:
            nm, value, size, info, other, shndx = struct.unpack_from("<IIIBBH", d, o)
        name = cstr(ss["off"] + nm)
        if not name:
            continue
        und = shndx == 0
        n_und += und
        n_def += not und
        if flt and flt.search(name):
            print(f"{tabname} {'U' if und else 'D'} 0x{value:08x} {size:6d} {name}")
    print(f"{tabname}: defined={n_def} undefined={n_und}")
