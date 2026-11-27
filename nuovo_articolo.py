"""Crea articoli del blog (mirror Avada) clonando l'articolo modello e aggiornando elenco categoria + home.

USO: python nuovo_articolo.py [--dry-run]   (dalla radice della repo)
- Un articolo = una voce in ARTICOLI (slug, title, desc, excerpt, img, body). Idempotente: se la cartella esiste, salta.
- Crea classifiche/<slug>/index.html (clone del modello), le immagini ritagliate in wp-content/uploads/2026/11/,
  aggiunge la card in category/classifiche/index.html e nella home (index.html). La sitemap la rigenera il deploy.
- Il modello e' l'articolo "Le 5 Location..." (post 4286). Non modificarlo: serve come base.
"""
import os, re, sys, json, html, shutil
DRY = "--dry-run" in sys.argv
OLD_SLUG = "classifica-le-5-location-per-eventi-piu-prestigiose-a-monterotondo-roma"
OLD_TITLE = "Le 5 Location Più Belle per Eventi a Monterotondo"
OLD_DESC = "In questa classifica andremo alla scoperta delle migliori ville per eventi nel territorio di Monterotondo, a due passi da Roma."
OLD_STEM = "2024/07/villa-tre-colli-roma"
OLD_DATE = "Luglio 1st, 2024"
OLD_ISO = "2024-07-01T15:57:03+00:00"
OLD_ID = "4286"
ORIG = "https://www.villatrecolli.com"
MESI = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
CTA = """<h2>Parliamone di persona</h2>
<p>Ogni evento ha numeri e desideri diversi, per questo preferiamo costruire il preventivo insieme a te. Chiamaci al <a href="tel:+393338495178">333 849 5178</a> o scrivi a <a href="mailto:info@villatrecolli.com">info@villatrecolli.com</a>: ti aspettiamo a Villa Tre Colli, in Via Guerrazzi 103 a Monterotondo (Roma), per un sopralluogo senza impegno. Trovi anche la <a href="../../contactwp/">pagina contatti</a>.</p>"""

