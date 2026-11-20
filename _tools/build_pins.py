#!/usr/bin/env python3
"""Build Pinterest pins for Daily Affirmations guides and a bulk-upload CSV.

  python3 _tools/build_pins.py [--start YYYY-MM-DD] [--per-day N]
  python3 _tools/build_pins.py --refresh 3   # daily: fresh pins for guides that already have pins

For every guide in dailyaffirmationsapp/guides/_src/guides.json that has no pins
yet (see _tools/seo/pins.json), it makes one list pin and two quote pins from the
guide's affirmation lists, renders them to dailyaffirmationsapp/pins/<id>.jpg
(via _tools/pins/render.js) and writes _tools/pins/upload.csv with only the new
pins. By default (--mode rss) the new pins go into one RSS feed per board at
dailyaffirmationsapp/pins/feeds/<board>.xml, which Pinterest auto-publishes from
(Settings > Import content > Auto-publish). --mode csv instead writes a scheduled
upload CSV (Settings > Import content > Upload .csv).

--refresh N makes N new pins (two quote pins and one list pin per 3) for guides that
already have pins, picking the guides pinned least recently, each on a different board,
with affirmations no earlier pin used. New ids continue the numbering (<slug>-quote-K,
<slug>-list-K); existing images, feed items and guids are never changed.

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
    "do-affirmations-work": ("Self Love Affirmations", "Believable affirmation"),
    "affirmations-for-relationships": ("Self Love Affirmations", "Relationship affirmation"),
    "abundance-affirmations": ("Gratitude Affirmations", "Abundance affirmation"),
    "affirmations-for-depression": ("Affirmations for Healing", "Gentle affirmation"),
    "how-to-make-affirmations-a-habit": ("Morning Affirmations", "Daily affirmation"),
    "affirmations-for-self-esteem": ("Self Love Affirmations", "Self-esteem affirmation"),
}
THEMES = ["night", "brand", "blush"]
# Quote pins use the app's own card themes (photos and textures), picked by pin id.
CARD_THEMES = json.loads((ROOT / "_tools" / "pins" / "themes" / "themes.json").read_text())


def card_theme(pin_id):
    import hashlib
    return CARD_THEMES[int(hashlib.md5(pin_id.encode()).hexdigest(), 16) % len(CARD_THEMES)]
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
        "pin_title": (f"{head.strip()}: {sub.strip()}" if sub.strip() else head.strip())[:100],
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


def render(pins):
    OUT.mkdir(exist_ok=True)
    jobs = [dict(p, out=str(OUT / f"{p['id']}.jpg"), **({"bg": card_theme(p["id"])} if p["kind"] == "quote" else {}))
            for p in pins]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f)
    env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(["node", str(ROOT / "_tools" / "pins" / "render.js"), f.name], check=True, env=env)
    os.unlink(f.name)


def interleave(pins):
    """Spread guides so one board doesn't get several pins in a row."""
    by_slug = {}
    for p in pins:
        by_slug.setdefault(p["slug"], []).append(p)
    order = []
    while any(by_slug.values()):
        for s in list(by_slug):
            if by_slug[s]:
                order.append(by_slug[s].pop(0))
    return order


def board_slug(board):
    return re.sub(r"[^a-z0-9]+", "-", board.lower()).strip("-")


def write_feeds(state):
    """One RSS feed per board with the pins marked via=rss (newest first, max 50).

    Pinterest (Settings > Import content > Auto-publish) maps each feed to one board and
    checks it about once a day; every new <item> becomes a Pin."""
    feeds = OUT / "feeds"
    feeds.mkdir(parents=True, exist_ok=True)
    esc = lambda t: html.escape(t, quote=True)
    for board in sorted({b for b, _ in GUIDES.values()}):
        items = [p for p in state if p.get("via") == "rss" and p["board"] == board][::-1][:50]
        url = f"{SITE}/dailyaffirmationsapp/pins/feeds/{board_slug(board)}.xml"
        out = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">',
               "<channel>", f"<title>{esc(board)} | Daily Affirmations</title>",
               f"<link>{SITE}/dailyaffirmationsapp/</link>",
               f'<atom:link href="{url}" rel="self" type="application/rss+xml"/>',
               f"<description>{esc(board)} from the Daily Affirmations app guides.</description>",
               "<language>en</language>"]
        for p in items:
            img = f"{SITE}/dailyaffirmationsapp/pins/{p['id']}.jpg"
            size = (OUT / f"{p['id']}.jpg").stat().st_size
            date = dt.datetime.fromisoformat(p["publish"]).strftime("%a, %d %b %Y %H:%M:%S +0000")
            out += ["<item>", f"<title>{esc(p['pin_title'])}</title>", f"<link>{esc(p['link'])}</link>",
                    f"<description>{esc(p['description'][:500])}</description>",
                    f'<guid isPermaLink="false">{p["id"]}</guid>', f"<pubDate>{date}</pubDate>",
                    f'<enclosure url="{img}" length="{size}" type="image/jpeg"/>',
                    f'<media:content url="{img}" medium="image" type="image/jpeg" width="1000" height="1500"/>',
                    "</item>"]
        out += ["</channel>", "</rss>"]
        (feeds / f"{board_slug(board)}.xml").write_text("\n".join(out) + "\n")


