"""Find references to odm_ext / PQ file paths in ELFs, configs, jars and APK dex/so entries.

usage: python -I pathscan.py <tree> [<tree> ...]   (trees = unpacked vendor/odm/system_ext/product/system)
"""
import os, re, sys, zipfile
pats = [b'odm_ext', b'tvconfig', b'pq_default.ini', b'tv_default.xml', b'tvconfig.conf', b'tvscan.conf', b'tv_rrt_define',
        b'tv_setting_config', b'UI_PQSetting', b'chmod_files', b'pq.db', b'overscan.db', b'cri_data', b'/mnt/vendor/param/pq']
rx = re.compile(b'[ -~]{0,60}(?:' + b'|'.join(re.escape(p) for p in pats) + b')[ -~]{0,60}')
hits = {}
def scan(name, data):
    found = sorted(set(m.group(0).decode('ascii', 'replace') for m in rx.finditer(data)))
    if found: hits[name] = found
for root in sys.argv[1:]:
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            try:
                if os.path.getsize(p) > 60_000_000: continue
                d = open(p, 'rb').read()
            except OSError: continue
            rel = p.replace(root, os.path.basename(root.rstrip('\\/')))
            if d[:4] == b'\x7fELF' or f.endswith(('.jar', '.odex', '.vdex', '.rc', '.xml', '.sh', '.cfg', '.conf', '.ini')):
                scan(rel, d)
            elif d[:2] == b'PK' and f.endswith(('.apk', '.jar')):
                try:
                    z = zipfile.ZipFile(p)
                    for n in z.namelist():
                        if n.endswith('.dex') or n.endswith('.so'):
                            scan(rel + '!' + n, z.read(n))
                except Exception: pass
for k in sorted(hits):
    print('##', k)
    for s in hits[k][:14]: print('   ', s)