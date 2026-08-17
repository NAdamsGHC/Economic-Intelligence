"""Parse the ONS Explore Local Statistics all-datasets workbook into the
reduced scorecard data object consumed by dashboard_src.html.

Per indicator (where Gateshead E08000037 has data): Gateshead full series,
best national benchmark (England > UK > GB > E&W) series, North East series,
NECA 7 + ONS economic statistical neighbour latest values, all-LAD latest
values (sorted, for rank/quartile/distribution), Gateshead 95% CI where the
table publishes one, source line, unit, period labels, polarity and domain.

Run via build.py; standalone: python parse_all.py [workbook.xlsx]
"""
import json
import re
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parent

GH = "E08000037"
NE = "E12000001"
BENCH_PREF = ["E92000001", "K02000001", "K03000001", "K04000001"]
BENCH_NAME = {"E92000001": "England", "K02000001": "UK", "K03000001": "Great Britain", "K04000001": "England & Wales"}
NECA = ["E08000037", "E08000021", "E08000022", "E08000023", "E08000024", "E06000047", "E06000057"]
NEIGH = ["E08000036", "E08000013", "E08000016", "E06000047", "E08000014",
         "W06000022", "W06000014", "E08000024", "E06000052", "W06000004",
         "W06000008", "W06000009", "E06000057", "E06000046", "W06000003",
         "E06000005", "E08000017", "E08000027", "E06000066", "N09000010"]
LAD_RE = re.compile(r"^(E06|E07|E08|E09|W06|S12|N09)")

# Indicators are keyed by NAME, not by ELS sheet number. ONS renumbers the
# all-datasets sheets between workbook generations (it did so between the
# 26/06/2026 and 23/07/2026 editions, shifting most sheets by +1), which
# silently dropped seven indicators and mis-assigned polarity on twenty more
# when these maps were keyed by number. Names are resolved to whatever sheet
# currently holds them, so a future renumbering is a no-op. If ONS renames an
# indicator the build fails loudly rather than shipping a wrong one.

