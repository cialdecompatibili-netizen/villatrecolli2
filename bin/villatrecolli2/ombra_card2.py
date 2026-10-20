"""Aggiorna il blocco <style id=vtc-leggibilita-card> in tutte le pagine (testo bianco forzato + ombra nera sfumata). Per cambiare l'ombra modificare NEW e rilanciare.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import os, re
ROOT = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
SKIP = {".git", "_out", "_cestino", "wp-content", "wp-includes", "node_modules", "_avada", "modules_source"}
NEW = (
    '<style id="vtc-leggibilita-card">'
    '.fusion-column-inner-bg-wrapper>.fusion-column-wrapper :is(h1,h2,h3,h4,h5,h6,p,span,a,strong,em,div){'
    'color:#fff !important;'
    'text-shadow:0 1px 1px rgba(0,0,0,.70),0 2px 4px rgba(0,0,0,.60),0 4px 12px rgba(0,0,0,.52),'
    '0 8px 28px rgba(0,0,0,.44),0 14px 50px rgba(0,0,0,.36),0 0 70px rgba(0,0,0,.28);}'
    '</style>'
)
pat = re.compile(r'<style id="vtc-leggibilita-card">.*?</style>', re.S)
tot = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
        if 'id="vtc-leggibilita-card"' not in t:
            continue
        t2 = pat.sub(lambda m: NEW, t, count=1)
        open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t2)
        tot += 1
print("aggiornate", tot)
