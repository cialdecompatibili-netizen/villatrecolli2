"""Prepara _out/ con il solo mirror statico (niente Jekyll, niente tool/admin/demo)."""
import os, shutil, subprocess, sys
OUT = "_out"; TMP = "_avada_site"
DIRS = ["admin","contatti","author","blog","categoria_portfolio","portfolio-items","servizi","servizi-a-roma","servizi-agli-edifici","servizi-ai-cittadini","servizi-alle-aziende","slide-page","wp-content","wp-includes"]
FILES = ["index.html","robots.txt","sitemap_index.xml","404.html","CNAME"]
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
repo = os.environ.get("GITHUB_REPOSITORY", "x/servizi.lazio").split("/")[-1]
baseurl = "" if os.path.isfile("CNAME") else "/" + repo
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

# --- Sitemap: generata a ogni deploy da tutte le pagine HTML realmente presenti in _out (mirror + Jekyll)
import re as _re
from urllib.parse import quote as _q
from xml.sax.saxutils import escape as _esc
if os.path.isfile("CNAME"):
    origin = "https://" + open("CNAME").read().strip()
else:
    origin = "https://%s.github.io%s" % (os.environ.get("GITHUB_REPOSITORY", "cialdecompatibili-netizen/servizi.lazio").split("/")[0], baseurl)
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
