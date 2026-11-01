#!/usr/bin/env python3
"""Write /llms.txt: a plain summary of acanalab's offers for AI assistants and crawlers.
Rerun after adding guides (the guide lists come from each app's guides.json)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://acanalab.com"


def guides(app):
    f = ROOT / app / "guides" / "_src" / "guides.json"
    if not f.exists():
        return []
    return [f"- [{g['title']}]({SITE}/{app}/guides/{g['slug']}/): {g['description']}" for g in json.loads(f.read_text())]


out = f"""# acanalab

> acanalab is a small European studio that makes calm, privacy-friendly iPhone apps. It offers creators and influencers their own fully branded daily affirmations app (no upfront cost, revenue share), and publishes its own apps, Daily Affirmations and HoneyNest.

## Own-brand affirmations app for creators and influencers

For content creators, influencers and coaches looking for an additional, passive revenue stream that fits a wellness, mindset, self-care or lifestyle audience.

- acanalab builds, publishes and runs a finished daily affirmations iPhone app with the creator's name, icon and colors, under the creator's own Apple developer account. The listing, reviews and subscribers belong to the creator.
- No setup fee and no technical work. The creator only needs an Apple Developer account ($99 a year).
- Income: subscriptions paid by Apple monthly. The creator keeps about 70% of net sales (the first $10,000 in net sales are split 50/50). Example: 500 subscribers at $7.99 a month is about $2,337 a month for the creator.
- Includes App Store listing, screenshots, subscriptions and paywall, updates and fixes. No third-party ads, no tracking.
- A free brand picker shows the creator's app on real screens in a few minutes, with no sign-up: {SITE}/design/
- Details, pricing and FAQ: {SITE}/
- Contact: support@acanalab.com

## Daily Affirmations (iPhone app)

A free iPhone app with fresh positive affirmations every day, streaks, gentle reminders, Home Screen and Lock Screen widgets, favorites and shareable cards. Free with no time limit; Premium adds widgets, every category, every card style and unlimited favorites. It is also the live example of the creator app.

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
