"""Villa Tre Colli (villatrecolli2) - WhatsApp in versione LUXURY + foto in 'Servizi inclusi'.
1) Pagine contatti (contactwp, contatti, en/contactwp, en/contact): il blocco id=vtc-whatsapp diventa una card elegante (nero caldo, oro champagne, serif).
2) Fine testo delle pagine di servizio (IT+EN): invito discreto 'scrivici su WhatsApp' (aside id=vtc-cta) con lo stesso stile, formato piccolo.
3) Servizi inclusi (IT+EN): foto hero della villa al tramonto (wp-content/uploads/2024/07/villa-tre-colli-roma.jpg) al posto dello slider vuoto.
Idempotente: rilanciando i blocchi vengono sostituiti (per cambiare testi/colori si modifica qui e si rilancia).
NB: sostituisce il vecchio contatti_whatsapp.py (NON rilanciare quello: rimetterebbe il blocco semplice).
Uso: python luxury_whatsapp.py [--apply]"""
import os, re, sys
from urllib.parse import quote

ROOT = r"C:\Users\Mirco\Desktop\repository\villatrecolli2"
APPLY = "--apply" in sys.argv
WA = "393338495178"
IMG = "wp-content/uploads/2024/07/villa-tre-colli-roma.jpg"

TXT = {
    "it": dict(kick_full="Villa Tre Colli &middot; Monterotondo, Roma", kick_mini="Villa Tre Colli", tit="Contattaci su WhatsApp",
               p="Per informazioni, date disponibili e preventivi scrivici direttamente su WhatsApp: ti rispondiamo noi.",
               b="Scrivici su WhatsApp", n="Oppure chiama il +39 333 849 5178", m="Buongiorno, vorrei avere informazioni su Villa Tre Colli.",
               alt="Villa Tre Colli al tramonto: piscina, fontana e terrazza illuminate"),
    "en": dict(kick_full="Villa Tre Colli &middot; Monterotondo, Rome", kick_mini="Villa Tre Colli", tit="Contact us on WhatsApp",
               p="For information, available dates and quotes, message us directly on WhatsApp: we will reply personally.",
               b="Message us on WhatsApp", n="Or call +39 333 849 5178", m="Hello, I would like some information about Villa Tre Colli.",
               alt="Villa Tre Colli at dusk: illuminated pool, fountain and terrace"),
}
CONTATTI = [("contactwp", "it"), ("contatti", "it"), ("en/contactwp", "en"), ("en/contact", "en")]
SERVIZI = [  # pagine di testo dove inserire l'invito a fine lettura
    ("la-villa", "it"), ("le-sale-di-villa-tre-colli", "it"), ("la-cucina-interna", "it"), ("lo-spazio-esterno", "it"),
    ("servizi-inclusi", "it"), ("matrimonio-a-villa-tre-colli", "it"), ("matrimonio-civile", "it"),
    ("battesimo-comunione-e-cresima-a-villa-tre-colli", "it"), ("compleanni-e-feste-a-tema", "it"), ("meeting-aziendali", "it"),
    ("catering-e-banqueting", "it"), ("animazione-e-musica", "it"), ("il-tunnel-dellamore", "it"), ("la-maison", "it"),
    ("location", "it"), ("villa-for-events", "it"),
    ("en/animation-and-music", "en"), ("en/baptisms-communions-and-confirmations-in-villa-tre-colli", "en"),
    ("en/birthdays-and-themed-parties", "en"), ("en/catering-banqueting", "en"), ("en/civil-wedding-in-villa-tre-colli", "en"),
    ("en/corporate-meetings", "en"), ("en/included-services", "en"), ("en/la-maison", "en"), ("en/location", "en"),
    ("en/outdoor-space", "en"), ("en/the-kitchen", "en"), ("en/the-tunnel-of-love", "en"), ("en/villa-for-events", "en"),
    ("en/villa-for-events-2", "en"), ("en/villa-tre-collis-halls", "en"), ("en/wedding-at-villa-tre-colli", "en"),
]
HERO = [("servizi-inclusi", "it"), ("en/included-services", "en")]

WA_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>')

