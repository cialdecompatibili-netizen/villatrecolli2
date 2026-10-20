#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nuovo.py - aggiunge contenuti a servizi.lazio con UNA chiamata (articolo, categoria) e pubblica.

USO (dalla cartella della repo, o da qualunque posto):

  Articolo con testo da file (HTML, oppure testo semplice con righe vuote tra i paragrafi e "# Titolo" per i sottotitoli):
    python bin/nuovo.py articolo --titolo "Preventivi stampa 3D" --cat servizi/stampa-3d --sezione servizi-alle-aziende/stampa-3d --file testo.html --desc "Descrizione SEO"

  Opzioni utili:
    --cat2 servizi/servizi-alle-aziende   categoria padre aggiuntiva (di default se la categoria ha 3 livelli aggiunge il padre da sola)
    --immagine foto.jpg                   immagine in evidenza (se manca ne viene generata una con il titolo)
    --sezione dir/sottodir                cartella dell'articolo = parte dell'URL (default: dalla categoria)
    --no-push                             crea i file e basta (niente commit/push/verifica)
    --file -                              legge il testo da stdin

  Categoria nuova (pagina elenco + voce nella barra laterale):
    python bin/nuovo.py categoria --slug servizi/servizi-ai-cittadini/ripetizioni --nome "Ripetizioni"

  Controllo (categorie vuote, ultimo wp_id):
    python bin/nuovo.py stato

