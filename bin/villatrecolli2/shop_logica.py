"""Villa Tre Colli (villatrecolli2) - SHOP: struttura chiara + tutti i prodotti NON DISPONIBILI (shop non ancora pronto).

COSA FA (IT + EN, solo le pagine shop: negozio, en/shop, categorie, schede prodotto)
1) Elenchi (negozio, categorie): i bottoni 'Aggiungi al carrello' diventano l'etichetta 'Non disponibile' (<span class="vtc-nd">).
2) Scheda prodotto: il form carrello (quantita' + bottone) diventa un riquadro 'Non disponibile al momento' con invito a scrivere
   su WhatsApp per preventivo (<aside class="vtc-nd-box">). Nessun acquisto possibile.
3) Classi WooCommerce dei prodotti: instock -> outofstock, tolto 'purchasable' (coerente con il resto del tema/CSS).
4) Pagine elenco: blocco introduttivo <section class="vtc-shop-intro"> con titolo, descrizione, avviso 'shop in preparazione' e
   navigazione tra le categorie (Tutti / Servizi per eventi / Abiti da sposa) -> la categoria non e' piu' una pagina muta.
   Barra 'Sort by / Show 12 products' nascosta via CSS (con 1-4 prodotti non serve).
I PREZZI restano visibili (servono quando lo shop partira'): per nasconderli o metterli a 0 si cambia qui e si rilancia.

PUNTI CRITICI
- Gli slug NON si cambiano (categoria 'Servizi' = slug 'software', EN 'software-en'): sono ripetuti in 130+ pagine (menu, widget,
  link). Cambia solo l'etichetta visibile nel blocco introduttivo.
- File UTF-8 misto a byte cp1252: leggere/scrivere con errors='surrogateescape' e newline=''. Testo inserito = solo ASCII (entita' HTML).
- Idempotente: intro/box/etichette hanno marcatori e vengono sostituiti; i bottoni gia' trasformati non esistono piu' (nessun doppione).
- Per RIATTIVARE lo shop: ripristinare dal commit precedente a questo script (git revert) o rifare i bottoni; il checkout WooCommerce
  non funziona comunque sul mirror statico (nessun WordPress), quindi finche' non c'e' un vero shop i prodotti devono restare non disponibili.

Uso: python shop_logica.py [--apply]   (senza --apply = dry-run)"""
import os, re, sys

ROOT = r"C:\Users\Mirco\Desktop\repository\villatrecolli2"
APPLY = "--apply" in sys.argv
WA = "https://wa.me/393338495178?text="
TXT = {
    "it": dict(nd="Non disponibile", box_t="Non disponibile al momento",
               box_p="Lo shop &egrave; in preparazione e questo servizio non &egrave; ancora acquistabile online. Per informazioni e preventivi scrivici su WhatsApp: ti rispondiamo noi.",
               box_b="Scrivici su WhatsApp", msg="Buongiorno, vorrei informazioni sui servizi di Villa Tre Colli.",
               avviso="Shop in preparazione: i prodotti non sono ancora disponibili all&#8217;acquisto.", tutti="Tutti i prodotti", cat_serv="Servizi per eventi", cat_abiti="Abiti da sposa"),
    "en": dict(nd="Not available", box_t="Not available at the moment",
               box_p="The shop is being set up and this service cannot be purchased online yet. For information and quotes, message us on WhatsApp: we will reply personally.",
               box_b="Message us on WhatsApp", msg="Hello, I would like some information about the services of Villa Tre Colli.",
               avviso="Shop coming soon: products are not available for purchase yet.", tutti="All products", cat_serv="Event services", cat_abiti="Wedding dresses"),
}
# pagina elenco -> (lingua, titolo, descrizione, cartella relativa verso le altre pagine shop)
ELENCHI = {
    "negozio": ("it", "Lo shop di Villa Tre Colli", "Servizi e pacchetti per il vostro evento: catering, allestimenti, musica e fotografia, pi&ugrave; una selezione di abiti da sposa.", "negozio"),
    "categoria-prodotto/software": ("it", "Servizi per eventi", "Catering, allestimento tavola, musica dal vivo e DJ set, servizio fotografico: tutto quello che serve per rendere speciale il vostro evento a Villa Tre Colli.", "cat"),
    "categoria-prodotto/abiti-da-sposa": ("it", "Abiti da sposa", "Una selezione di abiti da sposa per il vostro giorno pi&ugrave; importante. Per vederli e provarli, scriveteci: vi accompagniamo noi.", "cat"),
    "en/shop": ("en", "The Villa Tre Colli shop", "Services and packages for your event: catering, table setting, music and photography, plus a selection of wedding dresses.", "negozio"),
    "en/categoria-prodotto/software-en": ("en", "Event services", "Catering, table setting, live music and DJ sets, photography: everything you need to make your event at Villa Tre Colli special.", "cat"),
    "en/categoria-prodotto/abiti-da-sposa": ("en", "Wedding dresses", "A selection of wedding dresses for your most important day. To see and try them on, write to us: we will guide you.", "cat"),
}
SCHEDE_IT = ["prodotto/" + d for d in ("abito-da-sposa-in-seta", "allestimento-tavola", "animazione-musicale", "catering", "pacchetto-fotografico")]
SCHEDE_EN = ["en/prodotto/" + d for d in ("abito-da-sposa-in-seta", "catering", "live-music-dj", "photo-package", "table-setting")]

