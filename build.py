#!/usr/bin/env python3
"""HowMuchYarn.com site generator — v2 premium design.

SOURCES (edit these, then run `python3 build.py`):
  projects.json, guides.json,
  assets/css/main.css, assets/js/calculator.js, assets/img/*

GENERATED (never hand-edit — rerun the builder instead):
  index.html, projects/*.html, guides/*.html,
  about.html, contact.html, privacy-policy.html, terms.html,
  sitemap.xml, robots.txt
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://howmuchyarn.com"
SITE_NAME = "How Much Yarn"
TODAY = date(2026, 10, 7).isoformat()
YEAR = 2026
CONTACT_EMAIL = "hello@howmuchyarn.com"

# Set to True when ready to show ads (e.g. after AdSense approval).
# When False, ad slots are omitted from the generated pages entirely —
# flip the flag and rebuild to bring them back.
SHOW_ADS = False

# ---------------------------------------------------------------- data ---
def load_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

PROJECTS = load_json("projects.json")
GUIDES = load_json("guides.json")

def load_calc_data():
    src = (ROOT / "assets" / "js" / "calculator.js").read_text(encoding="utf-8")
    def grab(var):
        m = re.search(r"var %s = (\{.*?\n\});" % var, src, re.S)
        if not m:
            raise RuntimeError(var + " not found in calculator.js")
        return json.loads(re.sub(r"(\w+):", r'"\1":', m.group(1)))
    def grab_list(var):
        m = re.search(r"var %s = (\[.*?\n\]);" % var, src, re.S)
        if not m:
            raise RuntimeError(var + " not found in calculator.js")
        return json.loads(re.sub(r"(\w+):", r'"\1":', m.group(1)))
    return grab("PROJECT_YARDAGE"), grab_list("YARN_WEIGHTS"), grab("PROJECT_LABELS")

YARDAGE, WEIGHTS, LABELS = load_calc_data()
WEIGHT_ORDER = [w["id"] for w in WEIGHTS]
WEIGHT_NAME = {w["id"]: w["name"] for w in WEIGHTS}
WEIGHT_SKEIN = {w["id"]: w["skeinYards100g"] for w in WEIGHTS}
PROJ_BY_KEY = {p["key"]: p for p in PROJECTS}

# project key -> card/hero image
PROJECT_IMG = {
    "baby-blanket": "project-blanket.jpg", "throw-blanket": "project-blanket.jpg",
    "twin-blanket": "project-blanket.jpg", "queen-blanket": "project-blanket.jpg",
    "king-blanket": "project-blanket.jpg", "scarf": "project-scarf.jpg",
    "cowl": "project-cowl.jpg", "hat": "project-hat.jpg", "socks": "project-socks.jpg",
    "mittens": "project-mittens.jpg", "sweater": "project-sweater.jpg",
    "baby-sweater": "project-baby-sweater.jpg", "cardigan": "project-cardigan.jpg",
    "shawl": "project-shawl.jpg", "vest": "project-sweater.jpg",
    "market-bag": "project-market-bag.jpg", "amigurumi": "project-amigurumi.jpg",
    "rug": "project-rug.jpg",
}
GUIDE_IMG = {
    "yarn-weight-chart-explained": "guide-yarn-weight.jpg",
    "how-to-read-a-yarn-label": "guide-yarn-label.jpg",
    "fingering-vs-dk-vs-worsted": "guide-stitch-patterns.jpg",
    "how-to-substitute-yarn-in-a-pattern": "guide-substituting.jpg",
    "best-yarn-for-baby-blankets": "guide-choosing-yarn.jpg",
    "yarn-buffer-rule": "guide-buying-tips.jpg",
    "crochet-vs-knitting-yarn-usage": "guide-knitting-vs-crochet.jpg",
    "temperature-blanket-yarn-planning": "guide-yardage-charts.jpg",
}
POPULAR = [  # (project key, card label) — matches the approved mockup
    ("sweater", "Sweaters"), ("hat", "Hats"), ("scarf", "Scarves"),
    ("shawl", "Shawls"), ("throw-blanket", "Blankets"), ("market-bag", "Market Bag"),
]

def img_url(name):
    return f"{SITE}/assets/img/{name}"

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

# Relative prefix for internal links and assets: "" on root-level pages,
# "../" on pages one directory down (projects/, guides/).
# Relative URLs keep every page styled and clickable when the zip is opened
# locally via file://, and behave identically once deployed at the domain root.
# (Canonicals, OG tags, sitemap, and JSON-LD stay absolute — SEO requires it.)
RP = ""

# ------------------------------------------------------------ json-ld ---
def ld_org():
    return {"@context": "https://schema.org", "@type": "Organization",
            "name": SITE_NAME, "url": SITE + "/",
            "logo": img_url("logo-icon.png")}

def ld_website():
    return {"@context": "https://schema.org", "@type": "WebSite",
            "name": SITE_NAME, "url": SITE + "/",
            "description": "Free yarn yardage calculator: find out how much yarn you need for any knit or crochet project."}

def ld_webapp():
    return {"@context": "https://schema.org", "@type": "WebApplication",
            "name": "Yarn Yardage Calculator", "url": SITE + "/",
            "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "description": "Free interactive calculator: enter your project, yarn weight, and skein size to get exact yardage and skein counts."}

def ld_faq(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                           for f in faqs]}

def ld_breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                 "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def ld_article(g, image):
    secs = " ".join(re.sub(r"<[^>]+>", " ", s["html"]) for s in g["sections"])
    text = (g.get("lede") or "") + " " + secs
    return {"@context": "https://schema.org", "@type": "Article",
            "headline": g["h1"], "image": img_url(image),
            "author": {"@type": "Organization", "name": SITE_NAME},
            "publisher": {"@type": "Organization", "name": SITE_NAME,
                          "logo": {"@type": "ImageObject", "url": img_url("logo-icon.png")}},
            "datePublished": "2026-10-02", "dateModified": TODAY,
            "description": g["meta_desc"],
            "mainEntityOfPage": SITE + "/guides/" + g["slug"] + ".html"}

def ld_script(*objs):
    return '<script type="application/ld+json">\n' + json.dumps(
        list(objs), indent=1) + '\n</script>'

# --------------------------------------------------------- templates ---
FONTS_URL = ("https://fonts.googleapis.com/css2?"
             "family=Playfair+Display:wght@600;700;800&"
             "family=Inter:wght@400;500;600;700&"
             "family=Pinyon+Script&display=swap")

def head(title, desc, canon_path, og_image, ld_objs):
    canon = SITE + canon_path
    return f"""<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#355A47">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" type="image/png" sizes="32x32" href="{RP}assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{RP}assets/img/favicon-16.png">
