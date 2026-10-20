import os, glob, json, subprocess, shutil, re
R = r'C:\Users\mirco\Desktop\repository\servizi.lazio'
os.chdir(R)
base = '/servizi.lazio'
pages = sorted(os.path.relpath(f, '_avada_site/anteprima').replace(os.sep, '/')[:-len('/index.html')]
               for f in glob.glob('_avada_site/anteprima/**/index.html', recursive=True)
               if 'confronto' not in f)
pages = [p for p in pages if p and p != '.']
opts = ''.join('<option value="%s"%s>%s</option>' % (p, ' selected' if p == 'blog/elettricista' else '', p) for p in pages)
html = '''<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>Confronto originale / Jekyll</title>
<style>body{margin:0;font:14px system-ui;background:#222;color:#eee}header{padding:8px;display:flex;gap:10px;align-items:center}
select{max-width:60vw;padding:4px}.c{display:flex;height:calc(100vh - 44px)}.c div{flex:1;display:flex;flex-direction:column;border-left:2px solid #555}
.c b{padding:4px 8px;background:#333}iframe{flex:1;border:0;background:#fff}</style></head><body>
<header><b>Pagina:</b><select id="s">%s</select><a style="color:#fed03d" id="a" target="_blank">apri solo Jekyll</a>
<span style="opacity:.7">sinistra = sito attuale (mirror statico) &middot; destra = stessa pagina generata da Jekyll</span></header>
<div class="c"><div><b>ORIGINALE (mirror)</b><iframe id="l"></iframe></div><div><b>JEKYLL (anteprima)</b><iframe id="r"></iframe></div></div>
<script>var B="%s",s=document.getElementById("s");function g(){var p=s.value;l.src=B+"/"+p+"/";r.src=B+"/anteprima/"+p+"/";a.href=r.src;history.replaceState(0,"","#"+p)}
if(location.hash.length>1)s.value=decodeURIComponent(location.hash.slice(1));s.onchange=g;g();</script></body></html>''' % (opts, base)
os.makedirs('_avada_site/anteprima/confronto', exist_ok=True)
open('_avada_site/anteprima/confronto/index.html', 'w', encoding='utf8').write(html)
print(len(pages), 'pagine')
