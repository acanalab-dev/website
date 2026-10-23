#!/usr/bin/env python3
"""Builds the guides of every app on acanalab.com and the shared sitemap.

Each app in APPS has its sources in <folder>/guides/_src/:
  guides.json   one entry per guide (metadata, FAQ, related guides)
  <slug>.html   the article body (h2 sections with ids)

Run from anywhere:  python3 _tools/build_guides.py
With no arguments it builds every app. Pass folder names to rebuild only
those apps' guides (python3 _tools/build_guides.py honeynest); sitemap.xml
and robots.txt always list the pages of every app, so one app's build never
drops another app's pages. Writes <folder>/guides/<slug>/index.html, each
guides hub, sitemap.xml and robots.txt. Underscore folders are skipped by
GitHub Pages.
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://acanalab.com"

# Site pages outside any app that belong in the sitemap.
SITE_PAGES = ["/", "/privacy-policy", "/terms-of-use"]

APPS = [
    {
        "folder": "dailyaffirmationsapp",
        "name": "Daily Affirmations",
        "icon": "/app-icon.png",
        "guides_label": "Affirmation guides",
        "box_heading": "Make it a daily habit",
        "hub_title": "Affirmation Guides: Tips, Lists and Routines | Daily Affirmations",
        "hub_description": "Practical guides to affirmations: ready-to-use lists, how to write your own, and simple routines to make positive self-talk a daily habit.",
        "hub_lead": "Practical, no-fluff guides to affirmations: ready-to-use lists for every part of life, how to write your own, and simple routines that make the habit stick.",
        "hub_get": "Fresh affirmations every morning. Free to download. For iPhone.",
        "static_pages": ["/dailyaffirmationsapp/", "/dailyaffirmationsapp/privacy-policy",
                         "/dailyaffirmationsapp/terms-of-use"],
        # App Store campaign tags (ct=) on each badge; store.js adds pt= and mt=.
        "campaigns": False,
    },
    {
        "folder": "honeynest",
        "name": "HoneyNest",
        "icon": "/honeynest/app-icon.png",
        "guides_label": "Couples money guides",
        "box_heading": "Track it together",
        "hub_title": "Couples Money Guides: Splitting Bills and Shared Expenses | HoneyNest",
        "hub_description": "Practical guides for couples on splitting bills, tracking shared expenses and talking about money, with worked examples and checklists.",
        "hub_lead": "Practical guides for couples on splitting bills, tracking shared expenses and talking about money. Worked examples and checklists, no jargon. General tips only, not financial advice.",
        "hub_get": "Track shared expenses with your partner. Free to download. For iPhone.",
        "static_pages": ["/honeynest/", "/honeynest/privacy-policy", "/honeynest/terms-of-use"],
        "campaigns": True,
    },
]

e = html.escape


def version(path):
    """Short content hash for cache busting: browsers refetch a file only when it changes."""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def store(ct=None):
    """App Store badge; the app's store.js fills in the link (with the ct= campaign when given)."""
    data = f' data-ct="{ct}"' if ct else ""
    return f"""<a class="store soon" href="#"{data} target="_blank" rel="noopener" aria-label="Download on the App Store">
      <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M16.37 12.6c-.02-2.2 1.8-3.26 1.88-3.31-1.02-1.5-2.62-1.7-3.19-1.72-1.36-.14-2.65.8-3.34.8-.69 0-1.75-.78-2.88-.76-1.48.02-2.85.86-3.61 2.19-1.54 2.67-.39 6.62 1.11 8.79.73 1.06 1.6 2.25 2.75 2.2 1.1-.04 1.52-.71 2.85-.71s1.71.71 2.88.69c1.19-.02 1.94-1.08 2.67-2.14.84-1.23 1.19-2.42 1.21-2.48-.03-.01-2.32-.89-2.33-3.55zM14.17 6.13c.61-.74 1.02-1.76.91-2.78-.88.04-1.94.59-2.57 1.32-.56.65-1.06 1.69-.93 2.69.98.08 1.98-.5 2.59-1.23z"/></svg>
      <span><small>Download on the</small><b>App Store</b></span>
    </a>"""


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


class App:
    def __init__(self, cfg):
        self.cfg = cfg
        self.folder = cfg["folder"]
        self.name = cfg["name"]
        self.dir = ROOT / self.folder
        self.guides_dir = self.dir / "guides"
        self.src = self.guides_dir / "_src"
        self.path = f"/{self.folder}/"
        self.url = f"{SITE}{self.path}"
        self.hub_url = f"{self.url}guides/"
        self.css_v = version(self.guides_dir / "guides.css")
        self.store_v = version(self.dir / "store.js")

    def guides(self):
        return json.loads((self.src / "guides.json").read_text())

    def store(self, ct):
        return store(ct if self.cfg["campaigns"] else None)

    def head(self, title, description, url, image, extra_ld):
        ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in extra_ld)
        icon = self.cfg["icon"]
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
<link rel="icon" type="image/png" href="{icon}">
<link rel="apple-touch-icon" href="{icon}">
<link rel="stylesheet" href="{self.path}guides/guides.css?v={self.css_v}">
{ld}
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="home" href="{self.path}"><img src="{icon}" alt="" width="32" height="32">{e(self.name)}</a>
  <nav><a href="{self.path}guides/">Guides</a><a class="get" href="{self.path}">Get the app</a></nav>
