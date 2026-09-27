#!/usr/bin/env python3
"""THE PERENNIAL — the Garden's almanac of the year: one chapter per month, built from everything the papers recorded
(headlines, weather, tokens, payroll, streaks, incidents, B.I.G's ideas, extras, funnies, arrivals and passings).
Rebuilt nightly, so the current month's chapter grows day by day.   Usage: build_perennial.py [YEAR]
"""
import calendar, datetime as dt, glob, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, ROOT)
import pubkit as pk   # noqa: E402
import flipbook as fb   # noqa: E402
from pubkit import e   # noqa: E402

fb.CSS_FILE = "perennial.css"
REPO = "https://github.com/real-CAK3D/ThePerennial"
DWD = os.path.join(pk.DW, "site", "data")
SMOKE = os.path.join(pk.GARDEN, "sunday-smoke")


def month_data(y, m):
    days = []
    for day in range(1, calendar.monthrange(y, m)[1] + 1):
        d = dt.date(y, m, day).isoformat()
        ed = pk.load(os.path.join(pk.DW, "drafts", d + ".json"))
        w = pk.load(os.path.join(DWD, "weather-%s.json" % d))
        u = pk.load(os.path.join(DWD, "usage-%s.json" % d))
        p = pk.load(os.path.join(DWD, "payroll-%s.json" % d))
        if not (ed or w or u or p):
            continue
        today = (w.get("days") or [{}])[0]
        days.append({"date": d, "headline": (ed.get("headline") or {}).get("title"), "high": today.get("high"), "low": today.get("low"),
                     "sky": today.get("short") or (w.get("now") or {}).get("text"), "tokens": u.get("total") or 0,
                     "pay": sum(r.get("today", 0) for r in p.get("rows") or []), "potg": (p.get("employee_of_the_day") or {}).get("agent"),
                     "incidents": len(ed.get("police_blotter") or []), "report_day": u.get("day")})
    extras = [x for x in (pk.load(f) for f in glob.glob(os.path.join(pk.GARDEN, "extra-extra", "data", "%04d-%02d-*.json" % (y, m))))]
    ideas = sum(len(pk.load(f).get("items") or []) for f in glob.glob(os.path.join(DWD, "market-%04d-%02d-*.json" % (y, m))))
    strips = sum(len((pk.load(f).get("funnies") or {}).get("strips") or []) for f in glob.glob(os.path.join(SMOKE, "strips", "%04d-%02d-*.json" % (y, m))))
    born = passed = 0
    for f in glob.glob(os.path.join(DWD, "obits-%04d-%02d-*.json" % (y, m))):
        o = pk.load(f)
        born += len(o.get("born") or [])
        passed += len(o.get("passed") or [])
    return {"days": days, "extras": extras, "ideas": ideas, "strips": strips, "born": born, "passed": passed}


