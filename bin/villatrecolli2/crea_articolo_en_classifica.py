"""Crea la versione inglese dell'articolo 'Le 5 Location Piu Belle per Eventi a Monterotondo'
in en/rankings/<slug>/, la inserisce nell'archivio en/category/rankings, nel widget
'Recent Posts' e collega i selettori di lingua IT <-> EN.
Base: pagina en/category/rankings (header/footer/sidebar EN) + corpo articolo della pagina IT."""
import os, re, urllib.parse

R = r"C:\Users\mirco\Desktop\repository\villatrecolli2"
IT_SLUG = "classifica-le-5-location-per-eventi-piu-prestigiose-a-monterotondo-roma"
EN_SLUG = "the-5-most-beautiful-event-venues-in-monterotondo"
IT_PATH = f"classifiche/{IT_SLUG}/index.html"
EN_PATH = f"en/rankings/{EN_SLUG}/index.html"
TITLE = "The 5 Most Beautiful Event Venues in Monterotondo"
DESC = "In this ranking we explore the best event venues in the Monterotondo area, just a stone's throw from Rome."
TITLE_RE = r"Le 5 Location Pi.{1,3}? Belle per Eventi a Monterotondo"
TITLE_ENC_IT = r"Le%205%20Location%20Pi%C3%B9%20Belle%20per%20Eventi%20a%20Monterotondo"
TITLE_ENC_EN = urllib.parse.quote(TITLE)

PARAS = [
 "With its historic charm and enchanting landscapes, Monterotondo is the ideal place to organise memorable events. Whether it is a wedding, a private party or a corporate event, this town offers a variety of venues able to meet every need. Here is an overview of the five best event venues in Monterotondo.",
 "Just outside Rome, in the thriving town of Monterotondo, Villa Tre Colli is set in an Eden of serenity and nature, surrounded by a splendid hilly landscape. This majestic and elegant villa, resting on a green hill, offers a 360-degree panoramic view that lets you enjoy a breathtaking sunset. Villa Tre Colli is perfect for weddings, christenings, communions, birthdays, themed parties, meetings and business dinners. The villa has generous indoor and outdoor spaces, including well-kept gardens and refined halls, which can be personalised to meet every need. The catering and banqueting services on offer are of the highest quality, making sure every event is a success.",
 "Villa Valentini is one of the most prestigious venues in Monterotondo. Located in the heart of the town, this historic villa offers an elegant and refined atmosphere, perfect for weddings and high-end parties. Its large gardens are ideal for outdoor ceremonies, while the tastefully decorated interior halls can host receptions and gala dinners. The villa also has an in-house kitchen providing high-quality catering, making sure every event is a success.",
 "A few kilometres from Monterotondo, the Conventino di Mentana is an ancient convent turned into a splendid event venue. This charming place combines the beauty of historic architecture with the tranquillity of its well-kept gardens. It is the ideal choice for romantic weddings and important celebrations. The Conventino offers several reception halls, each with its own unique character, and outdoor spaces that are perfect for cocktails and aperitifs. Its serene atmosphere and natural beauty make it an unforgettable setting for any event.",
 "Set in nature, Tenuta La Selva is a rustic and charming venue, perfect for outdoor events. Located in a vast green area, this estate offers a relaxed and natural setting, ideal for those who want an informal yet elegant atmosphere. The estate has large green spaces, a swimming pool and welcoming facilities that can host weddings, private parties and corporate events. The beauty of the surrounding landscape and the tranquillity of the place guarantee a unique experience for all guests.",
 "This historic village, located near Monterotondo, is an exclusive venue for prestigious events. With its historic buildings and lush gardens, Borgo Boncompagni Ludovisi offers a unique and unforgettable experience. It is the perfect place for luxury weddings, corporate events and private parties. The village has several reception halls, each with its own style and character, and large outdoor spaces that can be used for ceremonies and cocktails. The combination of history, elegance and natural beauty makes this venue one of the best in the area.",
]
EXCERPT = PARAS[0][:230].rsplit(" ", 1)[0]

def rd(p): return open(os.path.join(R, p), "rb").read().decode("utf8", "surrogateescape")
def wr(p, s):
    os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
    open(os.path.join(R, p), "wb").write(s.encode("utf8", "surrogateescape"))

IT = rd(IT_PATH)
E = rd("en/category/rankings/index.html")
CATIT = rd("category/classifiche/index.html")

def tr_common(s):
    s = re.sub(TITLE_RE, TITLE, s)
    s = s.replace("Luglio 1st, 2024", "July 1st, 2024").replace("Articoli scritti da admin", "Posts by admin")
    s = s.replace("Annulla risposta", "Cancel reply")
    return s