ARTICOLI = [
 dict(slug="quanto-costa-un-matrimonio-budget-roma-nord", id="4301", iso="2026-11-27T09:10:00+00:00", d=(27, 10, 2026),
  title="Quanto costa un matrimonio: budget reale e consigli (Roma nord)",
  desc="Quanto costa sposarsi oggi in Italia? Dati aggiornati, come si divide il budget e 6 modi concreti per risparmiare senza rinunciare alla festa.",
  excerpt="Quanto costa davvero sposarsi? Cifre aggiornate, come si divide il budget e sei consigli per tenere i costi sotto controllo.",
  img="2026/10/card-sale-hd.jpg", stem="blog-quanto-costa-matrimonio",
  body="""<h1>Quanto costa un matrimonio: budget reale e consigli (Roma nord)</h1>
<p>Sposarsi costa più di quanto si immagina il giorno della proposta. Secondo il Rapporto sul Settore Nuziale 2026 di Matrimonio.com, basato su oltre 3.100 coppie sposate nel 2025, in Italia si spendono in media 25.970 euro, il 9% in più dell’anno precedente. Per un matrimonio con circa 100 invitati si arriva a circa 238 euro a persona, e tre coppie su dieci superano i 30.000 euro.</p>
<h2>Dove va a finire il budget</h2>
<p>La voce più pesante è il ricevimento: tra location e pranzo o cena assorbe in genere più della metà del totale. Per il solo catering, le guide di settore indicano per i matrimoni una forbice che parte da circa 90 euro a persona e può superare i 150, a seconda di menu e servizio. Le stime di Federconsumatori per il 2026, che includono tutti i servizi per 100 invitati, vanno da circa 48.000 a oltre 118.000 euro: la distanza dipende quasi interamente dallo stile che scegli.</p>
<h2>Sei modi concreti per tenere i costi sotto controllo</h2>
<ul>
<li><strong>Parti dal numero di invitati.</strong> Ogni ospite in più pesa mediamente 238 euro: dieci invitati in meno significano circa 2.380 euro risparmiati.</li>
<li><strong>Scegli una location con i servizi dentro.</strong> Cucina interna, catering, allestimento e musica nello stesso posto evitano fornitori separati, noleggi e trasporti.</li>
<li><strong>Chiedi un preventivo “tutto compreso” per iscritto</strong>, con l’elenco di cosa è incluso (tavoli, sedie, tovagliato, personale, servizio).</li>
<li><strong>Cerimonia e ricevimento nello stesso luogo.</strong> Si evitano spostamenti e si riduce lo stress per gli ospiti.</li>
<li><strong>Valuta date e giorni meno richiesti.</strong> Chiedi sempre se ci sono condizioni diverse fuori dai weekend più ambiti.</li>
<li><strong>Tieni un margine per gli imprevisti.</strong> Mettere da parte circa il 10% del budget evita brutte sorprese all’ultimo.</li>
</ul>
<h2>E a Villa Tre Colli?</h2>
<p>Il costo dipende da numero di invitati, menu e servizi scelti, quindi preferiamo preparare un preventivo su misura dopo averti conosciuto. Alla villa trovi <a href="../../la-cucina-interna/">cucina interna</a>, <a href="../../catering-e-banqueting/">catering e banqueting</a>, <a href="../../animazione-e-musica/">animazione e musica</a>, <a href="../../lo-spazio-esterno/">spazio esterno</a> e il suggestivo <a href="../../il-tunnel-dellamore/">Tunnel dell’Amore</a>: tutto nello stesso luogo, per organizzare un <a href="../../matrimonio-a-villa-tre-colli/">matrimonio</a> senza rincorrere dieci fornitori.</p>
<p>Leggi anche: <a href="../come-scegliere-la-location-matrimonio-10-domande/">Come scegliere la location: 10 domande da fare prima del sopralluogo</a>.</p>
""" + CTA),
 dict(slug="come-scegliere-la-location-matrimonio-10-domande", id="4302", iso="2026-11-27T09:20:00+00:00", d=(27, 10, 2026),
  title="Come scegliere la location per il matrimonio: 10 domande",
  desc="10 domande da fare prima di prenotare la location per il matrimonio: capienza, piano B per la pioggia, cosa è incluso, orari, parcheggio e preventivo.",
  excerpt="Prima di prenotare un sopralluogo, ecco le 10 domande che ti evitano brutte sorprese: capienza, maltempo, servizi inclusi, orari e preventivo.",
  img="2026/10/card-sale.jpg", stem="blog-scegliere-location-matrimonio",
  body="""<h1>Come scegliere la location per il matrimonio: 10 domande da fare prima del sopralluogo</h1>
<p>La location è la scelta che condiziona tutte le altre: budget, numero di invitati, stile, perfino la data. Prima di dire sì a un sopralluogo (e soprattutto a una caparra) ecco le dieci domande che conviene fare a qualunque struttura.</p>
<h2>1. Quanti invitati ci stanno davvero comodi?</h2>
<p>Chiedi la capienza sia a sedere sia per l’aperitivo, e se cambia tra sala interna e spazi esterni.</p>
<h2>2. Si può celebrare la cerimonia sul posto?</h2>
<p>Cerimonia e ricevimento nello stesso luogo fanno risparmiare tempo e spostamenti. Chiedi dove si svolge e con quale allestimento.</p>
<h2>3. Cosa succede se piove?</h2>
<p>Un buon piano B coperto non è un dettaglio: pretendi di vederlo, non solo di sentirne parlare.</p>
<h2>4. Cucina interna o catering esterno?</h2>
<p>Con una cucina interna il menu si discute con chi lo prepara e il servizio è più semplice da coordinare. Chiedi se puoi assaggiare prima di decidere.</p>
<h2>5. Cosa è incluso nel prezzo?</h2>
<p>Tavoli, sedie, tovagliato, personale, allestimento di base, musica: fatti scrivere cosa c’è dentro e cosa è extra.</p>
<h2>6. Quali sono orari e limiti?</h2>
<p>Fino a che ora si può restare e fino a quando c’è la musica? Meglio saperlo prima di costruire la serata.</p>
<h2>7. Parcheggio e accessibilità?</h2>
<p>Pensa agli ospiti anziani, a chi ha difficoltà a camminare e ai bambini: verifica parcheggio, accessi e spazi.</p>
<h2>8. Quanto è facile da raggiungere per gli invitati?</h2>
<p>Valuta il percorso da Roma e dai paesi vicini: una location comoda mette tutti di buon umore.</p>
<h2>9. A che ora andare al sopralluogo?</h2>
<p>Se la cerimonia sarà nel tardo pomeriggio, vai alla stessa ora: capirai luce, atmosfera e temperatura reali.</p>
<h2>10. Preventivo, caparra e disdetta</h2>
<p>Chiedi tutto per iscritto: totale, acconti, scadenze e condizioni se la data cambia.</p>
<h2>Vieni a vedere Villa Tre Colli</h2>
<p>La villa sorge su una collina alle porte di Roma, a Monterotondo, con <a href="../../le-sale-di-villa-tre-colli/">sale interne</a>, <a href="../../lo-spazio-esterno/">spazio esterno</a>, <a href="../../la-cucina-interna/">cucina interna</a> e <a href="../../servizi-inclusi/">servizi inclusi</a>. Il modo migliore per giudicare è vederla dal vivo: porta con te questa lista.</p>
<p>Leggi anche: <a href="../quanto-costa-un-matrimonio-budget-roma-nord/">Quanto costa un matrimonio: budget reale e consigli</a>.</p>
""" + CTA),
 dict(slug="festa-comunione-cresima-battesimo-come-organizzarla", id="4303", iso="2026-11-27T09:30:00+00:00", d=(27, 10, 2026),
  title="Festa di comunione, cresima o battesimo: come organizzarla",
  desc="Come organizzare la festa di comunione, cresima o battesimo a Roma nord: quando prenotare, invitati, menu bimbi, animazione, torta e budget.",
  excerpt="Quando prenotare, come gestire invitati, menu per grandi e piccoli, animazione e budget: la guida per una festa serena.",
  img="2026/10/card-battesimo.jpg", stem="blog-festa-comunione-cresima-battesimo",
  body="""<h1>Festa di comunione, cresima o battesimo: come organizzarla senza stress</h1>
<p>Comunione, cresima e battesimo sono giornate in cui conta tanto la cerimonia quanto la festa che segue. Con un po’ di organizzazione il pranzo diventa un bel ricordo per tutta la famiglia, bambini compresi. Ecco da dove partire.</p>
<h2>Prenota appena hai la data</h2>
<p>Le date vicine alle celebrazioni religiose sono quelle più richieste: appena la parrocchia comunica il giorno, contatta la location e chiedi la disponibilità. Più aspetti, meno scelta hai.</p>
<h2>Fai la lista degli invitati prima del resto</h2>
<p>Il numero di ospiti decide sala, menu e budget. Separa adulti e bambini: i menu e i costi possono essere diversi, e chiedere un prezzo per ciascuna categoria evita sorprese.</p>
<h2>Pensa ai bambini</h2>
<p>Una festa con tanti piccoli ospiti funziona meglio se c’è qualcosa da fare: giochi, animazione, spazi aperti dove correre in sicurezza. Alla villa trovi <a href="../../animazione-e-musica/">animazione e musica</a> e uno <a href="../../lo-spazio-esterno/">spazio esterno</a> immerso nel verde.</p>
<h2>Menu per grandi e piccoli</h2>
<p>Con una <a href="../../la-cucina-interna/">cucina interna</a> puoi concordare un menu che accontenti sia i nonni sia i più piccoli, con opzioni per allergie e intolleranze. Chiedi sempre cosa è compreso.</p>
<h2>Orari, torta e dettagli</h2>
<ul>
<li>Concorda l’orario di arrivo tenendo conto della cerimonia in chiesa.</li>
<li>Decidi chi porta torta e bomboniere e quando consegnarle.</li>
<li>Scegli un tema per l’allestimento e chiedi se la location può occuparsene.</li>
<li>Fissa il momento della torta e delle foto di gruppo, quando i bambini sono ancora riposati.</li>
</ul>
<h2>Il budget</h2>
<p>Chiedi un preventivo scritto con il costo per adulto e per bambino e l’elenco dei servizi inclusi. Così puoi confrontare davvero le proposte e non solo i prezzi finali.</p>
<h2>A Villa Tre Colli</h2>
<p>Organizziamo feste di <a href="../../battesimo-comunione-e-cresima-a-villa-tre-colli/">battesimo, comunione e cresima</a> a Monterotondo, a pochi minuti da Roma, con servizio completo dal ricevimento al <a href="../../catering-e-banqueting/">catering</a>.</p>
<p>Leggi anche: <a href="../festa-18-anni-compleanni-a-tema-idee-consigli/">Festa di 18 anni e compleanni a tema</a>.</p>
""" + CTA),
 dict(slug="festa-18-anni-compleanni-a-tema-idee-consigli", id="4304", iso="2026-11-27T09:40:00+00:00", d=(27, 10, 2026),
  title="Festa di 18 anni e compleanni a tema: idee e consigli",
  desc="Idee e consigli per organizzare una festa di 18 anni o un compleanno a tema a Roma nord: musica, animazione, spazio esterno, torta e budget.",
  excerpt="Dal tema alla musica, dalla torta agli spazi all’aperto: come organizzare una festa di 18 anni o un compleanno che nessuno dimentica.",
  img="2026/10/card-compleanni.jpg", stem="blog-festa-18-anni-compleanni",
  body="""<h1>Festa di 18 anni e compleanni a tema: idee e consigli per organizzarli</h1>
<p>Il diciottesimo è una di quelle feste che si ricordano per sempre; un compleanno a tema, per grandi o piccoli, può diventare l’evento dell’anno. La differenza la fanno la scelta del luogo e qualche decisione presa per tempo.</p>
<h2>Scegli il tema (e rispettalo nei dettagli)</h2>
<p>Un tema chiaro guida tutto: allestimento, musica, dress code, torta. Anni 2000, cinema, estate, bianco e oro: l’importante è che il festeggiato lo senta suo. Chiedi alla location se può occuparsi dell’allestimento.</p>
<h2>La musica fa la serata</h2>
<p>Per un diciottesimo scegli DJ o musica dal vivo in base ai gusti degli invitati. Alla villa il servizio di <a href="../../animazione-e-musica/">animazione e musica</a> aiuta a costruire la scaletta della festa, dall’arrivo degli ospiti al taglio della torta.</p>
<h2>Spazi all’aperto per muoversi liberi</h2>
<p>Un giardino o un’area esterna rende la festa più leggera: aperitivo, foto, giochi e chiacchiere si distribuiscono meglio. A Villa Tre Colli c’è lo <a href="../../lo-spazio-esterno/">spazio esterno</a> immerso nel verde, oltre alle <a href="../../le-sale-di-villa-tre-colli/">sale</a> per la parte più raccolta.</p>
<h2>Cena servita o buffet?</h2>
<p>Dipende dal clima della serata: la cena seduta dà ordine e occasione per i discorsi, il buffet più libertà. Con la <a href="../../la-cucina-interna/">cucina interna</a> si può costruire un menu su misura.</p>
<h2>Compleanni dei più piccoli</h2>
<p>Per i bambini conta il divertimento: giochi all’aperto, animazione, un tema che li appassioni e una torta scenografica. Scopri le nostre <a href="../../compleanni-e-feste-a-tema/">feste di compleanno e feste a tema</a>.</p>
<h2>Cosa chiedere nel preventivo</h2>
<ul>
<li>Costo per persona e durata della festa.</li>
<li>Cosa comprende (allestimento, musica, servizio, torta).</li>
<li>Orari di inizio e fine, e regole sulla musica.</li>
<li>Numero minimo e massimo di invitati.</li>
</ul>
<p>Leggi anche: <a href="../festa-comunione-cresima-battesimo-come-organizzarla/">Festa di comunione, cresima o battesimo: come organizzarla</a>.</p>
""" + CTA),
]

