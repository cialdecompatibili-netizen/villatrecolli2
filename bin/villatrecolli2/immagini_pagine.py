"""Villa Tre Colli (villatrecolli2) - FOTO nelle pagine di servizio che ne sono prive (IT + EN).

COSA FA
1) HERO: in cima al testo una foto grande con cornice oro (classe vtc-hero). Se la pagina ha lo slider Avada VUOTO
   (<div class="fusion-flexslider ... post-slideshow"> con <img src="">), lo sostituisce; altrimenti la mette prima di post-content.
2) FOTO A META' TESTO (classe vtc-fig): dopo il paragrafo piu' vicino a meta' del testo (solo se la mappa ne prevede una).
Le foto sono scelte A MANO per tema nella mappa PAGINE qui sotto (nessuna casualita'): per cambiare una foto basta cambiare
il percorso (relativo a wp-content/uploads) e rilanciare con --apply.

PUNTI CRITICI
- File del sito: UTF-8 MISTO a byte cp1252 (si vedono come '?' nelle accentate): leggere/scrivere con errors='surrogateescape' e
  newline='' (cosi' i byte e gli a-capo restano identici). Il testo inserito qui e' solo ASCII (entita' HTML per gli accenti).
- Idempotente: i blocchi hanno marcatori (vtc-hero / vtc-fig / style#vtc-img-css) e rilanciando vengono sostituiti, mai duplicati.
- Misura immagine: sceglie la variante gia' ridimensionata (NOME-1200x900.jpg) piu' vicina a ~1200 px; se non esiste usa l'originale
  solo se pesa < 350 KB. Cosi' le pagine non diventano pesanti (non scarica nulla, usa solo i file gia' nella repo).
- Percorsi RELATIVI (../ per ogni livello): come le altre immagini del mirror. Il CSS e' in un solo <style id="vtc-img-css"> nel <head>.
- NON toccare i blocchi WhatsApp (luxury_whatsapp.py): questo script non li modifica.

Uso: python immagini_pagine.py [--apply]    (senza --apply = dry-run: stampa cosa farebbe)"""
import os, re, sys

ROOT = r"C:\Users\Mirco\Desktop\repository\villatrecolli2"
UP = os.path.join(ROOT, "wp-content", "uploads")
APPLY = "--apply" in sys.argv