def extra_quote(g, index, done_ids):
    """One more quote pin for a guide that already has pins (used to seed the RSS feeds)."""
    slug = g["slug"]
    base = pins_for(g, index)
    if not base:
        return None
    used = set(base[0]["items"]) | {p["text"] for p in base[1:]}
    rest = [i for i in affirmations(slug) if i not in used and 22 <= len(i) <= 62]
    k = 3
    while f"{slug}-quote-{k}" in done_ids:
        k += 1
    if len(rest) < k:
        return None
    q = rest[int(len(rest) * (0.25 + 0.5 * ((k - 3) % 2)))] if k == 3 else rest[(k * 7) % len(rest)]
    p = dict(base[1], id=f"{slug}-quote-{k}", text=q, theme=THEMES[(index + k) % len(THEMES)])
    label = GUIDES[slug][1]
    count = len(affirmations(slug))
    head = g["title"].partition(":")[0].strip()
    p["pin_title"] = f"{q} | {label}"[:100]
    p["description"] = (f"\"{q}\" Save this {label.lower()} for when you need it. "
                        f"Find {count} more {head.lower()} in our free guide.")
    return p


def used_texts(g, index, state):
    """Every affirmation already shown on a pin of this guide."""
    slug = g["slug"]
    base = pins_for(g, index)
    used = set(base[0]["items"]) | {p["text"] for p in base[1:]} if base else set()
    for p in state:
        if p["slug"] != slug:
            continue
        used |= set(p.get("items", []))
        if p.get("text"):
            used.add(p["text"])
        elif p["kind"] == "quote" and " | " in p.get("pin_title", ""):
            used.add(p["pin_title"].rsplit(" | ", 1)[0])
    return used


def next_id(slug, kind, taken):
    k = 2
    while f"{slug}-{kind}-{k}" in taken or (OUT / f"{slug}-{kind}-{k}.jpg").exists():
        k += 1
    return f"{slug}-{kind}-{k}", k