def chapter(y, m, md):
    name = dt.date(y, m, 1).strftime("%B")
    days = md["days"]
    toks = [x for x in days if x["tokens"]]
    highs = [x for x in days if isinstance(x.get("high"), (int, float))]
    lows = [x for x in days if isinstance(x.get("low"), (int, float))]
    potg = {}
    for x in days:
        if x["potg"]:
            potg[x["potg"]] = potg.get(x["potg"], 0) + 1
    mvp = max(potg.items(), key=lambda kv: kv[1]) if potg else None
    stats = [("Days recorded", len(days)), ("Tokens burned", fb._k(sum(x["tokens"] for x in days))), ("Pretend payroll", "$%.2f" % sum(x["pay"] for x in days)),
             ("Incidents on the blotter", sum(x["incidents"] for x in days)), ("Extras printed", len(md["extras"])), ("Side gigs B.I.G filed", md["ideas"]),
             ("Comic strips drawn", md["strips"]), ("Arrivals · passings", "%d · %d" % (md["born"], md["passed"]))]
    moon = []
    try:
        sys.path.insert(0, pk.DW)
        import collect_inputs as ci
        for day in range(1, calendar.monthrange(y, m)[1] + 1):
            ph = ci._moon(dt.datetime(y, m, day, 21, tzinfo=ci.TZ))[0]
            if ph in ("Full Moon", "New Moon") and (not moon or moon[-1][1] != ph):
                moon.append((day, ph))
    except Exception:
        pass
    records = [("Warmest day", "%s° on %s" % (max(highs, key=lambda x: x["high"])["high"], pk.nice(max(highs, key=lambda x: x["high"])["date"], "%b %-d")) if highs else "—"),
               ("Coldest night", "%s° on %s" % (min(lows, key=lambda x: x["low"])["low"], pk.nice(min(lows, key=lambda x: x["low"])["date"], "%b %-d")) if lows else "—"),
               ("Busiest token day", "%s on %s" % (fb._k(max(toks, key=lambda x: x["tokens"])["tokens"]), pk.nice(max(toks, key=lambda x: x["tokens"])["date"], "%b %-d")) if toks else "—"),
               ("Player of the Month", "%s (%d× Player of the Game)" % mvp if mvp else "—")]
    opener = ('<div class="pr-chapter"><div class="pr-num">Chapter %d</div><h2 class="pr-month">%s</h2><div class="pr-year">%d</div>'
              '<div class="pr-stats">%s</div><div class="pr-records"><h4>Records of the month</h4><ul>%s</ul></div>%s</div>'
              % (m, e(name), y, "".join('<div><small>%s</small><b>%s</b></div>' % (e(a), e(b)) for a, b in stats),
                 "".join("<li><b>%s:</b> %s</li>" % (e(a), e(b)) for a, b in records),
                 ('<p class="pr-moon">%s</p>' % " · ".join("%s %s" % ("🌕" if p == "Full Moon" else "🌑", "%s %d" % (name[:3], dd)) for dd, p in moon)) if moon else ""))
    rows = "".join('<tr><td>%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td></tr>'
                   % (e(pk.nice(x["date"], "%a %-d")), e(x["headline"] or "—"), ("%s°/%s°" % (x["high"], x["low"])) if x.get("high") is not None else "—",
                      fb._k(x["tokens"]) if x["tokens"] else "—", e(x["potg"] or "")) for x in days)
    diary = '<div class="pr-diary"><h3>The Days of %s</h3><table class="agate"><thead><tr><th>Day</th><th>The Double Wide\'s headline</th><th>Weather</th><th>Tokens</th><th>Player of the Game</th></tr></thead><tbody>%s</tbody></table>%s</div>' % (
        e(name), rows or '<tr><td colspan="5">Nothing recorded yet.</td></tr>',
        ('<h3>Extras</h3><ul>%s</ul>' % "".join("<li>%s — %s</li>" % (e(pk.nice(x["at"][:10], "%b %-d")), e(x.get("headline"))) for x in md["extras"])) if md["extras"] else "")
    return [fb.page("%s %d" % (name, y), opener, " pr-open"), fb.page("The Days of %s" % name, diary)]