# ---- MAPPA: pagina -> (hero, fig). Ogni foto = (percorso in uploads, alt IT, alt EN). fig puo' essere None.
V = "2025/06/"
FOTO = {
    "tramonto":   ("2024/07/villa-tre-colli-roma.jpg", "Villa Tre Colli al tramonto: piscina, fontana e terrazza illuminate", "Villa Tre Colli at dusk: illuminated pool, fountain and terrace"),
    "piscina_sera": (V + "480378654_2635388993314358_6863031252597421525_n.jpg", "La piscina di Villa Tre Colli al tramonto, con la statua e le luci", "The pool at Villa Tre Colli at sunset, with the statue and soft lights"),
    "piscina_giorno": (V + "504885294_2744204625766127_548432150261417415_n.jpg", "La piscina di Villa Tre Colli con gli ombrelloni e la terrazza", "The pool at Villa Tre Colli with parasols and the terrace"),
    "fontana":    (V + "480268121_2634771646709426_3833008680700077021_n.jpg", "Il giardino con la fontana e il prato curato di Villa Tre Colli", "The garden with the fountain and the manicured lawn of Villa Tre Colli"),
    "tunnel":     (V + "479251685_2631911450328779_6419799193491099283_n.jpg", "Il Tunnel dell'amore di Villa Tre Colli, un viale di fiori e piante", "The Tunnel of Love at Villa Tre Colli, an avenue of flowers and plants"),
    "gelsomino":  (V + "480198543_2635394163313841_7477218362186893016_n.jpg", "Il passaggio fiorito di gelsomino con la scalinata", "The flowering jasmine archway with its stairway"),
    "cerimonia":  (V + "486220226_2666297070223550_7286773552908198325_n.jpg", "La sala per la cerimonia con il tavolo degli sposi decorato di fiori", "The ceremony hall with the couple's table decorated with flowers"),
    "giardino_cerimonia": ("2024/03/matrimonio-civile-home.jpg", "La cerimonia civile nel giardino di Villa Tre Colli, con l'arco di fiori", "The civil ceremony in the garden of Villa Tre Colli, with the flower arch"),
    "sala_tavoli": (V + "495654578_2716124255240831_3603234743885722183_n.jpg", "La sala ricevimenti apparecchiata con eleganza", "The reception hall elegantly set"),
    "tavolo":     (V + "tavolo.jpg", "Il grande tavolo imperiale apparecchiato nella sala", "The large imperial table set in the hall"),
    "sala_rosa":  (V + "sala-rosa.jpg", "La sala di Villa Tre Colli illuminata per la festa", "The hall at Villa Tre Colli lit up for the party"),
    "terrazza":   ("2026/10/card-meeting.jpg", "La terrazza di Villa Tre Colli al tramonto", "The terrace at Villa Tre Colli at sunset"),
    "buffet":     ("2024/07/catering.jpg", "Il buffet di Villa Tre Colli: antipasti e piatti curati nei dettagli", "The buffet at Villa Tre Colli: starters and dishes prepared in every detail"),
    "staff":      (V + "494136555_2704394273080496_7322322242449331918_n.jpg", "Lo staff di sala di Villa Tre Colli", "The dining room staff of Villa Tre Colli"),
    "animazione": ("2026/10/card-animazione.jpg", "Animazione e giochi per i piu' piccoli", "Entertainment and games for the little ones"),
    "aerea":      (V + "506761845_9753675204742994_6720137305750527035_n.jpg", "Veduta dall'alto di Villa Tre Colli con la piscina", "Aerial view of Villa Tre Colli with the pool"),
    "collina":    (V + "506849494_9753675234742991_9197460533639280085_n.jpg", "Villa Tre Colli sulla collina, immersa nel verde", "Villa Tre Colli on its hill, surrounded by greenery"),
    "scalinata":  ("2024/03/home-hero-bg-sfilata-scaledx2.jpg", "La scalinata illuminata di Villa Tre Colli di sera", "The illuminated staircase of Villa Tre Colli in the evening"),
    "spazio_est": ("2024/04/spazio-esterno-villa-tre-colli.jpg", "Villa Tre Colli all'imbrunire con il giardino e la terrazza", "Villa Tre Colli at dusk with the garden and the terrace"),
}
# pagina IT -> (hero, fig) ; la pagina EN corrispondente sta in EN
PAGINE = {
    "servizi-inclusi":              ("tramonto", "cerimonia"),
    "matrimonio-a-villa-tre-colli": ("piscina_sera", "fontana"),
    "matrimonio-civile":            ("cerimonia", "giardino_cerimonia"),
    "battesimo-comunione-e-cresima-a-villa-tre-colli": ("sala_tavoli", "tavolo"),
    "compleanni-e-feste-a-tema":    ("sala_rosa", "piscina_giorno"),
    "meeting-aziendali":            ("tavolo", "terrazza"),
    "catering-e-banqueting":        ("buffet", "staff"),
    "animazione-e-musica":          ("sala_rosa", "animazione"),
    "il-tunnel-dellamore":          ("tunnel", "gelsomino"),
    "la-maison":                    ("scalinata", None),
    "location":                     ("aerea", None),
    "villa-for-events":             ("collina", "spazio_est"),
}
EN = {
    "servizi-inclusi": "en/included-services", "matrimonio-a-villa-tre-colli": "en/wedding-at-villa-tre-colli",
    "matrimonio-civile": "en/civil-wedding-in-villa-tre-colli",
    "battesimo-comunione-e-cresima-a-villa-tre-colli": "en/baptisms-communions-and-confirmations-in-villa-tre-colli",
    "compleanni-e-feste-a-tema": "en/birthdays-and-themed-parties", "meeting-aziendali": "en/corporate-meetings",
    "catering-e-banqueting": "en/catering-banqueting", "animazione-e-musica": "en/animation-and-music",
    "il-tunnel-dellamore": "en/the-tunnel-of-love", "la-maison": "en/la-maison", "location": "en/location",
    "villa-for-events": "en/villa-for-events",
}

CSS = (
    '<style id="vtc-img-css">'
    '.vtc-hero{position:relative;margin:0 0 38px;border-radius:3px;overflow:hidden;box-shadow:0 22px 48px -18px rgba(0,0,0,.45)}'
    '.vtc-hero img{display:block;width:100%;height:clamp(230px,40vw,440px);object-fit:cover;object-position:50% 60%}'
    '.vtc-hero:after{content:"";position:absolute;inset:12px;border:1px solid rgba(230,207,155,.75);pointer-events:none}'
    '.vtc-fig{position:relative;clear:both;margin:40px auto;max-width:100%;border-radius:3px;overflow:hidden;box-shadow:0 18px 40px -20px rgba(0,0,0,.5)}'
    '.vtc-fig img{display:block;width:100%;height:auto}'
    '.vtc-fig:after{content:"";position:absolute;inset:10px;border:1px solid rgba(230,207,155,.7);pointer-events:none}'
    '@media (max-width:640px){.vtc-hero{margin-bottom:26px}.vtc-fig{margin:28px auto}.vtc-fig:after{inset:7px}}'
    '</style>'
)

TOK = re.compile(r'<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<(/?)(?:div|aside)\b[^>]*>', re.S | re.I)


def fine_blocco(t, start):
    """(inizio, fine) del '</div>' che chiude il div aperto in t[start]; conta i div annidati e salta script/style/commenti."""
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