# polarity: +1 higher is better, -1 lower is better, 0 context/neutral
POL = {
    "Total population": 0,
    "Population density": 0,
    "Five-year population change": 0,
    "Median age": 0,
    "Population aged 0 to 15": 0,
    "Population aged 16 to 64": 0,
    "Population aged 65 and over": 0,
    "Employment rate (Great Britain)": 1,
    "Modelled unemployment rate": -1,
    "Economic inactivity rate (Great Britain)": -1,
    "Claimant Count": -1,
    "Gross median weekly pay": 1,
    "Gross disposable household income per head": 1,
    "Children in relative poverty before housing costs": -1,
    "Children in relative poverty after housing costs": -1,
    "Fuel poverty (England)": -1,
    "Gross value added per hour worked": 1,
    "Gross value added per job filled": 1,
    "Gross domestic product per head at current market prices": 1,
    "Gross domestic product per head in chained volume measures": 1,
    "Active businesses": 0,
    "Business births": 1,
    "Business deaths": -1,
    "High growth businesses": 1,
    "One-year business survival rate": 1,
    "Two-year business survival rate": 1,
    "Three-year business survival rate": 1,
    "Four-year business survival rate": 1,
    "Five-year business survival rate": 1,
    "Net additions to the housing stock (England)": 1,
    "Average house price": 0,
    "Housing affordability ratio (residence-based)": -1,
    "First-time buyer mortgage sales": 1,
    "Communication and language skills by end of early years foundation stage": 1,
    "Literacy skills by end of early years foundation stage": 1,
    "Maths skills by end of early years foundation stage": 1,
    "Pupils meeting the expected standard in reading, writing and maths at the end of Key Stage 2": 1,
    "GCSEs in English and Maths": 1,
    "Persistent absences for all pupils": -1,
    "Persistent absences for pupils eligible for free school meals": -1,
    "Persistent absences for pupils looked after by local authorities": -1,
    "Further education and skills learner achievements": 1,
    "Further education and skills participation": 1,
    "Apprenticeship achievements (England)": 1,
    "Apprenticeship starts (England)": 1,
    "Level 3 or above qualifications (Great Britain)": 1,
    "No qualifications": -1,
    "Female healthy life expectancy": 1,
    "Male healthy life expectancy": 1,
    "Cigarette smokers": -1,
    "Adult obesity prevalence": -1,
    "Healthy weight prevalence in children at reception age": 1,
    "Healthy weight prevalence in children at Year 6 age": 1,
    "Obesity prevalence in children at reception age": -1,
    "Obesity prevalence in children at Year 6 age": -1,
    # NCMP bands are mutually exclusive, so a low "overweight" share is a
    # by-product of a high "obese" share, not a strength. Context-only.
    "Overweight prevalence in children at reception age": 0,
    "Overweight prevalence in children at Year 6 age": 0,
    "Underweight prevalence in children at reception age": -1,
    "Underweight prevalence in children at Year 6 age": -1,
    "Cancer diagnosis at stage 1 and 2": 1,
    "Preventable cardiovascular mortality (England)": -1,
    "Anxiety": -1,
    "Feeling life is worthwhile": 1,
    "Happiness": 1,
    "Life satisfaction": 1,
    "Greenhouse gas emissions": -1,
    "Domestic electricity consumption": 0,
    "Domestic gas consumption": 0,
    "Air pollution regulating": 0,
    "Greenhouse gas regulating": 0,
    "Urban heat regulating": 0,
    "Gigabit capable broadband": 1,
    "Premises below 30Mbps": -1,
    "4G coverage": 1,
    "5G coverage": 1,
    "Public electric vehicle chargers": 1,
    "Motor vehicle flow": 0,
    "Food outlets": 0,
    "Supermarkets": 1,
    "Sports facilities": 1,
    "Museums": 1,
    "Residents within a 30 minute walk of their nearest library": 1,
    "Residents within a 30 minute walk of their nearest railway station": 1,
    "Engaged with the arts": 1,
    "Visited a heritage site": 1,
    "Visited a museum or gallery": 1,
    "Visited a public library": 1,
    "Average length of short-term let stay": 0,
    "Number of guest nights at a short-term let": 0,
}