CSS = (
    '<style id="vtc-lux-css">'
    '.vtc-hero{position:relative;margin:0 0 38px;border-radius:3px;overflow:hidden;box-shadow:0 22px 48px -18px rgba(0,0,0,.45)}'
    '.vtc-hero img{display:block;width:100%;height:clamp(230px,40vw,440px);object-fit:cover;object-position:50% 60%}'
    '.vtc-hero:after{content:"";position:absolute;inset:12px;border:1px solid rgba(230,207,155,.75);pointer-events:none}'
    '.vtc-lux{--g:#c9a96a;--g2:#e6cf9b;position:relative;clear:both;max-width:760px;margin:56px auto;padding:46px 34px 40px;text-align:center;'
    'color:#efe9db;background:radial-gradient(120% 140% at 50% 0%,#2b2d2f 0%,#1b1c1e 72%);border-radius:3px;box-shadow:0 26px 60px -24px rgba(0,0,0,.6)}'
    '.vtc-lux:before{content:"";position:absolute;inset:10px;border:1px solid rgba(201,169,106,.55);border-radius:2px;pointer-events:none}'
    '.vtc-lux:after{content:"";position:absolute;inset:16px;border:1px solid rgba(201,169,106,.16);pointer-events:none}'
    '.vtc-lux .vtc-orn{display:flex;align-items:center;justify-content:center;gap:14px;margin:0 auto 18px}'
    '.vtc-lux .vtc-orn i{display:block;width:64px;height:1px;background:linear-gradient(90deg,transparent,var(--g))}'
    '.vtc-lux .vtc-orn i+b+i{background:linear-gradient(270deg,transparent,var(--g))}'
    '.vtc-lux .vtc-orn b{display:block;width:7px;height:7px;background:var(--g);transform:rotate(45deg)}'
    '.vtc-lux .vtc-kick{margin:0 0 12px;font:600 12px/1.4 "PT Sans",Arial,sans-serif;letter-spacing:.34em;text-transform:uppercase;color:var(--g)}'
    '.vtc-lux h2.vtc-tit{margin:0 0 14px;padding:0;font:italic 400 clamp(27px,4.6vw,38px)/1.2 "Cormorant Garamond","Playfair Display",Georgia,"Times New Roman",serif;'
    'color:#fff;letter-spacing:.01em}'
    '.vtc-lux .vtc-txt{margin:0 auto 28px;max-width:540px;font:400 17px/1.75 Georgia,"Times New Roman",serif;color:#d9d2c1}'
    '.vtc-lux a.vtc-btn{display:inline-flex;align-items:center;gap:12px;padding:15px 34px;border:1px solid var(--g);color:#1b1c1e;'
    'background:linear-gradient(135deg,var(--g2),var(--g));font:700 13px/1 "PT Sans",Arial,sans-serif;letter-spacing:.2em;text-transform:uppercase;'
    'text-decoration:none;border-radius:2px;transition:transform .35s cubic-bezier(.22,.61,.36,1),box-shadow .35s ease,background .35s ease,color .35s ease}'
    '.vtc-lux a.vtc-btn svg{width:20px;height:20px;fill:currentColor;flex:none}'
    '.vtc-lux a.vtc-btn:hover,.vtc-lux a.vtc-btn:focus-visible{transform:translateY(-2px);box-shadow:0 12px 26px -10px rgba(201,169,106,.7);background:transparent;color:var(--g2)}'
    '.vtc-lux .vtc-tel{margin:24px 0 0;font:400 14px/1.4 "PT Sans",Arial,sans-serif;letter-spacing:.14em}'
    '.vtc-lux .vtc-tel a{color:#d9d2c1;text-decoration:none;border-bottom:1px solid rgba(201,169,106,.45);padding-bottom:3px;transition:color .3s ease,border-color .3s ease}'
    '.vtc-lux .vtc-tel a:hover{color:var(--g2);border-color:var(--g2)}'
    '.vtc-lux.vtc-mini{margin:54px auto 12px;padding:36px 30px 32px}'
    '.vtc-lux.vtc-mini .vtc-txt{font-style:italic;font-size:18px;margin-bottom:24px}'
    '@media (max-width:640px){.vtc-lux{margin:36px 10px;padding:40px 20px 34px}.vtc-lux.vtc-mini{margin:40px 10px 10px;padding:34px 20px 30px}'
    '.vtc-lux a.vtc-btn{padding:15px 22px;letter-spacing:.14em}.vtc-lux .vtc-orn i{width:42px}}'
    '@media (prefers-reduced-motion:reduce){.vtc-lux a.vtc-btn,.vtc-lux .vtc-tel a{transition:none}}'
    '</style>'
)


def href(d):
    return "https://wa.me/%s?text=%s" % (WA, quote(d["m"]))


def blocco_contatti(lang):
    d = TXT[lang]
    return ('<div id="vtc-whatsapp" class="vtc-lux"><div class="vtc-orn"><i></i><b></b><i></i></div>'
            '<p class="vtc-kick">%s</p><h2 class="vtc-tit">%s</h2><p class="vtc-txt">%s</p>'
            '<a class="vtc-btn" href="%s" target="_blank" rel="noopener">%s<span>%s</span></a>'
            '<p class="vtc-tel"><a href="tel:+%s">%s</a></p></div>') % (d["kick_full"], d["tit"], d["p"], href(d), WA_SVG, d["b"], WA, d["n"])


