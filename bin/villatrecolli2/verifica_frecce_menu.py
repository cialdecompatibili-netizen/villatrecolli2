"""Verifica: ogni voce di primo livello con sottomenu (li.menu-item-has-children.fusion-dropdown-menu, escluso il selettore lingua)
deve avere la freccetta (fusion-megamenu-icon). Uso: python verifica_frecce_menu.py [cartella_out]  (default: _out nella repo)
La freccia viene aggiunta in automatico da pubblica_statico.py a ogni deploy: se qui trovi mancanze, il deploy non e' stato rieseguito."""
import os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_out")
RX = re.compile(r'<li\b(?=[^>]*\bmenu-item-has-children\b)(?=[^>]*\bfusion-dropdown-menu\b)(?![^>]*wpml-ls)[^>]*>(?:\s*<span\b[^>]*></span>)*\s*<a\b[^>]*>(.*?)</a>', re.S)
tot = mancano = 0
for dp, dn, fn in os.walk(OUT):
    dn[:] = [d for d in dn if d not in ("wp-content", "wp-includes", "admin")]
    for f in fn:
        if not f.endswith(".html"): continue
        p = os.path.join(dp, f)
        for m in RX.finditer(open(p, encoding="utf8", errors="replace").read()):
            tot += 1
            if "fusion-megamenu-icon" not in m.group(1):
                mancano += 1
                if mancano < 10: print("MANCA:", p, re.sub(r"<[^>]+>", "", m.group(1)).strip())
print("voci con sottomenu:", tot, "senza freccia:", mancano)