<link rel="apple-touch-icon" href="{RP}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS_URL}" rel="stylesheet">
<link rel="stylesheet" href="{RP}assets/css/main.css">
{ld_script(*ld_objs)}
</head>"""

def site_header(active):
    def nav(href, label, key):
        cls = ' class="active"' if active == key else ""
        return f'<a href="{href}"{cls}>{label}</a>'
    return f"""<header class="site-header">
<div class="container header-inner">
<a class="brand" href="{RP}index.html" aria-label="{SITE_NAME} home">
<img src="{RP}assets/img/logo-icon.png" alt="{SITE_NAME} logo" width="38" height="38">
<span>How Much <span class="yarn">Yarn</span></span>
</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
</button>
<nav class="main-nav" id="site-nav" aria-label="Main navigation">
{nav(RP + "index.html", "Calculator", "calc")}
{nav(RP + "projects/index.html", "Projects", "projects")}
{nav(RP + "guides/index.html", "Guides", "guides")}
<a class="search-btn" href="{RP}projects/index.html" aria-label="Browse all projects">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
</a>
</nav>
</div>
</header>"""

def site_footer():
    proj_links = "".join(
        f'<li><a href="{RP}projects/{p["slug"]}.html">{esc(LABELS[p["key"]])}</a></li>'
        for p in PROJECTS[:6])
    guide_links = "".join(
        f'<li><a href="{RP}guides/{g["slug"]}.html">{esc(g["h1"])}</a></li>'
        for g in GUIDES[:5])
    return f"""<footer class="site-footer">
<div class="container">
<div class="footer-grid">
<div>
<div class="footer-brand">
<img src="{RP}assets/img/logo-icon.png" alt="" width="34" height="34">
<span>How Much <span class="yarn">Yarn</span></span>
</div>
<p>The free yarn yardage calculator for knitters and crocheters. Accurate estimates, skein counts, and plain-English guides — no guesswork, no wasted yarn.</p>
</div>
<div>
<h3>Popular projects</h3>
<ul>{proj_links}</ul>
</div>
<div>
<h3>Guides</h3>
<ul>{guide_links}</ul>
</div>
<div>
<h3>About</h3>
<ul>
<li><a href="{RP}about.html">About us</a></li>
<li><a href="{RP}contact.html">Contact</a></li>
<li><a href="{RP}privacy-policy.html">Privacy policy</a></li>
<li><a href="{RP}terms.html">Terms of use</a></li>
</ul>
</div>
</div>
<p class="disclosure"><strong>Disclosure:</strong> {SITE_NAME} is reader-supported. We display ads to keep the calculator free for everyone; advertising never influences our yardage estimates.</p>
<div class="footer-bottom">
<span>&copy; {YEAR} {SITE_NAME}. Free yarn yardage calculator.</span>
<span>Yardage figures are planning estimates — always check your pattern.</span>
</div>
</div>
</footer>"""

def cookie_bar():
    return f"""<div class="cookie-bar" id="cookie-bar" role="dialog" aria-label="Cookie notice">
