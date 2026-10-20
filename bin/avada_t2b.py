"""Tappa 2b Jekyll/Avada: pagine categoria (archivi) generate dai contenuti.
Uso (radice repo): python bin/avada_t2b.py
- layout _avada/_layouts/avada-archivio.html (testata e coda dalla pagina mirror servizi/servizi-agli-edifici/pulizie)
- collection 'categorie': _avada/_categorie/<percorso>.html (una per categoria, elenco = articoli con quella categoria)
- articoli: campi excerpt e thumb_card (320x202) nel front matter
NON lanciare 'avada_build.py gen': cancella _avada e rifa' la tappa 1."""
import re, os, glob, html, sys
REPO = r'C:\Users\mirco\Desktop\repository\servizi.lazio'
os.chdir(REPO)
A = '_avada'
REL = re.compile(r'(?:\.\./)+')
REF = 'servizi/servizi-agli-edifici/pulizie'

def rd(p): return open(p, encoding='utf-8', newline='').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='').write(s)

# ---------- 1. articoli: excerpt + thumb_card
def clean_text(body):
    b = body.replace('{% raw %}', '').replace('{% endraw %}', '')
    b = re.sub(r'<style.*?</style>|<script.*?</script>|<nav class="auto-toc".*?</nav>', ' ', b, flags=re.S)
    b = re.sub(r'<div class="fusion-alert.*?</div></div></div>', ' ', b, flags=re.S)
    b = re.sub(r'<[^>]+>', ' ', b)
    b = html.unescape(b)
    b = re.sub(r'\{\{.*?\}\}|\{%.*?%\}', ' ', b)
    return re.sub(r'\s+', ' ', b).strip()

def excerpt(body, n=40):
    w = clean_text(body).split(' ')
    s = ' '.join(w[:n])
    return s