DOMAINS = [
    ("Population", [
        "Total population",
        "Population density",
        "Five-year population change",
        "Median age",
        "Population aged 0 to 15",
        "Population aged 16 to 64",
        "Population aged 65 and over",
    ]),
    ("Work & income", [
        "Employment rate (Great Britain)",
        "Modelled unemployment rate",
        "Economic inactivity rate (Great Britain)",
        "Claimant Count",
        "Gross median weekly pay",
        "Gross disposable household income per head",
        "Children in relative poverty before housing costs",
        "Children in relative poverty after housing costs",
        "Fuel poverty (England)",
    ]),
    ("Economy & productivity", [
        "Gross value added per hour worked",
        "Gross value added per job filled",
        "Gross domestic product per head at current market prices",
        "Gross domestic product per head in chained volume measures",
    ]),
    ("Business", [
        "Active businesses",
        "Business births",
        "Business deaths",
        "High growth businesses",
        "One-year business survival rate",
        "Two-year business survival rate",
        "Three-year business survival rate",
        "Four-year business survival rate",
        "Five-year business survival rate",
    ]),
    ("Housing", [
        "Net additions to the housing stock (England)",
        "Average house price",
        "Housing affordability ratio (residence-based)",
        "First-time buyer mortgage sales",
    ]),
    ("Education & skills", [
        "Communication and language skills by end of early years foundation stage",
        "Literacy skills by end of early years foundation stage",
        "Maths skills by end of early years foundation stage",
        "Pupils meeting the expected standard in reading, writing and maths at the end of Key Stage 2",
        "GCSEs in English and Maths",
        "Persistent absences for all pupils",
        "Persistent absences for pupils eligible for free school meals",
        "Persistent absences for pupils looked after by local authorities",
        "Further education and skills learner achievements",
        "Further education and skills participation",
        "Apprenticeship achievements (England)",
        "Apprenticeship starts (England)",
        "Level 3 or above qualifications (Great Britain)",
        "No qualifications",
    ]),
    ("Health & wellbeing", [
        "Female healthy life expectancy",
        "Male healthy life expectancy",
        "Cigarette smokers",
        "Adult obesity prevalence",
        "Healthy weight prevalence in children at reception age",
        "Healthy weight prevalence in children at Year 6 age",
        "Obesity prevalence in children at reception age",
        "Obesity prevalence in children at Year 6 age",
        "Overweight prevalence in children at reception age",
        "Overweight prevalence in children at Year 6 age",
        "Underweight prevalence in children at reception age",
        "Underweight prevalence in children at Year 6 age",
        "Cancer diagnosis at stage 1 and 2",
        "Preventable cardiovascular mortality (England)",
        "Anxiety",
        "Feeling life is worthwhile",
        "Happiness",
        "Life satisfaction",
    ]),
    ("Environment & energy", [
        "Greenhouse gas emissions",
        "Domestic electricity consumption",
        "Domestic gas consumption",
        "Air pollution regulating",
        "Greenhouse gas regulating",
        "Urban heat regulating",
    ]),
    ("Connectivity & transport", [
        "Gigabit capable broadband",
        "Premises below 30Mbps",
        "4G coverage",
        "5G coverage",
        "Public electric vehicle chargers",
        "Motor vehicle flow",
    ]),
    ("Amenities & culture", [
        "Food outlets",
        "Supermarkets",
        "Sports facilities",
        "Museums",
        "Residents within a 30 minute walk of their nearest library",
        "Residents within a 30 minute walk of their nearest railway station",
        "Engaged with the arts",
        "Visited a heritage site",
        "Visited a museum or gallery",
        "Visited a public library",
        "Average length of short-term let stay",
        "Number of guest nights at a short-term let",
    ]),
]

# indicator whose ONS header says (%) but whose measure is a ratio
RATIO_UNIT_INDICATOR = "Housing affordability ratio (residence-based)"

# Sheets deliberately excluded: not single-value LA indicators.
SKIP_SHEETS = {"population by age and sex"}


def sheet_index(wb):
    """Map normalised indicator title -> sheet name, for every numbered sheet."""
    idx = {}
    for s in wb.sheetnames:
        if not s.isdigit():
            continue
        for i, r in enumerate(wb[s].iter_rows(values_only=True)):
            if i > 3:
                break
            if r and r[0]:
                key = re.sub(r"\s*\[note \d+\]\s*", "", str(r[0])).strip().lower()
                idx.setdefault(key, s)
                break
    return idx


def resolve(wb):
    """Resolve the configured indicator names to current sheet numbers."""
    idx = sheet_index(wb)
    order, missing = [], []
    for _, names in DOMAINS:
        for n in names:
            s = idx.get(n.strip().lower())
            if s is None:
                missing.append(n)
            else:
                order.append((int(s), n))
    if missing:
        raise SystemExit(
            "ELS workbook no longer contains %d configured indicator(s):\n  "
            % len(missing)
            + "\n  ".join(missing)
            + "\nONS may have renamed or withdrawn them. Update DOMAINS/POL in "
              "parse_all.py deliberately - do not let the build drop them silently."
        )
    # The other half of the guard: an ELS sheet that carries Gateshead data but
    # is not configured is a silent omission, and the product claims to cover
    # every ELS indicator for the borough. Nation-specific sheets with no
    # Gateshead row are ignored - they are excluded correctly and by design.
    configured = {n.strip().lower() for _, names in DOMAINS for n in names}
    extra = []
    for title, s in idx.items():
        if title in configured or title in SKIP_SHEETS:
            continue
        if has_gateshead(wb[s]):
            extra.append("%s (sheet %s)" % (title, s))
    if extra:
        print(
            "WARNING: %d ELS sheet(s) carry Gateshead data but are not "
            "configured in DOMAINS, so they are being excluded:\n  " % len(extra)
            + "\n  ".join(sorted(extra))
            + "\nAdd to DOMAINS/POL deliberately, or to SKIP_SHEETS to record "
              "that the exclusion is intended."
        )
    return order