def ordinale(n):
    return "%dth" % n if 10 <= n % 100 <= 20 else "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def make_images(a):
    src = os.path.join("wp-content", "uploads", *a["img"].split("/"))
    dst_dir = os.path.join("wp-content", "uploads", "2026", "11")
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if DRY: return Image is not None
    os.makedirs(dst_dir, exist_ok=True)
    if Image is None:
        shutil.copy(src, os.path.join(dst_dir, a["stem"] + ".jpg")); return False
    im = Image.open(src).convert("RGB")
    def crop(w, h, name):
        sc = max(w / im.width, h / im.height)
        r = im.resize((max(w, round(im.width * sc)), max(h, round(im.height * sc))))
        x, y = (r.width - w) // 2, (r.height - h) // 2
        r.crop((x, y, x + w, y + h)).save(os.path.join(dst_dir, name), "JPEG", quality=85)
    crop(900, 900, a["stem"] + ".jpg")
    for w, h in [(200, 200), (400, 400), (600, 600), (800, 800), (669, 272)]:
        crop(w, h, "%s-%dx%d.jpg" % (a["stem"], w, h))
    return True

def trasforma(t, a, variants):
    e = lambda x: html.escape(x, quote=False).replace('"', "&quot;")
    date_it = "%s %s, %d" % (MESI[a["d"][1]].capitalize(), ordinale(a["d"][0]), a["d"][2])
    t = t.replace(OLD_SLUG, a["slug"]).replace(OLD_TITLE, e(a["title"])).replace(OLD_DESC, e(a["desc"]))
    t = t.replace(OLD_DATE, date_it).replace(OLD_ISO, a["iso"])
    t = re.sub(r"(?<!\d)%s(?!\d)" % OLD_ID, a["id"], t)
    new = "2026/11/" + a["stem"]
    if variants:
        t = t.replace(OLD_STEM, new)
    else:
        t = re.sub(re.escape(OLD_STEM) + r"-\d+x\d+\.jpg", new + ".jpg", t).replace(OLD_STEM, new)
    return t.replace('data-title="villa tre colli roma"', 'data-title="%s"' % e(a["title"]))

