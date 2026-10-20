"""Toglie da tutti gli HTML il blocco demo Avada 'Top Sliding Bar' (fusion-sliding-bar-wrapper) contando i <div> annidati. Idempotente.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import os, re

ROOT = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
SKIP = {".git", "_out", "_cestino", "wp-content", "wp-includes", "node_modules", "_avada", "modules_source"}
START = '<div class="fusion-sliding-bar-wrapper">'
tok = re.compile(r"<div\b|</div\s*>", re.I)

tot = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
        i = t.find(START)
        if i < 0:
            continue
        depth = 0
        end = None
        for m in tok.finditer(t, i):
            depth += 1 if m.group(0).lower().startswith("<div") else -1
            if depth == 0:
                end = m.end()
                break
        if end is None:
            print("KO bilanciamento", p)
            continue
        t = t[:i] + t[end:]
        open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t)
        tot += 1
print("ripulite", tot, "pagine")
