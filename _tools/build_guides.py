#!/usr/bin/env python3
"""Builds the Daily Affirmations guides and the site sitemap.

Sources live in dailyaffirmationsapp/guides/_src/:
  guides.json   one entry per guide (metadata, FAQ, related guides)
  <slug>.html   the article body (h2 sections with ids)

Run from anywhere:  python3 _tools/build_guides.py
Writes dailyaffirmationsapp/guides/<slug>/index.html, the guides hub,
sitemap.xml and robots.txt. Underscore folders are skipped by GitHub Pages.
"""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://acanalab.com"
APP = ROOT / "dailyaffirmationsapp"
GUIDES = APP / "guides"
SRC = GUIDES / "_src"
APP_URL = f"{SITE}/dailyaffirmationsapp/"
HUB_URL = f"{APP_URL}guides/"

# Pages outside the guides that belong in the sitemap.
STATIC_PAGES = ["/", "/dailyaffirmationsapp/", "/privacy-policy", "/terms-of-use",
                "/dailyaffirmationsapp/privacy-policy", "/dailyaffirmationsapp/terms-of-use"]

e = html.escape


def version(path):
    """Short content hash for cache busting: browsers refetch a file only when it changes."""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


CSS_V = version(GUIDES / "guides.css")
STORE_V = version(APP / "store.js")

# Same badge as the app page; dailyaffirmationsapp/store.js fills in the App Store link.
STORE = """<a class="store soon" href="#" target="_blank" rel="noopener" aria-label="Download on the App Store">
      <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M16.37 12.6c-.02-2.2 1.8-3.26 1.88-3.31-1.02-1.5-2.62-1.7-3.19-1.72-1.36-.14-2.65.8-3.34.8-.69 0-1.75-.78-2.88-.76-1.48.02-2.85.86-3.61 2.19-1.54 2.67-.39 6.62 1.11 8.79.73 1.06 1.6 2.25 2.75 2.2 1.1-.04 1.52-.71 2.85-.71s1.71.71 2.88.69c1.19-.02 1.94-1.08 2.67-2.14.84-1.23 1.19-2.42 1.21-2.48-.03-.01-2.32-.89-2.33-3.55zM14.17 6.13c.61-.74 1.02-1.76.91-2.78-.88.04-1.94.59-2.57 1.32-.56.65-1.06 1.69-.93 2.69.98.08 1.98-.5 2.59-1.23z"/></svg>
      <span><small>Download on the</small><b>App Store</b></span>
    </a>"""


def head(title, description, url, image, extra_ld):
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in extra_ld)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/app-icon.png">
<link rel="apple-touch-icon" href="/app-icon.png">
<link rel="stylesheet" href="/dailyaffirmationsapp/guides/guides.css?v={CSS_V}">
{ld}
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="home" href="/dailyaffirmationsapp/"><img src="/app-icon.png" alt="" width="32" height="32">Daily Affirmations</a>
  <nav><a href="/dailyaffirmationsapp/guides/">Guides</a><a class="get" href="/dailyaffirmationsapp/">Get the app</a></nav>
</div></header>
"""


FOOT = f"""<script src="/dailyaffirmationsapp/store.js?v={STORE_V}"></script>
<footer><div><b>© 2026 acanalab</b><a href="/dailyaffirmationsapp/">Daily Affirmations</a><a href="/dailyaffirmationsapp/guides/">Guides</a><a href="/dailyaffirmationsapp/privacy-policy">Privacy Policy</a><a href="/dailyaffirmationsapp/terms-of-use">Terms of Use</a></div></footer>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "4be6ca5b24cc460ebc172901ce154768"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


def card(g):
    return f'<li><a href="/dailyaffirmationsapp/guides/{g["slug"]}/"><b>{e(g["h1"])}</b><span>{e(g["card"])}</span></a></li>'


