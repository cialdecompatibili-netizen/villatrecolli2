"""Crea card-sale-hd.jpg dalla foto originale 960x540 e aggiorna i riferimenti nelle pagine. Percorsi assoluti Windows.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import os
from PIL import Image
ROOT = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
SKIP = {".git", "_out", "_cestino", "wp-content", "wp-includes", "node_modules", "_avada", "modules_source"}
src = os.path.join(ROOT, "wp-content", "uploads", "2025", "06", "495654578_2716124255240831_3603234743885722183_n.jpg")
dst = os.path.join(ROOT, "wp-content", "uploads", "2026", "10", "card-sale-hd.jpg")
im = Image.open(src).convert("RGB")
print("origine", im.size)
im.save(dst, "JPEG", quality=95, subsampling=0, optimize=True)
print("salvata", os.path.getsize(dst))
n = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
        if "card-sale.jpg" in t:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t.replace("card-sale.jpg", "card-sale-hd.jpg"))
            n += 1
print("pagine aggiornate", n)
