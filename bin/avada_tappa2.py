"""Tappa 2 Jekyll/Avada: sidebar e 'Post correlati' generati dai contenuti.
Uso (dalla radice del repo): python bin/avada_tappa2.py
Idempotente: se rilanciato non rompe niente.
- aggiunge al front matter di ogni articolo: thumb (66x66), thumb_full, thumb_alt
- _avada/_data/categorie.yml (slug, nome) dalla sidebar originale
- include generati: side.html, w-recenti.html, w-tabs.html, w-categorie.html, related.html, data-it.html
- ogni *-post.html: blocco 'Post correlati' sostituito da {% include avada/related.html %}
- ogni articolo: avada_side -> avada/side.html (i vecchi N-side.html vengono eliminati)"""
import os, re, glob, sys
R = r'C:\Users\mirco\Desktop\repository\servizi.lazio'
os.chdir(R)
INC = '_avada/_includes/avada'
BASE = '{% endraw %}{{ site.baseurl }}{% raw %}'

def rd(p):
    return open(p, encoding='utf-8', newline='').read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='').write(t)

# 1. modello sidebar e related dal primo articolo (se gia' migrato, dal backup)
src_side = INC + '/_tappa1_side.html'
src_post = INC + '/_tappa1_post.html'
if not os.path.exists(src_side):
    wr(src_side, rd(INC + '/1297-side.html'))
    wr(src_post, rd(INC + '/1297-post.html'))
side = rd(src_side); post = rd(src_post)

# 2. categorie
cats = re.findall(r'<li class="cat-item cat-item-(\d+)"><a href="' + re.escape(BASE) + r'/([^"]+?)/">([^<]+)</a>', side)
if not cats:
    sys.exit('categorie non trovate nella sidebar modello')
y = '# slug (come nel front matter "categorie"), nome visibile, id WP\n'
for cid, slug, nome in cats:
    y += '- slug: "%s"\n  nome: "%s"\n  id: %s\n' % (slug, nome.replace('"', '\\"'), cid)
wr('_avada/_data/categorie.yml', y)

# 3. front matter articoli: thumb
alt_by_key = {}
import subprocess
_files = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD', INC], capture_output=True, text=True).stdout.split()
for _f in _files:
    if not _f.endswith('.html'): continue
    _t = subprocess.run(['git', 'show', 'HEAD:' + _f], capture_output=True, encoding='utf-8').stdout or ''
    for tag in re.findall(r'<img [^>]*>', _t):
        m = re.search(r'src="[^"]*?/wp-content/uploads/([^"?]+)"', tag); a = re.search(r'alt="([^"]*)"', tag)
        if m and a and a.group(1):
            k = re.sub(r'(-\d+x\d+)?\.\w+$', '', m.group(1))
            alt_by_key.setdefault(k, a.group(1))
n_fm = 0; n_thumb_miss = 0; n_thumb_new = 0
for f in glob.glob('_avada/_lazio/**/*.html', recursive=True):
    t = rd(f)
    nl = '\r\n' if '\r\n' in t[:400] else '\n'
    m = re.match(r'---\r?\n(.*?)\r?\n---\r?\n', t, re.S)
    if not m: continue
    fm = m.group(1).replace('\r\n', '\n')
    fm = re.sub(r'^thumb(_full|_alt)?: .*\n?', '', fm, flags=re.M).rstrip('\n')
    add = []
    if True:
        og = re.search(r'^og_image: "(.*)"$', fm, re.M)
        title = re.search(r'^title: "(.*)"$', fm, re.M)
        if og:
            full = re.sub(r'^https?://[^/]+', '', og.group(1))
            th = re.sub(r'(\.\w+)$', r'-66x66\1', full)
            pf = full.lstrip('/').replace('/', os.sep); pt = th.lstrip('/').replace('/', os.sep)
            if not os.path.exists(pt) and os.path.exists(pf):
                try:
                    from PIL import Image
                    im = Image.open(pf).convert('RGB'); w, h = im.size; s = min(w, h)
                    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((66, 66), Image.LANCZOS)
                    im.save(pt, quality=85); n_thumb_new += 1
                except Exception as e:
                    print('thumb non creato', pf, e)
            if not os.path.exists(pt):
                n_thumb_miss += 1; th = full
            key = re.sub(r'^/wp-content/uploads/', '', re.sub(r'\.\w+$', '', full))
            alt = alt_by_key.get(key) or (title.group(1) if title else '')
            alt = alt.replace('\\', '\\\\').replace('"', '\\"')
            add += ['thumb: "%s"' % th, 'thumb_full: "%s"' % full, 'thumb_alt: "%s"' % alt]
        else:
            add += ['thumb: ""', 'thumb_full: ""', 'thumb_alt: ""']
    if re.search(r'^avada_side: "avada/\d+-side.html"', fm, re.M):
        fm = re.sub(r'^avada_side: .*$', 'avada_side: "avada/side.html"', fm, flags=re.M)
    if add or fm != m.group(1):
        fm = fm + ('\n' if add else '') + '\n'.join(add)
        t = '---' + nl + fm.replace('\n', nl) + nl + '---' + nl + t[m.end():]
        wr(f, t); n_fm += 1