def build(y):
    pk.sync_portraits(SITE)
    today = dt.date.today()
    months = [m for m in range(1, 13) if dt.date(y, m, 1) <= today and (y, m) >= (2026, 9)]
    chapters, index, n = [], [], 3
    for m in months:
        md = month_data(y, m)
        pages = chapter(y, m, md)
        index.append((m, n, len(md["days"])))
        chapters += pages
        n += len(pages)
    seal = '<a class="seal" href="/" aria-label="Back to The Corner Chronicle">%s</a>' % fb.SEAL
    art = pk.draw_image(os.path.join(SITE, "img", "covers", "%d.jpg" % y), (
        "An antique 19th-century almanac woodcut engraving, pure black ink line art on plain white paper, no color, no gray fill, no text or lettering anywhere. "
        "A roughly square decorative vignette: in the middle a small New England farmhouse with a big red-oak tree and a vegetable garden under a sun and a crescent moon; "
        "around it, four small corner scenes for the four seasons in Maine: spring planting seedlings, summer haying a field, autumn apple and pumpkin harvest, "
        "winter splitting firewood in the snow. Tiny details: a Raspberry Pi-sized little radio antenna on the farmhouse roof, a friendly dog. "
        "Framed by an ornate engraved border of vines, leaves and wheat. Fine cross-hatching like an old almanac cover. No faces in close-up, no portraits."), size="1024x1024", max_px=900)
    chap = months[-1] if months else 1
    cover = fb.page("The Perennial", (
        '<div class="alm"><span class="alm-hole" aria-hidden="true"></span><div class="alm-seal">%s</div>'
        '<div class="alm-no">No. %d</div><div class="alm-the">THE</div><h1 class="alm-t">Perennial</h1><div class="alm-kind">GARDEN&#39;S ALMANAC</div>'
        '<div class="alm-plan">Calculated on a new and improved plan for the year of our Garden</div><div class="alm-year">%d</div>'
        '%s'
        '<p class="alm-blurb">Being the %s year since the Garden took root. Containing the Moon&#39;s phases, the weather as it fell, the records of the year, '
        'every day&#39;s headline, and a variety of <i>New, Useful &amp; Entertaining Matter</i>.</p>'
        '<div class="alm-for">Fitted for the meridian of <b>LEWISTON, MAINE</b>, but will serve for all the Garden&#39;s machines</div>'
        '<div class="alm-grow">Now growing: Chapter %d — %s</div>'
        '<div class="alm-foot"><span>Established 2026 by the Garden</span><span>Price: One Season</span></div></div>')
        % (seal, y - 2025, y, ('<div class="alm-art"><img src="../img/covers/%d.jpg" alt="Almanac woodcut of the four seasons around a Maine farmhouse"></div>' % y) if art else '<div class="alm-art alm-rule">✿ ☀ ✿ ☾ ✿</div>',
           ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"][min(y - 2026, 9)], chap,
           e(dt.date(y, chap, 1).strftime("%B"))), " hardcover pr-cov")
    toc = fb.page("Contents", '<div class="pr-toc"><h2>Contents</h2><p class="small">One chapter per month, written by the Garden itself. Tap a month.</p><ol>%s</ol></div>'
                  % "".join('<li><a data-goto="%d">%s <span>%d days recorded</span></a></li>' % (pg, e(dt.date(y, m, 1).strftime("%B")), nd) for m, pg, nd in index))
    back = fb.page("Back Page", ('<div class="gum"><span>THE PERENNIAL · %d EDITION</span></div><div class="pb-body">%s<h2 class="pb-title">The Perennial</h2>'
                                 '<p>Compiled nightly from The Double Wide, The Sunday Smoke, Roach Clips and Extra! Extra!.<br>A new chapter takes root every month.</p>%s'
                                 '<p class="pb-code">%d edition · updated %s</p></div>') % (y, seal, fb.back_codes(REPO, "ThePerennial"), y, today.isoformat()), " hardcover back")
    html = fb.book([cover, toc] + chapters + [back], date=today.isoformat(), no=y, lists={}, paper="The Perennial", motto="Comes back every year, deeper rooted",
                   gum="THE GARDEN'S ALMANAC · CALCULATED FOR LEWISTON, MAINE", price="PRICE: ONE SEASON", delivered="COMPILED BY THE GARDEN",
                   flap="The Perennial · the Garden's almanac", body_class="pub-pr", est="FOR THE YEAR OF OUR GARDEN")
    os.makedirs(os.path.join(SITE, "issues"), exist_ok=True)
    open(os.path.join(SITE, "issues", "%d.html" % y), "w").write(html)
    open(os.path.join(SITE, "index.html"), "w").write(html.replace('href="../', 'href="').replace('src="../', 'src="'))
    eds = pk.issues(SITE, pattern=r"\d{4}")
    pk.archive_page(SITE, os.path.join(ROOT, fb.CSS_FILE), "pub-pr", "The Perennial", "every edition", "".join('<li><a href="issues/%s.html">%s edition</a></li>' % (x, x) for x in eds), "🌿")
    pk.latest(SITE, "The Perennial", today.isoformat(), "%d edition — now growing: %s" % (y, dt.date(y, months[-1], 1).strftime("%B") if months else "—"), "", [],
              cover=("img/covers/%d.jpg" % y) if art else "")
    print("perennial built:", y, len(months), "chapters")


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today().year)
