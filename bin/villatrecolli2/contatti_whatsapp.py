"""Pagine contatti villatrecolli2: il form WPForms (WordPress) non funziona sul mirror statico -> bottone WhatsApp.
Pagine: contactwp/ (voce di menu 'contatti' IT), en/contactwp/ (EN), contatti/ e en/contact/ (stub con solo il titolo).
Il numero e' quello gia' presente nella barra telefono del sito (tel:+393338495178). Per cambiarlo: modificare WA qui e rilanciare --apply.
Idempotente (riconosce il blocco con id vtc-whatsapp e lo sostituisce). Uso: python contatti_whatsapp.py [--apply]"""
import os, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
APPLY = "--apply" in sys.argv
WA = "393338495178"
TXT = {
 "it": dict(h="Contattaci su WhatsApp", p="Per informazioni, date disponibili e preventivi scrivici direttamente su WhatsApp: ti rispondiamo noi.",
            b="Scrivici su WhatsApp", n="Oppure chiama il +39 333 849 5178", m="Buongiorno, vorrei avere informazioni su Villa Tre Colli."),
 "en": dict(h="Contact us on WhatsApp", p="For information, available dates and quotes, message us directly on WhatsApp: we will reply personally.",
            b="Message us on WhatsApp", n="Or call +39 333 849 5178", m="Hello, I would like some information about Villa Tre Colli."),
}
ICON = '<svg width="24" height="24" viewBox="0 0 32 32" aria-hidden="true" style="vertical-align:middle;margin-right:10px"><path fill="#fff" d="M4 4h24a2 2 0 0 1 2 2v15a2 2 0 0 1-2 2H14l-7 6v-6H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/></svg>'
def block(lang):
    d = TXT[lang]
    from urllib.parse import quote
    href = "https://wa.me/%s?text=%s" % (WA, quote(d["m"]))
    return ('<div id="vtc-whatsapp" style="max-width:640px;margin:40px auto;padding:36px 28px;text-align:center;border:1px solid #e2e2e2;border-radius:6px;">'
            '<h2 style="margin:0 0 14px;">%s</h2><p style="margin:0 0 26px;line-height:1.6;">%s</p>'
            '<a href="%s" target="_blank" rel="noopener" style="display:inline-block;background:#25D366;color:#fff;font-weight:700;font-size:18px;padding:16px 34px;border-radius:40px;text-decoration:none;">%s%s</a>'
            '<p style="margin:22px 0 0;font-size:15px;"><a href="tel:+%s" style="color:inherit;">%s</a></p></div>') % (d["h"], d["p"], href, ICON, d["b"], WA, d["n"])

PAGES = [("contactwp/index.html", "it"), ("en/contactwp/index.html", "en"), ("contatti/index.html", "it"), ("en/contact/index.html", "en")]
for rel, lang in PAGES:
    p = os.path.join(R, *rel.split("/"))
    t = open(p, "rb").read().decode("utf8", "surrogateescape")
    i = t.find('<div class="post-content">')
    if i < 0:
        print(rel, "post-content non trovato"); continue
    seg_end = t.find("</section>", i)
    seg = t[i:seg_end]
    new_seg = None
    m = re.search(r'<div id="vtc-whatsapp".*?</div>\s*(?=</div>|$)', seg, re.S)
    w = re.search(r'<div class="wpforms-container.*?</form>\s*</div>', seg, re.S)
    if w:
        new_seg = seg[:w.start()] + block(lang) + seg[w.end():]
    elif 'id="vtc-whatsapp"' in seg:
        a = seg.find('<div id="vtc-whatsapp"'); b = seg.find("</p></div>", a) + len("</p></div>")
        new_seg = seg[:a] + block(lang) + seg[b:]
    else:
        pm = re.search(r'<p>[^<]{0,40}</p>', seg)
        if pm:
            new_seg = seg[:pm.start()] + block(lang) + seg[pm.end():]
    if new_seg is None:
        print(rel, "nessun form/stub riconosciuto"); continue
    out = t[:i] + new_seg + t[seg_end:]
    print(rel, "OK", "wpforms" if w else "stub/idempotente", len(t), "->", len(out), "(applicato)" if APPLY else "(dry-run)")
    if APPLY and out != t:
        open(p, "wb").write(out.encode("utf8", "surrogateescape"))
