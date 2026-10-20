"""Sostituisce i prodotti demo Homestart / MedX (e le versioni EN) con
'Allestimento tavola' / 'Pacchetto fotografico' (EN: Table Setting / Photo Package)
in tutto il mirror di villatrecolli.com (repo villatrecolli2).
Lavora sui byte (surrogateescape) per non toccare la codifica del resto dei file."""
import os, re, subprocess, sys
from PIL import Image

R = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
UP = R + r"\wp-content\uploads"

def git(*a):
    r = subprocess.run(["git", "-C", R] + list(a), capture_output=True, text=True, encoding="utf8", errors="replace")
    if r.returncode:
        print("GIT ERR", a, r.stderr.strip())
    return r.stdout

# ---------- 1. immagini ----------
def crop_save(src, box, dst):
    im = Image.open(src).convert("RGB").crop(box).resize((500, 650), Image.LANCZOS)
    im.save(dst, quality=88, optimize=True)
crop_save(UP + r"\2025\06\486220226_2666297070223550_7286773552908198325_n.jpg", (433, 0, 1615, 1536), UP + r"\2019\03\allestimento-tavola.jpg")
crop_save(UP + r"\2025\06\479520026_2634787763374481_7140271076512822357_n.jpg", (0, 36, 1080, 1440), UP + r"\2019\03\pacchetto-fotografico.jpg")
IMGNEW = {"homestart": "allestimento-tavola.jpg", "medx": "pacchetto-fotografico.jpg"}

# ---------- 2. testi ----------
TXT = {
 "it": {
  "allest": dict(name="Allestimento tavola",
    s=["Un allestimento curato per la tavola degli sposi e degli ospiti: tovagliato coordinato, centrotavola floreali, segnaposto, candele e mise en place completa, pensati insieme a voi nello stile della festa.",
       "Include il sopralluogo in villa, la prova tavola prima dell'evento e il montaggio e lo smontaggio a cura del nostro staff."],
    l=["Scegliamo insieme palette, fiori e dettagli in base alla stagione e al tipo di evento, dal matrimonio al compleanno. Ogni allestimento &egrave; realizzato con materiali di nostra propriet&agrave; e pu&ograve; essere personalizzato per numero di ospiti e disposizione delle sale."],
    c=["Tovagliato e runner coordinati", "Centrotavola floreali di stagione", "Montaggio e smontaggio inclusi"]),
  "foto": dict(name="Pacchetto fotografico",
    s=["Il servizio fotografico completo per il vostro giorno pi&ugrave; importante, tra le sale, i giardini, la piscina e i vialetti fioriti di Villa Tre Colli: dai preparativi al taglio della torta, con un fotografo professionista dedicato.",
       "Tutte le immagini selezionate vengono post-prodotte e consegnate in una galleria online privata, insieme a un album fotografico da 30 pagine."],
    l=["Prima del giorno dell'evento organizziamo un sopralluogo con il fotografo per scegliere insieme i punti pi&ugrave; belli della villa e la scaletta degli scatti."],
    c=["Fotografo professionista per 8 ore", "Galleria online privata", "Album fotografico da 30 pagine"]),
 },
 "en": {
  "allest": dict(name="Table Setting",
    s=["A carefully designed setting for the bridal table and your guests' tables: matching linens, floral centrepieces, place cards, candles and a complete table layout, planned with you to suit the style of your event.",
       "Includes a site visit at the villa, a table trial before the event, and set-up and clear-down by our staff."],
    l=["Together we choose palette, flowers and details according to the season and the occasion, from weddings to birthdays. Every setting is made with our own materials and can be tailored to the number of guests and the layout of the rooms."],
    c=["Matching linens and runners", "Seasonal floral centrepieces", "Set-up and clear-down included"]),
  "foto": dict(name="Photo Package",
    s=["A complete photo service for your most important day, across the halls, gardens, pool and flowering paths of Villa Tre Colli: from the preparations to the cake cutting, with a dedicated professional photographer.",
       "All selected images are post-processed and delivered in a private online gallery, together with a 30-page photo album."],
    l=["Before the event we arrange a visit with the photographer to choose the best spots in the villa and plan the shot list together."],
    c=["Professional photographer for 8 hours", "Private online gallery", "30-page photo album"]),
 },
}
SLUG = {"it": {"homestart": "allestimento-tavola", "homestartinglese": "allestimento-tavola", "medx": "pacchetto-fotografico"},
        "en": {"homestart": "table-setting", "homestartinglese": "table-setting", "medx": "photo-package"}}
PID = {"2891": ("it", "allest"), "2889": ("it", "foto"), "3635": ("en", "allest"), "4278": ("en", "foto")}
PRODDIRS = {"prodotto/homestart": ("it", "allest"), "prodotto/medx": ("it", "foto"),
            "en/prodotto/homestartinglese": ("en", "allest"), "en/prodotto/medx": ("en", "foto")}
NEWDIR = {"prodotto/homestart": "prodotto/allestimento-tavola", "prodotto/medx": "prodotto/pacchetto-fotografico",
          "en/prodotto/homestartinglese": "en/prodotto/table-setting", "en/prodotto/medx": "en/prodotto/photo-package"}

URLRE = re.compile(r'((?:https?://[^"\'\s<>]*?/)|(?:(?:\.\./)+)|(?:\./))?((?:en/)?)prodotto/(homestartinglese|homestart|medx)(?=[/"\'#?\s<&])')
IMGRE = re.compile(r'(https?://www\.villatrecolli\.com/)?((?:\.\./)*)wp-content/uploads/2019/03/(homestart|medx)-product(?:-en)?\.png')
LEFT = re.compile(r'(homestart|medx)-product(?:-en)?')

