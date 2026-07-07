"""Refresh economy/els-scorecard.html from the live ONS Explore Local
Statistics all-datasets workbook.

Steps: download workbook -> parse to scorecard_data.json -> if the data
actually changed (ignoring the workbook's own generation date), render the
dashboard with today's build date. When nothing changed, the previous JSON is
left untouched so the git working tree stays clean and the Action skips the
commit.

Usage: python build/els-scorecard/build.py [existing-workbook.xlsx]
Passing a workbook path skips the download (local dev).
"""
import datetime
import json
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parent.parent
WB_URL = "https://www.ons.gov.uk/explore-local-statistics/files/all-datasets.xlsx"

sys.path.insert(0, str(BASE))
from parse_all import parse  # noqa: E402

def comparable(d):
    # round-trip through JSON so int keys / tuples compare like the on-disk copy
    d = json.loads(json.dumps(d))
    d.pop("elsGenerated", None)   # ONS regenerates the file on a cycle; only data changes matter
    return d

def main():
    data_dir = BASE / "data"
    data_dir.mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        wb = Path(sys.argv[1])
        print(f"Using local workbook {wb}")
    else:
        wb = data_dir / "all-datasets.xlsx"
        print(f"Downloading {WB_URL} ...")
        req = urllib.request.Request(WB_URL, headers={"User-Agent": "Mozilla/5.0 (els-scorecard refresh)"})
        with urllib.request.urlopen(req, timeout=300) as r:
            wb.write_bytes(r.read())
        print(f"  {wb.stat().st_size/1e6:.1f} MB")

    new = parse(wb)
    print(f"Parsed {len(new['ind'])} indicators (workbook generated {new['elsGenerated']})")

    json_path = data_dir / "scorecard_data.json"
    if json_path.exists():
        old = json.loads(json_path.read_text(encoding="utf-8"))
        if comparable(old) == comparable(new):
            print("No data changes — leaving dashboard as is.")
            return

    json_path.write_text(json.dumps(new, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    new["built"] = datetime.date.today().isoformat()
    src = (BASE / "dashboard_src.html").read_text(encoding="utf-8")
    assert "__DATA__" in src
    out_path = REPO / "economy" / "els-scorecard.html"
    out_path.write_text(src.replace("__DATA__", json.dumps(new, separators=(",", ":"), ensure_ascii=False), 1),
                        encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size/1024:.0f} KB)")

if __name__ == "__main__":
    main()