def blocco_cta(lang):
    d = TXT[lang]
    return ('<aside id="vtc-cta" class="vtc-lux vtc-mini"><div class="vtc-orn"><i></i><b></b><i></i></div>'
            '<p class="vtc-kick">%s</p><p class="vtc-txt">%s</p>'
            '<a class="vtc-btn" href="%s" target="_blank" rel="noopener">%s<span>%s</span></a>'
            '<p class="vtc-tel"><a href="tel:+%s">%s</a></p></aside>') % (d["kick_mini"], d["p"], href(d), WA_SVG, d["b"], WA, d["n"])


def blocco_hero(lang, depth):
    return '<figure class="vtc-hero"><img src="%s%s" alt="%s" width="900" height="900" decoding="async"></figure>' % ("../" * depth, IMG, TXT[lang]["alt"])


TOK = re.compile(r'<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<(/?)(?:div|aside)\b[^>]*>', re.S | re.I)


def fine_blocco(t, start):
    """indice di '</div>'/'</aside>' che chiude il blocco aperto in t[start]."""
    depth = 0
    for m in TOK.finditer(t, start):
        g = m.group(1)
        if g is None:
            continue
        if g == "":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return m.start(), m.end()
    return None


def leggi(rel):
    p = os.path.join(ROOT, *rel.split("/"), "index.html")
    if not os.path.exists(p):
        return p, None
    return p, open(p, encoding="utf-8", errors="surrogateescape", newline="").read()


def con_css(t):
    if 'id="vtc-lux-css"' in t:
        return re.sub(r'<style id="vtc-lux-css">.*?</style>', lambda m: CSS, t, count=1, flags=re.S)
    i = t.find("</head>")
    return t if i < 0 else t[:i] + CSS + t[i:]


stato = {}


def salva(p, t0, t1, etichetta):
    if t1 == t0:
        stato[etichetta] = stato.get(etichetta, 0)
        return
    stato[etichetta] = stato.get(etichetta, 0) + 1
    if APPLY:
        open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t1)


problemi = []
fatte = {}
# --- 1) pagine contatti
for rel, lang in CONTATTI:
    p, t = leggi(rel)
    if t is None:
        problemi.append(rel + ": non esiste"); continue
    a = t.find('<div id="vtc-whatsapp"')
    if a < 0:
        problemi.append(rel + ": blocco vtc-whatsapp non trovato"); continue
    e = fine_blocco(t, a)
    t1 = con_css(t[:a] + blocco_contatti(lang) + t[e[1]:])
    fatte.setdefault(p, [t, t1])[1] = t1

# --- 2) hero in Servizi inclusi (prima del post-content)
for rel, lang in HERO:
    p, t = leggi(rel)
    if t is None:
        problemi.append(rel + ": non esiste"); continue
    cur = fatte.get(p, [t, t])[1]
    depth = rel.count("/") + 1
    fig = blocco_hero(lang, depth)
    if 'class="vtc-hero"' in cur:
        cur = re.sub(r'<figure class="vtc-hero".*?</figure>', lambda m: fig, cur, count=1, flags=re.S)
    else:
        s = cur.find('<div class="fusion-flexslider fusion-flexslider-loading flexslider post-slideshow">')
        if s >= 0:
            e = fine_blocco(cur, s)
            cur = cur[:s] + fig + cur[e[1]:]
        else:
            i = cur.find('<div class="post-content">')
            if i < 0:
                problemi.append(rel + ": post-content non trovato (hero)"); continue
            cur = cur[:i] + fig + cur[i:]
    fatte[p] = [fatte.get(p, [t, t])[0], con_css(cur)]

# --- 3) invito a fine lettura nelle pagine di servizio
for rel, lang in SERVIZI:
    p, t = leggi(rel)
    if t is None:
        problemi.append(rel + ": non esiste"); continue
    cur = fatte.get(p, [t, t])[1]
    cta = blocco_cta(lang)
    a = cur.find('<aside id="vtc-cta"')
    if a >= 0:
        e = fine_blocco(cur, a)
        cur = cur[:a] + cta + cur[e[1]:]
    else:
        i = cur.find('<div class="post-content">')
        if i < 0:
            problemi.append(rel + ": post-content non trovato (cta)"); continue
        e = fine_blocco(cur, i)
        if e is None:
            problemi.append(rel + ": chiusura post-content non trovata"); continue
        cur = cur[:e[0]] + cta + cur[e[0]:]
    fatte[p] = [fatte.get(p, [t, t])[0], con_css(cur)]

n = 0
for p, (t0, t1) in fatte.items():
    if t1 != t0:
        n += 1
        if APPLY:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t1)
print("SCRITTO" if APPLY else "DRY-RUN (aggiungi --apply)")
print("pagine modificate:", n, "di", len(fatte))
for x in problemi:
    print("  !", x)
