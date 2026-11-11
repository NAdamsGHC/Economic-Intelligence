"""Pull every bill in the current Parliamentary session for What's New and the Horizon Calendar.

    python build/horizon/sweep_bills.py --from 2026-11-09 --to 2026-11-15 --out ../schedule/build-2026-11-16
    python build/horizon/sweep_bills.py --horizon             # dry run, prints what would change in horizon.json
    python build/horizon/sweep_bills.py --horizon --write     # writes horizon.json

Added 11 November 2026. Nathaniel's steer was that every bill is pulled into What's New
and the horizon scan, that local, digital and visitor economy bills are the priority, that
each bill shows its stage, and that a flag shows whether any documentation is attached.

Source: the UK Parliament Bills API (https://bills-api.parliament.uk), which is the data
behind bills.parliament.uk. It is free and keyless. Note that the session filter is
`Session=`. `SessionId=` is silently ignored and returns every bill since 2004.

What it does
  1. Finds the current session (the highest session id on recently updated bills) unless
     --session is given, and pulls every bill in it, carried-over bills included.
  2. For each bill, reads the long title, the stage history and the publications.
  3. Tags priority themes from bills_watch.json (local, digital, visitor), matching the
     short and long titles. The matched words are kept so a false match is easy to spot.
  4. The documentation flag is "Yes" if Parliament lists any publication against the bill,
     with the document types named. "None yet" is common for presentation bills, whose
     text is often never printed.
  5. What's New mode (--from, --to, --out) writes bills.md, bills.csv and bills-fragment.html.
     The fragment holds the priority table, the bills that moved in the window (a stage
     sitting, a new document or Royal Assent inside the window) and the complete register
     folded in a details block, ready to paste into the edition.
  6. Horizon mode (--horizon) adds every future stage sitting to horizon.json under the
     "bill" category, one item per bill stage, with later sittings of the same stage noted.
     Priority bills are amber. Government bills off our themes are green. Private members'
     and private bills off our themes are green and marked routine, so they sit behind the
     calendar's "Show routine items" toggle rather than swamping it. Every sitting is
     provisional, because the Commons and Lords only firm up business a week or two ahead.
     Sittings that drop off the Bills site schedule before their date are moved to archive
     with the reason.

Read-only on the web. Writes only to --out and, with --write, horizon.json. Never deletes (G8).
"""
import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SRC = REPO / "horizon" / "horizon.json"
WATCH = HERE / "bills_watch.json"
API = "https://bills-api.parliament.uk/api/v1/"
SITE = "https://bills.parliament.uk/bills/"

TYPES = {1: "Government", 2: "Private members' (Lords)", 3: "Consolidation", 4: "Hybrid", 5: "Private members' (ten minute rule)",
         6: "Private", 7: "Private members' (ballot)", 8: "Private members' (presentation)", 9: "Draft", 10: "Supply and Appropriation"}
GOVERNMENT = {1, 3, 4, 10}

# Publication types worth naming in the documentation flag, in display order. Others count but are summarised.
KEY_DOCS = [("Bill", "Bill text"), ("Bill (with Explanatory Memorandum)", "Bill text"), ("Explanatory Notes", "Explanatory Notes"),
            ("Impact Assessments", "Impact Assessment"), ("Briefing papers", "Library briefing"), ("Library Notes", "Library briefing"),
            ("Delegated Powers Memorandum", "Delegated Powers Memorandum"), ("Act of Parliament", "Act text"),
            ("Government document", "Government document"), ("Select Committee report", "Committee report"),
            ("Written evidence", "Written evidence")]


