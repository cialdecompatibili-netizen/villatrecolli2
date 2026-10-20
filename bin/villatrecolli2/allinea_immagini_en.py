"""Allinea le immagini delle pagine EN a quelle delle pagine IT corrispondenti (mirror villatrecolli2).
Motivo: sul sito originale molte pagine /en/ sono testo semplice senza le foto della versione italiana.
Per ogni pagina EN 'semplice' (senza fusion-builder-row) con pagina IT collegata via hreflang="it":
  - prende le <img> di contenuto dell'IT che mancano nell'EN (confronto per nome file senza suffisso -WxH),
  - le inserisce nell'EN dopo il paragrafo nella stessa posizione relativa (k-esimo paragrafo di N -> round(k*M/N)),
  - riscrive i percorsi wp-content/ per la profondita' della pagina EN.
Idempotente: rilanciato non aggiunge doppioni. Uso: python allinea_immagini_en.py [--apply]
Pagine EN con layout Avada (home, negozio, categorie) sono escluse di proposito: vanno viste a mano."""
import os, re, subprocess, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
APPLY = "--apply" in sys.argv

def rd(p): return open(p, "rb").read().decode("utf8", "surrogateescape")
def region(t):
    i = t.find('<div class="post-content">'); j = t.find('<div class="fusion-woocommerce-quick-view-overlay">')
    return (i, j) if i >= 0 and j > i else (-1, -1)
def base(u):
    n = os.path.basename(u.split("?")[0])
    return re.sub(r"-\d+x\d+(?=\.[a-z]+$)", "", n).lower()
def img_src(tag):
    m = re.search(r'data-orig-src="([^"]+)"', tag) or re.search(r'\bsrc="([^"]*uploads[^"]*)"', tag)
    return m.group(1) if m else ""

tracked = subprocess.run(["git", "-C", R, "ls-files", "en/*/index.html"], capture_output=True, text=True).stdout.split()
tot = 0
for rel in tracked:
    p = os.path.join(R, rel); t = rd(p)
    m = re.search(r'<link rel="alternate" hreflang="it" href="([^"]*)"', t)
    i, j = region(t)
    if not m or i < 0: continue
    reg = t[i:j]
    if "fusion-builder-row" in reg: continue
    u = re.sub(r"^https?://[^/]+/(?:villatrecolli2/)?", "", m.group(1)).strip("/")
    ip = os.path.join(R, *u.split("/"), "index.html")
    if not u or not os.path.isfile(ip): continue
    it = rd(ip); a, b = region(it)
    if a < 0: continue
    ireg = it[a:b]
    have = {base(img_src(x)) for x in re.findall(r"<img\b[^>]*>", reg)}
    # sequenza IT: paragrafi con testo e immagini
    seq = []
    for mm in re.finditer(r"<img\b[^>]*>|<p\b[^>]*>(.*?)</p>", ireg, re.S):
        if mm.group(0).startswith("<img"):
            seq.append(("img", mm.group(0)))
        else:
            if re.sub(r"<[^>]+>|&nbsp;|\s", "", mm.group(1) or ""):
                seq.append(("p", None))
            for im in re.findall(r"<img\b[^>]*>", mm.group(0)):
                seq.append(("img", im))
    # immagini dentro <p> gia' contate sopra come img; qui contiamo i paragrafi di testo
    N = sum(1 for k, _ in seq if k == "p")
    miss = []; k = 0
    for kind, tag in seq:
        if kind == "p": k += 1; continue
        s = img_src(tag)
        if not s or "logo" in s or "uploads" not in s: continue
        if base(s) in have: continue
        have.add(base(s)); miss.append((k, tag))
    if not miss: continue
    ps = [mm.end() for mm in re.finditer(r"<p\b[^>]*>(.*?)</p>", reg, re.S) if re.sub(r"<[^>]+>|&nbsp;|\s", "", mm.group(1))]
    firstp = re.search(r"<p\b", reg)
    M = len(ps)
    if M == 0 or not firstp: continue
    depth = len(rel.split("/")) - 1
    ins = []
    for k, tag in miss:
        tag = re.sub(r"(?:\.\./)+(wp-content)", lambda x: "../" * depth + x.group(1), tag)
        tag = re.sub(r'https?://(?:www\.)?villatrecolli\.com/(wp-content)', lambda x: "../" * depth + x.group(1), tag)
        pos = firstp.start() if k == 0 else ps[min(M - 1, max(0, round(k * M / max(N, 1)) - 1))]
        ins.append((pos, '<p style="text-align:center">' + tag + "</p>" if k else '<p style="text-align:center">' + tag + "</p>\n"))
    for pos, html in sorted(ins, key=lambda x: -x[0]):
        reg = reg[:pos] + html + reg[pos:]
    print(("APPLY" if APPLY else "DRY  "), rel, "+%d img" % len(miss), [base(img_src(x[1])) for x in miss][:3])
    tot += len(miss)
    if APPLY:
        open(p, "wb").write((t[:i] + reg + t[j:]).encode("utf8", "surrogateescape"))
print("immagini aggiunte:", tot)
