# SEO Strategy: rank howmuchyarn.com fast for "yarn yardage calculator"

Researched 2026-10-07. Keyword foundation: `yarn-keywords-seo.xlsx` (88 keywords, 12 short-tail + 76 long-tail, 10 flagged top wins).

## 1. The opening (why this is winnable)

A fresh SERP check for **"yarn yardage calculator"** shows no dominant brand owning the term.
The top results are thin, aging blog tutorials — "calculate yardage by weighing your yarn,"
"yardage by swatch" — on small craft blogs (most 1–3 years old, rarely updated). Nobody offers
what we offer: a **real interactive project-based calculator** on an **exact-match domain**.

That gives us three compounding edges:
1. **Exact-match domain** — howmuchyarn.com *is* the query. Still unregistered as of 2026-10-07 (RDAP 404). **Register it now** before someone else does.
2. **Tool UX signals** — an interactive calculator earns long dwell time, low bounce, and return visits. Google reads those as satisfaction signals, especially for "calculator" intent queries.
3. **Long-tail moat** — 18 project pages target "how much yarn for X" / "how many skeins for X" (all Easy tier), each with yardage charts + FAQs. Competitors have one generic page; we have a topical cluster.

## 2. What's already baked into the build

- Unique titles (50–60 chars) + meta descriptions (150–160) on all 33 pages
- Canonicals, OG/Twitter cards with real images, `theme-color`
- JSON-LD: Organization + WebSite everywhere; WebApplication on the calculator; FAQPage on all Q&A content; BreadcrumbList; Article on guides
- Semantic HTML5, single H1 per page, descriptive alt text
- Internal linking: every project page deep-links into the calculator (`?project=`), related-project cards, guide ↔ project cross-links
- Speed: static HTML, one small CSS file, one small JS file, no frameworks, deferred scripts, lazy-loaded images
- AdSense-ready: 3 reserved-height ad slots/page (no CLS), cookie consent, privacy/terms/about/contact, ad disclosure in footer

## 3. 90-day rank-fast plan

### Days 1–7 — Launch the right way
- [ ] Register howmuchyarn.com; point it at Cloudflare Pages (repo → `tool-site-yarn`, output = repo root)
- [ ] Force HTTPS + www→apex (or apex→www) single canonical; verify canonicals resolve
- [ ] Submit sitemap.xml in Google Search Console + Bing Webmaster Tools; request indexing on `/` first
- [ ] Set up GA4 (or privacy-friendly analytics) + Search Console from day one — you can't improve what you don't measure

### Days 8–30 — Get the long tail indexed and clicked
- [ ] Request indexing for all 18 project pages + 8 guides (GSC URL inspection, a few per day — looks natural)
- [ ] **Pinterest** is the highest-ROI channel for this niche: create pins for each project chart ("How much yarn for a baby blanket? — chart"), link to the page. Craft content lives on Pinterest.
- [ ] Answer 2–3 real questions/week on r/knitting, r/crochet, Ravelry forums with genuinely helpful answers + link only when it directly answers the question (no spam — one removal hurts more than ten links help)
- [ ] Add the site to 5–10 free tool/calculator directories

### Days 31–90 — Build topical authority
- [ ] Publish one new guide or project page every 1–2 weeks (the generator makes this cheap: add JSON, run `build.py`). Priority from the keyword sheet: temperature blankets, granny-square math, amigurumi sizing
- [ ] Outreach: email 20 craft bloggers/pattern designers offering the calculator as a free embed/link resource for their patterns ("link your readers to exact yardage") — resource-page links convert well in this niche
- [ ] Refresh dates quarterly ("Updated October 2026") — freshness matters against stale 2023–2024 competitors
- [ ] Once 15+ pages are indexed with steady impressions, apply for AdSense (policy pages + real content already in place)

## 4. What to watch (weekly, 10 minutes)

- Search Console: impressions/clicks for "yarn yardage calculator" + top 5 long-tails; average position trend
- Which project pages get clicks → expand those topics first (more sizes, more weights)
- Calculator engagement: if bounce is high on `/`, the hero/CTA needs work, not the SEO
- Competitor watch: if a big brand (Lion Brand, Yarnspirations) ships a calculator, our moat becomes the long-tail cluster + Pinterest traffic — keep publishing

## 5. What NOT to do

- Don't buy links or use AI-content farms — one manual action erases months of clean work
- Don't keyword-stuff; the copy already targets one keyword per page
- Don't change URLs after launch — the slugs are the asset
- Don't apply for AdSense before there's real indexed content + some traffic (rejection slows you down)