<p>We use cookies to keep the site working and to show ads that keep the calculator free. See our <a href="{RP}privacy-policy.html">privacy policy</a>.</p>
<button type="button">Got it</button>
</div>"""

def base(title, desc, canon_path, og_image, ld_objs, body, active=""):
    return f"""<!DOCTYPE html>
<html lang="en">
{head(title, desc, canon_path, og_image, ld_objs)}
<body>
<a class="skip-link" href="#main">Skip to content</a>
{site_header(active)}
<main id="main">
{body}
</main>
{site_footer()}
{cookie_bar()}
<script src="{RP}assets/js/calculator.js" defer></script>
</body>
</html>"""

def ad_slot():
    if not SHOW_ADS:
        return ""
    return """<div class="container"><div class="ad-slot" aria-hidden="true">
<!-- AdSense: paste your responsive display ad code inside this .ad-slot div -->
<div class="ad-ph">Responsive ad<br>(replaced by your AdSense code)</div>
</div></div>"""

def faq_block(faqs):
    items = "".join(
        f"<details><summary>{esc(f['q'])}</summary><div class=\"a\"><p>{esc(f['a'])}</p></div></details>"
        for f in faqs)
    return f'<div class="faq">{items}</div>'

def guide_card(g, desc=False):
    """Guide card with the short display title (SEO title stays in <title>/H1)."""
    d = f'\n<span class="desc">{esc(g["meta_desc"][:120])}…</span>' if desc else ""
    return f"""<a class="pcard guides" href="{RP}guides/{g["slug"]}.html">
<img src="{RP}assets/img/{GUIDE_IMG[g["slug"]]}" alt="{esc(g["h1"])}" loading="lazy" width="640" height="400">
<span class="cap">{esc(g.get("card") or g["h1"])} <span class="go" aria-hidden="true">&rarr;</span></span>{d}</a>"""

# ---------------------------------------------- calculator widget ---
ICONS = {
    "project": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 4v16M4 12h16"/></svg>',
    "weight": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3 3 8l9 5 9-5-9-5zM3 13l9 5 9-5"/></svg>',
    "skein": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 17V7m0 10h16M4 7h16M7 7v10M17 7v10"/></svg>',
    "buffer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z"/></svg>',
}

def calc_widget(preset=""):
    return f"""<div class="calc-grid" id="yarn-calc" data-preset-project="{preset}">
