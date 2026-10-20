"""Controlla online (github.io/villatrecolli2) home IT e /en/: titolo, immagini che rispondono 200, colonne con solo colore. Solo lettura.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import urllib.request, re, urllib.parse
UA = {"User-Agent": "Mozilla/5.0"}
B = "https://cialdecompatibili-netizen.github.io/villatrecolli2/"


def g(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40)
        return r.status, r.read()
    except Exception as e:
        return getattr(e, "code", str(e)), b""


for u in (B, B + "en/"):
    s, b = g(u)
    t = b.decode("utf8", "ignore")
    print(u, s, re.findall(r"<title>(.*?)</title>", t, re.S)[:1], "img tag:", len(re.findall(r"<img", t)))
    imgs = set(re.findall(r'(?:src|data-orig-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp))', t))
    bad = 0
    for i in imgs:
        a = urllib.parse.urljoin(u, i)
        if "github.io" not in a:
            continue
        st, _ = g(a)
        if st != 200:
            bad += 1
            print("KO", st, a)
    print("immagini", len(imgs), "ko", bad)
    # card Avada senza immagine: fusion-image-element / fusion-builder-column con background vuoto
    cards = re.findall(r'class="[^"]*fusion-column-wrapper[^"]*"[^>]*style="([^"]*)"', t)
    vuote = [c for c in cards if "background-image" not in c and "background-color" in c]
    print("colonne con solo colore:", len(vuote))
