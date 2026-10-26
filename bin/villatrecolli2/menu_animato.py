"""Menu: (1) mobile leggibile = stesso look del dropdown desktop (fondo bianco, testo scuro #212934, barra nera sopra),
(2) animazione delicata al passaggio del mouse / tocco: sottolineatura verde che cresce sotto la voce (+ barretta verde a sinistra e
leggero scorrimento del testo nel menu mobile).
Causa del bug: Avada mette i link del menu mobile a #cccccc !important su sfondo #fff (illeggibili).
Inserisce <style id="vtc-menu-animato"> prima di </head> in tutte le pagine che hanno il menu Avada. Idempotente: per cambiare CSS
modificare CSS qui sotto e rilanciare (il blocco viene sostituito). Villa Tre Colli (villatrecolli2).
Uso (PowerShell): python bin\\villatrecolli2\\menu_animato.py          -> dry-run
                  python bin\\villatrecolli2\\menu_animato.py --apply  -> scrive"""
import os, re, sys

ROOT = r"C:\Users\Mirco\Desktop\repository\villatrecolli2"
SKIP = {".git", "_out", "_cestino", "wp-content", "wp-includes", "node_modules", "_avada", "modules_source", "__pycache__"}
APPLY = "--apply" in sys.argv

W = ".fusion-menu-element-wrapper"
L = W + " .fusion-menu-element-list"
TOP = L + ">li>a .menu-text"
SUB = L + " .sub-menu>li>a>span:not(.fusion-megamenu-icon)"
M = W + ".collapse-enabled:not(#vtc-m)"          # :not(#id) = specificita' alta, batte le regole Avada con !important
GREEN = "#a0ce4e"
DARK = "#212934"
STATI = [":hover", ":focus-within", ":active"]


def sel_state(kind, stati, suffix):
    base = L + ">li" if kind == "top" else L + " .sub-menu>li"
    tail = ">a .menu-text" if kind == "top" else ">a>span:not(.fusion-megamenu-icon)"
    return ",".join(base + s + tail + suffix for s in stati)


css = []
# --- 1) sottolineatura animata (desktop + mobile)
for tgt in (TOP, SUB):
    css.append(tgt + "{position:relative;display:inline-block;transition:transform .3s cubic-bezier(.22,.61,.36,1)}")
    css.append(tgt + "::after{content:'';position:absolute;left:0;right:0;bottom:-6px;height:2px;border-radius:2px;"
               "background:linear-gradient(90deg,rgba(160,206,78,0),%s 25%%,%s 75%%,rgba(160,206,78,0));"
               "transform:scaleX(0);transform-origin:center;opacity:0;pointer-events:none;"
               "transition:transform .38s cubic-bezier(.22,.61,.36,1),opacity .3s ease}" % (GREEN, GREEN))
for kind in ("top", "sub"):
    css.append(sel_state(kind, STATI, "::after") + "{transform:scaleX(1);opacity:1}")
    css.append(sel_state(kind, [".current-menu-item"], "::after") + "{transform:scaleX(1);opacity:.55}")

# --- 2) mobile: stesso look del dropdown desktop, testo leggibile
css.append(M + " .fusion-menu-element-list{box-shadow:0 -4px 0 0 #000,0 14px 30px rgba(0,0,0,.18)}")
css.append(M + " ul li>a{color:%s!important;font-size:16px;font-weight:500;letter-spacing:.2px;"
               "border-bottom:1px solid rgba(33,41,52,.08);"
               "transition:background-color .28s ease,box-shadow .28s ease}" % DARK)
css.append(M + " ul li>a .fusion-megamenu-icon{color:%s!important}" % DARK)
css.append(M + " ul li>.fusion-open-nav-submenu-on-click:before{color:%s!important}" % DARK)
css.append(M + " ul.sub-menu li>a{font-size:15px;font-weight:400;background:#f9f9fb!important;padding-left:2.4em!important}")
hov = ",".join(M + " ul li" + s + ">a" for s in STATI + [".current-menu-item", ".current-menu-ancestor", ".current-menu-parent", ".expanded"])
css.append(hov + "{color:%s!important;background:#f3f4f7!important;box-shadow:inset 4px 0 0 0 %s}" % (DARK, GREEN))
css.append(",".join(M + " ul li" + s + ">a .menu-text" for s in STATI) + "{transform:translateX(5px)}")
css.append(",".join(M + " ul li" + s + ">a>span:not(.fusion-megamenu-icon)" for s in STATI) + "{transform:translateX(5px)}")
css.append(M + " ul li.current-menu-item>a{font-weight:600}")

# --- 3) rispetto di chi disattiva le animazioni
css.append("@media (prefers-reduced-motion:reduce){" + TOP + "," + SUB + "," + TOP + "::after," + SUB + "::after,"
           + M + " ul li>a{transition:none!important}}")

BLOCCO = '<style id="vtc-menu-animato">' + "".join(css) + "</style>"
pat = re.compile(r'<style id="vtc-menu-animato">.*?</style>', re.S)

tot = nuove = aggiornate = senza_menu = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
        tot += 1
        if "fusion-menu-element-wrapper" not in t:
            senza_menu += 1
            continue
        if 'id="vtc-menu-animato"' in t:
            t2 = pat.sub(lambda m: BLOCCO, t, count=1)
            if t2 == t:
                continue
            aggiornate += 1
        else:
            i = t.find("</head>")
            if i < 0:
                continue
            t2 = t[:i] + BLOCCO + t[i:]
            nuove += 1
        if APPLY:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t2)

print(("SCRITTO" if APPLY else "DRY-RUN (nessun file toccato; aggiungi --apply)"))
print("html letti %d | con menu: nuove %d, aggiornate %d | senza menu Avada %d" % (tot, nuove, aggiornate, senza_menu))
print("dimensione blocco CSS: %d byte" % len(BLOCCO))