Cosa fa da solo: slug dal titolo, wp_id progressivo, data nel PASSATO (Jekyll non pubblica le date future),
miniature 66x66 e 320x202, front matter completo, commit, push su main, attesa del deploy, verifica che la
pagina e la sitemap rispondano. Le categorie vuote restano fuori dalla sitemap (noindex automatico).
"""
import argparse, datetime, glob, io, json, os, re, shutil, subprocess, sys, time, unicodedata, urllib.request

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(R)
LAZIO = os.path.join("_avada", "_lazio")
CATD = os.path.join("_avada", "_categorie")
CATYML = os.path.join("_avada", "_data", "categorie.yml")
SITO = "https://servizi.lazio.it"  # dominio proprio (file CNAME); l'anteprima github.io non esiste piu'
if os.path.isfile("CNAME"):
    SITO = "https://" + open("CNAME").read().strip()


def log(*a):
    print(*[str(x).encode("ascii", "replace").decode() for x in a])


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit("ERRORE comando: %s\n%s%s" % (cmd, r.stdout, r.stderr))
    return (r.stdout + r.stderr).strip()


def scrivi(path, testo):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)


def prossimo_wp_id():
    mx = 9100
    for p in glob.glob(os.path.join("_avada", "**", "*.html"), recursive=True):
        with io.open(p, encoding="utf-8", errors="ignore") as f:
            head = f.read(3000)
        m = re.search(r"^wp_id:\s*\"?(\d+)", head, re.M)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def q(v):
    return json.dumps(v, ensure_ascii=False)


def corpo_html(testo):
    if "<" in testo:
        return testo
    out = []
    testo = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", testo)
    for blocco in re.split(r"\n\s*\n", testo.strip()):
        blocco = blocco.strip()
        if blocco.startswith("# "):
            out.append("<h2>%s</h2>" % blocco[2:].strip())
        else:
            out.append("<p>%s</p>" % blocco.replace("\n", " "))
    return "\n".join(out) + "\n"


def immagini(slug, titolo, sorgente, adesso):
    from PIL import Image, ImageDraw, ImageFont
    cart = os.path.join("wp-content", "uploads", "%04d" % adesso.year, "%02d" % adesso.month)
    os.makedirs(cart, exist_ok=True)
    if sorgente:
        im = Image.open(sorgente).convert("RGB")
    else:
        W, H = 1280, 960
        im = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(im)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=(31 + int(y / H * 40), 58 + int(y / H * 30), 95 + int(y / H * 50)))
        try:
            f1 = ImageFont.truetype("arialbd.ttf", 84)
        except Exception:
            f1 = ImageFont.load_default()
        righe, riga = [], ""
        for parola in titolo.split():
            if d.textlength((riga + " " + parola).strip(), font=f1) > W - 160 and riga:
                righe.append(riga); riga = parola
            else:
                riga = (riga + " " + parola).strip()
        righe.append(riga)
        y0 = (H - len(righe) * 110) // 2
        for i, r_ in enumerate(righe[:5]):
            w = d.textlength(r_, font=f1)
            d.text(((W - w) / 2, y0 + i * 110), r_, font=f1, fill="white")
    W, H = im.size
    im.save(os.path.join(cart, slug + ".jpg"), quality=88)
    for (tw, th), suf in (((66, 66), "-66x66"), ((320, 202), "-320x202")):
        ratio = tw / th
        cw, ch = (int(H * ratio), H) if W / H > ratio else (W, int(W / ratio))
        box = ((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)
        im.crop(box).resize((tw, th), Image.LANCZOS).save(os.path.join(cart, slug + suf + ".jpg"), quality=88)
    base = "/wp-content/uploads/%04d/%02d/%s" % (adesso.year, adesso.month, slug)
    return base, W, H


def padre(cat):
    parti = cat.split("/")
    return "/".join(parti[:-1]) if len(parti) > 2 else None


def attendi_deploy(url_pagina, attesa=420):
    h = sh("git rev-parse --short HEAD")
    log("deploy in corso per", h, "...")
    t0 = time.time()
    ok = False
    while time.time() - t0 < attesa:
        sh("git fetch -q origin", check=False)
        if h in sh("git log origin/gh-pages -1 --format=%s", check=False):
            ok = True
            break
        time.sleep(15)
    log("workflow deploy:", "OK" if ok else "NON confermato entro il tempo")
    stato = None
    for _ in range(12):
        try:
            stato = urllib.request.urlopen(url_pagina, timeout=20).status
            break
        except Exception:
            time.sleep(15)
    log("pagina", url_pagina, "->", stato or "NON raggiungibile")
    return stato == 200


def pubblica(msg, url_pagina):
    sh("git add -A")
    sh('git commit -q -m %s -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"' % json.dumps(msg))
    sh("git pull -q --rebase origin main", check=False)
    sh("git push -q origin main")
    if not attendi_deploy(url_pagina):
        sys.exit("ATTENZIONE: la pagina non risponde ancora 200: controlla Actions su GitHub.")
    try:
        sm = urllib.request.urlopen(SITO + "/sitemap.xml", timeout=20).read().decode("utf-8", "ignore")
        log("sitemap: %d URL, la nuova pagina c'e': %s" % (sm.count("<loc>"), url_pagina.replace(SITO, "").strip("/") in sm))
    except Exception as e:
        log("sitemap non letta:", e)


def cmd_articolo(a):
    if a.file == "-":
        testo = sys.stdin.read()
    else:
        with io.open(a.file, encoding="utf-8") as f:
            testo = f.read()
    testo = corpo_html(testo)
    cat = a.cat.strip("/")
    if not cat.startswith("servizi/"):
        sys.exit("--cat deve iniziare con servizi/ (es. servizi/stampa-3d)")
    if not os.path.isfile(os.path.join(CATD, cat + ".html")):
        sys.exit("Categoria inesistente: %s. Creala prima con: python bin/nuovo.py categoria --slug %s --nome \"Nome\"" % (cat, cat))
    sezione = (a.sezione or cat.split("/", 1)[1]).strip("/")
    slug = slugify(a.slug or a.titolo)
    dest = os.path.join(LAZIO, *sezione.split("/"), slug + ".html")
    if os.path.exists(dest):
        sys.exit("Esiste gia': " + dest)
    adesso = datetime.datetime.now() - datetime.timedelta(days=1)  # passato: Jekyll salta le date future
    data = adesso.strftime("%Y-%m-%dT%H:%M:%S")
    desc = a.desc or re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", testo)).strip()[:155]
    seo = a.seo or (a.titolo + " - Servizi Lazio")
    base, W, H = immagini(slug, a.titolo, a.immagine, adesso)
    cats = [cat] + ([a.cat2] if a.cat2 else ([padre(cat)] if padre(cat) else ([ "servizi/" + sezione.split("/")[0] ] if sezione.split("/")[0] != cat.split("/", 1)[1] else [])))
    cats = [c for i, c in enumerate(cats) if c and c not in cats[:i]]
    alt = a.alt or a.titolo
    fm = "---\n" + "\n".join("%s: %s" % (k, v) for k, v in [
        ("layout", q("avada-articolo")), ("title", q(a.titolo)), ("description", q(desc)), ("seo_title", q(seo)),
        ("date", q(data)), ("last_modified_at", q(data)), ("wp_id", prossimo_wp_id()), ("wp_tipo", q("post")),
        ("categorie", json.dumps(cats)), ("og_image", q("https://servizi.lazio.it" + base + ".jpg")),
        ("og_w", q(str(W))), ("og_h", q(str(H))), ("og_type", q("image/jpeg")),
        ("thumb", q(base + "-66x66.jpg")), ("thumb_full", q(base + ".jpg")), ("thumb_alt", q(alt)),
        ("excerpt", q(desc)), ("thumb_card", q(base + "-320x202.jpg")), ("thumb_w", q(str(W))), ("thumb_h", q(str(H))),
        ("render_with_liquid", "false"), ("thumb_caption", q("")),
        ("categorie_visibili", json.dumps([cat])), ("thumb_titolo", q(alt))]) + "\n---\n\n"
    scrivi(dest, fm + testo)
    log("creato", dest.replace(os.sep, "/"))
    url = "%s/%s/%s/" % (SITO, sezione, slug)
    if a.no_push:
        log("(--no-push) URL previsto:", url)
    else:
        pubblica("Nuovo articolo: " + a.titolo, url)


def cmd_categoria(a):
    slug = a.slug.strip("/")
    if not slug.startswith("servizi/"):
        sys.exit("--slug deve iniziare con servizi/")
    dest = os.path.join(CATD, *slug.split("/")) + ".html"
    if os.path.exists(dest):
        sys.exit("Categoria gia' esistente: " + dest)
    wp = prossimo_wp_id()
    scrivi(dest, "---\nlayout: \"avada-archivio\"\ntitle: %s\nseo_title: %s\ndescription: %s\ncat: %s\ncat_slug: %s\nwp_id: \"%d\"\n---\n"
           % (q(a.nome), q(a.nome + " - Servizi Lazio"), q(a.desc or ""), q(slug), q(slug.split("/")[-1]), wp))
    with io.open(CATYML, encoding="utf-8") as f:
        y = f.read()
    if '"%s"' % slug not in y:
        ids = [int(x) for x in re.findall(r"^\s*id:\s*(\d+)", y, re.M)] or [100]
        with io.open(CATYML, "a", encoding="utf-8", newline="\n") as f:
            f.write(("" if y.endswith("\n") else "\n") + "- slug: %s\n  nome: %s\n  id: %d\n" % (q(slug), q(a.nome), max(ids) + 1))
    log("creata categoria", slug)
    if not a.no_push:
        pubblica("Nuova categoria: " + a.nome, "%s/%s/" % (SITO, slug))


def cmd_stato(a):
    usate = set()
    for p in glob.glob(os.path.join(LAZIO, "**", "*.html"), recursive=True):
        with io.open(p, encoding="utf-8", errors="ignore") as f:
            m = re.search(r"^categorie:\s*(\[.*\])", f.read(3000), re.M)
        if m:
            try:
                usate.update(json.loads(m.group(1)))
            except Exception:
                pass
    tutte = [os.path.relpath(p, CATD).replace(os.sep, "/")[:-5] for p in glob.glob(os.path.join(CATD, "**", "*.html"), recursive=True)]
    log("articoli:", len(glob.glob(os.path.join(LAZIO, "**", "*.html"), recursive=True)), "| categorie:", len(tutte), "| prossimo wp_id:", prossimo_wp_id())
    log("categorie vuote (noindex, fuori dalla sitemap):")
    for c in sorted(tutte):
        if c not in usate:
            log("  -", c)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Aggiunge articoli e categorie a servizi.lazio")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a1 = sp.add_parser("articolo")
    a1.add_argument("--titolo", required=True); a1.add_argument("--cat", required=True); a1.add_argument("--file", required=True)
    a1.add_argument("--cat2"); a1.add_argument("--sezione"); a1.add_argument("--slug"); a1.add_argument("--desc"); a1.add_argument("--seo")
    a1.add_argument("--immagine"); a1.add_argument("--alt"); a1.add_argument("--no-push", action="store_true")
    a2 = sp.add_parser("categoria")
    a2.add_argument("--slug", required=True); a2.add_argument("--nome", required=True); a2.add_argument("--desc"); a2.add_argument("--no-push", action="store_true")
    sp.add_parser("stato")
    a = ap.parse_args()
    {"articolo": cmd_articolo, "categoria": cmd_categoria, "stato": cmd_stato}[a.cmd](a)
