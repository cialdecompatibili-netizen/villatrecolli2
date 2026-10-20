"""Prepara _out/ con il solo mirror statico (niente Jekyll, niente tool/admin/demo).

NOTE PER LE PROSSIME SESSIONI (leggere prima di toccare qualcosa)
- Questo sito (villatrecolli2) = mirror HTML di villatrecolli.com (WordPress + tema Avada), NON al-folio.
  al-folio resta solo come motore della repo (_layouts, plugin, admin): le sue pagine sono escluse in _config.yml.
- Le pagine modificate A MANO stanno nella radice della repo (index.html, en/, la-villa/, ...). Questo script le COPIA in _out/
  e poi le RIFINISCE (link, CSS, sitemap, hreflang). _out/ si rigenera a ogni deploy: non modificare mai _out/ a mano.
- Deploy = push su main -> workflow "Deploy site" -> branch gh-pages. Online dopo ~1 minuto (Ctrl+F5 per la cache).
- Gli URL ASSOLUTI https://www.villatrecolli.com/... nei file sorgente sono NORMALI: li riscrive questo script in locale
  (solo se il file esiste nel clone). Quindi anche un'immagine nuova va messa in wp-content/uploads/ e puo' essere citata
  con l'URL dell'originale: diventa locale al deploy. Se il file NON esiste in locale, il link resta sul sito originale.
- Problemi gia' risolti (non rifarli): home coperta da _pages di servizi.lazio (SOLO_MIRROR), cartelle del mirror non
  pubblicate (DIRS dinamico), font/icone del menu bloccati cross-origin (sezione CSS), link che uscivano dal clone.
"""
import os, shutil, subprocess, sys
OUT = "_out"; TMP = "_avada_site"
DIRS = ["admin","contatti","author","blog","categoria_portfolio","portfolio-items","servizi","servizi-a-roma","servizi-agli-edifici","servizi-ai-cittadini","servizi-alle-aziende","slide-page","wp-content","wp-includes"]
FILES = ["index.html","robots.txt","sitemap_index.xml","404.html","CNAME"]
# PUNTO CRITICO: una cartella nuova nella radice viene pubblicata SOLO se contiene un index.html con "avada-html-layout"
# nei primi 4000 caratteri (pagina Avada). Una pagina nuova scritta a mano senza quel marcatore NON va online (404).
# Le cartelle che iniziano con "." o "_" e assets/bin/docs/test/modules_source sono escluse di proposito.
# dir del mirror: ogni cartella radice con un index.html Avada (dinamico: dipende dal sito copiato) + wp-content/wp-includes
for _d in sorted(os.listdir(".")):
    if not os.path.isdir(_d) or _d in DIRS or _d.startswith((".", "_")) or _d in ("assets", "bin", "docs", "test", "modules_source"):
        continue
    _ok = False
    for _dp, _dn, _fn in os.walk(_d):
        if "index.html" in _fn and "avada-html-layout" in open(os.path.join(_dp, "index.html"), encoding="utf-8", errors="ignore").read(4000):
            _ok = True; break
    if _ok:
        DIRS.append(_d)
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
for d in DIRS:
    if os.path.isdir(d): shutil.copytree(d, os.path.join(OUT, d))
# admin/repo.txt: nome del repo per il login dell'admin su dominio proprio (solo il token da inserire)
if os.environ.get("GITHUB_REPOSITORY") and os.path.isdir(os.path.join(OUT, "admin")):
    open(os.path.join(OUT, "admin", "repo.txt"), "w").write(os.environ["GITHUB_REPOSITORY"].strip() + "\n")
for f in FILES:
    if os.path.isfile(f): shutil.copy(f, OUT)
open(os.path.join(OUT, ".nojekyll"), "w").close()

