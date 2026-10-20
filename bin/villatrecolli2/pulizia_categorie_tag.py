import re, subprocess
R = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
def git(*a):
    r = subprocess.run(["git", "-C", R] + list(a), capture_output=True, text=True, encoding="utf8", errors="replace")
    if r.returncode: print("GIT ERR", a, r.stderr[:200])
    return r.stdout
for d in ["shop-online", "tag-prodotto", "en/tag-prodotto"]:
    git("rm", "-r", "-q", "-f", d)
fl = [x for x in git("ls-files", "*.html").split("\n") if x and not x.startswith(("wp-", "_out", "_avada"))]
n = 0
for f in fl:
    p = R + "/" + f
    t = open(p, "rb").read().decode("utf8", "surrogateescape")
    if not re.search(r"categoria-prodotto/software", t): continue
    en = f.startswith("en/") or "software-en" in f
    L = "Services" if en else "Servizi"
    o = t
    t = t.replace(">Software<", ">%s<" % L).replace("Software Archivi", "%s Archivi" % L).replace("Software Archives", "%s Archives" % L)
    t = re.sub(r'("name":")Software(")', r"\g<1>%s\2" % L, t)
    t = t.replace('title="Software"', 'title="%s"' % L).replace('aria-label="Software"', 'aria-label="%s"' % L)
    if t != o:
        open(p, "wb").write(t.encode("utf8", "surrogateescape")); n += 1
print("categoria rinominata in", n, "file")
left = [f for f in fl if re.search(r">Software<|Software Archivi|\"name\":\"Software\"", open(R + "/" + f, "rb").read().decode("utf8", "surrogateescape"))]
print("residui Software:", left)
