#!/usr/bin/env python3
"""Add/refresh JSON-LD on the homepage (creator offer) and the Daily Affirmations app page.

Idempotent: replaces the block between <!-- schema:start --> and <!-- schema:end -->.
The homepage FAQ schema is generated from its <details><summary> FAQ, so rerun after editing it.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://acanalab.com"
ORG = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "acanalab", "url": f"{SITE}/",
       "logo": f"{SITE}/app-icon.png", "email": "support@acanalab.com"}


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def inject(path, graph):
    p = ROOT / path
    t = p.read_text()
    block = ('<!-- schema:start -->\n<script type="application/ld+json">\n'
             + json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=1, ensure_ascii=False)
             + "\n</script>\n<!-- schema:end -->\n")
    if "<!-- schema:start -->" in t:
        t = re.sub(r"<!-- schema:start -->.*?<!-- schema:end -->\n", lambda m: block, t, flags=re.S)
    else:
        t = t.replace("</head>", block + "</head>", 1)
    p.write_text(t)


home = (ROOT / "index.html").read_text()
faq = [{"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}}
       for q, a in re.findall(r"<details>\s*<summary>(.*?)</summary>\s*(.*?)</details>", home, re.S)]
inject("index.html", [
    ORG,
    {"@type": "Service", "@id": f"{SITE}/#service", "name": "White-label affirmations app for creators",
     "serviceType": "White-label iPhone app for creators and influencers",
     "description": ("acanalab builds and publishes a fully branded daily affirmations iPhone app for "
                     "creators and influencers, under the creator's own Apple developer account. No setup fee: "
                     "the creator keeps about 70% of net subscription sales (50/50 on the first $10,000), "
                     "paid by Apple monthly. A passive income stream that fits wellness, mindset and lifestyle audiences."),
     "provider": {"@id": f"{SITE}/#org"}, "url": f"{SITE}/", "areaServed": "Worldwide",
     "audience": {"@type": "Audience", "audienceType": "Content creators, influencers, coaches"},
     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                "description": "No upfront cost; revenue share on subscription sales."}},
    {"@type": "WebPage", "@id": f"{SITE}/#webpage", "url": f"{SITE}/", "name": "Your Own Affirmations App",
     "about": {"@id": f"{SITE}/#service"}, "publisher": {"@id": f"{SITE}/#org"}},
    {"@type": "FAQPage", "mainEntity": faq},
])

inject("dailyaffirmationsapp/index.html", [
    ORG,
    {"@type": "MobileApplication", "@id": f"{SITE}/dailyaffirmationsapp/#app", "name": "Daily Affirmations",
     "operatingSystem": "iOS", "applicationCategory": "LifestyleApplication",
     "url": f"{SITE}/dailyaffirmationsapp/",
     "installUrl": "https://apps.apple.com/app/id6809586170",
     "sameAs": ["https://apps.apple.com/app/id6809586170", "https://www.pinterest.com/getdailyaffirmationsapp/"],
     "image": f"{SITE}/dailyaffirmationsapp/og-image.jpg",
     "description": ("Daily Affirmations is a free iPhone app with fresh positive affirmations every day, "
                     "streaks, gentle reminders, Home Screen and Lock Screen widgets and shareable cards. "
                     "Free with no time limit; Premium adds widgets, every category, every card style and unlimited favorites."),
     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
     "publisher": {"@id": f"{SITE}/#org"}},
])
print(f"homepage FAQ items: {len(faq)}")