n_art = 0
for f in glob.glob(A + '/_lazio/**/*.html', recursive=True):
    t = rd(f)
    m = re.match(r'---(\r?\n)(.*?)\r?\n---\r?\n', t, re.S)
    if not m: continue
    nl = m.group(1)
    fm = m.group(2).replace('\r\n', '\n')
    body = t[m.end():]
    fm = re.sub(r'^(excerpt|thumb_card): .*\n?', '', fm, flags=re.M).rstrip('\n')
    full = re.search(r'^thumb_full: "(.*)"$', fm, re.M).group(1)
    card = ''
    if full:
        card = re.sub(r'(\.\w+)$', r'-320x202\1', full)
        pc = card.lstrip('/').replace('/', os.sep); pf = full.lstrip('/').replace('/', os.sep)
        if not os.path.exists(pc) and os.path.exists(pf):
            try:
                from PIL import Image
                im = Image.open(pf).convert('RGB'); w, h = im.size
                r = 320 / 202
                if w / h > r: nw = int(h * r); box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
                else: nh = int(w / r); box = (0, (h - nh) // 2, w, (h - nh) // 2 + nh)
                im.crop(box).resize((320, 202), Image.LANCZOS).save(pc, quality=85)
            except Exception as e:
                print('thumb card non creato', pf, e); card = full
        elif not os.path.exists(pc): card = full
    ex = excerpt(body).replace('\\', '\\\\').replace('"', '\\"')
    fm += '\nexcerpt: "%s"\nthumb_card: "%s"' % (ex, card)
    wr(f, '---' + nl + fm.replace('\n', nl) + nl + '---' + nl + body); n_art += 1
print('articoli aggiornati', n_art)

# ---------- 2. layout archivio dalla pagina mirror
t = rd(REF + '/index.html')
i = t.index('<main'); j = t.index('</main>') + len('</main>')
head, tail = t[:i], t[j:]
seo = re.search(r'<title>(.*?)</title>', head, re.S).group(1)
desc = re.search(r'<meta name="description" content="([^"]*)"', head).group(1)
tit = re.search(r'<h1 class="entry-title">([^<]*)</h1>', head).group(1)
cid = re.search(r'category-(\d+) ', head).group(1)
slug_last = REF.split('/')[-1]
def tok(s):
    s = re.sub(r'(<meta[^>]*?(?:name="description"|property="og:description")[^>]*?content=")[^"]*', r'\1@@DESC@@', s)
    s = s.replace('<title>' + seo + '</title>', '<title>@@SEOTITLE@@</title>')
    s = s.replace('content="' + seo + '"', 'content="@@SEOTITLE@@"')
    s = s.replace('https:\\/\\/servizi.lazio.it\\/' + REF.replace('/', '\\/') + '\\/', '@@JCANON@@')
    s = s.replace('https://servizi.lazio.it/' + REF + '/', '@@CANON@@')
    s = s.replace('https%3A%2F%2Fservizi.lazio.it%2F' + REF.replace('/', '%2F') + '%2F', 'https%3A%2F%2Fservizi.lazio.it@@ENC@@')
    s = s.replace('<h1 class="entry-title">' + tit + '</h1>', '<h1 class="entry-title">@@TITLE@@</h1>')
    s = s.replace('&raquo; ' + tit + ' Feed', '&raquo; @@TITLE@@ Feed')
    s = s.replace('"name":"' + tit + '"', '"name":"@@TITLE@@"')
    s = s.replace('category-' + slug_last + ' category-' + cid, 'category-@@SLUG@@ category-@@ID@@')
    s = REL.sub('@B@/', s)
    s = s.replace('@B@/' + REF + '/', '@@PATH@@')
    return s
TOK = {'@@SEOTITLE@@': '{{ page.seo_title | default: page.title | escape }}', '@@TITLE@@': '{{ page.title | escape }}',
       '@@DESC@@': '{{ page.description | escape }}', '@@CANON@@': 'https://servizi.lazio.it{{ canon }}',
       '@@JCANON@@': "https:\\/\\/servizi.lazio.it{{ canon | replace: '/', '\\/' }}", '@@ENC@@': '{{ canon | url_encode }}',
       '@@PATH@@': '{{ canon }}', '@@SLUG@@': '{{ page.cat_slug }}', '@@ID@@': '{{ page.wp_id }}', '@B@': '{{ site.baseurl }}'}
def lq(s):
    out = '{% raw %}' + s.replace('{% raw %}', '').replace('{% endraw %}', '') + '{% endraw %}'
    for k in sorted(TOK, key=len, reverse=True):
        out = out.replace(k, '{% endraw %}' + TOK[k] + '{% raw %}')
    return out.replace('{% raw %}{% endraw %}', '')
h2, t2 = tok(head), tok(tail)
for nm, s in (('head', h2), ('tail', t2)):
    res = [m.group(0)[:150] for m in re.finditer(r'[^<>"]{0,60}(?:' + re.escape(tit) + r'|' + re.escape(slug_last) + r')[^<>"]{0,40}', s)]
    print('residui', nm, len(res), [r for r in res if 'megamenu' not in r][:6])
main = '''<main id="main" class="clearfix ">
<div class="fusion-row" style="">
<section id="content" class="full-width" style="width: 100%;">
<div id="posts-container" class="fusion-blog-archive fusion-blog-layout-medium-wrapper fusion-clearfix">
<div class="fusion-posts-container fusion-blog-layout-medium fusion-blog-pagination fusion-blog-rollover " data-pages="1">
{%- assign lista = site.lazio | sort: "date" | reverse -%}
{%- for p in lista -%}{%- if p.categorie contains page.cat %}
{%- assign purl = p.url | remove_first: site.avada_prefix %}
<article id="post-{{ p.wp_id }}" class="fusion-post-medium post fusion-clearfix post-{{ p.wp_id }} type-post status-publish format-standard has-post-thumbnail hentry">
<div class="fusion-flexslider flexslider fusion-flexslider-loading fusion-post-slideshow">
<ul class="slides">
<li>
<div class="fusion-image-wrapper fusion-image-size-fixed" aria-haspopup="true">
<img width="320" height="202" src="{{ site.baseurl }}{{ p.thumb_card }}" class="attachment-blog-medium size-blog-medium wp-post-image" alt="{{ p.thumb_alt | escape }}" decoding="async" loading="lazy" />
<div class="fusion-rollover">
<div class="fusion-rollover-content">
<a class="fusion-rollover-link" href="{{ site.baseurl }}{{ purl }}">{{ p.title | escape }}</a>
<div class="fusion-rollover-sep"></div>
<h4 class="fusion-rollover-title">
<a class="fusion-rollover-title-link" href="{{ site.baseurl }}{{ purl }}">{{ p.title | escape }}</a>
</h4>
<a class="fusion-link-wrapper" href="{{ site.baseurl }}{{ purl }}" aria-label="{{ p.title | escape }}"></a>
</div>
</div>
</div>
</li>
</ul>
</div>
<div class="fusion-post-content post-content">
<h2 class="entry-title fusion-post-title"><a href="{{ site.baseurl }}{{ purl }}">{{ p.title | escape }}</a></h2>
<div class="fusion-post-content-container">
<p>{{ p.excerpt | escape }}</p>
</div>
</div>
<div class="fusion-clearfix"></div>
<div class="fusion-meta-info">
<div class="fusion-alignleft"><span class="vcard rich-snippet-hidden"><span class="fn"><a href="{{ site.baseurl }}/author/daniele/" title="Articoli scritti da Daniele F." rel="author">Daniele F.</a></span></span><span class="updated rich-snippet-hidden">{{ p.last_modified_at | date: "%Y-%m-%dT%H:%M:%S+00:00" }}</span>
{%- for cs in p.categorie -%}
{%- assign cd = site.data.categorie | where: "slug", cs | first -%}
{%- if cd -%}<a href="{{ site.baseurl }}/{{ cs }}/" rel="category tag">{{ cd.nome }}</a>{%- unless forloop.last -%}, {%- endunless -%}{%- endif -%}
{%- endfor -%}
<span class="fusion-inline-sep">|</span></div>
<div class="fusion-alignright">
<a href="{{ site.baseurl }}{{ purl }}" class="fusion-read-more">Continua a leggere </a>
</div>
</div>
</article>
{%- endif -%}{%- endfor %}
</div>
</div>
</section>
</div> <!-- fusion-row -->
</main>{% raw %}'''
lay = "{%- assign canon = page.url | remove_first: site.avada_prefix -%}\n" + lq(h2) + main.replace('{% endraw %}', '').replace('{% raw %}', '') + lq(t2)
wr(A + '/_layouts/avada-archivio.html', '---\n---\n' + lay)

# ---------- 3. pagine categoria
cats = {}
for p in glob.glob('servizi/**/index.html', recursive=True):
    d = p.replace('\\', '/')[:-len('/index.html')]
    s = rd(p)
    if len(s) < 1000 or '<main' not in s: continue
    hd = s[:s.index('<main')]
    cats[d] = dict(
        seo=re.search(r'<title>(.*?)</title>', hd, re.S).group(1),
        desc=re.search(r'<meta name="description" content="([^"]*)"', hd).group(1) if re.search(r'<meta name="description" content="([^"]*)"', hd) else '',
        title=re.search(r'<h1 class="entry-title">([^<]*)</h1>', hd).group(1),
        id=(re.search(r'category-(\d+) ', hd) or [0, ''])[1])
shutil_dir = A + '/_categorie'
import shutil
shutil.rmtree(shutil_dir, ignore_errors=True)
for d, c in sorted(cats.items()):
    q = lambda v: v.replace('\\', '\\\\').replace('"', '\\"')
    wr('%s/%s.html' % (shutil_dir, d), '---\nlayout: "avada-archivio"\ntitle: "%s"\nseo_title: "%s"\ndescription: "%s"\ncat: "%s"\ncat_slug: "%s"\nwp_id: "%s"\n---\n' % (q(html.unescape(c['title'])), q(html.unescape(c['seo'])), q(html.unescape(c['desc'])), d, d.split('/')[-1], c['id']))
print('pagine categoria', len(cats))

# ---------- 4. config
for cfg, perm in ((A + '/_config.yml', '/:path/'), (A + '/_config_preview.yml', '/anteprima/:path/')):
    c = rd(cfg)
    if 'categorie:' not in c:
        c = c.rstrip('\n') + '\n  categorie:\n    output: true\n    permalink: %s\n' % perm
        wr(cfg, c)
print('config ok')
