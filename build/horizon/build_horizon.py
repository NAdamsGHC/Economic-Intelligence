"""Build the Horizon Calendar page from horizon/horizon.json.

    python build/horizon/build_horizon.py

horizon.json is the single source of truth. This script validates it, embeds it
in template.html to write horizon/index.html, and writes horizon/horizon.ics for
people who want the dated items in their own calendar. Run it after every edit
to horizon.json. It never edits the json itself.
"""
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SRC = REPO / "horizon" / "horizon.json"
TEMPLATE = HERE / "template.html"
OUT_HTML = REPO / "horizon" / "index.html"
OUT_ICS = REPO / "horizon" / "horizon.ics"

RAGS = {"r", "a", "g"}
STATUSES = {"confirmed", "provisional", "expected", "published"}
REQUIRED = ["id", "date", "title", "category", "rag", "status", "why", "source", "verified"]


def validate(doc):
    errors = []
    cats = doc.get("categories", {})
    seen = set()
    for i, x in enumerate(doc.get("items", [])):
        where = f"item {i} ({x.get('id', '?')})"
        for k in REQUIRED:
            if k not in x:
                errors.append(f"{where}: missing {k}")
        if x.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(x.get("id"))
        try:
            date.fromisoformat(x.get("date", ""))
            date.fromisoformat(x.get("verified", ""))
        except ValueError:
            errors.append(f"{where}: date or verified is not YYYY-MM-DD")
        if x.get("rag") not in RAGS:
            errors.append(f"{where}: rag must be r, a or g")
        if x.get("status") not in STATUSES:
            errors.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if x.get("category") not in cats:
            errors.append(f"{where}: unknown category {x.get('category')}")
        src = x.get("source", {})
        if not str(src.get("url", "")).startswith("http"):
            errors.append(f"{where}: source.url must be a full link to the primary source")
        if x.get("status") == "expected" and not x.get("date_label"):
            errors.append(f"{where}: an expected item needs a date_label (month or season)")
        if "time" in x and not re.fullmatch(r"\d\d:\d\d", x["time"]):
            errors.append(f"{where}: time must be HH:MM, UK time")
    return errors


def ics_escape(s):
    return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out = []
    while len(line.encode("utf-8")) > 74:
        cut = 74
        while len(line[:cut].encode("utf-8")) > 74:
            cut -= 1
        out.append(line[:cut])
        line = " " + line[cut:]
    out.append(line)
    return "\r\n".join(out)


def build_ics(doc):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Gateshead Economic Intelligence//Horizon Calendar//EN",
             "CALSCALE:GREGORIAN", "X-WR-CALNAME:Gateshead Horizon Calendar"]
    for x in doc["items"]:
        if x.get("date_label") or x["status"] == "published":
            continue  # only items with a fixed day go into other people's calendars
        d = x["date"].replace("-", "")
        nxt = date.fromordinal(date.fromisoformat(x["date"]).toordinal() + 1).isoformat().replace("-", "")
        desc = x["why"] + (" Action: " + x["action"] if x.get("action") else "") + \
            (" Time: " + x["time"] + " UK." if x.get("time") else "") + \
            " Status: " + x["status"] + ". Source: " + x["source"]["name"] + " " + x["source"]["url"]
        lines += ["BEGIN:VEVENT", f"UID:{x['id']}@gateshead-economic-intelligence", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{d}", f"DTEND;VALUE=DATE:{nxt}",
                  fold("SUMMARY:" + ics_escape({"r": "[Red] ", "a": "[Amber] ", "g": ""}[x["rag"]] + x["title"])),
                  fold("DESCRIPTION:" + ics_escape(desc)), fold("URL:" + x["source"]["url"]),
                  "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    errors = validate(doc)
    if errors:
        print("horizon.json failed validation:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    doc["items"].sort(key=lambda x: (x["date"], x.get("time") or "99", x["title"]))
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*DATA*/", payload)
    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_ICS.write_text(build_ics(doc), encoding="utf-8", newline="")
    n = len(doc["items"])
    print(f"Built {OUT_HTML.relative_to(REPO)} and {OUT_ICS.relative_to(REPO)} from {n} items "
          f"({len(doc.get('pending_verification', []))} claims pending verification, not shown).")


if __name__ == "__main__":
    main()