def refresh_pins(guides, state, n):
    """n fresh pins for already-pinned guides: least recently pinned guides first, one per board."""
    taken = {p["id"] for p in state}
    last = {}
    for p in state:
        last[p["slug"]] = max(last.get(p["slug"], ""), p["publish"])
    cands = [(last[g["slug"]], sum(p["slug"] == g["slug"] for p in state), i, g)
             for i, g in enumerate(guides) if g["slug"] in GUIDES and g["slug"] in last]
    cands.sort(key=lambda c: (c[0], c[1]))
    kinds = ["quote", "list", "quote"]
    out, boards = [], set()
    for _, count_pins, i, g in cands:
        if len(out) >= n:
            break
        slug = g["slug"]
        board, label = GUIDES[slug]
        if board in boards:
            continue
        items = affirmations(slug)
        if len(items) < 10:
            continue
        used = used_texts(g, i, state)
        head, _, sub = g["title"].partition(":")
        head = head.strip()
        count = len(items)
        link = f"{SITE}/dailyaffirmationsapp/guides/{slug}/?utm_source=pinterest&utm_medium=social&utm_campaign=pins"
        kind = kinds[len(out) % len(kinds)]
        short = [t for t in items if t not in used and len(t) <= 46]
        if kind == "list" and len(short) < 5:
            kind = "quote"
        if kind == "list":
            pid, k = next_id(slug, "list", taken)
            # Rotate the start so repeat list pins of one guide show different lines.
            off = (count_pins * 3) % len(short)
            listed = spread(short[off:] + short[:off], 5)
            p = {"id": pid, "slug": slug, "board": board, "kind": "list", "theme": THEMES[(i + k) % len(THEMES)],
                 "kicker": "5 to save for today", "title": head, "items": listed, "cta": f"Read all {count}",
                 "pin_title": f"{head}: {listed[0]}"[:100],
                 "description": (f"{head} to save: {' '.join(listed[:3])} Read all {count} in the free guide.")[:500],
                 "link": link}
        else:
            rest = [t for t in items if t not in used and 22 <= len(t) <= 62]
            if not rest:
                continue
            pid, k = next_id(slug, "quote", taken)
            q = rest[(count_pins * 7) % len(rest)]
            p = {"id": pid, "slug": slug, "board": board, "kind": "quote", "theme": THEMES[(i + k) % len(THEMES)],
                 "kicker": label, "text": q, "pin_title": f"{q} | {label}"[:100],
                 "description": f"\"{q}\" Save this {label.lower()} for when you need it. "
                                f"Find {count} more {head.lower()} in our free guide.",
                 "link": link}
        taken.add(p["id"])
        boards.add(board)
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["rss", "csv"], default="rss",
                    help="rss (default): add new pins to the board feeds; csv: write a scheduled upload.csv")
    ap.add_argument("--seed", action="store_true", help="also add one extra quote pin for every guide (rss)")
    ap.add_argument("--refresh", type=int, metavar="N",
                    help="rss: make N fresh pins for guides that already have pins (daily run)")
    ap.add_argument("--start", help="csv: first publish day; default: the day after the last scheduled pin, or tomorrow")
    ap.add_argument("--per-day", type=int, default=2)
    args = ap.parse_args()

    state = json.loads(STATE.read_text()) if STATE.exists() else []
    done = {p["slug"] for p in state}
    done_ids = {p["id"] for p in state}
    guides = json.loads((SRC / "guides.json").read_text())
    new = []
    if args.refresh:
        args.mode = "rss"
        new = refresh_pins(guides, state, args.refresh)
    for i, g in enumerate(guides if not args.refresh else []):
        if g["slug"] not in GUIDES:
            continue
        if g["slug"] not in done:
            new += pins_for(g, i)
        elif args.seed and args.mode == "rss":
            p = extra_quote(g, i, done_ids)
            if p:
                new.append(p)
    if not new:
        print("No new pins.")
        if args.mode == "rss":
            write_feeds(state)
        return

    order = interleave(new)
    render(order)

    if args.mode == "csv":
        if args.start:
            start = dt.date.fromisoformat(args.start)
        else:
            last = max((dt.date.fromisoformat(p["publish"][:10]) for p in state), default=dt.date.today())
            start = max(dt.date.today(), last) + dt.timedelta(days=1)
        with CSV_OUT.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
            for n, p in enumerate(order):
                day = start + dt.timedelta(days=n // args.per_day)
                p["publish"] = f"{day.isoformat()}T{TIMES[n % args.per_day]}:00"
                w.writerow([p["pin_title"], f"{SITE}/dailyaffirmationsapp/pins/{p['id']}.jpg", p["board"], "",
                            p["description"][:500], p["link"], p["publish"], ""])
        for p in order:
            state.append({k: p[k] for k in ("id", "slug", "board", "kind", "publish")} | {"via": "csv"})
        where = f"CSV at {CSV_OUT.relative_to(ROOT)}, scheduled {order[0]['publish']} to {order[-1]['publish']}"
    else:
        # Space pubDates an hour apart so feed readers keep the interleaved order.
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0, second=0, minute=0, tzinfo=None)
        for n, p in enumerate(order):
            p["publish"] = (now - dt.timedelta(hours=len(order) - n)).isoformat()
            state.append({k: p[k] for k in ("id", "slug", "board", "kind", "publish", "pin_title", "description", "link")}
                         | {k: p[k] for k in ("text", "items") if args.refresh and k in p} | {"via": "rss"})
        write_feeds(state)
        where = f"added to the RSS feeds in {(OUT / 'feeds').relative_to(ROOT)}"
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(order)} pins rendered to {OUT.relative_to(ROOT)}, {where}")


if __name__ == "__main__":
    sys.exit(main())
