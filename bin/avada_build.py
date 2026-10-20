"""Tappa 1 jekyll-avada: genera in _avada/ layout + sidecar + articoli Jekyll da _lazio e dalle pagine mirror.
uso: python avada_build.py gen | build | compare | all
"""
import re, os, sys, shutil, subprocess, difflib, json, glob
REPO = r'C:\Users\mirco\Desktop\repository\servizi.lazio'
os.chdir(REPO)
A = '_avada'
REF = 'blog/elettricista'
REL = re.compile(r'(?:\.\./)+')

def read(p): return open(p, encoding='utf8', newline='').read()
def write(p, s):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    open(p, 'w', encoding='utf8', newline='').write(s)

TOK = {
    '@@SEOTITLE@@': "{{ page.seo_title | default: page.title | escape }}",
    '@@TITLE@@': "{{ page.title | escape }}",
    '@@DESC@@': "{{ page.description | escape }}",
    '@@CANON@@': "https://servizi.lazio.it{{ canon }}",
    '@@JCANON@@': "https:\\/\\/servizi.lazio.it{{ canon | replace: '/', '\\/' }}",
    '@@PUB@@': '{{ page.date | date: "%Y-%m-%dT%H:%M:%S+00:00" }}',
    '@@MOD@@': '{{ page.last_modified_at | date: "%Y-%m-%dT%H:%M:%S+00:00" }}',
    '@@ID@@': '{{ page.wp_id }}',
    '@@OGIMG@@': '{{ page.og_image }}',
    '@@OGW@@': '{{ page.og_w }}',
    '@@OGH@@': '{{ page.og_h }}',
    '@@OGT@@': '{{ page.og_type }}',
    '@@SIDE@@': '{% include {{ page.avada_side }} %}',
    '@@ENC@@': '{{ canon | url_encode }}',
    '@@PATH@@': '{{ canon }}',
    '@B@': '{{ site.baseurl }}',
}

def lq(s):
    """testo statico -> raw Liquid, con i token sostituiti da espressioni Liquid"""
    s = s.replace('{% raw %}', '').replace('{% endraw %}', '')
    out = '{% raw %}' + s + '{% endraw %}'
    for tok in sorted(TOK, key=len, reverse=True):
        out = out.replace(tok, '{% endraw %}' + TOK[tok] + '{% raw %}')
    return out

def split_page(t):
    sec = t.index('<section id="content"')
    art = t.index('<article id="post-')
    m = re.compile(r'<div class="post-content[^"]*">').search(t, art)
    body_start = m.end()
    meta = t.index('<div class="fusion-meta-info">', body_start)
    body_end = t.rfind('</div>', body_start, meta)
    art_end = t.index('</article>', meta)
    a0 = t.index('<aside id="sidebar"', art_end); a1 = t.index('</aside>', a0) + len('</aside>')
    return dict(head=t[:sec], pre=t[sec:body_start], body=t[body_start:body_end], post=t[body_end:art_end], tail=t[art_end:a0] + '@@SIDE@@' + t[a1:], side=t[a0:a1])

def ogmeta(t):
    def g(p):
        m = re.search(p, t); return m.group(1) if m else ''
    return dict(og_image=g(r'<meta property="og:image" content="([^"]*)"'), og_w=g(r'og:image:width" content="([^"]*)"'),
                og_h=g(r'og:image:height" content="([^"]*)"'), og_type=g(r'og:image:type" content="([^"]*)"'))

def frontmatter(txt):
    m = re.match(r'---\r?\n(.*?)\r?\n---\r?\n', txt, re.S)
    return m.group(1), txt[m.end():]

def fm_get(fm, k):
    m = re.search(r'^' + k + r':\s*"?(.*?)"?\s*$', fm, re.M); return m.group(1) if m else ''

def make_template():
    t = read(REF + '/index.html')
    sp = split_page(t)
    fm, body = frontmatter(read('_lazio/' + REF + '.html'))
    title = fm_get(fm, 'title'); seo = fm_get(fm, 'seo_title'); desc = fm_get(fm, 'description')
    wid = fm_get(fm, 'wp_id'); dt = fm_get(fm, 'date'); mod = fm_get(fm, 'last_modified_at')
    og = ogmeta(t)
    def tpl(s):
        s = re.sub(r'<meta property="og:description" content="[^"]*"\s*/?>', '<meta property="og:description" content="@@DESC@@" />', s, flags=re.S)
        s = s.replace(desc, '@@DESC@@')
        s = s.replace('https:\\/\\/servizi.lazio.it\\/' + REF.replace('/', '\\/') + '\\/', '@@JCANON@@')
        s = s.replace('https://servizi.lazio.it/' + REF + '/', '@@CANON@@')
        s = s.replace(seo, '@@SEOTITLE@@')
        s = s.replace(title, '@@TITLE@@')
        if og['og_image']:
            s = s.replace(og['og_image'], '@@OGIMG@@')
            s = re.sub(r'(og:image:width" content=")[^"]*', r'\1@@OGW@@', s)
            s = re.sub(r'(og:image:height" content=")[^"]*', r'\1@@OGH@@', s)
            s = re.sub(r'(og:image:type" content=")[^"]*', r'\1@@OGT@@', s)
        s = re.sub(r'(article:published_time" content=")[^"]*', r'\1@@PUB@@', s)
        s = re.sub(r'(article:modified_time" content=")[^"]*', r'\1@@MOD@@', s)
        s = s.replace('https%3A%2F%2Fservizi.lazio.it%2F' + REF.replace('/', '%2F') + '%2F', 'https%3A%2F%2Fservizi.lazio.it@@ENC@@')
        s = re.sub(r'("datePublished":")[^"]*', r'\1@@PUB@@', s)
        s = re.sub(r'("dateModified":")[^"]*', r'\1@@MOD@@', s)
        s = re.sub(r'("caption":")[^"]*', r'\1@@TITLE@@', s)
        s = s.replace(wid, '@@ID@@')
        s = REL.sub('@B@/', s)
        s = s.replace('@B@/' + REF + '/', '@@PATH@@')
        return s
    head = tpl(sp['head']); tail = tpl(sp['tail'])
    for nm, s in (('head', head), ('tail', tail)):
        res = [w for w in (title, title.lower(), seo, dt[:10], 'elettricista') if w and w in s.replace('@@TITLE@@', '')]
        print('residui', nm, res)
    lay = ("{%- assign canon = page.url | remove_first: site.avada_prefix -%}\n" + lq(head) +
           "{% include {{ page.avada_pre }} %}{{ content }}{% include {{ page.avada_post }} %}\n" + lq(tail).replace('{% raw %}{% endraw %}',''))
    write(A + '/_layouts/avada-articolo.html', '---\n---\n' + lay)