# --- Jekyll: articoli e categorie (_avada/) sovrapposti al mirror, stesso URL. baseurl: con CNAME "" altrimenti /<repo> (anteprima github.io)
repo = os.environ.get("GITHUB_REPOSITORY", "x/villatrecolli2").split("/")[-1]
baseurl = "" if os.path.isfile("CNAME") else "/" + repo
# PUNTO CRITICO - NON mettere SOLO_MIRROR = False: riattiva l'overlay Jekyll di _avada/ (vecchio sito servizi.lazio)
# che si sovrappone al mirror: la home tornava "Servizi Lazio" e senza grafica. Qui conta solo il mirror di villatrecolli.com.
SOLO_MIRROR = True  # villatrecolli: vale solo il mirror di villatrecolli.com, niente overlay Jekyll di _avada (era il vecchio servizi.lazio)
if not SOLO_MIRROR:
    open("_avada/_config_deploy.yml", "w").write('baseurl: "%s"\navada_prefix: ""\n' % baseurl)
    shutil.rmtree(TMP, ignore_errors=True)
    cmd = os.environ.get("JEKYLL_CMD", "jekyll") + " build -s _avada -d " + TMP + " --config _avada/_config.yml,_avada/_config_deploy.yml"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print((r.stdout + r.stderr)[-1500:])
    if r.returncode != 0 or not os.path.isdir(TMP): sys.exit("build Jekyll fallita")
    n = 0
    for dp, dn, fn in os.walk(TMP):
        for f in fn:
            src = os.path.join(dp, f); dst = os.path.join(OUT, os.path.relpath(src, TMP))
            os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(src, dst); n += 1
    print("jekyll:", n, "file sovrapposti")
    if baseurl:  # anteprima su github.io: i link root-relative nel testo degli articoli vanno prefissati col baseurl
        import re
        pre = re.compile(r'((?:href|src|action|poster|data-src)=")/(?!/|%s/)' % re.escape(baseurl.strip("/")))
        sset = re.compile(r'(srcset=")([^"]*)"')
        fixset = lambda m: m.group(1) + re.sub(r'(^|,\s*)/(?!/|%s/)' % re.escape(baseurl.strip("/")), lambda k: k.group(1) + baseurl + "/", m.group(2)) + '"'
        for dp, dn, fn in os.walk(TMP):
            for f in fn:
                if not f.endswith(".html"): continue
                p = os.path.join(OUT, os.path.relpath(os.path.join(dp, f), TMP))
                s = open(p, encoding="utf-8", newline="").read()
                s2 = sset.sub(fixset, pre.sub(lambda m: m.group(1) + baseurl + "/", s))
                if s2 != s: open(p, "w", encoding="utf-8", newline="").write(s2)
    print("ok", sum(len(f) for _,_,f in os.walk(OUT)), "file")

# PUNTO CRITICO: _esiste() decide tutto. Se una pagina/immagine NON e' nel clone il link resta (o torna) sul sito originale:
# e' voluto (es. /shop, selettore lingua). Per far restare un link nel clone basta creare la cartella/file nella repo.
# admin/, wp-content/, wp-includes/ sono esclusi dal ciclo di riscrittura dei link.
# --- Rifinitura link (anteprima github.io): link assoluti a villatrecolli.com -> locali se la pagina esiste nel clone;
# root-relative -> prefisso baseurl; relativi rotti (es. versione /en/ non copiata) -> sito originale
import re as _r2, posixpath as _pp
from urllib.parse import unquote as _uq
ORIG = "https://www.villatrecolli.com"
def _esiste(rel):
    rel = _uq(rel.split("#")[0].split("?")[0]).strip("/")
    t = os.path.join(OUT, *rel.split("/")) if rel else OUT
    return os.path.isfile(t) or os.path.isfile(os.path.join(t, "index.html"))
_abs = _r2.compile(r"(?:https?:)?//(?:www\.)?villatrecolli\.com(/[^\"'\s,)<>\\]*)?")
_root = _r2.compile(r'((?:href|src|action|poster|data-src)=")/(?!/)([^"]*)"')
_rel = _r2.compile(r'((?:href|src)=")(?![a-zA-Z][a-zA-Z0-9+.-]*:|/|#|\?)([^"]+)"')
def _fix_abs(m):
    path = m.group(1) or "/"
    return (baseurl + path) if _esiste(path) else m.group(0)