def crea_pagina(T, a, variants):
    t = trasforma(T, a, variants)
    # corpo
    m = re.search(r'(<div class="post-content">\n\t\t\t\t)<h1>.*?(\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="fusion-meta-info">)', t, re.S)
    assert m, "corpo non trovato"
    t = t[:m.start()] + m.group(1) + a["body"].rstrip("\n") + m.group(2) + t[m.end():]
    # JSON-LD (slash escapati: il deploy non li tocca)
    url = "%s/classifiche/%s/" % (ORIG, a["slug"]); img = "%s/wp-content/uploads/2026/11/%s.jpg" % (ORIG, a["stem"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": ORIG + "/#website", "url": ORIG + "/", "name": "Villa Tre Colli ®", "inLanguage": "it-IT"},
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": a["title"] + " - Villa Tre Colli ®", "isPartOf": {"@id": ORIG + "/#website"},
         "datePublished": a["iso"], "dateModified": a["iso"], "description": a["desc"], "inLanguage": "it-IT"},
        {"@type": "Article", "@id": url + "#article", "isPartOf": {"@id": url + "#webpage"}, "mainEntityOfPage": {"@id": url + "#webpage"},
         "headline": a["title"], "datePublished": a["iso"], "dateModified": a["iso"], "image": img,
         "publisher": {"@type": "Organization", "name": "Villa Tre Colli ®", "telephone": "+39 333 849 5178"}, "inLanguage": "it-IT"}]}
    js = json.dumps(ld, ensure_ascii=True).replace("/", "\\/")
    t, n = re.subn(r'(<script type="application/ld\+json"[^>]*>).*?(</script>)', lambda m_: m_.group(1) + js + m_.group(2), t, count=1, flags=re.S)
    assert n == 1, "json-ld"
    # og:image + og:description
    extra = ''
    if 'property="og:image"' not in t: extra += '<meta property="og:image" content="%s" />\n' % img
    if 'property="og:description"' not in t: extra += '<meta property="og:description" content="%s" />\n' % html.escape(a["desc"], quote=True)
    k = t.find('<meta property="og:url"')
    assert k > 0, "og:url"
    t = t[:k] + extra + t[k:]
    return t