<div class="card">
<div class="card-head">
<span class="mark"><img src="{RP}assets/img/logo-icon.png" alt="" width="40" height="40"></span>
<div><h2>Calculate Your Yarn Needs</h2>
<p>Select your project, yarn weight, and enter your yarn details to get an instant estimate.</p></div>
</div>
<div class="field-grid">
<div class="field">
<label for="f-project">{ICONS["project"]} Project</label>
<select id="f-project" data-field="project" aria-label="Project"></select>
</div>
<div class="field">
<label for="f-weight">{ICONS["weight"]} Yarn weight</label>
<select id="f-weight" data-field="weight" aria-label="Yarn weight"></select>
</div>
<div class="field">
<label for="f-skein">{ICONS["skein"]} Yards per skein <span style="font-weight:400">(from your label)</span></label>
<input id="f-skein" data-field="skein" type="number" min="1" inputmode="numeric" value="220" aria-describedby="skein-hint">
<p class="hint" id="skein-hint">Auto-filled for the chosen weight — change it to match your yarn.</p>
</div>
<div class="field">
<label for="f-buffer">{ICONS["buffer"]} Safety buffer (%)</label>
<input id="f-buffer" data-field="buffer" type="number" min="0" max="50" inputmode="numeric" value="10" aria-describedby="buffer-hint">
<p class="hint" id="buffer-hint">10–15% covers gauge differences and mistakes.</p>
</div>
</div>
<button class="btn-primary" data-action="calculate" type="button">Calculate Yarn <span class="arr">&rsaquo;</span></button>
</div>
<div class="card results-card" aria-live="polite">
<div class="card-head">
<span class="mark" style="background:var(--sage)"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--forest)" stroke-width="2" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/></svg></span>
<div><h2>Your Results</h2>
<p>Your estimated yarn yardage and skein count.</p></div>
</div>
<div data-field="result"></div>
</div>
</div>"""

# ------------------------------------------------------------ index ---
INDEX_FAQS = [
    {"q": "How does the yarn yardage calculator work?",
     "a": "Pick your project and yarn weight, enter the yardage printed on your yarn label, and the calculator returns total yardage (in yards and meters) plus how many skeins to buy — with a safety buffer for gauge differences and mistakes."},
    {"q": "How accurate are the yardage estimates?",
     "a": "They are planning estimates for average-size projects and typical gauges, drawn from standard craft references (Lion Brand, Craft Yarn Council charts). Your gauge, stitch pattern, and finished size move the numbers, which is why we add a 10–15% buffer and always recommend one extra skein."},
    {"q": "Does crochet use more yarn than knitting?",
     "a": "Yes — crochet generally uses about 25–30% more yarn than knitting for the same finished size, because crochet stitches are taller and denser. If you are adapting a knit estimate for a crochet project, add roughly a quarter more yardage."},
    {"q": "What does yarn weight mean?",
     "a": "Yarn weight is the Craft Yarn Council's name for strand thickness, numbered 0 (lace, thinnest) to 6 (super bulky, thickest). It is not the physical weight of the skein. Thicker yarn needs fewer total yards, but each skein also holds fewer yards."},
    {"q": "How many skeins of yarn do I need?",
     "a": "Divide your total estimated yardage (including buffer) by the yardage per skein on your yarn label, then round up. The calculator does this automatically — enter your label's yards-per-skein and it reports the exact skein count."},
    {"q": "Should I buy extra yarn beyond the estimate?",
     "a": "Yes. Buy at least one extra skein beyond the estimate. Running out mid-project is risky because dye lots vary between batches and the same color can look slightly different."},
]

def build_index():
    global RP; RP = ""
    badges = "".join([
        ('<span class="badge"><span class="ic g"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8h12l1 12H5L6 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg></span>All project types</span>'),
        ('<span class="badge"><span class="ic t"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8 7.5 20 19M8 16.5 20 5"/></svg></span>Knit &amp; crochet</span>'),
        ('<span class="badge"><span class="ic g"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h8M8 16h5"/></svg></span>Accurate estimates</span>'),
        ('<span class="badge"><span class="ic t"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20s-7-4.5-9-9c-1.2-2.7.5-6 3.7-6 2 0 3.7 1.2 5.3 3.4 1.6-2.2 3.3-3.4 5.3-3.4 3.2 0 4.9 3.3 3.7 6-2 4.5-9 9-9 9z"/></svg></span>Free to use</span>'),
    ])

    popular_cards = "".join(
        f"""<a class="pcard" href="{RP}projects/{PROJ_BY_KEY[k]["slug"]}.html">
