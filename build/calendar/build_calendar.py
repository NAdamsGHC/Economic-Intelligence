"""Build the public Production Calendar page.

    transparency/production-calendar.html

Reads the team's production calendar (Gateshead/schedule/schedule.json), the
staged proposals (Gateshead/schedule/proposed/*.md) and the public wording file
(Gateshead/schedule/public-calendar.json). Only what the public wording file
names is published. Owner fields, notes, email text, log outputs and file paths
never reach the page. Anything without public wording is left off and listed in
the build output, so it can be given a title before the next push.

Run after any change to schedule.json, a staging or commissioning of a proposal,
or the public wording file, then run check_voice.py over the output.

    python build/calendar/build_calendar.py
    python build/calendar/build_calendar.py --today 2026-11-19   # fixed date, for testing
"""
import calendar
import datetime as dt
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHED = ROOT.parent / "schedule"
sys.path.insert(0, str(ROOT / "build" / "transparency"))
from build import page, nice_date  # noqa: E402

WEEKS_AHEAD = 13
RECENT_DAYS = 42
WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def esc(s):
    return html.escape(str(s), quote=True)


def long_date(d):
    return f"{d.strftime('%a')} {d.day} {d.strftime('%B %Y')}"


def nth_weekday(year, month, n, wd):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if dt.date(year, month, d).weekday() == wd]
    return dt.date(year, month, days[-1] if n == "last" else days[int(n) - 1])


def occurrences(pattern, start, end):
    """Dates a pattern falls on, from start to end inclusive."""
    kind, _, rest = pattern.partition(":")
    out = []
    if kind == "weekly":
        d = start + dt.timedelta(days=(WD[rest] - start.weekday()) % 7)
        while d <= end:
            out.append(d)
            d += dt.timedelta(days=7)
        return out
    if kind in ("monthly", "months"):
        if kind == "monthly":
            months, (n, wd) = range(1, 13), rest.split(":")
        else:
            m, n, wd = rest.split(":")
            months = [int(x) for x in m.split(",")]
        y, m = start.year, start.month
        while dt.date(y, m, 1) <= end:
            if m in months:
                d = nth_weekday(y, m, n, WD[wd])
                if start <= d <= end:
                    out.append(d)
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        return out
    return out


def bank_holidays():
    """England and Wales bank holidays from gov.uk (keyless). Empty set if offline."""
    try:
        import urllib.request
        with urllib.request.urlopen("https://www.gov.uk/bank-holidays.json", timeout=15) as r:
            data = json.load(r)
        return {dt.date.fromisoformat(e["date"]) for e in data["england-and-wales"]["events"]}
    except Exception as e:  # noqa: BLE001
        print(f"Bank holidays not fetched ({e}); planned dates are not checked against them")
        return set()


def span(a, b):
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    if a.year == b.year and a.month == b.month:
        return f"{a.day} to {b.day} {b.strftime('%B %Y')}"
    return f"{nice_date(a.isoformat())} to {nice_date(b.isoformat())}"


