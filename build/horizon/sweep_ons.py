"""Refresh the ONS part of horizon.json from the ONS release calendar, and retire old items.

    python build/horizon/sweep_ons.py            # dry run, prints what would change
    python build/horizon/sweep_ons.py --write    # writes horizon.json

What it does
  1. Pulls six months of upcoming releases from the ONS release calendar API.
  2. Keeps only the series in RULES (the ones we use). Extend RULES, never add
     ONS releases to horizon.json by hand.
  3. Adds new releases, and updates the date, time or status of ones already held
     (same id). Every move is printed so it can go in the chat report and the log.
  4. Marks items dated before today as published, and moves items more than 14 days
     past into "archive".
It never touches non-ONS items apart from step 4. Those are verified by hand at
their own source (see gateshead-briefing/references/horizon-scan.md).
Run build_horizon.py afterwards.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SRC = REPO / "horizon" / "horizon.json"
API = "https://api.beta.ons.gov.uk/v1/search/releases"

# regex on the ONS title, display title, why it matters, rag, routine
RULES = [
    (r"^UK Labour Market:? \w+ 20\d\d$", "UK labour market, with regional tables and PAYE Real Time Information",
     "Gateshead's claimant count and payrolled employees, and the regional labour market tables.", "a", False),
    (r"^Consumer price inflation, UK: \w+ 20\d\d$", "Consumer price inflation", "Feeds the cost-of-living index.", "g", True),
    (r"^GDP monthly estimate, UK: \w+ 20\d\d$", "GDP monthly estimate", "National growth context.", "g", True),
    (r"^GDP first quarterly estimate, UK: [\w ]+ 20\d\d$", "GDP first quarterly estimate", "National growth context for the quarterly monitor.", "g", False),
    (r"^Private rent and house prices", "Private rent and house prices", "Local authority rents and house prices, so a Gateshead cut.", "g", True),
    (r"^Public sector finances, UK: \w+ 20\d\d$", "Public sector finances", "Fiscal backdrop.", "g", True),
    (r"^Business Register and Employment Survey", "BRES, provisional and revised results",
     "Employee jobs by industry for Gateshead. Supersedes the BRES figures across our products.", "a", False),
    (r"Business Demography 20\d\d$", "Business demography", "Local business births, deaths and survival.", "a", False),
    (r"^Regional and subregional labour productivity", "Regional and subregional labour productivity",
     "Gateshead's GVA per hour and per filled job.", "r", False),
    (r"^Regional economic activity by gross domestic product", "Regional economic activity by GDP",
     "Gateshead's GVA, with a revised back series.", "r", False),
    (r"^Regional gross disposable household income", "Regional gross disposable household income",
     "Gateshead's household income per head.", "a", False),
    (r"^UK business; activity, size and location", "UK Business Counts",
     "A new business counts vintage that supersedes the figures we publish.", "r", False),
    (r"^Employee earnings in the UK", "Employee earnings in the UK (ASHE)", "Resident and workplace earnings for Gateshead.", "a", False),
    (r"^Population estimates by output areas", "Small-area population estimates", "Ward and neighbourhood populations for the places work.", "a", False),
    (r"^Population estimates for the UK", "Population estimates for the UK", "National and country totals.", "g", False),
    (r"not in education, employment or training", "Young people not in education, employment or training (NEET)",
     "UK and regional NEET context for the youth employment thread.", "a", False),
    (r"^Long-term international migration", "Long-term international migration", "Population change context.", "g", False),
    (r"^Provisional population estimate for the UK", "Provisional UK population estimate", "National context.", "g", False),
    (r"^Working and workless households", "Working and workless households", "Household worklessness context.", "g", False),
    (r"^Children living in long-term workless", "Children in long-term workless households", "Child poverty context.", "g", False),
    (r"^Life expectancy for local areas", "Life expectancy for local areas", "Gateshead life expectancy refresh.", "g", False),
    (r"Tourism Satellite Account", "UK Tourism Satellite Account", "Visitor economy context for the levy work.", "g", False),
    (r"^Travel trends", "Travel trends", "Visitor economy context.", "g", False),
    (r"^Short-term lets", "Short-term lets through online platforms",
     "Part of the overnight-stay baseline the visitor levy work needs.", "a", False),
    (r"^International trade in UK nations, regions and cities", "International trade in UK nations, regions and cities", "Regional export context.", "g", False),
    (r"^Local sites and numbers of employees linked to companies involved in international trade", "Local sites and employees linked to international trade in services", "Subnational trade exposure.", "g", False),
    (r"^UK National Accounts, The Blue Book", "UK National Accounts, the Blue Book", "Method changes feed the next regional accounts.", "g", False),
    (r"^Labour Force Survey quality update", "Labour Force Survey quality update", "Quality of the survey behind every APS estimate we publish.", "a", False),
    (r"^Investigating non-response to the Labour Force Survey", "Investigating non-response to the Labour Force Survey", "Survey quality behind the APS.", "g", False),
    (r"^Productivity flash estimate", "Productivity flash estimate", "Headline productivity. On the new component method from November 2026.", "a", False),
    (r"^Household Costs Indices", "Household Costs Indices", "Feeds the cost-of-living index.", "g", False),
    (r"^Estimates of green jobs", "Estimates of green jobs", "Green economy context.", "g", False),
    (r"^Low carbon and renewable energy economy, UK", "Low carbon and renewable energy economy", "Green economy context.", "g", False),
    (r"^Trends in UK business dynamism", "Trends in UK business dynamism and productivity", "Productivity context.", "g", False),
    (r"^Insights on UK labour market dynamism", "Labour market dynamism from linked employer-employee data", "Labour market context.", "g", False),
    (r"^Average household income", "Average household income", "Household income context.", "g", False),
]


def uk_local(iso):
    """UTC timestamp to UK local date and time. BST runs from the last Sunday in March to the last Sunday in October."""
    t = datetime.fromisoformat(iso.replace("Z", "+00:00")).replace(tzinfo=None)

    def last_sunday(y, m):
        d = date(y, m, 31)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    y = t.year
    start = datetime.combine(last_sunday(y, 3), datetime.min.time()) + timedelta(hours=1)
    end = datetime.combine(last_sunday(y, 10), datetime.min.time()) + timedelta(hours=1)
    t = t + timedelta(hours=1 if start <= t < end else 0)
    return t.strftime("%Y-%m-%d"), t.strftime("%H:%M")


def fetch(today, months=6):
    to = (today + timedelta(days=31 * months)).isoformat()
    q = {"fromDate": today.isoformat(), "toDate": to, "limit": 1000,
         "release-type": "type-upcoming", "sort": "release_date_asc"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=60))["releases"], to


def suffix(title):
    m = re.search(r":\s*(.+)$", title)
    return ", " + m.group(1) if m and not re.search(r"^\w+ 20\d\d$", m.group(1)) else ""


def main():
    write = "--write" in sys.argv
    today = date.today()
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    held = {x["id"]: x for x in doc["items"]}
    releases, to = fetch(today)
    added, changed = [], []
    seen_keys = set()
    for r in releases:
        de = r["description"]
        if de.get("cancelled") or de.get("published"):
            continue
        for rx, disp, why, rag, routine in RULES:
            if not re.search(rx, de["title"]):
                continue
            d, t = uk_local(de["release_date"])
            key = (disp, d)
            if key in seen_keys:
                break
            seen_keys.add(key)
            conf = bool(de.get("finalised"))
            label = de.get("provisional_date") if not conf else None
            if label and re.search(r"\d{1,2} \w+ 20\d\d", label):
                label = None  # a provisional day, not a range
            iid = "ons-" + r["uri"].rstrip("/").split("/")[-1]
            new = {"id": iid, "date": d, "title": disp + ("" if routine else suffix(de["title"])),
                   "category": "data", "rag": rag, "status": "confirmed" if conf else "provisional",
                   "why": why, "source": {"name": "ONS release calendar", "url": "https://www.ons.gov.uk" + r["uri"]},
                   "verified": today.isoformat()}
            if conf:
                new["time"] = t
            if label:
                new["date_label"] = label
            if routine:
                new["routine"] = True
            if iid in held:
                old = held[iid]
                moves = [f"{k} {old.get(k)} -> {new.get(k)}" for k in ("date", "time", "status", "date_label") if old.get(k) != new.get(k)]
                if moves:
                    changed.append(f"{old['title']}: " + "; ".join(moves))
                for k in ("date", "status"):
                    old[k] = new[k]
                for k in ("time", "date_label"):
                    if k in new:
                        old[k] = new[k]
                    else:
                        old.pop(k, None)
                old["verified"] = today.isoformat()  # keeps our own why, rag and action
            else:
                doc["items"].append(new)
                held[iid] = new
                added.append(f"{d} {new['title']}")
            break

    # retire: past items become published, then archive after 14 days
    cutoff = (today - timedelta(days=14)).isoformat()
    removed = []
    keep = []
    for x in doc["items"]:
        if x["date"] < today.isoformat() and not x.get("date_label"):
            x["status"] = "published"
        if x["date"] < cutoff:
            doc.setdefault("archive", []).append(x)
            removed.append(f"{x['date']} {x['title']}")
        else:
            keep.append(x)
    doc["items"] = keep
    doc["window"]["ons_to"] = to

    print(f"ONS calendar to {to}: {len(added)} added, {len(changed)} changed, {len(removed)} retired to archive")
    for a in added:
        print("  + " + a)
    for c in changed:
        print("  ~ " + c)
    for rm in removed:
        print("  - " + rm)
    if write:
        doc["items"].sort(key=lambda x: (x["date"], x.get("time") or "99", x["title"]))
        SRC.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
        print("horizon.json written. Add a log entry, then run build_horizon.py.")
    else:
        print("Dry run. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