def get(path, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(API + path, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def current_session():
    items = get("Bills?SortOrder=DateUpdatedDescending&Take=50")["items"]
    return max(max(b["includedSessionIds"]) for b in items)


def words(stage):
    """Parliament's '2nd reading' as house style 'second reading'."""
    s = stage[:1].lower() + stage[1:]  # keeps "Lords" and "Commons" capitalised inside a stage name
    for a, b in (("1st", "first"), ("2nd", "second"), ("3rd", "third")):
        s = s.replace(a, b)
    return s


def day(iso):
    return iso[:10] if iso else None


def load_bills(session):
    out, skip = [], 0
    while True:
        r = get(f"Bills?Session={session}&Take=250&Skip={skip}")
        out += r["items"]
        skip += 250
        if skip >= r["totalResults"]:
            break
    return out


def enrich(b):
    bid = b["billId"]
    detail = get(f"Bills/{bid}")
    stages = get(f"Bills/{bid}/Stages?Take=200")["items"]
    pubs = get(f"Bills/{bid}/Publications")["publications"]
    b["longTitle"] = detail.get("longTitle") or ""
    b["stages"] = stages
    b["pubs"] = pubs
    return b


def themes_for(b, watch):
    text = b["shortTitle"] + " " + b.get("longTitle", "")
    hits = {}
    for key, t in watch["themes"].items():
        words = sorted({m.group(0).strip().lower() for p in t["patterns"] for m in re.finditer(p, text, re.I)})
        if words:
            hits[key] = words
    sid = str(b["billId"])
    for key in watch.get("include", {}).get(sid, {}).get("themes", []):
        hits.setdefault(key, ["added by hand"])
    if sid in watch.get("exclude", {}):
        hits = {}
    return hits


def doc_flag(pubs):
    if not pubs:
        return "None yet", []
    names = []
    for raw, label in KEY_DOCS:
        if any(p["publicationType"]["name"].strip() == raw for p in pubs) and label not in names:
            names.append(label)
    others = len([p for p in pubs if p["publicationType"]["name"].strip() not in dict(KEY_DOCS)])
    if others:
        names.append(f"{others} other")
    return f"Yes ({len(pubs)})", names


def stage_text(b):
    cs = b.get("currentStage")
    if b.get("billWithdrawn"):
        return "Withdrawn " + day(b["billWithdrawn"])
    if b.get("isDefeated"):
        return "Defeated"
    if not cs:
        return "No stage recorded"
    if cs["description"] == "Royal Assent":
        return "Royal Assent (Act)"
    return f"{cs['house']}, {words(cs['description'])}"


def build(session, today, frm, to, cache=None):
    watch = json.loads(WATCH.read_text(encoding="utf-8"))
    if cache and Path(cache).exists() and date.fromtimestamp(Path(cache).stat().st_mtime) == today:
        bills = json.loads(Path(cache).read_text(encoding="utf-8"))  # same-day pull, so both modes can share one fetch
    else:
        bills = load_bills(session)
        with ThreadPoolExecutor(max_workers=8) as ex:
            bills = list(ex.map(enrich, bills))
        if cache:
            Path(cache).parent.mkdir(parents=True, exist_ok=True)
            Path(cache).write_text(json.dumps(bills, ensure_ascii=False), encoding="utf-8")
    rows = []
    for b in bills:
        sittings = sorted(((day(s["date"]), st) for st in b["stages"] for s in st["stageSittings"] if s.get("date")),
                          key=lambda x: (x[0], x[1].get("sortOrder", 0)))
        past = [x for x in sittings if x[0] < today.isoformat()]
        future = [x for x in sittings if x[0] >= today.isoformat()]
        flag, docs = doc_flag(b["pubs"])
        th = themes_for(b, watch)
        moved = []
        if frm:
            upto = min(to, today.isoformat())  # a sitting only counts once it has happened, not when it is merely scheduled
            for d, st in sittings:
                if frm <= d <= upto:
                    moved.append(f"{st['house']} {words(st['description'])} on {date.fromisoformat(d).strftime('%d %b').lstrip('0')}")
            new_docs = {}
            for p in b["pubs"]:
                d = day(p.get("displayDate"))
                if d and frm <= d <= upto:
                    k = p["publicationType"]["name"].strip()
                    new_docs[k] = new_docs.get(k, 0) + 1
            moved = list(dict.fromkeys(moved))
            if new_docs:
                moved.append("New documents published, " + ", ".join(f"{k} ({n})" if n > 1 else k for k, n in new_docs.items()))
        rows.append({
            "id": b["billId"], "title": b["shortTitle"], "long_title": b.get("longTitle", ""),
            "type": TYPES.get(b["billTypeId"], str(b["billTypeId"])), "government": b["billTypeId"] in GOVERNMENT,
            "private": b["billTypeId"] not in GOVERNMENT, "stage": stage_text(b),
            "last_sitting": past[-1][0] if past else "", "next_sitting": future[0][0] if future else "",
            "next_stage": f"{future[0][1]['house']}, {words(future[0][1]['description'])}" if future else "",
            "docs_flag": flag, "docs": docs, "themes": th, "priority": bool(th), "moved": moved,
            "is_act": b.get("isAct"), "url": SITE + str(b["billId"]), "future": future,
            "last_update": day(b.get("lastUpdate")),
        })
    rows.sort(key=lambda r: (not r["priority"], not r["government"], r["title"]))
    return rows, watch


def theme_label(r, watch):
    return ", ".join(watch["themes"][k]["label"] for k in r["themes"]) or "Not on our themes"


# ---------------------------------------------------------------- What's New outputs

def write_whatsnew(rows, watch, session, frm, to, out):
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "bills.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["bill_id", "title", "type", "stage", "last_sitting", "next_sitting", "next_stage", "documents", "document_types",
                    "priority_themes", "matched_words", "moved_in_window", "url", "long_title"])
        for r in rows:
            w.writerow([r["id"], r["title"], r["type"], r["stage"], r["last_sitting"], r["next_sitting"], r["next_stage"], r["docs_flag"],
                        "; ".join(r["docs"]), theme_label(r, watch) if r["priority"] else "",
                        "; ".join(f"{k}: {', '.join(v)}" for k, v in r["themes"].items()), " | ".join(r["moved"]), r["url"], r["long_title"]])

    pri = [r for r in rows if r["priority"]]
    moved = [r for r in rows if r["moved"]]
    nodocs = [r for r in rows if r["docs_flag"] == "None yet"]
    fd = lambda d: date.fromisoformat(d).strftime("%d %B %Y").lstrip("0")
    counts = (f"The current session of Parliament has {len(rows)} bills, {sum(r['government'] for r in rows)} of them government bills, "
              f"{sum(1 for r in rows if r['is_act'])} already Acts. "
              f"{len(pri)} touch the local, digital or visitor economy. {len(moved)} moved between {fd(frm)} and {fd(to)}. "
              f"{len(nodocs)} have no documents published yet.")

    md = [f"# Parliamentary bills, {frm} to {to}", "", counts, "",
          "Source: UK Parliament Bills API (bills.parliament.uk), pulled " + date.today().isoformat() + ".", "",
          "## Priority bills", "", "| Bill | Type | Theme | Stage | Next sitting | Documents | Moved in window |", "|---|---|---|---|---|---|---|"]
    for r in pri:
        md.append(f"| [{r['title']}]({r['url']}) | {r['type']} | {theme_label(r, watch)} | {r['stage']} | "
                  f"{(r['next_sitting'] + ' ' + r['next_stage']) if r['next_sitting'] else 'None scheduled'} | "
                  f"{r['docs_flag']}{(': ' + ', '.join(r['docs'])) if r['docs'] else ''} | {'; '.join(r['moved']) or 'No'} |")
    md += ["", "## Matched words, to check for false matches", ""]
    for r in pri:
        md.append(f"- {r['title']} ({r['id']}) " + "; ".join(f"{k}: {', '.join(v)}" for k, v in r["themes"].items()))
    (out / "bills.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    e = html.escape

    def docs_cell(r):
        if r["docs_flag"] == "None yet":
            return '<span class="rag g">NONE YET</span>'
        return f'<span class="rag a">YES</span> {e(", ".join(r["docs"]))}'

    def nice(d):
        return date.fromisoformat(d).strftime("%d %b %Y").lstrip("0")

    def row(r, theme=True):
        if not r["next_sitting"]:
            nxt = "None scheduled"
        elif r["next_stage"] == r["stage"]:
            nxt = e(nice(r["next_sitting"]))
        else:
            nxt = f"{e(nice(r['next_sitting']))}, {e(r['next_stage'])}"
        cells = [f'<a href="{e(r["url"])}">{e(r["title"])}</a>', e(r["type"])]
        if theme:
            cells.append(e(theme_label(r, watch)))
        cells += [e(r["stage"]), nxt, docs_cell(r)]
        return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"

    head = "<tr><th>Bill</th><th>Type</th><th>Theme</th><th>Stage now</th><th>Next sitting</th><th>Documents</th></tr>"
    frag = [f"<!-- Generated by build/horizon/sweep_bills.py on {date.today().isoformat()} for {frm} to {to}. Paste under the edition's Parliamentary Bills heading. -->",
            "<h2>Parliamentary Bills</h2>",
            f"<p>{e(counts)} Taken from the UK Parliament Bills site. The documents column shows whether Parliament has published anything "
            "against the bill, such as the bill text, Explanatory Notes, an Impact Assessment or a Library briefing.</p>",
            "<h3>Bills on our priority themes</h3>",
            '<div class="wn-scroll"><table class="wn-cal">' + head + "".join(row(r) for r in pri) + "</table></div>",
            f"<h3>Bills that moved, {e(fd(frm))} to {e(fd(to))}</h3>"]
    if moved:
        frag.append('<div class="wn-scroll"><table class="wn-cal"><tr><th>Bill</th><th>Theme</th><th>What happened</th><th>Stage now</th><th>Documents</th></tr>' +
                    "".join(f'<tr><td><a href="{e(r["url"])}">{e(r["title"])}</a></td><td>{e(theme_label(r, watch))}</td>'
                            f'<td>{e("; ".join(r["moved"]))}</td><td>{e(r["stage"])}</td><td>{docs_cell(r)}</td></tr>' for r in moved) + "</table></div>")
    else:
        frag.append("<p>No bill had a stage sitting or a new document in the window.</p>")
    frag += ['<details class="wn-fold">',
             f"<summary>Every bill in the session, {len(rows)} in all ({len(pri)} on our themes, {len(nodocs)} with no documents yet)</summary>",
             '<div class="wn-scroll"><table class="wn-log">' + head + "".join(row(r) for r in rows) + "</table></div>", "</details>"]
    (out / "bills-fragment.html").write_text("\n".join(frag) + "\n", encoding="utf-8")
    print(counts)
    print(f"Wrote bills.md, bills.csv and bills-fragment.html to {out}")
    print("Priority bills:")
    for r in pri:
        print(f"  {r['title']} [{theme_label(r, watch)}] {r['stage']}; docs {r['docs_flag']}" + (f"; moved: {'; '.join(r['moved'])}" if r["moved"] else ""))


# ---------------------------------------------------------------- Horizon

def horizon(rows, watch, today, write):
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    doc["categories"].setdefault("bill", "Bill stage in Parliament")
    held = {x["id"]: x for x in doc["items"]}
    fresh = {}
    for r in rows:
        by_stage = {}
        for d, st in r["future"]:
            by_stage.setdefault(st["id"], (st, []))[1].append(d)
        for sid, (st, dates) in by_stage.items():
            dates = sorted(set(dates))
            iid = f"bill-{r['id']}-{sid}"
            if r["priority"]:
                rag, routine = "a", False
                why = f"{theme_label(r, watch)} bill. {r['long_title']}"
            elif r["government"]:
                rag, routine = "g", False
                why = f"Government bill off our priority themes. {r['long_title']}"
            else:
                rag, routine = "g", True
                why = f"{r['type']} bill off our priority themes. {r['long_title']}"
            if len(dates) > 1:
                why += f" This stage has {len(dates)} sittings scheduled, the last on {dates[-1]}."
            why += f" Documents published: {r['docs_flag'].lower()}" + (f" ({', '.join(r['docs'])})." if r["docs"] else ".")
            item = {"id": iid, "date": dates[0], "title": f"{st['house']} {words(st['description'])} of the {r['title']}",
                    "category": "bill", "rag": rag, "status": "provisional", "why": why.strip(),
                    "source": {"name": f"UK Parliament, Bills site, {r['title']} stages", "url": r["url"] + "/stages"},
                    "verified": today.isoformat(), "bill_stage_now": r["stage"], "bill_documents": r["docs_flag"]}
            if routine:
                item["routine"] = True
            fresh[iid] = item

    added, changed, dropped = [], [], []
    for iid, new in fresh.items():
        if iid in held:
            old = held[iid]
            moves = [f"{k} {old.get(k)} -> {new.get(k)}" for k in ("date", "rag", "bill_stage_now", "bill_documents") if old.get(k) != new.get(k)]
            if moves:
                changed.append(f"{old['title']}: " + "; ".join(moves))
            action = old.get("action")
            old.update(new)
            if action:
                old["action"] = action  # keep any action we wrote by hand
        else:
            doc["items"].append(new)
            added.append(f"{new['date']} {new['title']}" + (" (routine)" if new.get("routine") else ""))
    keep = []
    for x in doc["items"]:
        if x["id"].startswith("bill-") and x["id"] not in fresh and x["date"] >= today.isoformat() and x["status"] != "published":
            x["retired"] = f"Dropped from the Bills site schedule before its date, found {today.isoformat()}"
            doc.setdefault("archive", []).append(x)
            dropped.append(f"{x['date']} {x['title']}")
        else:
            keep.append(x)
    doc["items"] = keep

    pri = sum(1 for x in fresh.values() if x["rag"] == "a")
    print(f"Bills: {len(fresh)} future bill stages ({pri} priority, {sum(1 for x in fresh.values() if x.get('routine'))} routine). "
          f"{len(added)} added, {len(changed)} changed, {len(dropped)} dropped off the schedule")
    for a in added:
        if "(routine)" not in a:
            print("  + " + a)
    rt = [a for a in added if "(routine)" in a]
    if rt:
        print(f"  + and {len(rt)} routine private members' and private bill stages")
    for c in changed:
        print("  ~ " + c)
    for d in dropped:
        print("  - " + d)
    if write:
        doc["items"].sort(key=lambda x: (x["date"], x.get("time") or "99", x["title"]))
        SRC.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
        print("horizon.json written. Add a log entry, then run build_horizon.py.")
    else:
        print("Dry run. Re-run with --write to apply.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--to")
    ap.add_argument("--out")
    ap.add_argument("--horizon", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--session", type=int)
    ap.add_argument("--cache", help="JSON file to keep the raw pull in. Reused if written today, so a second run takes seconds")
    a = ap.parse_args()
    if not a.horizon and not (a.frm and a.to and a.out):
        ap.error("give --from, --to and --out for What's New, or --horizon")
    today = date.today()
    session = a.session or current_session()
    rows, watch = build(session, today, a.frm, a.to, a.cache)
    if a.frm:
        write_whatsnew(rows, watch, session, a.frm, a.to, Path(a.out))
    if a.horizon:
        horizon(rows, watch, today, a.write)


if __name__ == "__main__":
    main()