_bp = baseurl.strip("/")
for _dp, _dn, _fn in os.walk(OUT):
    _dn[:] = [d for d in _dn if not (_dp == OUT and d in ("admin", "wp-content", "wp-includes"))]
    for _f in _fn:
        if not _f.endswith(".html"): continue
        _p = os.path.join(_dp, _f)
        _s = open(_p, encoding="utf-8", newline="").read()
        _pd = os.path.relpath(_dp, OUT).replace(os.sep, "/")
        _pd = "" if _pd == "." else _pd
        def _fix_root(m):
            rest = m.group(2)
            if _bp and (rest == _bp or rest.startswith(_bp + "/")): return m.group(0)
            full = "/" + rest
            if not baseurl: return m.group(0)
            return m.group(1) + (baseurl + full if _esiste(full) else ORIG + full) + '"'
        def _fix_rel(m):
            v = m.group(2)
            t = _pp.normpath(_pp.join(_pd, v.split("#")[0].split("?")[0]))
            if t.startswith("..") or t == "." or _esiste(t): return m.group(0)
            return m.group(1) + ORIG + "/" + t + '"'
        _n = _abs.sub(_fix_abs, _s)
        _n = _root.sub(_fix_root, _n)
        _n = _rel.sub(_fix_rel, _n)
        if _n != _s: open(_p, "w", encoding="utf-8", newline="").write(_n)

# PUNTO CRITICO: senza questa sezione i font delle icone (frecce del menu) vengono bloccati dal browser perche' cross-origin.
# --- CSS: font e immagini citati con URL assoluto/protocol-relative dell'originale -> locali (altrimenti i font cross-origin vengono bloccati: sparivano le icone/frecce del menu)
_cssu = _r2.compile(r"""((?:https?:)?//(?:www\.)?villatrecolli\.com)(/wp-content/[^)"'\s,;?#]+)""")
def _fix_css(m):
    return (baseurl + m.group(2)) if _esiste(m.group(2)) else m.group(0)
for _dp, _dn, _fn in os.walk(OUT):
    for _f in _fn:
        if not _f.endswith(".css"): continue
        _p = os.path.join(_dp, _f)
        _s = open(_p, encoding="utf-8", errors="ignore", newline="").read()
        _n = _cssu.sub(_fix_css, _s)
        if _n != _s: open(_p, "w", encoding="utf-8", newline="").write(_n)

# PUNTO CRITICO: freccetta dei sottomenu AUTOMATICA. Avada la mette solo se la voce di primo livello ha dentro
# <span class="fusion-megamenu-icon"><i class="glyphicon fa-angle-down fas"></i></span> e la classe fusion-flex-link sul <a>.
# Nel mirror alcune voci con sottomenu (es. "Blog") non l'hanno, quindi qui la aggiungiamo a OGNI voce di primo livello
# (li.menu-item-has-children.fusion-dropdown-menu) che ne e' priva, in tutte le pagine e in tutte le lingue.
# Cosi' una voce nuova con sottomenu avra' la freccia senza toccare l'HTML a mano. Il selettore lingua (wpml-ls) e' escluso di proposito.
# Per verificare: python bin/villatrecolli2/verifica_frecce_menu.py
# --- Menu: freccetta ai sottomenu aggiunta in automatico
_li_sub = _r2.compile(r'(<li\b(?=[^>]*\bmenu-item-has-children\b)(?=[^>]*\bfusion-dropdown-menu\b)(?![^>]*wpml-ls)[^>]*>(?:\s*<span\b[^>]*></span>)*\s*)<a\b([^>]*)>(.*?)</a>', _r2.S)
_ARROW = '<span class="fusion-megamenu-icon"><i class="glyphicon fa-angle-down fas" aria-hidden="true"></i></span>'
def _add_arrow(m):
    inner = m.group(3)
    if "fusion-megamenu-icon" in inner or 'class="menu-text"' not in inner:
        return m.group(0)
    attrs = m.group(2)
    if "fusion-flex-link" not in attrs:
        attrs = _r2.sub(r'class="', 'class="fusion-flex-link ', attrs, count=1)
    return m.group(1) + "<a" + attrs + ">" + inner.replace('<span class="menu-text">', _ARROW + '<span class="menu-text">', 1) + "</a>"