print('front matter aggiornati:', n_fm, '| thumb 66x66 mancanti (uso immagine intera):', n_thumb_miss)

# 4. include generati
wr(INC + '/data-it.html', '''{%- assign mesi = "Gennaio,Febbraio,Marzo,Aprile,Maggio,Giugno,Luglio,Agosto,Settembre,Ottobre,Novembre,Dicembre" | split: "," -%}
{%- assign mi = include.d | date: "%-m" | minus: 1 -%}
{%- assign g = include.d | date: "%-d" | plus: 0 -%}
{%- assign u = g | modulo: 10 -%}
{%- if g >= 11 and g <= 13 -%}{%- assign suf = "th" -%}{%- elsif u == 1 -%}{%- assign suf = "st" -%}{%- elsif u == 2 -%}{%- assign suf = "nd" -%}{%- elsif u == 3 -%}{%- assign suf = "rd" -%}{%- else -%}{%- assign suf = "th" -%}{%- endif -%}
{{ mesi[mi] }} {{ g }}{{ suf }}, {{ include.d | date: "%Y" }}''')

wr(INC + '/w-recenti.html', '''{%- assign ord = site.lazio | sort: "date" | reverse -%}
<ul>
{%- for p in ord limit: 5 %}
<li>
<a href="{{ site.baseurl }}{{ p.url | remove_first: site.avada_prefix }}">{{ p.title | escape }}</a>
</li>
{%- endfor %}
</ul>''')

def li(p):
    return ('''<li>
<div class="image">
<a href="{{ site.baseurl }}{{ %(p)s.url | remove_first: site.avada_prefix }}" aria-label="{{ %(p)s.title | escape }}"><img width="66" height="66" src="{{ site.baseurl }}{{ %(p)s.thumb }}" class="attachment-recent-works-thumbnail size-recent-works-thumbnail wp-post-image" alt="{{ %(p)s.thumb_alt | escape }}" decoding="async" loading="lazy" /></a>
</div>
<div class="post-holder">
<a href="{{ site.baseurl }}{{ %(p)s.url | remove_first: site.avada_prefix }}">{{ %(p)s.title | escape }}</a>
<div class="fusion-meta">
{%% include avada/data-it.html d=%(p)s.date %%}
</div>
</div>
</li>''' % {'p': p})

wr(INC + '/w-tabs.html', '''{%- assign ord = site.lazio | sort: "date" | reverse -%}
{%- assign tot = ord.size -%}
{%- assign base = page.wp_id | modulo: tot -%}
<section id="pyre_tabs-widget-2" class="widget fusion-tabs-widget" style="border-style: solid;border-color:transparent;border-width:0px;">
<div class="fusion-tabs-widget-wrapper fusion-tabs-widget-2 fusion-tabs-clean fusion-tabs-image-default tab-holder">
<nav class="fusion-tabs-nav">
<ul class="tabset tabs">
<li class="active"><a href="#" data-link="fusion-tab-popular">Popular</a></li>
<li><a href="#" data-link="fusion-tab-recent">Recent</a></li>
</ul>
</nav>
<div class="fusion-tabs-widget-content tab-box tabs-container">
<div class="fusion-tab-popular fusion-tab-content tab tab_content" data-name="fusion-tab-popular">
<ul class="fusion-tabs-widget-items news-list">
{%- for k in (0..2) %}
{%- assign idx = k | times: 37 | plus: base | modulo: tot %}
{%- assign p = ord[idx] %}
''' + li('p') + '''
{%- endfor %}
</ul>
</div>
<div class="fusion-tab-recent fusion-tab-content tab tab_content" data-name="fusion-tab-recent" style="display: none;">
<ul class="fusion-tabs-widget-items news-list">
{%- for p in ord limit: 3 %}
''' + li('p') + '''
{%- endfor %}
</ul>
</div>
</div>
</div>
</section>''')

wr(INC + '/w-categorie.html', '''{%- assign usate = site.lazio | map: "categorie" | join: "|" | prepend: "|" | append: "|" -%}
<ul>
{%- for c in site.data.categorie %}
{%- assign chiave = c.slug | prepend: "|" | append: "|" %}
{%- if usate contains chiave %}
<li class="cat-item cat-item-{{ c.id }}"><a href="{{ site.baseurl }}/{{ c.slug }}/">{{ c.nome }}</a>
</li>
{%- endif %}
{%- endfor %}
</ul>''')

