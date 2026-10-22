#!/usr/bin/env python3
"""Builds the Daily Affirmations guides and the site sitemap.

Sources live in dailyaffirmationsapp/guides/_src/:
  guides.json   one entry per guide (metadata, FAQ, related guides)
  <slug>.html   the article body (h2 sections with ids)

Run from anywhere:  python3 _tools/build_guides.py
Writes dailyaffirmationsapp/guides/<slug>/index.html, the guides hub,
sitemap.xml and robots.txt. Underscore folders are skipped by GitHub Pages.
"""
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
<link rel="stylesheet" href="/dailyaffirmationsapp/guides/guides.css">
{ld}
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="home" href="/dailyaffirmationsapp/"><img src="/app-icon.png" alt="" width="32" height="32">Daily Affirmations</a>
  <nav><a href="/dailyaffirmationsapp/guides/">Guides</a><a class="get" href="/dailyaffirmationsapp/">Get the app</a></nav>
</div></header>
"""


FOOT = """<footer><div><b>© 2026 acanalab</b><a href="/dailyaffirmationsapp/">Daily Affirmations</a><a href="/dailyaffirmationsapp/guides/">Guides</a><a href="/dailyaffirmationsapp/privacy-policy">Privacy Policy</a><a href="/dailyaffirmationsapp/terms-of-use">Terms of Use</a></div></footer>
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
    <a class="btn" href="/dailyaffirmationsapp/">Get Daily Affirmations for iPhone</a>
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