CSS = ('<style id="vtc-shop-css">'
       '.catalog-ordering{display:none!important}'
       '.vtc-shop-intro{max-width:880px;margin:10px auto 34px;padding:30px 26px;text-align:center;border-top:1px solid #c9a96a;border-bottom:1px solid #c9a96a}'
       '.vtc-shop-intro h2{margin:0 0 12px;font:italic 400 clamp(26px,4.4vw,36px)/1.2 "Cormorant Garamond","Playfair Display",Georgia,serif;color:#212934}'
       '.vtc-shop-intro p{margin:0 auto 14px;max-width:640px;font:400 16px/1.7 Georgia,"Times New Roman",serif;color:#4a4a4a}'
       '.vtc-shop-intro p.vtc-avviso{display:inline-block;margin:6px 0 18px;padding:7px 16px;border:1px solid #c9a96a;color:#8a6d2f;'
       'font:700 12px/1.4 "PT Sans",Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase}'
       '.vtc-shop-intro nav{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}'
       '.vtc-shop-intro nav a{padding:9px 20px;border:1px solid #c9a96a;color:#212934;text-decoration:none;font:600 13px/1 "PT Sans",Arial,sans-serif;letter-spacing:.1em;text-transform:uppercase;transition:background .3s,color .3s}'
       '.vtc-shop-intro nav a:hover,.vtc-shop-intro nav a.on{background:#212934;color:#e6cf9b}'
       '.vtc-nd{display:inline-block;padding:9px 16px;border:1px solid #bbb;color:#777;background:#f4f4f4;font:600 13px/1 "PT Sans",Arial,sans-serif;letter-spacing:.06em;cursor:not-allowed}'
       '.vtc-nd-box{margin:24px 0;padding:22px 24px;border:1px solid #c9a96a;background:#faf7f0}'
       '.vtc-nd-box strong{display:block;margin-bottom:8px;font:700 15px/1.3 "PT Sans",Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#8a6d2f}'
       '.vtc-nd-box p{margin:0 0 14px;font:400 15px/1.65 Georgia,serif;color:#4a4a4a}'
       '.vtc-nd-box a{display:inline-block;padding:11px 24px;background:#212934;color:#e6cf9b;text-decoration:none;font:700 12px/1 "PT Sans",Arial,sans-serif;letter-spacing:.16em;text-transform:uppercase}'
       '.vtc-nd-box a:hover{background:#c9a96a;color:#212934}'
       '</style>')


def leggi(rel):
    p = os.path.join(ROOT, *rel.split("/"), "index.html")
    return p, (open(p, encoding="utf-8", errors="surrogateescape", newline="").read() if os.path.exists(p) else None)


