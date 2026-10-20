"""Card home: copia l'immagine di data-bg-url (wrapper) nello span data-bg (strato sopra) dove c'era immagine-grigia-1.jpg. Idempotente.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import os, re

ROOT = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
SKIP = {".git", "_out", "_cestino", "wp-content", "wp-includes", "node_modules", "_avada", "modules_source"}
pat = re.compile(
    r'(data-bg-url=")([^"]+)(")((?:(?!fusion-column-inner-bg-wrapper).)*?)'
    r'(<span class="fusion-column-inner-bg-image[^"]*"[^>]*?data-bg=")([^"]*immagine-grigia-1\.jpg)(")',
    re.S,
)
tot = files = 0
left = {}
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
        if "immagine-grigia-1.jpg" not in t:
            continue
        n = 0

        def rep(m):
            global n
            n += 1
            return m.group(1) + m.group(2) + m.group(3) + m.group(4) + m.group(5) + m.group(2) + m.group(7)

        t2 = pat.sub(rep, t)
        if n:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t2)
            tot += n
            files += 1
        rest = len(re.findall(r'fusion-column-inner-bg-image[^>]*data-bg="[^"]*immagine-grigia-1\.jpg', t2))
        if rest:
            left[os.path.relpath(p, ROOT)] = rest
print("card sistemate", tot, "in", files, "file")
print("ancora grigie:", left)
