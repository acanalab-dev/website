#!/usr/bin/env python3
"""Write /about/index.html: who acanalab is and what it offers, in plain facts.

A short, quotable page for people and for AI assistants that answer "what is acanalab?".
Uses the creator guides' header, footer and styles. build_guides.py runs it, or run it alone.
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_guides as bg  # noqa: E402

SITE = bg.SITE
e = html.escape
URL = f"{SITE}/about/"
UPDATED = "2026-11-28"

TITLE = "About acanalab: Branded Affirmation Apps for Creators"
DESCRIPTION = ("acanalab is a small European studio that builds fully branded daily affirmations iPhone apps for "
               "creators and influencers, published under the creator's own Apple account. How it works, pricing and who it's for.")
ANSWER = ("acanalab is a small European app studio. It builds a finished daily affirmations app for iPhone with a creator's "
          "name, icon and colors, and publishes it under the creator's own Apple Developer account, so the app, the listing "
          "and the subscribers belong to the creator. There's no technical work for the creator. On the Partner plan there's "
          "no setup fee and the creator keeps 70% of net subscription sales; on Pay once the creator pays a one-time fee and "
          "keeps 100%. acanalab also publishes its own iPhone apps, Daily Affirmations and HoneyNest.")

FAQ = [
    ("What is acanalab?", ANSWER),
    ("Who is acanalab for?", "Content creators, influencers and coaches with a wellness, mindset, self-care, faith or lifestyle "
     "audience who want a branded app as an extra, recurring revenue stream."),
    ("How much does acanalab cost?", "Partner: $0 upfront, and the creator keeps 70% of net sales. Pay once: a one-time fee "
     "($4,900 regular price), and the creator keeps 100% of sales. Either way the creator pays Apple $99 a year for the "
     "Apple Developer Program."),
    ("Where is acanalab based?", "In Europe. It works with creators worldwide, by email at support@acanalab.com."),
    ("How do I get started with acanalab?", "Design your app for free in a few minutes at acanalab.com/design/, with no "
     "sign-up, then get in touch at support@acanalab.com."),
]

BODY = f"""
<h2 id="what">What acanalab does</h2>
<p>acanalab gives creators and influencers their own daily affirmations app for iPhone. We build it with your name, icon and colors, publish it on the App Store under your own Apple Developer account, and keep it updated. Your followers get a daily dose of encouragement from you, right on their phones, and you earn from subscriptions every month.</p>
<ul>
<li><b>What's in the app:</b> hundreds of affirmations across many topics, a fresh one every day, streaks and gentle reminders, Home Screen and Lock Screen widgets, favorites, shareable cards, calm card styles and a short private reflection on favorites written on the iPhone.</li>
<li><b>Ownership:</b> your Apple account, your listing, your reviews and your subscribers. Apple pays you directly.</li>
<li><b>Your work:</b> pick your look, set up your Apple Developer account and share the app. No coding.</li>
<li><b>Privacy:</b> no third-party ads and no tracking. We prepare a privacy policy and terms of use in your name.</li>
</ul>
<p>See it working in <a href="/dailyaffirmationsapp/">Daily Affirmations</a>, our own app on the App Store, which your app is built from.</p>

<h2 id="pricing">Pricing</h2>
<table>
<thead><tr><th></th><th>Partner</th><th>Pay once</th></tr></thead>
<tbody>
<tr><td>Upfront</td><td>$0</td><td>One-time fee ($4,900 regular price)</td></tr>
<tr><td>You keep</td><td>70% of net sales</td><td>100% of net sales</td></tr>
<tr><td>Updates</td><td>Free while our share averages $250 a month or more</td><td>Fixes free for 12 months, new features quoted</td></tr>
</tbody>
</table>
<p>Your only other cost is Apple's $99 a year. Current offers are on the <a href="/#pricing">homepage</a>. For the full breakdown, see <a href="/guides/how-much-does-it-cost-to-make-an-affirmation-app/">what an affirmation app costs</a> and <a href="/guides/how-much-money-can-an-affirmation-app-make/">how much it can earn</a>.</p>

<h2 id="who">Who it's for</h2>
<p>Creators, influencers and coaches whose audience already comes to them for encouragement: wellness, mindset, self-care, faith, fitness and lifestyle. It isn't a good fit if you need Android at launch, want a different kind of app, or don't have an audience yet. See <a href="/guides/branded-app-for-creators-compared/">how acanalab compares with agencies, freelancers and app builders</a>.</p>

<h2 id="apps">Our own apps</h2>
<ul>
<li><a href="/dailyaffirmationsapp/">Daily Affirmations</a>: fresh positive affirmations every day, free on iPhone.</li>
<li><a href="/honeynest/">HoneyNest</a>: shared expense tracking for couples, on iPhone.</li>
</ul>

<h2 id="contact">Contact</h2>
<p>Email <a href="mailto:support@acanalab.com">support@acanalab.com</a>, or see your own app first in the free <a href="/design/">brand picker</a>.</p>
"""


def main():
    app = bg.App(next(c for c in bg.APPS if c["folder"] == ""))
    ld = [
        {"@context": "https://schema.org", "@type": "AboutPage", "url": URL, "name": TITLE, "description": DESCRIPTION,
         "dateModified": UPDATED, "about": {"@id": f"{SITE}/#org"}},
        {"@context": "https://schema.org", "@type": "Organization", "@id": f"{SITE}/#org", "name": "acanalab",
         "url": f"{SITE}/", "logo": f"{SITE}/app-icon.png", "email": "support@acanalab.com", "description": ANSWER,
         "areaServed": "Worldwide",
         "sameAs": ["https://apps.apple.com/app/id6809586170", "https://apps.apple.com/app/id6775592748",
                    "https://www.pinterest.com/getdailyaffirmationsapp/"]},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        bg.crumbs_ld([(app.name, app.url), ("About", URL)]),
    ]
    faq_html = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
    page = app.head(TITLE, DESCRIPTION, URL, f"{SITE}/og-image.jpg", ld) + f"""
<main class="wrap">
<article>
<p class="crumbs"><a href="/">{e(app.name)}</a> › About</p>
<h1>What is acanalab?</h1>
<p class="lead">A small European studio that builds calm, privacy-friendly iPhone apps, and gives creators their own branded affirmations app.</p>
<p class="meta">Updated {UPDATED}</p>
<div class="answer"><b>Short answer</b><p>{e(ANSWER)}</p></div>
{BODY.strip()}

{app.app_box(app.cfg["box_text"], "about")}

<h2 id="faq">Frequently asked questions</h2>
{faq_html}
</article>
</main>
""" + app.foot()
    out = bg.ROOT / "about" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)


if __name__ == "__main__":
    main()
