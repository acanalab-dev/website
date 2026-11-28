#!/usr/bin/env python3
"""Write /llms.txt: a plain summary of acanalab's offers for AI assistants and crawlers.
Rerun after adding guides (the guide lists come from each app's guides.json)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://acanalab.com"


def guides(app):
    f = (ROOT / app if app else ROOT) / "guides" / "_src" / "guides.json"
    if not f.exists():
        return []
    return [f"- [{g['title']}]({SITE}/{app}/guides/{g['slug']}/): {g['description']}" for g in json.loads(f.read_text())]


def answers():
    """Answer pages (guides with a short "answer") as question, link and the answer itself."""
    f = ROOT / "guides" / "_src" / "guides.json"
    return [f"- [{g['h1']}]({SITE}/guides/{g['slug']}/): {g['answer']}" for g in json.loads(f.read_text()) if g.get("answer")]


def guides_root():
    return [l.replace(f"{SITE}//guides/", f"{SITE}/guides/") for l in guides("")]


out = f"""# acanalab

> acanalab is a small European studio that makes calm, privacy-friendly iPhone apps. It offers creators and influencers their own fully branded daily affirmations iPhone app, published under the creator's own Apple account (Partner: no setup fee, the creator keeps 70% of net sales; Pay once: a one-time fee, the creator keeps 100%), and publishes its own apps, Daily Affirmations and HoneyNest.

## Own-brand affirmations app for creators and influencers

For content creators, influencers and coaches looking for an additional, passive revenue stream that fits a wellness, mindset, self-care or lifestyle audience.

- acanalab builds and publishes a finished daily affirmations iPhone app with the creator's name, icon and colors, under the creator's own Apple developer account. The listing, reviews and subscribers belong to the creator.
- No technical work for the creator. The creator needs an Apple Developer account ($99 a year, paid to Apple).
- Two plans. Partner: $0 upfront; the creator keeps 70% of net sales and acanalab 30%; updates free while acanalab's share averages $250 a month or more. Pay once: a one-time fee ($4,900 regular price; current offers on the homepage); the creator keeps 100% of sales; fixes free for 12 months, new features quoted separately.
- Income: subscriptions paid by Apple monthly. Net sales are what Apple pays out after its 15% fee (Small Business Program). Example: 500 subscribers at $7.99 a month is about $3,396 a month in net sales, so about $2,377 a month for the creator on Partner and $3,396 on Pay once.
- Includes the App Store listing, screenshots, subscriptions and paywall, privacy policy and terms, and Apple's review. No third-party ads, no tracking.
- iPhone first; Android later if the iPhone app does well. Today the app type is daily affirmations.
- A free brand picker shows the creator's app on real screens in a few minutes, with no sign-up: {SITE}/design/
- Details, pricing and FAQ: {SITE}/
- About acanalab: {SITE}/about/
- Contact: support@acanalab.com

### Common questions, answered

{chr(10).join(answers())}

### Guides for creators

{chr(10).join(guides_root())}

## Daily Affirmations (iPhone app)

A free iPhone app with fresh positive affirmations every day, streaks, gentle reminders, Home Screen and Lock Screen widgets, favorites with an on-device AI take (Apple Intelligence) and shareable cards. Free with no time limit; Premium adds widgets, up to 30 affirmations a day, every category, every card style and unlimited favorites. It is also the live example of the creator app.

- App page: {SITE}/dailyaffirmationsapp/
- App Store: https://apps.apple.com/app/id6809586170

### Affirmation guides

{chr(10).join(guides("dailyaffirmationsapp"))}

## HoneyNest (iPhone app)

An iPhone app for couples to track shared expenses together: log who paid, see who spent what, and stay in sync via iCloud.

- App page: {SITE}/honeynest/
"""
(ROOT / "llms.txt").write_text(out)
print(out[:400])