# ---------------- articolo (corpo) ----------------
art = IT[IT.find("<article"):IT.find("</article>") + len("</article>")]
art = tr_common(art)
art = art.replace("../../wp-content/", "../../../wp-content/")
art = art.replace("../../category/classifiche/", "../../category/rankings/")
art = art.replace(f"../../classifiche/{IT_SLUG}/", f"../../rankings/{EN_SLUG}/")
art = art.replace(f'href="/classifiche/{IT_SLUG}/#respond"', f'href="../../rankings/{EN_SLUG}/#respond"')
art = art.replace(">Classifiche</a>", ">Rankings</a>")
art = art.replace('name="wpml_language_code" type="hidden" value="it"', 'name="wpml_language_code" type="hidden" value="en"')
art = art.replace("post-4286", "post-4287").replace("value='4286'", "value='4287'").replace("category-classifiche", "category-rankings")
# paragrafi
h = art.find("</h1>")
end = art.find("</div>", h)
seg = art[h:end]
it = iter(PARAS)
seg = re.sub(r"<p>.*?</p>", lambda m: "<p>%s</p>" % next(it), seg, flags=re.S)
art = art[:h] + seg + art[end:]
# link di condivisione
art = art.replace(f"www.villatrecolli.com%2Fclassifiche%2F{IT_SLUG}%2F", f"www.villatrecolli.com%2Fen%2Frankings%2F{EN_SLUG}%2F")
art = art.replace(f"www.villatrecolli.com/classifiche/{IT_SLUG}/", f"www.villatrecolli.com/en/rankings/{EN_SLUG}/")
art = art.replace(TITLE_ENC_IT, TITLE_ENC_EN)
art = re.sub(re.escape(TITLE_ENC_EN) + r"%0D%0A[^\"&]*", lambda m: TITLE_ENC_EN + "%0D%0A" + urllib.parse.quote(EXCERPT), art)
assert "Monterotondo, con il suo" not in art

# ---------------- pagina ----------------
page = E
page = page.replace(" avada-html-is-archive", "", 1)
page = re.sub(r"<body[^>]*>", lambda m: re.search(r"<body[^>]*>", IT).group(0), page, count=1)
# head
i = page.find('<link rel="alternate" hreflang'); j = page.find("<!-- / Yoast SEO plugin. -->") + len("<!-- / Yoast SEO plugin. -->")
EN_URL = f"https://www.villatrecolli.com/en/rankings/{EN_SLUG}/"
IT_URL = f"https://www.villatrecolli.com/classifiche/{IT_SLUG}/"
IMG = "https://www.villatrecolli.com/wp-content/uploads/2024/07/villa-tre-colli-roma.jpg"
head = f'''<link rel="alternate" hreflang="it" href="{IT_URL}" />
<link rel="alternate" hreflang="en" href="{EN_URL}" />
<link rel="alternate" hreflang="x-default" href="{IT_URL}" />

	<!-- This site is optimized with the Yoast SEO plugin v17.8 - https://yoast.com/wordpress/plugins/seo/ -->
	<title>{TITLE} - Villa Tre Colli &reg;</title>
	<meta name="description" content="{DESC}" />
	<link rel="canonical" href="{EN_URL}" />
	<meta property="og:locale" content="en_US" />
	<meta property="og:type" content="article" />
	<meta property="og:title" content="{TITLE} - Villa Tre Colli &reg;" />
	<meta property="og:description" content="{DESC}" />
	<meta property="og:url" content="{EN_URL}" />
	<meta property="og:site_name" content="Villa Tre Colli &reg;" />
	<meta property="article:published_time" content="2024-07-01T15:33:01+00:00" />
	<meta property="article:modified_time" content="2024-07-01T15:57:03+00:00" />
	<meta property="og:image" content="{IMG}" />
	<meta property="og:image:width" content="900" />
	<meta property="og:image:height" content="900" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:label1" content="Written by" />
	<meta name="twitter:data1" content="admin" />
	<meta name="twitter:label2" content="Est. reading time" />
	<meta name="twitter:data2" content="3 minutes" />
	<script type="application/ld+json" class="yoast-schema-graph">{{"@context":"https://schema.org","@graph":[{{"@type":"WebSite","@id":"https://www.villatrecolli.com/#website","url":"https://www.villatrecolli.com/","name":"Villa Tre Colli \\u00ae","description":"","inLanguage":"en-US"}},{{"@type":"ImageObject","@id":"{EN_URL}#primaryimage","inLanguage":"en-US","url":"{IMG}","contentUrl":"{IMG}","width":900,"height":900}},{{"@type":"WebPage","@id":"{EN_URL}#webpage","url":"{EN_URL}","name":"{TITLE} - Villa Tre Colli \\u00ae","isPartOf":{{"@id":"https://www.villatrecolli.com/#website"}},"primaryImageOfPage":{{"@id":"{EN_URL}#primaryimage"}},"datePublished":"2024-07-01T15:33:01+00:00","dateModified":"2024-07-01T15:57:03+00:00","description":"{DESC}","breadcrumb":{{"@id":"{EN_URL}#breadcrumb"}},"inLanguage":"en-US","potentialAction":[{{"@type":"ReadAction","target":["{EN_URL}"]}}]}},{{"@type":"BreadcrumbList","@id":"{EN_URL}#breadcrumb","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://www.villatrecolli.com/en/home/"}},{{"@type":"ListItem","position":2,"name":"{TITLE}"}}]}}]}}</script>
	<!-- / Yoast SEO plugin. -->'''
