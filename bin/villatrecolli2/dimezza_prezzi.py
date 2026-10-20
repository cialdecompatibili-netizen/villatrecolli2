"""Prezzi shop villatrecolli2: dimezzati rispetto ai demo, Pacchetto fotografico a 250 euro.
Mappa (vecchio -> nuovo): 1,200.00 -> 250.00 (Pacchetto fotografico/Photo Package), 850.00 -> 425.00 (Abito da sposa in seta),
800.00 -> 400.00 (Allestimento tavola/Table Setting), 60.00 -> 30.00 (Catering, Animazione musicale/Live Music DJ).
Sostituisce solo i prezzi nel markup WooCommerce (currencySymbol &euro; ... </bdi>), in tutti gli .html tracciati.
Idempotente: dopo la prima esecuzione i vecchi valori non esistono piu'. Uso: python dimezza_prezzi.py [--apply]"""
import os, re, subprocess, sys, collections
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
APPLY = "--apply" in sys.argv
MAP = {"1,200.00": "250.00", "850.00": "425.00", "800.00": "400.00", "60.00": "30.00"}
RE = re.compile(r'(currencySymbol">&euro;</span>)(1,200\.00|850\.00|800\.00|60\.00)(</bdi>)')
files = [x for x in subprocess.run(["git", "-C", R, "ls-files", "*.html"], capture_output=True, text=True, encoding="utf8", errors="replace").stdout.split("\n")
         if x and not x.startswith(("wp-content", "wp-includes", "_out", "_avada", "_layouts", "_includes"))]
cnt = collections.Counter(); nf = 0
for f in files:
    p = os.path.join(R, f)
    t = open(p, "rb").read().decode("utf8", "surrogateescape")
    def r(m):
        cnt[m.group(2)] += 1
        return m.group(1) + MAP[m.group(2)] + m.group(3)
    n = RE.sub(r, t)
    if n != t:
        nf += 1
        if APPLY:
            open(p, "wb").write(n.encode("utf8", "surrogateescape"))
print("file:", nf, "sostituzioni:", dict(cnt), "(applicato)" if APPLY else "(dry-run)")
# residui in altre forme (filtro prezzo, JSON-LD, data-attributi)
left = collections.Counter()
for f in files:
    t = open(os.path.join(R, f), "rb").read().decode("utf8", "surrogateescape")
    for m in re.finditer(r'(?:max_price|min_price|data-max|data-min|"price"\s*:|data-price|data-product_price|product:price:amount|"lowPrice"|"highPrice")[^<>]{0,40}', t):
        left[re.sub(r"\d{4,}", "#", m.group(0))[:70]] += 1
print("altre forme di prezzo:", left.most_common(10))