for _dp, _dn, _fn in os.walk(OUT):
    _dn[:] = [d for d in _dn if not (_dp == OUT and d in ("admin", "wp-content", "wp-includes"))]
    for _f in _fn:
        if not _f.endswith(".html"): continue
        _p = os.path.join(_dp, _f)
        _s = open(_p, encoding="utf-8", errors="surrogateescape", newline="").read()
        _n = _li_sub.sub(_add_arrow, _s)
        if _n != _s: open(_p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(_n)

# PUNTO CRITICO: la sitemap NON va scritta a mano, viene rigenerata qui a ogni deploy (con CNAME usa il dominio proprio,
# altrimenti github.io/<repo>). Pagine con noindex o redirect sono escluse di proposito.
# --- Sitemap: generata a ogni deploy da tutte le pagine HTML realmente presenti in _out (mirror + Jekyll)
import re as _re
from urllib.parse import quote as _q
from xml.sax.saxutils import escape as _esc
if os.path.isfile("CNAME"):
    origin = "https://" + open("CNAME").read().strip()
else:
    origin = "https://%s.github.io%s" % (os.environ.get("GITHUB_REPOSITORY", "cialdecompatibili-netizen/villatrecolli2").split("/")[0], baseurl)
SKIP_DIRS = {"admin", "wp-content", "wp-includes", ".git"}
urls = []
for dp, dn, fn in os.walk(OUT):
    dn[:] = [d for d in dn if not (dp == OUT and d in SKIP_DIRS)]
    for f in fn:
        if not f.endswith(".html") or f == "404.html": continue
        p = os.path.join(dp, f)
        head = open(p, encoding="utf-8", errors="ignore").read(4000).lower()
        if "noindex" in head or 'http-equiv="refresh"' in head: continue
        rel = os.path.relpath(p, OUT).replace(os.sep, "/")
        rel = "" if rel == "index.html" else (rel[:-11] if rel.endswith("/index.html") else rel)
        urls.append(origin + "/" + _q(rel) + ("/" if rel and not rel.endswith(".html") else ""))
urls = sorted(set(urls))
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join("  <url><loc>%s</loc></url>\n" % _esc(u) for u in urls) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
open(os.path.join(OUT, "sitemap_index.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <sitemap><loc>%s/sitemap.xml</loc></sitemap>\n</sitemapindex>\n' % origin)
rb = os.path.join(OUT, "robots.txt")
txt = open(rb).read() if os.path.isfile(rb) else ""
if "Sitemap:" not in txt: open(rb, "w").write(txt.rstrip("\n") + "\n\nSitemap: %s/sitemap.xml\n" % origin)
print("sitemap:", len(urls), "url ->", origin + "/sitemap.xml")

# --- hreflang assoluti: canonical/alternate/og:url devono essere URL completi (doppia lingua it/en)
_host = origin[: len(origin) - len(baseurl)] if baseurl else origin
_tag = _re.compile(r'<(?:link|meta)\b[^>]*(?:hreflang=|rel="canonical"|property="og:url")[^>]*>')
for _dp, _dn, _fn in os.walk(OUT):
    _dn[:] = [d for d in _dn if not (_dp == OUT and d in ("admin", "wp-content", "wp-includes"))]
    for _f in _fn:
        if not _f.endswith(".html"): continue
        _p = os.path.join(_dp, _f)
        _s = open(_p, encoding="utf-8", newline="").read()
        _n = _tag.sub(lambda m: _re.sub(r'((?:href|content)=")/(?!/)', lambda k: k.group(1) + _host + "/", m.group(0)), _s)
        if _n != _s: open(_p, "w", encoding="utf-8", newline="").write(_n)