page = page[:i] + head + page[j:]
# title bar
page = page.replace('<h1 class="entry-title">Rankings</h1>', f'<h1 class="entry-title">{TITLE}</h1>', 1)
page = page.replace('<span class="breadcrumb_last" aria-current="page">Rankings</span>', f'<span class="breadcrumb_last" aria-current="page">{TITLE}</span>', 1)
# selettore lingua
page = re.sub(r'(title="English" href=")[^"]*(")', lambda m: m.group(1) + f"../../rankings/{EN_SLUG}/" + m.group(2), page)
page = re.sub(r'(title="Italiano" href=")[^"]*(")', lambda m: m.group(1) + f"../../../classifiche/{IT_SLUG}/" + m.group(2), page)
# main
m0 = page.find("<main"); m1 = page.find("</main>")
mainE = page[m0:m1]
sec = re.search(r'<section id="content"[^>]*>', mainE)
aside = mainE.find("<aside")
newmain = mainE[:sec.end()] + "\n\t" + art + "\n\t</section>" + mainE[aside:]
page = page[:m0] + newmain + page[m1:]

# widget Recent Posts (pagina articolo + archivio)
RP = f'<li><a class="wp-block-latest-posts__post-title" href="../../rankings/{EN_SLUG}/">{TITLE}</a></li>'
def recent(s, href_prefix):
    s = s.replace("<h2>Post recenti</h2>", "<h2>Recent Posts</h2>")
    return re.sub(r'(<ul class="wp-block-latest-posts__list wp-block-latest-posts">)(</ul>)',
                  lambda m: m.group(1) + RP.replace("../../rankings", href_prefix) + m.group(2), s, count=1)
page = recent(page, "../../rankings")
wr(EN_PATH, page)

# ---------------- archivio categoria EN ----------------
card = re.search(r'<article [^>]*fusion-post-large[^>]*>.*?</article>', CATIT, re.S).group(0)
card = tr_common(card)
card = card.replace("../../wp-content/", "../../../wp-content/")
card = card.replace("../../category/classifiche/", "../../category/rankings/")
card = card.replace(f"../../classifiche/{IT_SLUG}/", f"../../rankings/{EN_SLUG}/")
card = card.replace(">Classifiche</a>", ">Rankings</a>").replace("post-4286", "post-4287").replace("category-classifiche", "category-rankings")
card = re.sub(r'(<div class="fusion-post-content-container">\s*<p>).*?(</p>)', lambda m: m.group(1) + EXCERPT + " [...]" + m.group(2), card, count=1, flags=re.S)
cat = E
cat = re.sub(r'(<div class="fusion-posts-container[^>]*>)(\s*)(</div>)', lambda m: m.group(1) + "\n" + card + "\n" + m.group(3), cat, count=1)
cat = recent(cat, "../../rankings")
wr("en/category/rankings/index.html", cat)

# ---------------- selettore lingua nella pagina IT ----------------
pat = re.compile(r'<li\s+id="menu-item-wpml-ls-74-(?:it|en)".*?(?=</ul></nav>)', re.S)
src = pat.findall(CATIT)
dst = pat.findall(IT)
print("switcher blocchi:", len(src), len(dst))
if src and len(src) == len(dst):
    k = iter(src)
    def sw(m):
        b = next(k)
        b = re.sub(r'(title="Italiano" href=")[^"]*(")', lambda x: x.group(1) + f"../../classifiche/{IT_SLUG}/" + x.group(2), b)
        b = re.sub(r'(title="English" href=")[^"]*(")', lambda x: x.group(1) + f"../../en/rankings/{EN_SLUG}/" + x.group(2), b)
        return b
    IT2 = pat.sub(sw, IT)
    # hreflang
    IT2 = IT2.replace(f'<link rel="alternate" hreflang="x-default" href="{IT_URL}" />',
                      f'<link rel="alternate" hreflang="en" href="{EN_URL}" />\n<link rel="alternate" hreflang="x-default" href="{IT_URL}" />', 1)
    wr(IT_PATH, IT2)
print("ok", EN_PATH)