# related.html: testata e coda come nell'originale, elementi generati
i = post.find('<section class="related-posts'); j = post.find('</section>', i) + len('</section>')
S = post[i:j].replace(BASE, '{{ site.baseurl }}')
a = S.find('<ul class="fusion-carousel-holder">') + len('<ul class="fusion-carousel-holder">')
b = S.find('</ul><!-- fusion-carousel-holder -->')
head, tail = S[:a], S[b:]
item = '''
{%- for p in sel %}
<li class="fusion-carousel-item">
<div class="fusion-carousel-item-wrapper">
<div class="fusion-image-wrapper" aria-haspopup="true">
<img width="{{ p.og_w }}" height="{{ p.og_h }}" src="{{ site.baseurl }}{{ p.thumb_full }}" class="attachment-full size-full wp-post-image" alt="{{ p.thumb_alt | escape }}" decoding="async" loading="lazy" />
<div class="fusion-rollover">
<div class="fusion-rollover-content">
<a class="fusion-rollover-link" href="{{ site.baseurl }}{{ p.url | remove_first: site.avada_prefix }}">{{ p.title | escape }}</a>
<div class="fusion-rollover-sep"></div>
<a class="fusion-link-wrapper" href="{{ site.baseurl }}{{ p.url | remove_first: site.avada_prefix }}" aria-label="{{ p.title | escape }}"></a>
</div>
</div>
</div>
<h4 class="fusion-carousel-title">
<a class="fusion-related-posts-title-link" href="{{ site.baseurl }}{{ p.url | remove_first: site.avada_prefix }}" target="_self" title="{{ p.title | escape }}">{{ p.title | escape }}</a>
</h4>
<div class="fusion-carousel-meta">
<span class="fusion-date">{% include avada/data-it.html d=p.date %}</span>
<span class="fusion-inline-sep">|</span>
<span><a href="{{ site.baseurl }}{{ p.url | remove_first: site.avada_prefix }}#respond">0 Commenti</a></span>
</div><!-- fusion-carousel-meta -->
</div><!-- fusion-carousel-item-wrapper -->
</li>
{%- endfor %}
'''
sel = '''{%- assign ord = site.lazio | sort: "date" | reverse -%}
{%- assign vistii = "|" | append: page.wp_id | append: "|" -%}
{%- assign n = 0 -%}
{%- assign sel = "" | split: "" -%}
{%- for cat in page.categorie -%}
{%- for p in ord -%}
{%- assign chiave = "|" | append: p.wp_id | append: "|" -%}
{%- if n < 4 and p.categorie contains cat -%}
{%- unless vistii contains chiave -%}
{%- assign sel = sel | push: p -%}
{%- assign vistii = vistii | append: p.wp_id | append: "|" -%}
{%- assign n = n | plus: 1 -%}
{%- endunless -%}
{%- endif -%}
{%- endfor -%}
{%- endfor -%}
{%- if sel.size > 0 -%}
'''
wr(INC + '/related.html', sel + head + item + tail + '\n{%- endif -%}\n')

# side.html: dal modello, con le sezioni generate
s = side
s = re.sub(r'<section id="recent-posts-2".*?</section>', lambda m: '<section id="recent-posts-2" class="widget widget_recent_entries">\n\t\t<div class="heading"><h4 class="widget-title">Articoli recenti</h4></div>' + '{% endraw %}{% include avada/w-recenti.html %}{% raw %}</section>', s, count=1, flags=re.S)
s = re.sub(r'<section id="recent-posts-3".*?</section>', lambda m: '<section id="recent-posts-3" class="widget widget_recent_entries">\n\t\t<div class="heading"><h4 class="widget-title">Articoli recenti</h4></div>' + '{% endraw %}{% include avada/w-recenti.html %}{% raw %}</section>', s, count=1, flags=re.S)
s = re.sub(r'<section id="pyre_tabs-widget-2".*?</section>', lambda m: '{% endraw %}{% include avada/w-tabs.html %}{% raw %}', s, count=1, flags=re.S)
s = re.sub(r'<section id="categories-2".*?</section>', lambda m: '<section id="categories-2" class="widget widget_categories"><div class="heading"><h4 class="widget-title">Categorie</h4></div>' + '{% endraw %}{% include avada/w-categorie.html %}{% raw %}</section>', s, count=1, flags=re.S)
assert s.count('include avada/') == 4, s.count('include avada/')
wr(INC + '/side.html', s)

# 5. post: related -> include
n_rel = 0; miss = []
for f in glob.glob(INC + '/*-post.html'):
    if os.path.basename(f).startswith('_'): continue
    t = rd(f)
    if 'include avada/related.html' in t: continue
    t2, k = re.subn(r'<section class="related-posts single-related-posts">.*?</section>', lambda m: '{% endraw %}{% include avada/related.html %}{% raw %}', t, count=1, flags=re.S)
    if k: wr(f, t2); n_rel += 1
    else: miss.append(os.path.basename(f))
print('post con related generato:', n_rel, '| senza blocco related:', len(miss), miss[:5])

# 6. via i vecchi side
n_del = 0
for f in glob.glob(INC + '/*-side.html'):
    os.remove(f); n_del += 1
print('side vecchi eliminati:', n_del)