def card(blk, a, variants):
    b = trasforma(blk, a, variants)
    return re.sub(r'(<div class="fusion-post-content-container">\s*<p>).*?(</p>)', lambda m: m.group(1) + html.escape(a["excerpt"], quote=False) + m.group(2), b, count=1, flags=re.S)

def inserisci(path, starts, blk_re, a, variants):
    s = open(path, encoding="utf-8", newline="").read()
    if a["slug"] in s: return "gia' presente"
    m = re.search(blk_re, s, re.S); assert m, "card modello in " + path
    new = card(m.group(0), a, variants)
    i = s.find(starts); assert i > 0
    if not DRY: open(path, "w", encoding="utf-8", newline="").write(s[:i] + new + "\n" + s[i:])
    return "ok"

if __name__ == "__main__":
    base = os.path.join("classifiche", OLD_SLUG, "index.html")
    T = open(base, encoding="utf-8", newline="").read()
    for a in ARTICOLI:
        d = os.path.join("classifiche", a["slug"])
        if os.path.isdir(d): print("salto (esiste):", a["slug"]); continue
        v = make_images(a)
        if not DRY:
            os.makedirs(d); open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="").write(crea_pagina(T, a, v))
        print("pagina", a["slug"], "- immagini ritagliate:", v,
              "| categoria:", inserisci(os.path.join("category", "classifiche", "index.html"), '<article id="post-', r'<article id="post-%s".*?</article>' % OLD_ID, a, v),
              "| home:", inserisci("index.html", '<article id="blog-1-post-', r'<article id="blog-1-post-%s".*?</article>' % OLD_ID, a, v))