</div></header>
"""

    def foot(self):
        p = self.path
        return f"""<script src="{p}store.js?v={self.store_v}"></script>
<footer><div><b>© 2026 acanalab</b><a href="{p}">{e(self.name)}</a><a href="{p}guides/">Guides</a><a href="{p}privacy-policy">Privacy Policy</a><a href="{p}terms-of-use">Terms of Use</a></div></footer>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "4be6ca5b24cc460ebc172901ce154768"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""

    def card(self, g):
        return f'<li><a href="{self.path}guides/{g["slug"]}/"><b>{e(g["h1"])}</b><span>{e(g["card"])}</span></a></li>'

    def build_guide(self, g, by_slug):
        url = f"{self.hub_url}{g['slug']}/"
        body = (self.src / f"{g['slug']}.html").read_text()
        toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
        image = f"{self.url}{g['image']}"
        ld = [
            {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"],
             "description": g["description"], "image": image, "datePublished": g["published"],
             "dateModified": g.get("modified", g["published"]), "mainEntityOfPage": url,
             "author": {"@type": "Organization", "name": "acanalab", "url": SITE + "/"},
             "publisher": {"@type": "Organization", "name": "acanalab", "url": SITE + "/"}},
            {"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                            for q, a in g["faq"]]},
            crumbs_ld([(self.name, self.url), ("Guides", self.hub_url), (g["h1"], url)]),
        ]
        toc_html = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
        faq_html = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in g["faq"])
        related = "\n".join(self.card(by_slug[s]) for s in g["related"] if s in by_slug)
        w, h = g.get("image_size", [600, 1304])
        page = self.head(g["title"] + f" | {self.name}", g["description"], url, image, ld) + f"""
<main class="wrap">
<article>
<p class="crumbs"><a href="{self.path}">{e(self.name)}</a> › <a href="{self.path}guides/">Guides</a></p>
<h1>{e(g["h1"])}</h1>
<p class="lead">{e(g["lead"])}</p>
<p class="meta">Updated {g.get("modified", g["published"])}</p>
<nav class="toc" aria-label="Contents"><b>In this guide</b><ol>{toc_html}<li><a href="#faq">FAQ</a></li></ol></nav>

{body.strip()}

<aside class="app">
  <img src="{self.path}{g["image"]}" alt="{e(g["image_alt"])}" width="{w}" height="{h}" loading="lazy">
  <div>
    <h2>{e(self.cfg["box_heading"])}</h2>
    <p>{e(g["app_text"])}</p>
    {self.store(g.get("ct", g["slug"]))}
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
""" + self.foot()
        out = self.guides_dir / g["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page)

    def build_hub(self, guides):
        c = self.cfg
        ld = [crumbs_ld([(self.name, self.url), ("Guides", self.hub_url)]),
              {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["guides_label"], "url": self.hub_url,
               "hasPart": [{"@type": "Article", "headline": g["h1"], "url": f"{self.hub_url}{g['slug']}/"} for g in guides]}]
        newest = sorted(guides, key=lambda g: g["published"], reverse=True)
        cards = "\n".join(self.card(g) for g in newest)
        page = self.head(c["hub_title"], c["hub_description"], self.hub_url, f"{self.url}og-image.jpg", ld) + f"""
<main class="wrap">
<article>
<p class="crumbs"><a href="{self.path}">{e(self.name)}</a> › Guides</p>
<h1>{e(c["guides_label"])}</h1>
<p class="lead">{e(c["hub_lead"])}</p>
<ul class="cards">
{cards}
</ul>
<aside class="get-app">
  <img src="{c["icon"]}" alt="" width="56" height="56">
  <h2>Get {e(self.name)}</h2>
  <p>{e(c["hub_get"])}</p>
  {self.store("guides-hub")}
</aside>
</article>
</main>
""" + self.foot()
        (self.guides_dir / "index.html").write_text(page)

    def build(self):
        guides = self.guides()
        by_slug = {g["slug"]: g for g in guides}
        for g in guides:
            self.build_guide(g, by_slug)
        self.build_hub(guides)
        return len(guides)

    def sitemap_urls(self):
        guides = self.guides()
        urls = [(SITE + p, None) for p in self.cfg["static_pages"]]
        if guides:
            urls.append((self.hub_url, max(g["published"] for g in guides)))
        urls += [(f"{self.hub_url}{g['slug']}/", g.get("modified", g["published"])) for g in guides]
        return urls


def build_sitemap(apps):
    urls = [(SITE + p, None) for p in SITE_PAGES]
    for app in apps:
        urls += app.sitemap_urls()
    rows = "\n".join(f"  <url><loc>{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>" for u, d in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    return len(urls)


def main(selected):
    apps = [App(c) for c in APPS]
    unknown = set(selected) - {a.folder for a in apps}
    if unknown:
        sys.exit(f"Unknown app folder(s): {', '.join(sorted(unknown))}")
    for app in apps:
        if not selected or app.folder in selected:
            print(f"{app.name}: built {app.build()} guides and hub")
    print(f"sitemap.xml ({build_sitemap(apps)} URLs, all apps) and robots.txt")


if __name__ == "__main__":
    main(sys.argv[1:])