def build_guide(g, by_slug):
    url = f"{HUB_URL}{g['slug']}/"
    body = (SRC / f"{g['slug']}.html").read_text()
    toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    image = f"{APP_URL}{g['image']}"
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"],
         "description": g["description"], "image": image, "datePublished": g["published"],
         "dateModified": g.get("modified", g["published"]), "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": "acanalab", "url": SITE + "/"},
         "publisher": {"@type": "Organization", "name": "acanalab", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in g["faq"]]},
        crumbs_ld([("Daily Affirmations", APP_URL), ("Guides", HUB_URL), (g["h1"], url)]),
    ]
    toc_html = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
    faq_html = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in g["faq"])
    related = "\n".join(card(by_slug[s]) for s in g["related"] if s in by_slug)
    page = head(g["title"] + " | Daily Affirmations", g["description"], url, image, ld) + f"""
<main class="wrap">
<article>
<p class="crumbs"><a href="/dailyaffirmationsapp/">Daily Affirmations</a> › <a href="/dailyaffirmationsapp/guides/">Guides</a></p>
<h1>{e(g["h1"])}</h1>
<p class="lead">{e(g["lead"])}</p>
<p class="meta">Updated {g.get("modified", g["published"])}</p>
<nav class="toc" aria-label="Contents"><b>In this guide</b><ol>{toc_html}<li><a href="#faq">FAQ</a></li></ol></nav>

{body.strip()}

<aside class="app">
  <img src="/dailyaffirmationsapp/{g["image"]}" alt="{e(g["image_alt"])}" width="600" height="1304" loading="lazy">
  <div>
    <h2>Make it a daily habit</h2>
    <p>{e(g["app_text"])}</p>
    {STORE}
  </div>
</aside>

<h2 id="faq">Frequently asked questions</h2>
{faq_html}

<h2>Related guides</h2>
<ul class="cards">
{related}
</ul>
</article>
</main>
""" + FOOT
    out = GUIDES / g["slug"] / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)


def build_hub(guides):
    title = "Affirmation Guides: Tips, Lists and Routines | Daily Affirmations"
    desc = "Practical guides to affirmations: ready-to-use lists, how to write your own, and simple routines to make positive self-talk a daily habit."
    ld = [crumbs_ld([("Daily Affirmations", APP_URL), ("Guides", HUB_URL)]),
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Affirmation guides", "url": HUB_URL,
           "hasPart": [{"@type": "Article", "headline": g["h1"], "url": f"{HUB_URL}{g['slug']}/"} for g in guides]}]
    newest = sorted(guides, key=lambda g: g["published"], reverse=True)
    cards = "\n".join(card(g) for g in newest)
    page = head(title, desc, HUB_URL, f"{APP_URL}og-image.jpg", ld) + f"""
<main class="wrap">
<article>
<p class="crumbs"><a href="/dailyaffirmationsapp/">Daily Affirmations</a> › Guides</p>
<h1>Affirmation guides</h1>
<p class="lead">Practical, no-fluff guides to affirmations: ready-to-use lists for every part of life, how to write your own, and simple routines that make the habit stick.</p>
<ul class="cards">
{cards}
</ul>
<aside class="get-app">
  <img src="/app-icon.png" alt="" width="56" height="56">
  <h2>Get Daily Affirmations</h2>
  <p>Fresh affirmations every morning. Free to download. For iPhone.</p>
  {STORE}
</aside>
</article>
</main>
""" + FOOT
    (GUIDES / "index.html").write_text(page)


def build_sitemap(guides):
    urls = [(SITE + p, None) for p in STATIC_PAGES] + [(HUB_URL, max(g["published"] for g in guides))]
    urls += [(f"{HUB_URL}{g['slug']}/", g.get("modified", g["published"])) for g in guides]
    rows = "\n".join(f"  <url><loc>{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>" for u, d in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


def main():
    guides = json.loads((SRC / "guides.json").read_text())
    by_slug = {g["slug"]: g for g in guides}
    for g in guides:
        build_guide(g, by_slug)
    build_hub(guides)
    build_sitemap(guides)
    print(f"Built {len(guides)} guides, hub, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
