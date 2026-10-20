"""Toglie l'attributo data-bg=...immagine-grigia-1.jpg residuo (sfondo grigio delle sezioni). Idempotente.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import os, re
ROOT = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
SKIP = {".git", "_out", "_cestino", "wp-content", "wp-includes", "node_modules", "_avada", "modules_source"}
attr = re.compile(r'\s?data-bg="[^"]*immagine-grigia-1\.jpg"')
tot = files = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
        if "immagine-grigia" not in t:
            continue
        t2, n = attr.subn("", t)
        if n:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t2)
            tot += n; files += 1
        r = len(re.findall("immagine-grigia", t2))
        if r:
            print("resta", os.path.relpath(p, ROOT), r)
print("tolti", tot, "in", files, "file")
