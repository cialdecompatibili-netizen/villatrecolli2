"""Sostituisce i prodotti demo CryptoTracker / Helpsuite v2 (IT+EN) con
'Catering' / 'Animazione musicale' (EN: Catering / Live Music & DJ) nel mirror villatrecolli2.
Stessa logica di sostituisci_prodotti_demo.py."""
import os, re, subprocess
from PIL import Image

R = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
UP = R + r"\wp-content\uploads"

def git(*a):
    r = subprocess.run(["git", "-C", R] + list(a), capture_output=True, text=True, encoding="utf8", errors="replace")
    if r.returncode:
        print("GIT ERR", a, r.stderr.strip())
    return r.stdout

def crop_save(src, box, dst):
    Image.open(src).convert("RGB").crop(box).resize((500, 650), Image.LANCZOS).save(dst, quality=88, optimize=True)
G = UP + r"\2025\06"
crop_save(G + r"\476897935_2631911333662124_8472293081700034231_n-1200x900.jpg" if False else [G + "\\" + x for x in os.listdir(G) if x.startswith("476897935")][0], (30, 0, 620, 768) if Image.open([G + "\\" + x for x in os.listdir(G) if x.startswith("476897935")][0]).size == (1024, 768) else (0, 0, 590, 768), UP + r"\2019\03\catering.jpg")
crop_save(G + r"\504885294_2744204625766127_548432150261417415_n.jpg", (0, 0, 1181, 1536), UP + r"\2019\03\animazione-musicale.jpg")
IMGNEW = {"crypto": "catering.jpg", "helpsuite": "animazione-musicale.jpg"}

TXT = {
 "it": {
  "cat": dict(name="Catering",
    s=["Un servizio di catering completo per il vostro evento: aperitivo di benvenuto, buffet o menu al tavolo, torta e brindisi, con personale di sala dedicato e prodotti selezionati.",
       "Il menu viene composto insieme a voi in base al tipo di festa, alla stagione e alle esigenze degli ospiti, con proposte anche vegetariane, per celiaci e per bambini."],
    l=["Prima dell'evento organizziamo un assaggio dei piatti per scegliere insieme il men&ugrave; definitivo. Il servizio comprende cucina, camerieri, stoviglie e riordino finale della sala."],
    c=["Aperitivo di benvenuto", "Men&ugrave; personalizzato con degustazione", "Personale di sala incluso"]),
  "mus": dict(name="Animazione musicale",
    s=["Musica dal vivo e DJ set per accompagnare ogni momento della festa, dall'aperitivo a bordo piscina al ballo di fine serata, con impianto audio e luci professionali.",
       "La scaletta viene concordata con voi in anticipo, dalle musiche per l'ingresso degli sposi ai brani richiesti dagli ospiti."],
    l=["Possiamo proporre un duo acustico per la cerimonia, una band per la cena e un DJ per la serata, in base al vostro stile e al numero di invitati."],
    c=["Musica dal vivo o DJ set", "Impianto audio e luci inclusi", "Scaletta personalizzata"]),
 },
 "en": {
  "cat": dict(name="Catering",
    s=["A complete catering service for your event: welcome aperitif, buffet or plated menu, cake and toast, with dedicated waiting staff and carefully selected ingredients.",
       "The menu is designed together with you according to the type of party, the season and your guests' needs, with vegetarian, gluten-free and children's options."],
    l=["Before the event we arrange a tasting so you can choose the final menu together with us. The service includes kitchen, waiters, tableware and a final clean-up of the room."],
    c=["Welcome aperitif", "Personalised menu with tasting", "Waiting staff included"]),
  "mus": dict(name="Live Music & DJ",
    s=["Live music and DJ sets to accompany every moment of the party, from the poolside aperitif to the late-night dance, with professional sound and lighting.",
       "The playlist is agreed with you in advance, from the music for the couple's entrance to the songs requested by your guests."],
    l=["We can offer an acoustic duo for the ceremony, a band for dinner and a DJ for the evening, depending on your style and the number of guests."],
    c=["Live music or DJ set", "Sound system and lights included", "Personalised playlist"]),
 },
}
SLUG = {"it": {"cryptotracker": "catering", "helpsuite-v2": "animazione-musicale"},
        "en": {"cryptotracker": "catering", "helpsuite-v2": "live-music-dj"}}
PID = {"2882": "cat", "2880": "mus"}
PRODDIRS = {"prodotto/cryptotracker": ("it", "cat"), "prodotto/helpsuite-v2": ("it", "mus"),
            "en/prodotto/cryptotracker": ("en", "cat"), "en/prodotto/helpsuite-v2": ("en", "mus")}