def has_gateshead(ws):
    # No row cap: the population-by-age-and-sex sheet is ~22,000 rows and
    # Gateshead first appears at ~14,150, so an early cut-off reports that
    # sheet as having no Gateshead data and understates the coverage count.
    for r in ws.iter_rows(values_only=True):
        if r and r[0] is not None and str(r[0]).strip() == GH:
            return True
    return False

MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def plabel(h):
    """Column header -> short period label."""
    s = str(h)
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:/P(\d+)([YMWD]))?", s)
    if not m:
        return s[:12]
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    n = int(m.group(4)) if m.group(4) else None
    u = m.group(5)
    if u == "Y":
        if n == 1:
            return f"{y}" if mo == 1 else f"{y}/{str(y+1)[2:]}"
        end = y + n - 1 if mo == 1 else y + n
        return f"{y}–{str(end)[2:]}"
    if u == "M":
        return f"{MON[mo-1]} {y}"
    if (mo, d) == (1, 1):
        return f"{y}"
    if mo == 6 and d == 30:
        return f"mid-{y}"
    return f"{MON[mo-1]} {y}"

def num(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s or s.startswith("["):
        return None
    try:
        return float(s)
    except ValueError:
        return None

def sig(v):
    if v is None:
        return None
    a = abs(v)
    if a >= 1000: return round(v)
    if a >= 100:  return round(v, 1)
    return round(v, 2)

def parse(workbook_path):
    wb = openpyxl.load_workbook(workbook_path, read_only=True)
    cover = [str(r[0]) for r in wb["Cover_sheet"].iter_rows(values_only=True) if r[0]]
    gen = next((l for l in cover if "generated" in l), "")
    gd = re.search(r"(\d{2})/(\d{2})/(\d{4})", gen)
    els_generated = f"{gd.group(3)}-{gd.group(2)}-{gd.group(1)}" if gd else ""

    names = {}
    ind = {}

    for t, cfg_name in resolve(wb):
        ws = wb[str(t)]
        rows = ws.iter_rows(values_only=True)
        title = unit = src = ""
        hdr = None
        for r in rows:
            c0 = str(r[0]).strip() if r[0] is not None else ""
            if c0.lower() == "area code":
                hdr = r
                break
            if not c0:
                continue
            low = c0.lower()
            if low.startswith("source"):
                # Some sheets publish several source lines (e.g. "Source 1: ONS",
                # "Source 2: NISRA"). Source 1 is the England/GB producer we use;
                # keeping the last one mis-attributed median pay to NISRA.
                if not src:
                    src = re.sub(r"^Source\s*\d*\s*:\s*", "", c0)
            elif low.startswith(("this worksheet", "some shorthand")):
                pass
            elif not title:
                title = re.sub(r"\s*\[note \d+\]\s*", "", c0).strip()
            elif not unit:
                unit = c0
        cols = [str(c) if c is not None else "" for c in hdr]
        has_measure = len(cols) > 2 and cols[2].strip().lower() == "measure"
        v0 = 3 if has_measure else 2
        ncols = len([c for c in cols if c])
        heads = cols[v0:ncols]
        labels = [plabel(h) for h in heads]

        um = re.search(r"\(([^)]*)\)\s*$", heads[0]) if heads else None
        unit_short = um.group(1) if um else ""
        if title == RATIO_UNIT_INDICATOR:
            unit_short = "ratio"   # ONS header says (%) but the measure is a ratio

        data = {}
        ci = {}
        for r in rows:
            code = str(r[0]) if r[0] is not None else ""
            if not code or code.lower() == "area code":
                continue
            vals = [num(v) for v in r[v0:ncols]]
            if has_measure:
                meas = str(r[2]).lower()
                if "lower conf" in meas or "upper conf" in meas:
                    if code == GH:
                        ci.setdefault(code, {})["lo" if "lower" in meas else "hi"] = vals
                    continue
            if code not in data:
                data[code] = vals
                if r[1] is not None:
                    names.setdefault(code, str(r[1]))

        if GH not in data or all(v is None for v in data[GH]):
            continue

        li = max(i for i, v in enumerate(data[GH]) if v is not None)
        bench_code = next((b for b in BENCH_PREF if b in data and data[b][li] is not None), None)
        lad_latest = {c: v[li] for c, v in data.items() if LAD_RE.match(c) and v[li] is not None}
        n = len(lad_latest)
        ghv = data[GH][li]
        rank_high = 1 + sum(1 for v in lad_latest.values() if v > ghv)

        nations = {c[0] for c in lad_latest}
        cov = ("UK" if nations >= {"E","W","S","N"} else
               "Great Britain" if nations >= {"E","W","S"} else
               "England & Wales" if nations >= {"E","W"} else
               "England" if nations == {"E"} else "+".join(sorted(nations)))

        keep = list(range(len(labels)))
        if len(labels) > 60:   # monthly series -> annual + latest
            keep = list(range(len(labels) - 1, -1, -12))[::-1]
        def pick(seq):
            return [sig(seq[i]) for i in keep] if seq else None

        gh_ci = None
        if GH in ci and "lo" in ci[GH] and "hi" in ci[GH]:
            lo, hi = ci[GH]["lo"][li], ci[GH]["hi"][li]
            if lo is not None and hi is not None:
                gh_ci = [sig(lo), sig(hi)]

        ind[t] = {
            "name": title, "unit": unit, "unitShort": unit_short,
            "src": src.replace("Source: ", ""), "pol": POL[cfg_name],
            "labels": [labels[i] for i in keep],
            "latest": labels[li],
            "gh": pick(data[GH]),
            "bench": pick(data[bench_code]) if bench_code else None,
            "benchCode": BENCH_NAME.get(bench_code),
            "ne": pick(data[NE]) if NE in data else None,
            "ghCI": gh_ci, "surveyCI": has_measure,
            "neca": {c: sig(data[c][li]) if c in data else None for c in NECA},
            "neigh": {c: sig(data[c][li]) if c in data else None for c in NEIGH},
            "ladSorted": sorted((sig(v) for v in lad_latest.values()), reverse=True),
            "n": n, "rankHigh": rank_high, "cov": cov,
        }

    byname = {v["name"]: k for k, v in ind.items()}

    numbered = [s for s in wb.sheetnames if s.isdigit()]
    gh_sheets = sum(1 for s in numbered if has_gateshead(wb[s]))

    return {
        "elsGenerated": els_generated,
        "sheetCount": len(numbered),
        "ghSheetCount": gh_sheets,
        "gh": GH,
        "neca": NECA, "neigh": NEIGH,
        "names": {c: names.get(c, c) for c in sorted(set(NECA) | set(NEIGH))},
        "domains": [{"name": d, "tables": [byname[n] for n in ts if n in byname]} for d, ts in DOMAINS],
        "ind": ind,
    }

if __name__ == "__main__":
    import sys
    wbpath = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "data" / "all-datasets.xlsx"
    out = parse(wbpath)
    dest = BASE / "data" / "scorecard_data.json"
    dest.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"Indicators: {len(out['ind'])} -> {dest}")
