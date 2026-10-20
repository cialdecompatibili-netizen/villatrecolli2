"""Come fix_card_grigie.py ma per en/home e le pagine demo element_category: assegna l'immagine per POSIZIONE della card usando index.html come riferimento.
Villa Tre Colli (villatrecolli2). Scritto il 20/10/2026. Lanciare da PowerShell: python <questo file>."""
import os, re

ROOT = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
pat = re.compile(
    r'(data-bg-url=")([^"]+)(")((?:(?!fusion-column-inner-bg-wrapper).)*?)'
    r'(<span class="fusion-column-inner-bg-image[^"]*"[^>]*?data-bg=")([^"]*)(")',
    re.S,
)


def rd(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8", errors="surrogateescape", newline="").read()


ref = [m.group(2) for m in pat.finditer(rd("index.html"))]
tails = [r[r.find("wp-content"):] for r in ref]
print(len(tails), [x.split("/")[-1] for x in tails])

targets = ["en/home/index.html", "element_category/columns/index.html", "element_category/elements/index.html",
           "element_category/post_cards/index.html", "element_category/sections/index.html"]
for rel in targets:
    t = rd(rel)
    k = [0]

    def rep(m):
        i = k[0]
        k[0] += 1
        cur = m.group(2)
        if "immagine-grigia" not in cur or i >= len(tails):
            return m.group(0)
        new = cur[:cur.find("wp-content")] + tails[i]
        return m.group(1) + new + m.group(3) + m.group(4) + m.group(5) + new + m.group(7)

    t2 = pat.sub(rep, t)
    open(os.path.join(ROOT, rel), "w", encoding="utf-8", errors="surrogateescape", newline="").write(t2)
    print(rel, "carte", k[0], "grigie rimaste", len(re.findall(r"immagine-grigia-1\.jpg", t2)))