def proposal_staged(path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^\*\*Staged:\*\*\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    return dt.date.fromisoformat(m.group(1) if m else path.name[:10])


def main(today):
    sched = json.loads((SCHED / "schedule.json").read_text(encoding="utf-8"))
    pub = json.loads((SCHED / "public-calendar.json").read_text(encoding="utf-8"))
    names = pub["items"]
    end = today + dt.timedelta(weeks=WEEKS_AHEAD)
    unlisted = []
    hols = bank_holidays()

    # ---- dated entries over the window ----
    entries = []  # (date, name, kind, status)
    regular = []
    for it in sched["items"]:
        p = names.get(it["id"])
        if not p:
            unlisted.append("schedule item " + it["id"])
            continue
        nd = dt.date.fromisoformat(it["next_due"]) if it.get("next_due") else None
        last = dt.date.fromisoformat(it["last_completed"]) if it.get("last_completed") else None
        if nd:
            st = "Running late" if nd < today else ("Due, bank holiday, will move" if nd in hols else "Due")
            entries.append((nd, p["name"], p["kind"], st))
            if p["pattern"] != "none":
                for d in occurrences(p["pattern"], nd + dt.timedelta(days=1), end):
                    entries.append((d, p["name"], p["kind"], "Bank holiday, will move" if d in hols else "Planned"))
        if it.get("cadence") != "one-off" or nd:
            regular.append((p, it, nd, last))
    # Major work counts as under way until its last milestone has passed.
    active = [w for w in pub.get("major_work", [])
              if max(dt.date.fromisoformat(m.get("end", m["date"])) for m in w["milestones"]) >= today]
    for w in active:
        for ms in w["milestones"]:
            d, e = dt.date.fromisoformat(ms["date"]), dt.date.fromisoformat(ms.get("end", ms["date"]))
            if e < today or d > end:
                continue
            name = w["name"] + ", " + ms["label"].lower()
            if e == d:
                entries.append((d, name, "Major work", "Planned"))
                continue
            # A milestone spanning days shows in every week it covers, from today on.
            name += f" ({span(ms['date'], ms['end'])})"
            day = max(d, today)
            while day <= min(e, end):
                entries.append((day, name, "Major work", "Under way" if day <= today else "Planned"))
                day = day - dt.timedelta(days=day.weekday()) + dt.timedelta(days=7)
    entries = [e for e in entries if e[0] <= end and (e[0] >= today or e[3] == "Running late")]
    entries.sort(key=lambda e: (e[0], e[2] != "Major work", e[1]))

    # ---- staged proposals ----
    staged = []
    for f in sorted((SCHED / "proposed").glob("*.md")):
        if f.name.lower() == "readme.md":
            continue
        p = pub["proposals"].get(f.name)
        if not p:
            unlisted.append("staged proposal " + f.name)
            continue
        if p.get("hide"):
            continue
        staged.append((proposal_staged(f), p))
    staged.sort(key=lambda s: s[0], reverse=True)

    # ---- recently completed, from the log (dates and public names only) ----
    since = today - dt.timedelta(days=RECENT_DAYS)
    done, seen = [], set()
    not_runs = set(pub.get("not_completions", []))
    for row in sched.get("log", []):
        try:
            d = dt.date.fromisoformat(row.get("date", ""))
        except ValueError:
            continue
        p = names.get(row.get("id"))
        # Every log row is a completion unless public-calendar.json lists it as not a run
        # (a date correction, a dropped edition). Never decided from the row's prose.
        if not p or d < since or d > today or f"{row['date']}|{row['id']}" in not_runs:
            continue
        key = (d, row["id"])
        if key not in seen:
            seen.add(key)
            done.append((d, p["name"], p["kind"]))
    for it in sched["items"]:
        p = names.get(it["id"])
        if p and it.get("last_completed"):
            d = dt.date.fromisoformat(it["last_completed"])
            if since <= d <= today and (d, it["id"]) not in seen:
                seen.add((d, it["id"]))
                done.append((d, p["name"], p["kind"]))
    done.sort(key=lambda r: r[0], reverse=True)

    # ---- page ----
    in28 = today + dt.timedelta(days=28)
    n28 = sum(1 for e in entries if e[0] <= in28 and e[2] != "Major work")
    late = sum(1 for e in entries if e[3] == "Running late")
    out = [f"""<style>
.pc-week{{margin:0 0 16px;}}
.pc-week h3{{font-size:14px;color:var(--gc-blue-dark);text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--gc-line-2);padding-bottom:4px;margin:0 0 4px;display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;}}
.pc-week h3 small{{font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;color:#6a7784;}}
.pc-week h3 .busy{{color:#7a5313;font-weight:700;}}
.pc-row{{display:grid;grid-template-columns:160px 1fr auto;gap:2px 12px;padding:6px 4px 6px 10px;border-bottom:1px solid var(--gc-line);border-left:4px solid #9aa5b0;font-size:13.5px;}}
.pc-row.k-major{{border-left-color:#045a90;background:#f3f8fc;}}
.pc-row.k-regular{{border-left-color:#266427;}}
.pc-row.k-oneoff{{border-left-color:#c9862a;}}
.pc-row .d{{font-weight:700;}}
.pc-row .s{{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:#41505e;white-space:nowrap;}}
.pc-row .s.late{{color:#8c1c1c;font-weight:700;}}
.pc-row .k{{display:block;font-size:12px;color:#6a7784;}}
.pc-key{{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:#41505e;margin:0 0 12px;}}
.pc-key i{{display:inline-block;width:4px;height:14px;vertical-align:-2px;margin-right:6px;}}
@media(max-width:620px){{.pc-row{{grid-template-columns:1fr auto;}}.pc-row .d{{grid-column:1/-1;}}}}
</style>
<p class="tp-kicker">Our Work</p>
<h1>Production Calendar</h1>
<p class="tp-byline">Last updated {nice_date(today.isoformat())}</p>
<p class="tp-lede">What the AI team is working on and when. Regular reports come round on a fixed cycle, major pieces of work take priority for set periods, and requests wait in a staging list until the site owner accepts them. An accepted request moves onto this calendar with its dates.</p>
<div class="tp-tiles">
<div><b>{n28}</b><span>items due or planned in the next four weeks</span></div>
<div><b>{late}</b><span>items running late</span></div>
<div><b>{len(active)}</b><span>major {'piece' if len(active) == 1 else 'pieces'} of work under way</span></div>
<div><b>{len(staged)}</b><span>requests staged and awaiting a decision</span></div>
</div>
"""]

    if active:
        out.append("<h2>Major Work Under Way</h2>")
        for w in active:
            rows = "".join(
                f"<tr><td>{esc(span(m['date'], m['end']) if m.get('end') else nice_date(m['date']))}</td><td>{esc(m['label'])}</td></tr>"
                for m in w["milestones"])
            out.append(f"<h3>{esc(w['name'])}</h3><p>{esc(w['what'])}.</p>"
                       f'<div class="tp-scroll"><table class="tp-table"><thead><tr><th>Date</th><th>Milestone</th></tr></thead><tbody>{rows}</tbody></table></div>')

    out.append(f"""<h2>Coming Up</h2>
<p>The next {WEEKS_AHEAD} weeks, week by week. Due dates are set. Planned dates follow each report's regular cycle and can move, for example when a source publishes late. The team only works when the site owner runs it, so an item can run a day or two late.</p>
<div class="pc-key"><span><i style="background:#045a90"></i>Major work</span><span><i style="background:#266427"></i>Regular report</span><span><i style="background:#9aa5b0"></i>Internal check</span><span><i style="background:#c9862a"></i>One-off</span></div>""")
    if not entries:
        out.append("<p>Nothing is scheduled in this window.</p>")
    busy_until = [max(dt.date.fromisoformat(m.get("end", m["date"])) for m in w["milestones"])
                  for w in active]
    weeks = {}
    for e in entries:
        wk = max(e[0], today) - dt.timedelta(days=max(e[0], today).weekday())
        weeks.setdefault(wk, []).append(e)
    cls = {"Major work": "k-major", "Regular report": "k-regular", "One-off": "k-oneoff"}
    for wk in sorted(weeks):
        rows = weeks[wk]
        n = sum(1 for e in rows if e[2] != "Major work")
        busy = any(wk <= b for b in busy_until) or n >= 4
        label = f"{n} item{'s' if n != 1 else ''}" + (' &middot; <span class="busy">limited capacity</span>' if busy else "")
        out.append(f'<div class="pc-week"><h3>Week of {wk.day} {wk.strftime("%B %Y")} <small>{label}</small></h3>')
        for d, name, kind, status in rows:
            out.append(f'<div class="pc-row {cls.get(kind, "")}"><span class="d">{esc(long_date(d))}</span>'
                       f'<span>{esc(name)}<span class="k">{esc(kind)}</span></span>'
                       f'<span class="s{" late" if status == "Running late" or "bank holiday" in status else ""}">{esc(status)}</span></div>')
        out.append("</div>")

    rrows = "".join(
        f"<tr><td>{esc(p['name'])}</td><td>{esc(p['kind'])}</td><td>{esc(p['what'])}</td>"
        f"<td>{esc(nice_date(nd.isoformat())) if nd else 'Complete'}</td><td>{esc(nice_date(last.isoformat())) if last else 'Not yet run'}</td></tr>"
        for p, it, nd, last in regular)
    out.append(f"""<h2>Everything on the Calendar</h2>
<div class="tp-scroll"><table class="tp-table"><thead><tr><th>Item</th><th>Type</th><th>What it is</th><th>Next due</th><th>Last done</th></tr></thead><tbody>{rrows}</tbody></table></div>""")

    out.append("<h2>Staged, Awaiting a Decision</h2>")
    out.append("<p>Requests and ideas the team has staged but the site owner has not yet accepted. They have no dates until they are accepted, when they move onto the calendar above.</p>")
    if staged:
        srows = "".join(f"<tr><td>{esc(p['title'])}</td><td>{esc(nice_date(d.isoformat()))}</td><td>{esc(p.get('note', ''))}</td></tr>"
                        for d, p in staged)
        out.append(f'<div class="tp-scroll"><table class="tp-table"><thead><tr><th>Request</th><th>Staged</th><th>Note</th></tr></thead><tbody>{srows}</tbody></table></div>')
    else:
        out.append("<p>Nothing is staged.</p>")

    out.append(f"<h2>Recently Completed</h2>")
    if done:
        drows = "".join(f"<tr><td>{esc(nice_date(d.isoformat()))}</td><td>{esc(n)}</td><td>{esc(k)}</td></tr>" for d, n, k in done)
        out.append(f'<p>The last {RECENT_DAYS // 7} weeks.</p><div class="tp-scroll"><table class="tp-table"><thead><tr><th>Completed</th><th>Item</th><th>Type</th></tr></thead><tbody>{drows}</tbody></table></div>')
    else:
        out.append(f"<p>Nothing completed in the last {RECENT_DAYS // 7} weeks.</p>")

    out.append("""<h2>How Work Reaches the Calendar</h2>
<ul>
<li>Requests go to the site owner, who passes them to the team. Nothing reaches the calendar without the site owner accepting it</li>
<li>An accepted request is given dates that fit around the regular reports and any major work, and appears in Coming Up</li>
<li>Major work, such as the Local Economic Assessment, takes priority for its set period, so a request accepted then will usually be dated after it</li>
<li>This page shows titles, dates and a one-line description only. The detail of each request stays with the site owner</li>
</ul>""")

    page("production-calendar.html", "Production Calendar",
         "What the Gateshead Economic Intelligence AI team is working on and when, what is staged, and when capacity is limited.",
         "\n".join(out))
    if unlisted:
        print("\nLeft off the page (no public wording in schedule/public-calendar.json):")
        for u in unlisted:
            print("  " + u)


if __name__ == "__main__":
    t = dt.date.today()
    if "--today" in sys.argv:
        t = dt.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
    main(t)
