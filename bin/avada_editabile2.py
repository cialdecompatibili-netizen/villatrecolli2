"""Seconda passata di avada_editabile: recupera da git HEAD (sidecar originali) la didascalia immagine e le categorie visibili."""
import re, glob, os, subprocess, html
R = r'C:\Users\mirco\Desktop\repository\servizi.lazio'
os.chdir(R)
A = '_avada'; INC = A + '/_includes/avada/'
def rd(p): return open(p, encoding='utf-8', newline='').read()
def wr(p, s): open(p, 'w', encoding='utf-8', newline='').write(s)
def git(p): return subprocess.run(['git', 'show', 'HEAD:' + p], capture_output=True, encoding='utf-8').stdout
q = lambda v: v.replace('\\', '\\\\').replace('"', '\\"')
n = 0
for f in glob.glob(A + '/_lazio/**/*.html', recursive=True):
    t = rd(f)
    m = re.match(r'---(\r?\n)(.*?)\r?\n---\r?\n', t, re.S)
    nl = m.group(1); fm = m.group(2).replace('\r\n', '\n'); body = t[m.end():]
    if 'categorie_visibili:' in fm: continue
    wid = re.search(r'^wp_id: "?(\d+)', fm, re.M).group(1)
    pre = git(INC + wid + '-pre.html'); post = git(INC + wid + '-post.html')
    assert pre and post, wid
    mc = re.search(r'data-rel="iLightbox\[gallery\d+\]"\s+title="([^"]*)"', pre)
    if not mc: print('senza didascalia', wid, re.findall(r'<a [^>]*>', pre)[:2])
    cap = mc.group(1) if mc else ''
    cap = html.unescape(cap)
    meta = post[post.index('fusion-meta-info-wrapper'):post.index('fusion-inline-sep')]
    slugs = [h.strip('/') for h in re.findall(r'href="(?:\{% endraw %\}\{\{ site\.baseurl \}\}\{% raw %\})?/?([^"]*)" rel="category tag"', meta)]
    slugs = [s.replace('{% endraw %}{{ site.baseurl }}{% raw %}', '').strip('/') for s in slugs]
    fm = fm.rstrip('\n') + '\nthumb_caption: "%s"\ncategorie_visibili: [%s]' % (q(cap), ', '.join('"%s"' % s for s in slugs))
    wr(f, '---' + nl + fm.replace('\n', nl) + nl + '---' + nl + body); n += 1
print('aggiornati', n)

# modelli
p = rd(INC + 'art-pre.html')
p = p.replace('title="" data-title="{{ page.thumb_alt | escape }}" data-caption=""', 'title="{{ page.thumb_caption | escape }}" data-title="{{ page.thumb_alt | escape }}" data-caption="{{ page.thumb_caption | escape }}"')
assert 'thumb_caption' in p
wr(INC + 'art-pre.html', p)
vis = '{%- for c in site.data.categorie -%}{%- if page.categorie_visibili contains c.slug -%}'
wr(INC + 'art-catclass.html', vis + ' category-{{ c.slug | split: "/" | last }}{%- endif -%}{%- endfor -%}')
wr(INC + 'art-catlink.html', '{%- assign first = true -%}' + vis +
   "{%- unless first -%}{{ ', ' }}{%- endunless -%}<a href=\"{{ site.baseurl }}/{{ c.slug }}/\" rel=\"category tag\">{{ c.nome }}</a>{%- assign first = false -%}{%- endif -%}{%- endfor -%}")
