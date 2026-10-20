#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pagespeed.py - ottimizzazioni dopo il report PageSpeed. Si puo' rilanciare senza danni (idempotente)."""
import io, os, re, glob
from PIL import Image
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(R)

# 1) IMMAGINI pesanti: massimo 1600 px sul lato lungo, JPEG qualita' 72 progressivo. Stesso nome file, si sostituisce solo se pesa meno.
for rel in ["2015/12/aquatic-plant-182635_1920.jpg", "2015/12/home-244125289.jpg", "2015/12/home-parallax-144609983.jpg",
            "2015/06/motor-yacht-634925_1920.jpg", "2015/12/about-call-to-action-57862405.jpg", "2015/12/project1-featured-294276386.jpg"]:
    p = os.path.join("wp-content", "uploads", *rel.split("/"))
    if not os.path.exists(p):
        print("manca", p); continue
    before = os.path.getsize(p)
    im = Image.open(p).convert("RGB")
    if max(im.size) > 1600:
        k = 1600.0 / max(im.size); im = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
    tmp = p + ".tmp"
    im.save(tmp, "JPEG", quality=72, optimize=True, progressive=True)
    if os.path.getsize(tmp) < before:
        os.replace(tmp, p)
    else:
        os.remove(tmp)
    print("img", rel, before // 1024, "->", os.path.getsize(p) // 1024, "KB")

def rd(p): return io.open(p, encoding="utf-8", newline="").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)

# 2) ANALYTICS: il vecchio tag Universal Analytics (UA-169611607-1) e' morto; Google lo girava gia' sul GA4. Un solo tag G- al suo posto.
n = 0
for p in glob.glob("_avada/**/*.html", recursive=True):
    s = rd(p)
    t = s.replace("gtag/js?id=UA-169611607-1", "gtag/js?id=G-0XM2HWE201").replace("gtag('config', 'UA-169611607-1')", "gtag('config', 'G-0XM2HWE201')")
    if t != s: wr(p, t); n += 1
print("analytics aggiornato in", n, "file")

# 3) HOME
h = "_avada/_pagine/home.html"
s = rd(h)
s = s.replace('href="http://themeforest.net/item/avada-responsive-multipurpose-theme/2833226?ref=ThemeFusion"', 'href="/contatti/"')   # il pulsante "Richiedi un preventivo" portava a ThemeForest
s = s.replace('class="testimonial-image" src=', 'class="testimonial-image" alt="Cliente soddisfatto" src=') if 'class="testimonial-image" alt=' not in s else s
s = s.replace("color:#747474", "color:#595959")                                   # contrasto testo grigio su bianco
if "preload" not in s.split("</head>")[0] or "hero-cantiere" not in s.split("</head>")[0]:
    s = s.replace("</head>", '<link rel="preconnect" href="https://www.googletagmanager.com">\n<link rel="preload" as="image" href="wp-content/uploads/2026/10/hero-cantiere.jpg" fetchpriority="high">\n</head>', 1)
wr(h, s)
print("home ok")

# 4) FONT: font-display swap, il testo si vede subito invece di aspettare il font
c = 0
for p in ["assets/fontawesome/css/all.min.css", "assets/fonts/roboto.css"] + glob.glob("wp-content/uploads/fusion-styles/*.css"):
    if not os.path.exists(p): continue
    s = rd(p)
    t = re.sub(r"@font-face\s*\{(?![^}]*font-display)", "@font-face{font-display:swap;", s)
    if t != s: wr(p, t); c += 1
print("font-display in", c, "css")