NEWDIR = {"prodotto/cryptotracker": "prodotto/catering", "prodotto/helpsuite-v2": "prodotto/animazione-musicale",
          "en/prodotto/cryptotracker": "en/prodotto/catering", "en/prodotto/helpsuite-v2": "en/prodotto/live-music-dj"}

URLRE = re.compile(r'((?:https?://[^"\'\s<>]*?/)|(?:(?:\.\./)+)|(?:\./))?((?:en/)?)prodotto/(cryptotracker|helpsuite-v2)(?=[/"\'#?\s<&])')
IMGRE = re.compile(r'(https?://www\.villatrecolli\.com/)?((?:\.\./)*)wp-content/uploads/2019/03/(crypto|helpsuite)-product(?:-en)?\.png')
LEFT = re.compile(r'(crypto|helpsuite)-product(?:-en)?')

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
    def u(m):
        g1, g2, s = m.group(1) or "", m.group(2), m.group(3)
        return g1 + g2 + "prodotto/" + SLUG[tgt_lang(g1, g2, fdir)][s]
    t = URLRE.sub(u, t)
    t = t.replace("%2Fen%2Fprodotto%2Fcryptotracker%2F", "%2Fen%2Fprodotto%2Fcatering%2F").replace("%2Fen%2Fprodotto%2Fhelpsuite-v2%2F", "%2Fen%2Fprodotto%2Flive-music-dj%2F")
    t = t.replace("%2Fprodotto%2Fcryptotracker%2F", "%2Fprodotto%2Fcatering%2F").replace("%2Fprodotto%2Fhelpsuite-v2%2F", "%2Fprodotto%2Fanimazione-musicale%2F")
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
    t = LEFT.sub(lambda m: "catering" if m.group(1) == "crypto" else "animazione-musicale", t)
    def block(m):
        pid = m.group(2)
        if pid not in PID:
            return m.group(0)
        b = m.group(1)
        L = "en" if "product_cat-software-en" in b else "it"
        d = TXT[L][PID[pid]]
        b = re.sub(r'(<div class="post-content">\s*)(.*?)(\s*<ul class="fusion-checklist)',
                   lambda x: x.group(1) + "\n\n".join(d["s"]) + "\n\n" + x.group(3).lstrip("\n"), b, count=1, flags=re.S)
        it = iter(d["c"])
        b = re.sub(r'(<div class="fusion-li-item-content" style="[^"]*">)(.*?)(</div>)',
                   lambda x: x.group(1) + next(it, x.group(2)) + x.group(3), b)
        return b
    t = re.sub(r'(<li class="product type-product post-(\d+) .*?\r?\n</li>)', block, t, flags=re.S)
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
            head = re.sub(r'<p>Sed ut perspiciatis.*?</p>', pp, head, flags=re.S)
            head = re.sub(r'content="Sed ut perspiciatis[^"]*"', 'content="%s"' % re.sub(r"<[^>]+>|\"", "", d["s"][0]), head)
            it = iter(d["c"])
            head = re.sub(r'(<div class="fusion-li-item-content" style="[^"]*">)(.*?)(</div>)',
                          lambda x: x.group(1) + next(it, x.group(2)) + x.group(3), head)
            t = head + tail
    n_cat, n_mus = TXT[lang]["cat"]["name"], TXT[lang]["mus"]["name"]
    t = re.sub(r"CryptoTracker", n_cat, t)
    t = re.sub(r"Helpsuite v2|Helpsuite", n_mus, t)
    t = t.replace('data-product_sku="HS001"', 'data-product_sku="MUS001"')
    return t

files = [x for x in git("ls-files", "*.html").split("\n") if x and not x.startswith(("wp-content", "wp-includes", "_out"))]
changed = 0
for f in files:
    p = os.path.join(R, f)
    raw = open(p, "rb").read().decode("utf8", "surrogateescape")
    if not re.search(r"(?i)cryptotracker|helpsuite|crypto-product", raw):
        continue
    new = process(f, raw)
    if new != raw:
        open(p, "wb").write(new.encode("utf8", "surrogateescape"))
        changed += 1
print("file modificati:", changed)
for old, new in NEWDIR.items():
    if os.path.isdir(os.path.join(R, old)):
        git("mv", old, new)
for old in ["crypto-product.png", "helpsuite-product.png"]:
    if os.path.exists(os.path.join(UP, "2019", "03", old)):
        git("rm", "-q", "-f", "wp-content/uploads/2019/03/" + old)
print("fatto")