def scegli(rel):
    """Percorso (relativo a uploads) della variante migliore: ~1200 px se esiste, altrimenti l'originale se leggero."""
    d, f = os.path.split(rel)
    stem, ext = os.path.splitext(f)
    folder = os.path.join(UP, *d.split("/"))
    best = None
    for n in os.listdir(folder):
        m = re.fullmatch(re.escape(stem) + r"-(\d+)x(\d+)" + re.escape(ext), n)
        if m:
            w = int(m.group(1))
            if best is None or abs(w - 1200) < abs(best[0] - 1200):
                best = (w, n)
    orig = os.path.join(folder, f)
    peso = os.path.getsize(orig) // 1024 if os.path.exists(orig) else 10**9
    if best and (peso >= 350 or best[0] >= 1000):
        return d + "/" + best[1]
    return rel


def dimensioni(rel):
    try:
        from PIL import Image
        with Image.open(os.path.join(UP, *rel.split("/"))) as im:
            return im.size
    except Exception:
        return (None, None)


def img_tag(chiave, lang, depth, eager):
    rel, alt_it, alt_en = FOTO[chiave]
    sel = scegli(rel)
    w, h = dimensioni(sel)
    dim = (' width="%d" height="%d"' % (w, h)) if w else ""
    alt = (alt_it if lang == "it" else alt_en).replace('"', "&quot;").replace("'", "&#8217;")
    ld = 'decoding="async"' + ("" if eager else ' loading="lazy"')
    return '<img src="%swp-content/uploads/%s" alt="%s"%s %s>' % ("../" * depth, sel, alt, dim, ld), sel


def leggi(rel):
    p = os.path.join(ROOT, *rel.split("/"), "index.html")
    if not os.path.exists(p):
        return p, None
    return p, open(p, encoding="utf-8", errors="surrogateescape", newline="").read()


def con_css(t):
    if 'id="vtc-img-css"' in t:
        return re.sub(r'<style id="vtc-img-css">.*?</style>', lambda m: CSS, t, count=1, flags=re.S)
    i = t.find("</head>")
    return t if i < 0 else t[:i] + CSS + t[i:]


def applica(t, hero, fig, lang, depth):
    """Ritorna (nuovo_testo, errore|None)."""
    i = t.find('<div class="post-content">')
    if i < 0:
        return t, "post-content non trovato"
    # 0) pulizia: via vecchi blocchi (idempotenza)
    t = re.sub(r'<figure class="vtc-fig".*?</figure>', "", t, flags=re.S)
    tag, _ = img_tag(hero, lang, depth, True)
    figure = '<figure class="vtc-hero">%s</figure>' % tag
    if 'class="vtc-hero"' in t:
        t = re.sub(r'<figure class="vtc-hero".*?</figure>', lambda m: figure, t, count=1, flags=re.S)
    else:
        s = t.find('<div class="fusion-flexslider fusion-flexslider-loading flexslider post-slideshow">', max(0, i - 3000), i + 50)
        if s >= 0:
            e = fine_blocco(t, s)
            if e is None:
                return t, "slider non chiuso"
            t = t[:s] + figure + t[e[1]:]
        else:
            t = t[:i] + figure + t[i:]
    # 1) foto a meta' testo: dopo il </p> piu' vicino al centro dei paragrafi di post-content (prima dell'invito WhatsApp)
    if fig:
        i = t.find('<div class="post-content">')
        fin = t.find('<aside id="vtc-cta"', i)
        if fin < 0:
            fin = fine_blocco(t, i)[0]
        fine_p = [m.end() for m in re.finditer(r"</p>", t[i:fin])]
        if len(fine_p) >= 3:
            pos = i + fine_p[len(fine_p) // 2 - 1]
            tag2, _ = img_tag(fig, lang, depth, False)
            t = t[:pos] + '\n<figure class="vtc-fig">%s</figure>' % tag2 + t[pos:]
        else:
            # PUNTO CRITICO: pagina fatta di elenco (<ul>) e pochi <p> (es. servizi-inclusi): dentro un <ul> una figura
            # sarebbe HTML non valido, quindi la foto va in fondo al testo, subito prima dell'invito WhatsApp.
            tag2, _ = img_tag(fig, lang, depth, False)
            t = t[:fin] + '<figure class="vtc-fig">%s</figure>\n' % tag2 + t[fin:]
    return con_css(t), None


riepilogo = []
for it, (hero, fig) in PAGINE.items():
    for rel, lang in ((it, "it"), (EN.get(it), "en")):
        if not rel:
            continue
        p, t = leggi(rel)
        if t is None:
            riepilogo.append((rel, "NON ESISTE")); continue
        depth = rel.count("/") + 1
        t1, err = applica(t, hero, fig, lang, depth)
        stato = "ok" if t1 != t else "invariata"
        if err:
            stato += " (" + err + ")"
            if "pochi paragrafi" in err:
                t1 = con_css(t1)  # hero comunque inserito
            else:
                riepilogo.append((rel, "SALTATA: " + err)); continue
        if t1 != t and APPLY:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t1)
        riepilogo.append((rel, stato))

print("SCRITTO" if APPLY else "DRY-RUN (aggiungi --apply per scrivere)")
for rel, s in riepilogo:
    print("  %-62s %s" % (rel, s))
