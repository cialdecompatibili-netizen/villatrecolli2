"""Rende gli articoli Jekyll/Avada completamente editabili (admin): niente piu' sidecar per articolo.
Uso (radice repo): python bin/avada_editabile.py
- crea _avada/_includes/avada/art-pre.html e art-post.html: modelli generati da titolo, immagine, categorie nel front matter
- ogni articolo in _avada/_lazio: corpo senza {% raw %}, senza {{ site.baseurl }} (link /percorso/), render_with_liquid: false,
  front matter con thumb_w/thumb_h; tolti avada_pre/avada_post/avada_side
- cancella i vecchi <id>-pre.html / <id>-post.html
NON rilanciare dopo aver modificato gli articoli a mano da admin (e' pensato per una conversione una tantum: e' idempotente solo sui file non ancora convertiti)."""
import re, glob, os, sys
R = r'C:\Users\mirco\Desktop\repository\servizi.lazio'
os.chdir(os.path.join(R, '_avada'))
INC = '_includes/avada/'
def rd(p): return open(p, encoding='utf-8', newline='').read()
def wr(p, s): open(p, 'w', encoding='utf-8', newline='').write(s)
RAW = lambda s: s.replace('{% raw %}', '').replace('{% endraw %}', '')

# ---------- 1. modelli da un articolo di riferimento (2445)
pre = RAW(rd(INC + '2445-pre.html')); post = RAW(rd(INC + '2445-post.html'))
alert_end = pre.index('<article')
alert, art = pre[:alert_end], pre[alert_end:]
art = re.sub(r'<article id="post-2445" class="[^"]*">',
  '<article id="post-{{ page.wp_id }}" class="post post-{{ page.wp_id }} type-post status-publish format-standard has-post-thumbnail hentry{% include avada/art-catclass.html %}">', art)
art = art.replace('>Elettricista</span>', '>{{ page.title | escape }}</span>')
art = re.sub(r' srcset="[^"]*"', '', art); art = re.sub(r' sizes="[^"]*"', '', art)
art = art.replace('iLightbox[gallery2445]', 'iLightbox[gallery{{ page.wp_id }}]')
art = art.replace('/wp-content/uploads/2020/07/electrician-2755686_1280.jpg', '{{ page.thumb_full }}')
art = art.replace('elettricista roma rieti frosinone latina viterbo', '{{ page.thumb_alt | escape }}')
art = art.replace('width="1280" height="938"', 'width="{{ page.thumb_w }}" height="{{ page.thumb_h }}"')
assert 'electrician' not in art and '2445' not in art.replace('{{ page.wp_id }}', ''), art[:2000]
wr(INC + 'art-pre.html', alert + art)

meta_a = post.index('<span class="updated rich-snippet-hidden">'); meta_b = post.index('<span class="fusion-inline-sep">')
post = post[:meta_a] + '<span class="updated rich-snippet-hidden">{{ page.last_modified_at | date: "%Y-%m-%dT%H:%M:%S+00:00" }}</span>{% include avada/art-catlink.html %}' + post[meta_b:]
post = post.replace('https%3A%2F%2Fservizi.lazio.it%2Fblog%2Felettricista%2F', 'https%3A%2F%2Fservizi.lazio.it{{ canon | url_encode }}')
post = post.replace('https://servizi.lazio.it/blog/elettricista/', 'https://servizi.lazio.it{{ canon }}')
post = re.sub(r'(&amp;t=|text=|&amp;title=|subject=)Elettricista', r'\1{{ page.title | url_encode }}', post)
post = re.sub(r'(summary=|description=)[^"&]*(?=&amp;|")', r'\1{{ page.excerpt | url_encode }}', post)
post = re.sub(r'media=https%3A%2F%2Fservizi\.lazio\.it%2F[^"]*', 'media=https%3A%2F%2Fservizi.lazio.it{{ page.thumb_full | url_encode }}', post)
assert 'lettricista' not in post, re.findall(r'.{60}lettricista.{60}', post)[:3]
wr(INC + 'art-post.html', '{%- assign canon = page.url | remove_first: site.avada_prefix -%}' + post)
leaf = ('{%- for c in site.data.categorie -%}{%- assign has = false -%}{%- if page.categorie contains c.slug -%}{%- assign has = true -%}'
        '{%- assign pref = c.slug | append: "/" -%}{%- for o in page.categorie -%}{%- if o != c.slug and o contains pref -%}{%- assign has = false -%}{%- endif -%}{%- endfor -%}{%- endif -%}')
wr(INC + 'art-catclass.html', leaf + '{%- if has %} category-{{ c.slug | split: "/" | last }}{%- endif -%}{%- endfor -%}')
wr(INC + 'art-catlink.html', '{%- assign first = true -%}' + leaf +
   '{%- if has -%}{%- unless first -%}, {%- endunless -%}<a href="{{ site.baseurl }}/{{ c.slug }}/" rel="category tag">{{ c.nome }}</a>{%- assign first = false -%}{%- endif -%}{%- endfor -%}')

# ---------- 2. layout: usa i modelli
L = '_layouts/avada-articolo.html'; t = rd(L)
t = t.replace('{% include {{ page.avada_pre }} %}{{ content }}{% include {{ page.avada_post }} %}', '{% include avada/art-pre.html %}{{ content }}{% include avada/art-post.html %}')
t = t.replace('{% include {{ page.avada_side }} %}', '{% include avada/side.html %}')
assert 'page.avada_' not in t
wr(L, t)

# ---------- 3. articoli
n = 0
for f in glob.glob('_lazio/**/*.html', recursive=True):
    t = rd(f)
    m = re.match(r'---(\r?\n)(.*?)\r?\n---\r?\n', t, re.S)
    nl = m.group(1); fm = m.group(2).replace('\r\n', '\n'); body = t[m.end():]
    wid = re.search(r'^wp_id: "?(\d+)', fm, re.M).group(1)
    if 'avada_pre:' not in fm: continue
    p = RAW(rd(INC + wid + '-pre.html'))
    mm = re.search(r'<img width="(\d+)" height="(\d+)"', p)
    w, h = (mm.group(1), mm.group(2)) if mm else ('', '')
    fm = re.sub(r'^avada_(side|pre|post): .*\n?', '', fm, flags=re.M).rstrip('\n')
    fm += '\nthumb_w: "%s"\nthumb_h: "%s"\nrender_with_liquid: false' % (w, h)
    body = RAW(body).replace('{{ site.baseurl }}/', '/')
    assert '{{' not in body and '{%' not in body, f
    wr(f, '---' + nl + fm.replace('\n', nl) + nl + '---' + nl + body)
    os.remove(INC + wid + '-pre.html'); os.remove(INC + wid + '-post.html'); n += 1
print('articoli convertiti', n)