def tgt_lang(g1, g2, fdir):
    if g2 == "en/":
        return "en"
    if g1 and g1.startswith("http"):
        return "it"
    ups = g1.count("../") if g1 else 0
    parts = fdir.split("/") if fdir else []
    base = parts[:max(0, len(parts) - ups)]
    return "en" if base[:1] == ["en"] else "it"

def paras(lst):
    return "\n".join("<p>%s</p>" % x for x in lst)

def process(f, t):
    lang = "en" if f.startswith("en/") else "it"
    fdir = os.path.dirname(f).replace("\\", "/")
    depth = len(fdir.split("/")) if fdir else 0
    # a. slug prodotto
    def u(m):
        g1, g2, s = m.group(1) or "", m.group(2), m.group(3)
        tl = tgt_lang(g1, g2, fdir)
        return g1 + g2 + "prodotto/" + SLUG[tl][s]
    t = URLRE.sub(u, t)
    t = t.replace("%2Fen%2Fprodotto%2Fmedx%2F","%2Fen%2Fprodotto%2Fphoto-package%2F").replace("%2Fen%2Fprodotto%2Fhomestartinglese%2F","%2Fen%2Fprodotto%2Ftable-setting%2F").replace("%2Fprodotto%2Fhomestart%2F","%2Fprodotto%2Fallestimento-tavola%2F").replace("%2Fprodotto%2Fmedx%2F","%2Fprodotto%2Fpacchetto-fotografico%2F")
    # b. immagini
    def im(m):
        absu, pre, s = m.group(1), m.group(2), m.group(3)
        new = "wp-content/uploads/2019/03/" + IMGNEW[s]
        if absu:
            i = m.string.rfind("<", 0, m.start())
            tag = re.match(r"<\s*(\w+)", m.string[i:i + 30])
            tag = tag.group(1).lower() if tag else ""
            if tag in ("a", "img", "div", "span", "source", "li", "p", "button"):
                return "../" * depth + new
            return absu + new
        return pre + new
    t = IMGRE.sub(im, t)
    t = LEFT.sub(lambda m: "allestimento-tavola" if m.group(1) == "homestart" else "pacchetto-fotografico", t)
    # c. blocchi di listing (li prodotto) con testo/checklist
    def block(m):
        pid = m.group(2)
        if pid not in PID:
            return m.group(0)
        L, k = PID[pid]
        d = TXT[L][k]
        b = m.group(1)
        b = re.sub(r'(<div class="post-content">\s*)(.*?)(\s*<ul class="fusion-checklist)',
                   lambda x: x.group(1) + "\n\n".join(d["s"]) + "\n\n" + x.group(3).lstrip("\n"), b, count=1, flags=re.S)
        it = iter(d["c"])
        b = re.sub(r'(<div class="fusion-li-item-content" style="[^"]*">)(.*?)(</div>)',
                   lambda x: x.group(1) + next(it, x.group(2)) + x.group(3), b)
        return b
    t = re.sub(r'(<li class="product type-product post-(\d+) .*?\r?\n</li>)', block, t, flags=re.S)
    # d. pagina singola prodotto
    for old, (L, k) in PRODDIRS.items():
        if f in (old + "/index.html", NEWDIR[old] + "/index.html"):
            d = TXT[L][k]
            cut = t.find('<li class="product type-product')
            head, tail = (t[:cut], t[cut:]) if cut > 0 else (t, "")
            cnt = [0]
            def pp(m):
                cnt[0] += 1
                return paras(d["s"]) if cnt[0] == 1 else paras(d["s"] + d["l"])
            head = re.sub(r'<p>(?:(?:italiano|inglese|english) ?)?Sed ut perspiciatis.*?</p>\s*<p>Nemo enim.*?</p>', pp, head, flags=re.S)
            it = iter(d["c"])
            head = re.sub(r'(<div class="fusion-li-item-content" style="[^"]*">)(.*?)(</div>)',
                          lambda x: x.group(1) + next(it, x.group(2)) + x.group(3), head)
            t = head + tail
    # e. nomi
    n_all, n_foto = TXT[lang]["allest"]["name"], TXT[lang]["foto"]["name"]
    t = re.sub(r"Homestartinglese|Homestart", n_all, t)
    t = t.replace("MedX", n_foto)
    t = t.replace('data-product_sku="MXN"', 'data-product_sku="FOT001"').replace('data-product_sku="MX001"', 'data-product_sku="FOT001"')
    return t

files = [x for x in git("ls-files", "*.html").split("\n") if x and not x.startswith(("wp-content", "wp-includes", "_out"))]
changed = 0
for f in files:
    p = os.path.join(R, f)
    raw = open(p, "rb").read().decode("utf8", "surrogateescape")
    if not re.search(r"(?i)homestart|medx|ingleseSed", raw):
        continue
    new = process(f, raw)
    if new != raw:
        open(p, "wb").write(new.encode("utf8", "surrogateescape"))
        changed += 1
print("file modificati:", changed)

# ---------- 3. rinomina cartelle e rimuovi vecchie immagini ----------
for old, new in NEWDIR.items():
    if os.path.isdir(os.path.join(R, old)):
        git("mv", old, new)
for old in ["homestart-product.png", "medx-product.png"]:
    if os.path.exists(os.path.join(UP, "2019", "03", old)):
        git("rm", "-q", "-f", "wp-content/uploads/2019/03/" + old)
print("fatto")