def link_cat(lang, tipo):
    """(url_tutti, url_servizi, url_abiti) relativi alla posizione della pagina elenco."""
    if lang == "it":
        return ("../negozio/", "../categoria-prodotto/software/", "../categoria-prodotto/abiti-da-sposa/") if tipo == "negozio" else ("../../negozio/", "../software/", "../abiti-da-sposa/")
    return ("../shop/", "../categoria-prodotto/software-en/", "../categoria-prodotto/abiti-da-sposa/") if tipo == "negozio" else ("../../shop/", "../software-en/", "../abiti-da-sposa/")


def comune(t, lang):
    d = TXT[lang]
    n0 = t
    # 1) bottoni elenco -> etichetta
    t = re.sub(r'<a href="\?add-to-cart=\d+"[^>]*add_to_cart_button[^>]*>[^<]*</a>', '<span class="vtc-nd">%s</span>' % d["nd"], t)
    # 2) form carrello scheda -> riquadro
    box = ('<aside class="vtc-nd-box"><strong>%s</strong><p>%s</p><a href="%s%s" target="_blank" rel="noopener">%s</a></aside>'
           % (d["box_t"], d["box_p"], WA, __import__("urllib.parse").parse.quote(d["msg"]), d["box_b"]))
    t = re.sub(r'<aside class="vtc-nd-box">.*?</aside>', lambda m: box, t, flags=re.S)
    if 'class="vtc-nd-box"' not in t:
        t = re.sub(r'<form class="cart"[^>]*>.*?</form>', lambda m: box, t, count=1, flags=re.S)
    # 3) classi stock (solo dentro class="... type-product ...")
    def fix(m):
        c = m.group(0)
        if "type-product" not in c:
            return c
        c = re.sub(r"\binstock\b", "outofstock", c)
        return re.sub(r"\s+purchasable\b", "", c)
    t = re.sub(r'class="[^"]*"', fix, t)
    # 4) css
    if 'id="vtc-shop-css"' in t:
        t = re.sub(r'<style id="vtc-shop-css">.*?</style>', lambda m: CSS, t, count=1, flags=re.S)
    else:
        i = t.find("</head>")
        t = t if i < 0 else t[:i] + CSS + t[i:]
    return t


def intro(t, rel, lang, titolo, desc, tipo):
    d = TXT[lang]
    a, b, c = link_cat(lang, tipo)
    on = lambda u: ' class="on"' if (rel.endswith("software") or rel.endswith("software-en")) and u == b or rel.endswith("abiti-da-sposa") and u == c or rel in ("negozio", "en/shop") and u == a else ""
    blk = ('<section class="vtc-shop-intro"><h2>%s</h2><p>%s</p><p class="vtc-avviso">%s</p>'
           '<nav><a href="%s"%s>%s</a><a href="%s"%s>%s</a><a href="%s"%s>%s</a></nav></section>'
           % (titolo, desc, d["avviso"], a, on(a), d["tutti"], b, on(b), d["cat_serv"], c, on(c), d["cat_abiti"]))
    t = re.sub(r'<section class="vtc-shop-intro">.*?</section>', "", t, flags=re.S)
    k = t.find('<div class="woocommerce-notices-wrapper"></div>', t.find('id="main"'))
    if k < 0:
        return t, "punto di inserimento non trovato"
    k += len('<div class="woocommerce-notices-wrapper"></div>')
    return t[:k] + blk + t[k:], None


res = []
for rel, (lang, titolo, desc, tipo) in ELENCHI.items():
    p, t = leggi(rel)
    if t is None:
        res.append((rel, "NON ESISTE")); continue
    t1, err = intro(t, rel, lang, titolo, desc, tipo)
    if err:
        res.append((rel, "SALTATA: " + err)); continue
    t1 = comune(t1, lang)
    if t1 != t and APPLY:
        open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t1)
    res.append((rel, "ok" if t1 != t else "invariata"))
for lista, lang in ((SCHEDE_IT, "it"), (SCHEDE_EN, "en")):
    for rel in lista:
        p, t = leggi(rel)
        if t is None:
            res.append((rel, "NON ESISTE")); continue
        t1 = comune(t, lang)
        if t1 != t and APPLY:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t1)
        res.append((rel, "ok" if t1 != t else "invariata"))
print("SCRITTO" if APPLY else "DRY-RUN (aggiungi --apply)")
for rel, s in res:
    print("  %-48s %s" % (rel, s))