def gen():
    shutil.rmtree(A, ignore_errors=True)
    write(A + '/_config.yml', 'title: Servizi Lazio\nurl: https://servizi.lazio.it\nbaseurl: ""\navada_prefix: ""\nplugins: []\n'
          'collections:\n  lazio:\n    output: true\n    permalink: /:path/\n')
    write(A + '/_config_preview.yml', 'baseurl: /servizi.lazio\navada_prefix: /anteprima\ncollections:\n  lazio:\n    output: true\n    permalink: /anteprima/:path/\n')
    make_template()
    n = bad = 0
    for f in glob.glob('_lazio/**/*.html', recursive=True):
        rel = os.path.relpath(f, '_lazio').replace(os.sep, '/')
        fm, body = frontmatter(read(f))
        if fm_get(fm, 'wp_tipo') != 'post':
            continue
        page = rel[:-5] + '/index.html'
        if not os.path.isfile(page):
            print('NO PAGE', rel); bad += 1; continue
        t = read(page)
        try:
            sp = split_page(t)
        except Exception as e:
            print('SPLIT FAIL', rel, e); bad += 1; continue
        wid = fm_get(fm, 'wp_id')
        og = ogmeta(t)
        fm2 = re.sub(r'^layout:.*$', 'layout: "avada-articolo"', fm, flags=re.M)
        fm2 += '\navada_side: "avada/%s-side.html"' % wid
        fm2 += '\navada_pre: "avada/%s-pre.html"\navada_post: "avada/%s-post.html"' % (wid, wid)
        for k, v in og.items(): fm2 += '\n%s: "%s"' % (k, v)
        write('%s/_includes/avada/%s-pre.html' % (A, wid), lq(REL.sub('@B@/', sp['pre'])))
        write('%s/_includes/avada/%s-post.html' % (A, wid), lq(REL.sub('@B@/', sp['post'])))
        write('%s/_includes/avada/%s-side.html' % (A, wid), lq(REL.sub('@B@/', sp['side'])))
        # corpo: da _lazio (modificabile da admin); wrapper raw riscritto
        b = sp['body']
        write('%s/_lazio/%s' % (A, rel), '---\n' + fm2 + '\n---\n' + lq(REL.sub('@B@/', b)))
        n += 1
    print('generati', n, 'errori', bad)

def build():
    shutil.rmtree('_avada_site', ignore_errors=True)
    os.environ['BUNDLE_GEMFILE'] = os.path.join(REPO, '_avada_Gemfile')
    r = subprocess.run('bundle exec jekyll build -s _avada -d _avada_site --config _avada/_config.yml,_avada/_config_preview.yml',
                       shell=True, capture_output=True, text=True)
    print((r.stdout + r.stderr)[-2500:])

def norm(s, old):
    i = s.index('<main'); s = s[i:]
    if old: s = REL.sub('/servizi.lazio/', s)
    s = re.sub(r'href="mailto:[^"]*"', 'href="mailto"', s)
    s = re.sub(r'Gagal mengambil konten\..*', '', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    return [x.strip() for x in s.replace('><', '>\n<').split('\n')]

def compare():
    ok = diff = 0; worst = []
    for f in glob.glob(A + '/_lazio/**/*.html', recursive=True):
        rel = os.path.relpath(f, A + '/_lazio').replace(os.sep, '/')[:-5]
        new = '_avada_site/anteprima/' + rel + '/index.html'
        if not os.path.isfile(new): print('MANCA', rel); diff += 1; continue
        a = norm(read(rel + '/index.html'), True); b = norm(read(new), False)
        if a == b: ok += 1
        else:
            diff += 1
            sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
            worst.append((sm.ratio(), rel, [(tag, a[i1:i2][:2], b[j1:j2][:2]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal'][:4]))
    print('identiche', ok, 'diverse', diff)
    for r, rel, ops in sorted(worst)[:5]:
        print('---', round(r, 4), rel)
        for o in ops: print('  ', str(o)[:600])

if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if c in ('gen', 'all'): gen()
    if c in ('build', 'all'): build()
    if c in ('compare', 'all'): compare()
