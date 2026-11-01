#!/usr/bin/env python3
"""Build Pinterest pins for Daily Affirmations guides and a bulk-upload CSV.

  python3 _tools/build_pins.py [--start YYYY-MM-DD] [--per-day N]

For every guide in dailyaffirmationsapp/guides/_src/guides.json that has no pins
yet (see _tools/seo/pins.json), it makes one list pin and two quote pins from the
guide's affirmation lists, renders them to dailyaffirmationsapp/pins/<id>.jpg
(via _tools/pins/render.js) and writes _tools/pins/upload.csv with only the new
pins, scheduled per_day a day from --start. Upload that CSV in Pinterest:
Settings > Import content > Upload .csv or .txt file.

Board names must match the boards on pinterest.com/getdailyaffirmationsapp exactly.
"""

import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "dailyaffirmationsapp"
SRC = APP / "guides" / "_src"
OUT = APP / "pins"
STATE = ROOT / "_tools" / "seo" / "pins.json"
CSV_OUT = ROOT / "_tools" / "pins" / "upload.csv"
SITE = "https://acanalab.com"

# Per guide: Pinterest board, quote-pin label, and hashtag-free keywords for the description.
GUIDES = {
    "morning-affirmations": ("Morning Affirmations", "Morning affirmation"),
    "self-love-affirmations": ("Self Love Affirmations", "Self-love affirmation"),
    "affirmations-for-anxiety": ("Affirmations for Anxiety and Stress", "Affirmation for anxiety"),
    "affirmations-for-stress": ("Affirmations for Anxiety and Stress", "Affirmation for stress"),
    "affirmations-for-confidence": ("Confidence and Success Affirmations", "Confidence affirmation"),
    "affirmations-for-success": ("Confidence and Success Affirmations", "Success affirmation"),
    "gratitude-affirmations": ("Gratitude Affirmations", "Gratitude affirmation"),
    "affirmations-for-sleep": ("Sleep and Bedtime Affirmations", "Bedtime affirmation"),
    "affirmations-for-healing": ("Affirmations for Healing", "Healing affirmation"),
    "short-positive-affirmations": ("Short Positive Affirmations", "Short affirmation"),
    "positive-affirmations-for-kids": ("Affirmations for Kids", "Affirmation for kids"),
    "affirmations-for-work": ("Affirmations for Work", "Work affirmation"),
}
THEMES = ["night", "brand", "blush"]
TIMES = ["08:30", "19:30", "13:00"]  # local publish times, spread across the day


def affirmations(slug):
    text = (SRC / f"{slug}.html").read_text()
    return [html.unescape(re.sub(r"<[^>]+>", "", li)).strip()
            for block in re.findall(r'<ol class="list">(.*?)</ol>', text, re.S)
            for li in re.findall(r"<li>(.*?)</li>", block, re.S)]


def spread(items, n):
    """n items spaced evenly through the list, so picks come from different sections."""
    if len(items) <= n:
        return items
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


def pins_for(g, index):
    slug = g["slug"]
    board, label = GUIDES[slug]
    items = affirmations(slug)
    if len(items) < 10:
        return []
    short = [i for i in items if len(i) <= 46]
    listed = spread(short, 5)
    rest = [i for i in items if i not in listed and 22 <= len(i) <= 62]
    quotes = spread(rest, 2)
    head, _, sub = g["title"].partition(":")
    count = len(items)
    link = f"{SITE}/dailyaffirmationsapp/guides/{slug}/?utm_source=pinterest&utm_medium=social&utm_campaign=pins"
    theme = lambda k: THEMES[(index + k) % len(THEMES)]
    pins = [{
        "id": f"{slug}-list", "slug": slug, "board": board, "kind": "list", "theme": theme(0),
        "kicker": sub.strip(), "title": head.strip(), "items": listed, "cta": f"Read all {count}",
        "pin_title": f"{head.strip()}: {sub.strip()}"[:100],
        "description": f"{g['description']} Save this list and read all {count} in the free guide.",
        "link": link,
    }]
    for k, q in enumerate(quotes, 1):
        pins.append({
            "id": f"{slug}-quote-{k}", "slug": slug, "board": board, "kind": "quote", "theme": theme(k),
            "kicker": label, "text": q,
            "pin_title": f"{q} | {label}"[:100],
            "description": f"\"{q}\" Save this {label.lower()} for when you need it. "
                           f"Find {count} more {head.strip().lower()} in our free guide.",
            "link": link,
        })
    return pins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=(dt.date.today() + dt.timedelta(days=1)).isoformat())
    ap.add_argument("--per-day", type=int, default=2)
    args = ap.parse_args()

    state = json.loads(STATE.read_text()) if STATE.exists() else []
    done = {p["slug"] for p in state}
    guides = json.loads((SRC / "guides.json").read_text())
    new = []
    for i, g in enumerate(guides):
        if g["slug"] in done or g["slug"] not in GUIDES:
            continue
        new += pins_for(g, i)
    if not new:
        print("No new pins.")
        return

    # Interleave guides so one board doesn't get several pins in a row.
    by_slug = {}
    for p in new:
        by_slug.setdefault(p["slug"], []).append(p)
    order = []
    while any(by_slug.values()):
        for s in list(by_slug):
            if by_slug[s]:
                order.append(by_slug[s].pop(0))

    OUT.mkdir(exist_ok=True)
    jobs = [dict(p, out=str(OUT / f"{p['id']}.jpg")) for p in order]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f)
    env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(["node", str(ROOT / "_tools" / "pins" / "render.js"), f.name], check=True, env=env)
    os.unlink(f.name)

    start = dt.date.fromisoformat(args.start)
    with CSV_OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
        for n, p in enumerate(order):
            day = start + dt.timedelta(days=n // args.per_day)
            p["publish"] = f"{day.isoformat()}T{TIMES[n % args.per_day]}:00"
            w.writerow([p["pin_title"], f"{SITE}/dailyaffirmationsapp/pins/{p['id']}.jpg", p["board"], "",
                        p["description"][:500], p["link"], p["publish"], ""])
    for p in order:
        state.append({k: p[k] for k in ("id", "slug", "board", "kind", "publish")})
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(order)} pins rendered to {OUT.relative_to(ROOT)}, CSV at {CSV_OUT.relative_to(ROOT)}, "
          f"scheduled {order[0]['publish']} to {order[-1]['publish']}")


if __name__ == "__main__":
    sys.exit(main())