<img src="{RP}assets/img/{PROJECT_IMG[k]}" alt="{esc(label)} — how much yarn you need" loading="lazy" width="400" height="400">
<span class="cap">{esc(label)} <span class="go" aria-hidden="true">&rarr;</span></span></a>"""
        for k, label in POPULAR)

    glance_rows = "".join(
        f"""<tr><td><a href="{RP}projects/{PROJ_BY_KEY[k]["slug"]}.html">{esc(LABELS[k])}</a></td>"""
        f"""<td class="num">{YARDAGE[k]["worsted"]:,} yds</td>"""
        f"""<td>{-(-int(YARDAGE[k]["worsted"] * 1.1) // WEIGHT_SKEIN["worsted"])} skeins*</td></tr>"""
        for k in ["baby-blanket", "throw-blanket", "scarf", "hat", "sweater", "shawl"])

    guide_cards = "".join(guide_card(g) for g in GUIDES)

    body = f"""<section class="hero"><div class="container hero-grid">
<div>
<p class="eyebrow">Free yarn calculator</p>
<h1>How Much Yarn Do You Need?</h1>
<p class="hero-sub">Get accurate yarn estimates for knitting and crochet projects. Find yardage and skein counts in seconds.</p>
<div class="badges">{badges}</div>
</div>
<div class="hero-media">
<img src="{RP}assets/img/hero.jpg" alt="Basket of yarn in terracotta, sage and cream with knitting needles" width="1200" height="750" fetchpriority="high">
<span class="hero-script" aria-hidden="true">Make<br>your next<br>project with<br>confidence</span>
</div>
</div></section>

<section class="calc-section"><div class="container">
{calc_widget()}
</div></section>

{ad_slot()}

<section class="section"><div class="container">
<div class="section-head">
<div><h2>Popular Projects</h2><p>Choose a project to see typical yardage ranges, helpful tips, and FAQs.</p></div>
<a class="link-more" href="{RP}projects/index.html">View all projects &rarr;</a>
</div>
<div class="cards">{popular_cards}</div>
</div></section>

<section class="section alt"><div class="container">
<div class="section-head"><div><h2>How it works</h2><p>Three steps to a shopping list you can trust.</p></div></div>
<div class="steps">
<div class="step"><span class="num">01</span><h3>Pick your project &amp; yarn weight</h3><p>Choose from 18 project types and 7 standard yarn weights, from lace to super bulky.</p></div>
<div class="step"><span class="num">02</span><h3>Enter your skein details</h3><p>Yards-per-skein auto-fills for the weight — or type the exact number from your yarn label.</p></div>
<div class="step"><span class="num">03</span><h3>Get yardage + skein count</h3><p>Instant totals in yards and meters, with a 10–15% safety buffer built in.</p></div>
</div>
</div></section>

<section class="section"><div class="container">
<div class="section-head"><div><h2>Yardage at a glance</h2><p>Worsted-weight estimates for popular projects (10% buffer included in skein counts).</p></div></div>
<div class="table-wrap"><table class="chart">
<thead><tr><th>Project</th><th>Estimated yardage</th><th>Skeins of 220 yd*</th></tr></thead>
<tbody>{glance_rows}</tbody>
</table></div>
<p class="hint" style="margin-top:10px">*Rounded up, with a 10% safety buffer. Exact counts vary by gauge and size — use the calculator above for your yarn.</p>
</div></section>

{ad_slot()}

<section class="section alt"><div class="container">
<div class="section-head">
<div><h2>Yarn guides</h2><p>Learn the math behind the estimates.</p></div>
<a class="link-more" href="{RP}guides/index.html">View all guides &rarr;</a>
</div>
<div class="cards guides">{guide_cards}</div>
</div></section>

<section class="section"><div class="container">
<div class="section-head"><div><h2>Frequently asked questions</h2></div></div>
<div class="prose" style="max-width:56em">{faq_block(INDEX_FAQS)}</div>
</div></section>

{ad_slot()}"""

    html = base(
        title="Yarn Yardage Calculator: How Much Yarn Do You Need? (Free)",
        desc="Free yarn yardage calculator: find out how much yarn you need for blankets, sweaters, scarves, hats and more — yardage and skein counts in seconds.",
        canon_path="/",
        og_image=img_url("hero.jpg"),
        ld_objs=[ld_org(), ld_website(), ld_webapp(), ld_faq(INDEX_FAQS)],
        body=body, active="calc")
    (ROOT / "index.html").write_text(html, encoding="utf-8")

# -------------------------------------------------- projects pages ---
def chart_rows(key):
    rows = []
    for wid in WEIGHT_ORDER:
        if wid not in YARDAGE[key]:
            continue
        yds = YARDAGE[key][wid]
        skeins = -(-int(yds * 1.1) // WEIGHT_SKEIN[wid])  # ceil, 10% buffer
        rows.append(
            f"<tr><td>{esc(WEIGHT_NAME[wid])}</td>"
            f'<td class="num">{yds:,} yds</td>'
            f"<td>{skeins} skeins</td></tr>")
    return "".join(rows)

def build_project(p):
    global RP; RP = "../"
    key = p["key"]
    img = PROJECT_IMG[key]
    label = LABELS[key]
    intro = "".join(f"<p>{x}</p>" for x in p["intro"])
    crumbs = [("Home", SITE + "/"), ("Projects", SITE + "/projects/"), (p["h1"], SITE + "/projects/" + p["slug"] + ".html")]

    related = [q for q in PROJECTS if q["key"] != key][:3]
    rel_cards = "".join(
        f"""<a class="pcard" href="{q["slug"]}.html">
<img src="{RP}assets/img/{PROJECT_IMG[q["key"]]}" alt="{esc(LABELS[q["key"]])} yarn yardage" loading="lazy" width="400" height="400">
<span class="cap">{esc(LABELS[q["key"]])} <span class="go" aria-hidden="true">&rarr;</span></span></a>"""
        for q in related)

    body = f"""<div class="container">
<nav class="breadcrumb" aria-label="Breadcrumb"><a href="{RP}index.html">Home</a> &rsaquo; <a href="index.html">Projects</a> &rsaquo; {esc(p["h1"])}</nav>
<article class="prose" style="max-width:none">
<h1>{esc(p["h1"])}</h1>
<div class="article-hero"><img src="{RP}assets/img/{img}" alt="{esc(p["h1"])}" width="1200" height="514" loading="lazy"></div>
<div class="prose">
<p class="lede">{esc(p["intro"][0])}</p>
{"".join(f"<p>{x}</p>" for x in p["intro"][1:])}
<div class="dims"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 9V5h4M20 15v4h-4M4 5l6 6M20 19l-6-6"/></svg><span><strong>Typical size:</strong> {esc(p["dims"])}</span></div>
</div>
<h2>Yardage chart: {esc(label.lower())} by yarn weight</h2>
<div class="table-wrap"><table class="chart">
<thead><tr><th>Yarn weight</th><th>Estimated yardage</th><th>Skeins needed*</th></tr></thead>
<tbody>{chart_rows(key)}</tbody>
</table></div>
<p class="hint" style="margin-top:10px">*Skein counts use typical skein sizes for each weight and include a 10% safety buffer, rounded up. Always check your yarn label — skein sizes vary by brand.</p>

<div class="cta-band">
<div><h2>Get your exact numbers</h2><p>Run {esc(label.lower())} through the free calculator with your yarn's label details.</p></div>
<a class="btn-light" href="{RP}index.html?project={key}">Calculate my yardage &rsaquo;</a>
</div>

<h2>Frequently asked questions</h2>
{faq_block(p["faqs"])}

<div class="related">
<div class="section-head"><div><h2>Related projects</h2></div><a class="link-more" href="index.html">View all &rarr;</a></div>
<div class="cards" style="grid-template-columns:repeat(3,1fr)">{rel_cards}</div>
</div>
</article>
</div>
{ad_slot()}"""

    html = base(
        title=p["title"], desc=p["meta_desc"],
        canon_path="/projects/" + p["slug"] + ".html",
        og_image=img_url(img),
        ld_objs=[ld_org(), ld_breadcrumb(crumbs), ld_faq(p["faqs"])],
        body=body, active="projects")
    (ROOT / "projects" / (p["slug"] + ".html")).write_text(html, encoding="utf-8")

def build_projects_index():
    global RP; RP = "../"
    cards = "".join(
        f"""<a class="pcard" href="{p["slug"]}.html">
<img src="{RP}assets/img/{PROJECT_IMG[p["key"]]}" alt="{esc(LABELS[p["key"]])} — yarn yardage and skein counts" loading="lazy" width="400" height="400">
<span class="cap">{esc(LABELS[p["key"]])} <span class="go" aria-hidden="true">&rarr;</span></span>
<span class="desc">{esc(p["meta_desc"][:110])}…</span></a>"""
        for p in PROJECTS)
    body = f"""<div class="container">
<nav class="breadcrumb" aria-label="Breadcrumb"><a href="{RP}index.html">Home</a> &rsaquo; Projects</nav>
<h1 style="margin-bottom:8px">Yarn Yardage by Project</h1>
<p class="hero-sub" style="margin-top:0">Pick your project for detailed yardage charts, skein counts, and FAQs — then run the numbers through the free calculator.</p>
<div class="cards" style="margin:30px 0 10px">{cards}</div>
</div>
{ad_slot()}"""
    html = base(
        title="Yarn Yardage by Project: Charts for 18 Knit & Crochet Projects",
        desc="Yardage charts and skein counts for 18 knit and crochet projects — blankets, sweaters, scarves, hats, socks and more, by yarn weight.",
        canon_path="/projects/",
        og_image=img_url("hero.jpg"),
        ld_objs=[ld_org(), ld_breadcrumb([("Home", SITE + "/"), ("Projects", SITE + "/projects/")])],
        body=body, active="projects")
    (ROOT / "projects" / "index.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------- guides pages ---
def build_guide(g):
    global RP; RP = "../"
    img = GUIDE_IMG[g["slug"]]
    secs = "".join(f'<h2>{esc(s["h2"])}</h2>\n{s["html"]}' for s in g["sections"])
    crumbs = [("Home", SITE + "/"), ("Guides", SITE + "/guides/"), (g["h1"], SITE + "/guides/" + g["slug"] + ".html")]
    others = [h for h in GUIDES if h["slug"] != g["slug"]][:3]
    rel = "".join(guide_card(h) for h in others)
    body = f"""<div class="container">
<nav class="breadcrumb" aria-label="Breadcrumb"><a href="{RP}index.html">Home</a> &rsaquo; <a href="index.html">Guides</a> &rsaquo; {esc(g["h1"])}</nav>
<article style="max-width:none">
<h1>{esc(g["h1"])}</h1>
<div class="article-hero"><img src="{RP}assets/img/{img}" alt="{esc(g["h1"])}" width="1200" height="514" loading="lazy"></div>
<div class="prose">
<p class="lede">{esc(g["lede"])}</p>
{secs}
</div>
<div class="cta-band">
<div><h2>Turn this into exact yardage</h2><p>Use the free calculator to convert what you learned into yardage and skein counts.</p></div>
<a class="btn-light" href="{RP}index.html">Open the calculator &rsaquo;</a>
</div>
<h2>Frequently asked questions</h2>
{faq_block(g["faqs"])}
<div class="related">
<div class="section-head"><div><h2>More guides</h2></div><a class="link-more" href="index.html">View all &rarr;</a></div>
<div class="cards guides">{rel}</div>
</div>
</article>
</div>
{ad_slot()}"""
    html = base(
        title=g["title"], desc=g["meta_desc"],
        canon_path="/guides/" + g["slug"] + ".html",
        og_image=img_url(img),
        ld_objs=[ld_org(), ld_breadcrumb(crumbs), ld_article(g, img), ld_faq(g["faqs"])],
        body=body, active="guides")
    (ROOT / "guides" / (g["slug"] + ".html")).write_text(html, encoding="utf-8")

def build_guides_index():
    global RP; RP = "../"
    cards = "".join(guide_card(g, desc=True) for g in GUIDES)
    body = f"""<div class="container">
<nav class="breadcrumb" aria-label="Breadcrumb"><a href="{RP}index.html">Home</a> &rsaquo; Guides</nav>
<h1 style="margin-bottom:8px">Yarn Guides</h1>
<p class="hero-sub" style="margin-top:0">The math behind the estimates: yarn weights, labels, substitution, buffers, and buying tips.</p>
<div class="cards guides" style="margin:30px 0 10px">{cards}</div>
</div>
{ad_slot()}"""
    html = base(
        title="Yarn Guides: Weights, Labels, Substitution & Yardage Tips",
        desc="Plain-English yarn guides: weight charts, reading yarn labels, substituting yarn, the buffer rule, and buying tips for knitters and crocheters.",
        canon_path="/guides/",
        og_image=img_url("guide-yarn-weight.jpg"),
        ld_objs=[ld_org(), ld_breadcrumb([("Home", SITE + "/"), ("Guides", SITE + "/guides/")])],
        body=body, active="guides")
    (ROOT / "guides" / "index.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------- policy pages ---
def policy_page(fname, title, desc, h1, prose_html):
    global RP; RP = ""
    body = f"""<div class="container">
<nav class="breadcrumb" aria-label="Breadcrumb"><a href="{RP}index.html">Home</a> &rsaquo; {esc(h1)}</nav>
<article class="prose">
<h1>{esc(h1)}</h1>
{prose_html}
</article>
</div>"""
    html = base(title=title, desc=desc, canon_path="/" + fname,
                og_image=img_url("hero.jpg"),
                ld_objs=[ld_org(), ld_breadcrumb([("Home", SITE + "/"), (h1, SITE + "/" + fname)])],
                body=body)
    (ROOT / fname).write_text(html, encoding="utf-8")

def build_policies():
    global RP; RP = ""
    policy_page("about.html",
        "About How Much Yarn — Free Yarn Yardage Calculator",
        "About How Much Yarn: the free yarn yardage calculator built for knitters and crocheters, with honest planning estimates and plain-English guides.",
        "About How Much Yarn",
        f"""<p class="lede">How Much Yarn is a free tool for knitters and crocheters who are tired of guessing at the yarn shop.</p>
<p>Every project page pairs a yardage chart — drawn from standard craft references such as Lion Brand and Craft Yarn Council guidelines — with an instant calculator that converts your yarn label's numbers into yardage and skein counts, including a safety buffer for gauge differences and mistakes.</p>
<p>We keep the tool free by showing ads. Advertising never influences our estimates: the math is the math, and the buffer guidance is the same advice you'd get at a good local yarn shop — buy one extra skein.</p>
<h2>What you'll find here</h2>
<ul><li><strong>The calculator</strong> — 18 project types, 7 yarn weights, instant yardage and skein counts.</li>
<li><strong>Project pages</strong> — yardage charts by yarn weight, typical sizes, and answers to common questions.</li>
<li><strong>Guides</strong> — yarn weights, reading labels, substitution math, and buying tips in plain English.</li></ul>
<h2>Contact</h2>
<p>Questions, corrections, or a project you'd like us to add? <a href="{RP}contact.html">Get in touch</a> — we read everything.</p>""")

    policy_page("contact.html",
        "Contact How Much Yarn",
        "Contact the How Much Yarn team: questions about the yarn yardage calculator, corrections, or project requests.",
        "Contact Us",
        f"""<p class="lede">Questions about an estimate, a correction to a chart, or a project you'd like us to add? We'd love to hear from you.</p>
<div class="contact-form">
<form action="mailto:{CONTACT_EMAIL}" method="post" enctype="text/plain">
<div class="field"><label for="c-name">Your name</label><input id="c-name" name="name" type="text" required autocomplete="name"></div>
<div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" required autocomplete="email"></div>
<div class="field"><label for="c-msg">Message</label><textarea id="c-msg" name="message" required></textarea></div>
<button class="btn-primary" type="submit" style="width:auto">Send message</button>
<p class="hint">This opens your email app addressed to {CONTACT_EMAIL}. We aim to reply within a few days.</p>
</form>
</div>""")

    policy_page("privacy-policy.html",
        "Privacy Policy — How Much Yarn",
        "Privacy policy for How Much Yarn: what data we collect, how cookies and advertising (Google AdSense) work, and your choices.",
        "Privacy Policy",
        f"""<p class="lede">Last updated: October 7, 2026. How Much Yarn ("we") respects your privacy. This policy explains what we collect and why.</p>
<h2>Information we collect</h2>
<p><strong>Calculator inputs.</strong> Everything you type into the calculator runs entirely in your browser — project, yarn weight, and skein details are never sent to our servers.</p>
<p><strong>Contact messages.</strong> If you email us, we receive your name, email address, and message so we can reply. We don't sell or share it.</p>
<p><strong>Analytics.</strong> We may use privacy-respecting analytics to understand which pages are popular. This data is aggregated and never tied to your identity.</p>
<h2>Cookies and advertising</h2>
<p>We show ads to keep the calculator free. Our advertising partners, including Google AdSense, may use cookies to serve ads based on your prior visits to this and other sites. Google's use of advertising cookies enables it and its partners to serve ads based on your visit to our site.</p>
<p>You may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" rel="noopener">Google's Ads Settings</a>. You can also clear or block cookies in your browser settings; the calculator works fine without them (your cookie-consent choice is stored on your own device).</p>
<h2>Data retention and your rights</h2>
<p>We keep contact emails only as long as needed to respond. You may ask us to delete your message at any time by emailing {CONTACT_EMAIL}.</p>
<h2>Children</h2>
<p>This site is a general-audience craft tool and is not directed at children under 13. We do not knowingly collect data from children.</p>
<h2>Changes</h2>
<p>We may update this policy as the site evolves; the "last updated" date above will change accordingly.</p>""")

    policy_page("terms.html",
        "Terms of Use — How Much Yarn",
        "Terms of use for How Much Yarn: estimates are planning guidance, acceptable use, and liability limits.",
        "Terms of Use",
        """<p class="lede">Last updated: October 7, 2026. By using How Much Yarn you agree to these terms.</p>
<h2>Estimates are planning guidance</h2>
<p>Yardage figures are planning estimates for average-size projects and typical gauges, drawn from standard craft references. Your gauge, stitch pattern, and finished size change the numbers. Always check your pattern's yardage, buy an extra skein, and confirm dye lots match before starting a large project. We are not liable for yarn shortages, over-purchases, or project outcomes.</p>
<h2>Acceptable use</h2>
<p>Use the calculator and content for personal, non-commercial purposes. Don't scrape the site aggressively, attempt to disrupt it, or republish our charts and guides as your own.</p>
<h2>Intellectual property</h2>
<p>Site design, copy, and photography are ours (or licensed to us). Project yardage data is compiled from public craft references; the presentation is original.</p>
<h2>Advertising</h2>
<p>We display third-party ads to keep the service free. Ad content is the responsibility of the advertisers.</p>
<h2>Changes</h2>
<p>We may update these terms; continued use of the site after changes means you accept them.</p>""")

# ------------------------------------------------------------- seo ---
def build_sitemap(urls):
    items = "\n".join(
        f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>'
        for u, cf, pr in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n',
        encoding="utf-8")

def build_robots():
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

# ----------------------------------------------------------------- ---
def main():
    (ROOT / "projects").mkdir(exist_ok=True)
    (ROOT / "guides").mkdir(exist_ok=True)

    build_index()
    build_projects_index()
    for p in PROJECTS:
        build_project(p)
    build_guides_index()
    for g in GUIDES:
        build_guide(g)
    build_policies()

    urls = [(SITE + "/", "weekly", "1.0"),
            (SITE + "/projects/", "weekly", "0.9"),
            (SITE + "/guides/", "weekly", "0.9")]
    urls += [(SITE + "/projects/" + p["slug"] + ".html", "monthly", "0.8") for p in PROJECTS]
    urls += [(SITE + "/guides/" + g["slug"] + ".html", "monthly", "0.7") for g in GUIDES]
    urls += [(SITE + "/about.html", "yearly", "0.4"),
             (SITE + "/contact.html", "yearly", "0.4"),
             (SITE + "/privacy-policy.html", "yearly", "0.3"),
             (SITE + "/terms.html", "yearly", "0.3")]
    build_sitemap(urls)
    build_robots()

    pages = 1 + 1 + len(PROJECTS) + 1 + len(GUIDES) + 4
    print(f"Built {pages} pages + sitemap.xml + robots.txt -> {ROOT}")

if __name__ == "__main__":
    main()
