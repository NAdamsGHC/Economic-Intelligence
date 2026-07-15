"""
Gateshead Business Map — data pipeline.

Fetches every (keyless) source, filters to Gateshead borough, enriches, scores,
and writes a single JSON blob to .cache/dashboard_data.json which render.py turns
into the self-contained dashboard HTML.

Design notes:
* All sources are public + keyless (no secrets).
* "Only geographically in Gateshead" is enforced by postcodes.io
  admin_district == E08000037 (point-in-borough), not by trusting the postcode.
* Graceful degradation: a failed enrichment source is logged to data["meta"]
  ["warnings"] and its score signal is dropped + re-normalised, never faked.
"""
from __future__ import annotations
import csv, io, json, re, sys, time, zipfile, hashlib, datetime as dt
from pathlib import Path
from collections import defaultdict, Counter
import requests
import config as C
import centres as CN
import highstreets as HS

csv.field_size_limit(1 << 24)
S = requests.Session(); S.headers.update(C.HTTP_HEADERS)
WARN: list[str] = []
def log(*a): print(*a, flush=True)
def warn(msg): WARN.append(msg); log("  ! WARN:", msg)


def http_json(url, *, method="GET", retries=3, **kw):
    kw.setdefault("timeout", C.HTTP_TIMEOUT)
    for i in range(retries):
        try:
            r = S.request(method, url, **kw)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


# --------------------------------------------------------------------------- #
# 1. Companies House bulk -> candidate Gateshead companies
# --------------------------------------------------------------------------- #
def load_companies():
    log("\n[1] Companies House bulk")
    zpath = None
    for d in C.companies_house_candidate_dates():
        p = C.CACHE_DIR / f"ch-{d}.zip"
        if p.exists():
            zpath = p; snapshot = d; break
    if not zpath:
        log("    no cached CH zip; run fetch_ch.py first"); sys.exit(2)
    log(f"    using {zpath.name}")

    companies, postcodes = [], set()
    prefixes = C.GATESHEAD_OUTCODE_PREFIXES
    with zipfile.ZipFile(zpath) as z:
        name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(name) as fh:
            reader = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"))
            field = {k.strip(): k for k in reader.fieldnames}  # CH headers have stray spaces
            def g(row, key, default=""):
                return (row.get(field.get(key, key)) or default).strip()
            n_seen = 0
            for row in reader:
                n_seen += 1
                pc = g(row, "RegAddress.PostCode").upper().replace("  ", " ")
                if not pc:
                    continue
                outcode = pc.split(" ")[0]
                if outcode not in prefixes:
                    continue
                sic1 = g(row, "SICCode.SicText_1")
                companies.append({
                    "num": g(row, "CompanyNumber"),
                    "name": g(row, "CompanyName"),
                    "pc": pc,
                    "addr1": g(row, "RegAddress.AddressLine1"),
                    "status": g(row, "CompanyStatus"),
                    "cat": g(row, "CompanyCategory"),
                    "inc": g(row, "IncorporationDate"),
                    "sic_raw": sic1,
                })
                postcodes.add(pc)
            log(f"    scanned {n_seen:,} companies; {len(companies):,} in candidate outcodes; "
                f"{len(postcodes):,} unique postcodes")
    return companies, postcodes, snapshot


# --------------------------------------------------------------------------- #
# 2. Geocode via postcodes.io (bulk) -> keep only E08000037
# --------------------------------------------------------------------------- #
def geocode(postcodes):
    log("\n[2] Geocoding via postcodes.io")
    out, pcs = {}, sorted(postcodes)
    for i in range(0, len(pcs), 100):
        batch = pcs[i:i + 100]
        js = http_json(C.POSTCODES_IO_BULK, method="POST", json={"postcodes": batch})
        for item in js["result"]:
            res = item.get("result")
            if not res:
                continue
            codes = res.get("codes", {})
            if codes.get("admin_district") != C.LAD_CODE:
                continue
            out[item["query"].upper()] = {
                "lat": res["latitude"], "lon": res["longitude"],
                "lsoa": codes.get("lsoa"),
                "ward": codes.get("admin_ward"), "ward_nm": res.get("admin_ward"),
            }
        if (i // 100) % 5 == 0:
            log(f"    {min(i+100,len(pcs))}/{len(pcs)} postcodes")
    log(f"    {len(out):,} postcodes confirmed inside Gateshead (E08000037)")
    return out


def _jitter(num, lat, lon):
    # spread firms sharing a postcode centroid within a ~50 m radius so individual
    # dots separate at street zoom, without overspilling into neighbouring streets.
    h = int(hashlib.md5(num.encode()).hexdigest(), 16)
    return (round(lat + ((h % 1000) / 1000 - 0.5) * 0.0009, 5),
            round(lon + (((h // 1000) % 1000) / 1000 - 0.5) * 0.0015, 5))


def build_company_points(companies, geo):
    log("\n[3] Building company points")
    # accountant / formation-agent cluster detection
    by_addr = Counter((c["addr1"].upper(), c["pc"]) for c in companies if c["addr1"])
    cluster_addrs = {a for a, n in by_addr.items() if n >= 15}
    pts, dropped = [], 0
    this_year = dt.date.today().year
    for c in companies:
        g = geo.get(c["pc"].upper())
        if not g or not g["lsoa"]:
            dropped += 1; continue
        sec = C.sic_section(c["sic_raw"])
        inc_year = inc_ym = None
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", c["inc"]) or re.match(r"(\d{4})-(\d{2})-(\d{2})", c["inc"])
        if m:
            if "/" in c["inc"]:
                inc_year, inc_ym = int(m.group(3)), f"{m.group(3)}-{m.group(2)}"
            else:
                inc_year, inc_ym = int(m.group(1)), f"{m.group(1)}-{m.group(2)}"
        lat, lon = _jitter(c["num"], g["lat"], g["lon"])
        status_l = c["status"].lower()
        distress = any(k in status_l for k in ("liquidation", "administration", "receiver", "voluntary arrangement"))
        pts.append({
            "n": c["name"][:80], "num": c["num"], "sec": sec,
            "sic": re.match(r"\d+", c["sic_raw"]).group(0) if re.match(r"\d+", c["sic_raw"]) else "",
            "desc": re.sub(r"^\d+\s*-\s*", "", c["sic_raw"])[:60],
            "st": c["status"], "ds": 1 if distress else 0,
            "iy": inc_year, "im": inc_ym, "lat": lat, "lon": lon,
            "lsoa": g["lsoa"], "wd": g["ward"],
            "cl": 1 if (c["addr1"].upper(), c["pc"]) in cluster_addrs else 0,
        })
    log(f"    {len(pts):,} Gateshead company points ({dropped:,} dropped: outside borough / ungeocodable); "
        f"{len(cluster_addrs)} mass-registration addresses flagged")
    return pts


# --------------------------------------------------------------------------- #
# 4. FSA food premises (real trading locations)
# --------------------------------------------------------------------------- #
def load_fsa(geo):
    log("\n[4] FSA food premises")
    h = {"x-api-version": "2", "Accept": "application/json"}
    # find Gateshead authority id
    auths = http_json(f"{C.FSA_BASE}/Authorities/basic", headers=h)["authorities"]
    laid = next((a["LocalAuthorityId"] for a in auths if a.get("Name", "").lower() == "gateshead"), None)
    if laid is None:
        warn("FSA: Gateshead authority not found"); return []
    pts, page = [], 1
    need_geo = set()
    raw = []
    while True:
        js = http_json(f"{C.FSA_BASE}/Establishments", headers=h,
                       params={"localAuthorityId": laid, "pageSize": 1000, "pageNumber": page})
        ests = js.get("establishments", [])
        if not ests:
            break
        raw.extend(ests); page += 1
        if page > 10:
            break
    for e in raw:
        gc = e.get("geocode") or {}
        lat = gc.get("latitude"); lon = gc.get("longitude")
        pc = (e.get("PostCode") or "").upper()
        lsoa = wd = None
        if pc in geo:
            lsoa, wd = geo[pc]["lsoa"], geo[pc]["ward"]
        if lat in (None, "") or lon in (None, ""):
            if pc in geo:
                lat, lon = geo[pc]["lat"], geo[pc]["lon"]
            else:
                need_geo.add(pc); continue
        try:
            lat = float(lat); lon = float(lon)
        except (TypeError, ValueError):
            continue
        pts.append({
            "n": (e.get("BusinessName") or "")[:80], "ty": e.get("BusinessType") or "",
            "rt": str(e.get("RatingValue") or ""), "lat": round(lat, 5), "lon": round(lon, 5),
            "lsoa": lsoa, "wd": wd,
        })
    log(f"    {len(pts):,} FSA premises (authority id {laid})")
    return pts


# --------------------------------------------------------------------------- #
# 5. IMD 2025 (File 7 CSV) + population denominators
# --------------------------------------------------------------------------- #
def load_imd(gateshead_lsoas):
    log("\n[5] IMD 2025")
    page = S.get(C.IMD2025_COLLECTION, timeout=C.HTTP_TIMEOUT).text
    m = re.search(r'https://assets\.publishing\.service\.gov\.uk/[^\s"\'<>]*File_7[^\s"\'<>]*\.csv', page)
    if not m:
        warn("IMD: File 7 CSV link not found on collection page"); return {}
    url = m.group(0)
    log(f"    {url.rsplit('/',1)[-1]}")
    txt = S.get(url, timeout=C.HTTP_TIMEOUT).text
    reader = csv.DictReader(io.StringIO(txt))
    cols = reader.fieldnames

    def findcol(*needles):
        for c in cols:
            cl = c.lower()
            if all(n in cl for n in needles):
                return c
        return None
    col_lsoa = findcol("lsoa", "code")
    col_rank = findcol("index of multiple deprivation", "rank")
    col_dec = findcol("index of multiple deprivation", "decile")
    col_score = findcol("index of multiple deprivation", "score")
    col_pop = findcol("total population")
    domain_cols = {
        "income": findcol("income", "score"), "employment": findcol("employment", "score"),
        "education": findcol("education", "score"), "health": findcol("health", "score"),
        "crime": findcol("crime", "score"),
        "barriers": findcol("barriers", "score"), "living": findcol("living", "score"),
    }
    out = {}
    gs = set(gateshead_lsoas)
    for row in reader:
        code = (row.get(col_lsoa) or "").strip()
        if code not in gs:
            continue
        def num(c):
            try:
                return float((row.get(c) or "").replace(",", ""))
            except (ValueError, TypeError, AttributeError):
                return None
        out[code] = {
            "rank": num(col_rank), "decile": num(col_dec), "score": num(col_score),
            "pop": num(col_pop),
            "domains": {k: num(v) for k, v in domain_cols.items() if v},
        }
    log(f"    {len(out):,} Gateshead LSOAs matched to IMD2025")
    return out


# --------------------------------------------------------------------------- #
# 6. Boundaries from ONS Open Geography Portal
# --------------------------------------------------------------------------- #
def _arcgis_query(service, *, where="1=1", out_fields="*", geojson=False, layer=0):
    url = f"{C.OGP_ARCGIS_ORG}/{service}/FeatureServer/{layer}/query"
    params = {"where": where, "outFields": out_fields,
              "f": "geojson" if geojson else "json", "returnGeometry": "true" if geojson else "false"}
    if not geojson:
        params["returnGeometry"] = "false"
    r = S.post(url, data=params, timeout=120)
    r.raise_for_status()
    return r.json()


def load_boundaries():
    log("\n[6] ONS Open Geography Portal boundaries")
    lu = _arcgis_query(C.OGP_LSOA_WD_LAD_LU, where=f"LAD24CD='{C.LAD_CODE}'",
                       out_fields="LSOA21CD,LSOA21NM,WD24CD,WD24NM")
    feats = lu.get("features", [])
    lsoa_ward, ward_nm = {}, {}
    for f in feats:
        a = f["attributes"]
        lsoa_ward[a["LSOA21CD"]] = a["WD24CD"]
        ward_nm[a["WD24CD"]] = a["WD24NM"]
    lsoas = sorted(lsoa_ward)
    wards = sorted(ward_nm)
    log(f"    lookup: {len(lsoas)} Gateshead LSOAs across {len(wards)} wards")

    def fetch_geo(service, codes, field):
        feats_out = []
        for i in range(0, len(codes), 60):
            chunk = codes[i:i + 60]
            clause = field + " IN (" + ",".join(f"'{c}'" for c in chunk) + ")"
            gj = _arcgis_query(service, where=clause, out_fields=field, geojson=True)
            feats_out.extend(gj.get("features", []))
        return feats_out

    lsoa_feats = fetch_geo(C.OGP_LSOA21_BSC, lsoas, "LSOA21CD")
    ward_gj = _arcgis_query(C.OGP_WARD24, where=f"LAD24CD='{C.LAD_CODE}'",
                            out_fields="WD24CD,WD24NM", geojson=True)
    ward_feats = ward_gj.get("features", [])
    log(f"    geometry: {len(lsoa_feats)} LSOA polygons, {len(ward_feats)} ward polygons")
    return lsoa_ward, ward_nm, lsoa_feats, ward_feats


# --------------------------------------------------------------------------- #
# 7. Innovation (UKRI Gateway to Research) — best effort, borough level
# --------------------------------------------------------------------------- #
def load_innovation():
    log("\n[7] UKRI Gateway to Research (innovation)")
    h = {"Accept": "application/json"}   # vendor types 406; plain json + page size >=10 works
    try:
        items, total = [], None
        for page in (1, 2, 3):
            js = http_json(f"{C.GTR_BASE}/projects", headers=h,
                           params={"q": "Gateshead", "s": 20, "p": page}, retries=2)
            total = js.get("totalSize")
            for pr in js.get("project", []):
                lf = pr.get("leadFunder")
                funder = lf.get("name") if isinstance(lf, dict) else (lf or "")
                items.append({
                    "title": (pr.get("title") or "")[:140],
                    "funder": str(funder)[:40],
                    "status": pr.get("status") or "",
                    "cat": pr.get("grantCategory") or "",
                    "start": (pr.get("start") or "")[:10],
                })
            if page >= (js.get("totalPages") or 1):
                break
        log(f"    {len(items)} GtR projects (of {total}) matching 'Gateshead'")
        return {"available": True, "total": total, "projects": items}
    except Exception as e:
        warn(f"GtR innovation unavailable: {type(e).__name__}")
        return {"available": False, "total": 0, "projects": []}


# --------------------------------------------------------------------------- #
# 8. Employment headline (Nomis BRES) — best effort
# --------------------------------------------------------------------------- #
def load_employment():
    log("\n[8] Nomis employment (best effort)")
    # BRES employment, Gateshead LAD. Try GSS code directly.
    for geo_param in (C.LAD_CODE, "1811939341"):
        try:
            url = f"{C.NOMIS_BASE}/NM_189_1.data.json"
            js = http_json(url, params={"geography": geo_param, "employment_status": "4",
                                        "measure": "1", "measures": "20100", "industry": "37748736"}, retries=1)
            obs = js.get("obs", [])
            if obs:
                val = obs[0]["obs_value"]["value"]
                log(f"    BRES employees (geo {geo_param}): {val}")
                return {"available": True, "employees": val}
        except Exception:
            continue
    warn("Nomis employment unavailable")
    return {"available": False, "employees": None}


# --------------------------------------------------------------------------- #
# 9. Scoring
# --------------------------------------------------------------------------- #
def _norm(d):
    vals = [v for v in d.values() if v is not None]
    if not vals:
        return {k: None for k in d}
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return {k: (0.0 if v is None else 0.5) for k, v in d.items()}
    return {k: (None if v is None else (v - lo) / (hi - lo)) for k, v in d.items()}


def compute_scores(company_pts, fsa_pts, imd, lsoa_ward, innovation):
    log("\n[9] Scoring")
    lsoas = sorted(set(lsoa_ward) | set(imd))
    this_year = dt.date.today().year
    comp_by_lsoa = defaultdict(list)
    for c in company_pts:
        comp_by_lsoa[c["lsoa"]].append(c)
    fsa_by_lsoa = Counter(p["lsoa"] for p in fsa_pts if p["lsoa"])

    raw = {}  # lsoa -> signal dict
    for ls in lsoas:
        cs = comp_by_lsoa.get(ls, [])
        n = len(cs)
        pop = (imd.get(ls) or {}).get("pop") or 0
        distress = sum(c["ds"] for c in cs)
        recent = sum(1 for c in cs if c["iy"] and c["iy"] >= this_year - 2)
        death = [C.SECTION_CHURN.get(c["sec"], (C.UK_OVERALL["birth_rate"], C.UK_OVERALL["death_rate"]))[1] for c in cs]
        birth = [C.SECTION_CHURN.get(c["sec"], (C.UK_OVERALL["birth_rate"], C.UK_OVERALL["death_rate"]))[0] for c in cs]
        consumer = sum(1 for c in cs if c["sec"] in C.CONSUMER_SIC_SECTIONS) + fsa_by_lsoa.get(ls, 0)
        raw[ls] = {
            "n": n, "pop": pop, "distress": distress, "recent": recent,
            "death_avg": (sum(death) / len(death)) if death else None,
            "birth_avg": (sum(birth) / len(birth)) if birth else None,
            "consumer": consumer,
            "imd_score": (imd.get(ls) or {}).get("score"),
            "density": (n / pop * 1000) if pop else None,
            "distress_share": (distress / n) if n else None,
            "recent_share": (recent / n) if n else None,
            "demand": (pop / (consumer + 1)) if pop else None,
        }

    deprivation = _norm({ls: raw[ls]["imd_score"] for ls in lsoas})
    live_distress = _norm({ls: raw[ls]["distress_share"] for ls in lsoas})
    fragility = _norm({ls: raw[ls]["death_avg"] for ls in lsoas})
    growth = _norm({ls: raw[ls]["birth_avg"] for ls in lsoas})
    dynamism = _norm({ls: raw[ls]["recent_share"] for ls in lsoas})
    agglomeration = _norm({ls: raw[ls]["density"] for ls in lsoas})
    demand = _norm({ls: raw[ls]["demand"] for ls in lsoas})

    iv_w = dict(C.SCORE_WEIGHTS["intervention"])   # vacancy + (innovation absent) handled below
    inv_w = dict(C.SCORE_WEIGHTS["investment"])
    if not innovation.get("available"):
        inv_w.pop("innovation", None)
        warn("investment score: innovation signal omitted (per-LSOA GtR not wired) and weights renormalised")
    iv_w.pop("vacancy", None)  # NNDR vacancy not available
    warn("intervention score: vacancy signal omitted (council NNDR open data not wired) and weights renormalised")

    def weighted(signals_weights, ls):
        tot, acc = 0.0, 0.0
        for key, (sig, w) in signals_weights.items():
            v = sig.get(ls)
            if v is None:
                continue
            acc += v * w; tot += w
        return (acc / tot * 100) if tot else None

    iv_sig = {"deprivation": (deprivation, iv_w.get("deprivation", 0)),
              "live_distress": (live_distress, iv_w.get("live_distress", 0)),
              "sector_fragility": (fragility, iv_w.get("sector_fragility", 0))}
    inv_sig = {"growth_sectors": (growth, inv_w.get("growth_sectors", 0)),
               "dynamism": (dynamism, inv_w.get("dynamism", 0)),
               "agglomeration": (agglomeration, inv_w.get("agglomeration", 0)),
               "underserved_demand": (demand, inv_w.get("underserved_demand", 0))}

    per_lsoa = {}
    for ls in lsoas:
        per_lsoa[ls] = {
            "intervention": weighted(iv_sig, ls),
            "investment": weighted(inv_sig, ls),
            "ward": lsoa_ward.get(ls),
            "n": raw[ls]["n"], "pop": raw[ls]["pop"],
            "distress": raw[ls]["distress"], "recent": raw[ls]["recent"],
            "imd_decile": (imd.get(ls) or {}).get("decile"),
            "imd_score": raw[ls]["imd_score"],
            "density": round(raw[ls]["density"], 2) if raw[ls]["density"] else None,
            "signals": {
                "deprivation": _r(deprivation.get(ls)), "live_distress": _r(live_distress.get(ls)),
                "sector_fragility": _r(fragility.get(ls)), "growth_sectors": _r(growth.get(ls)),
                "dynamism": _r(dynamism.get(ls)), "agglomeration": _r(agglomeration.get(ls)),
                "underserved_demand": _r(demand.get(ls)),
            },
        }

    # ward rollup (population-weighted)
    ward_acc = defaultdict(lambda: {"iv": 0.0, "inv": 0.0, "w": 0.0, "n": 0, "pop": 0, "distress": 0})
    for ls, d in per_lsoa.items():
        wd = d["ward"]
        if not wd:
            continue
        w = d["pop"] or 1
        if d["intervention"] is not None:
            ward_acc[wd]["iv"] += d["intervention"] * w
        if d["investment"] is not None:
            ward_acc[wd]["inv"] += d["investment"] * w
        ward_acc[wd]["w"] += w
        ward_acc[wd]["n"] += d["n"]; ward_acc[wd]["pop"] += d["pop"]; ward_acc[wd]["distress"] += d["distress"]
    per_ward = {}
    for wd, a in ward_acc.items():
        per_ward[wd] = {"intervention": _r(a["iv"] / a["w"]) if a["w"] else None,
                        "investment": _r(a["inv"] / a["w"]) if a["w"] else None,
                        "n": a["n"], "pop": a["pop"], "distress": a["distress"]}
    return per_lsoa, per_ward, iv_w, inv_w


def _r(v, nd=1):
    return None if v is None else round(v, nd)


# --------------------------------------------------------------------------- #
# 10. Sector saturation + borough headline
# --------------------------------------------------------------------------- #
def sector_summary(company_pts, total_pop):
    sec_counts = Counter(c["sec"] for c in company_pts)
    rows = []
    for sec, cnt in sec_counts.most_common():
        birth, death = C.SECTION_CHURN.get(sec, (C.UK_OVERALL["birth_rate"], C.UK_OVERALL["death_rate"]))
        rows.append({
            "sec": sec, "label": C.SECTION_LABELS.get(sec, sec), "count": cnt,
            "per_1k": round(cnt / total_pop * 1000, 2) if total_pop else None,
            "birth": birth, "death": death,
        })
    return rows


def main():
    t0 = time.time()
    companies, postcodes, snapshot = load_companies()
    geo = geocode(postcodes)
    company_pts = build_company_points(companies, geo)

    fsa_pts = load_fsa(geo)
    lsoa_ward, ward_nm, lsoa_feats, ward_feats = load_boundaries()
    imd = load_imd(set(lsoa_ward) | {c["lsoa"] for c in company_pts})
    innovation = load_innovation()
    employment = load_employment()

    per_lsoa, per_ward, iv_w, inv_w = compute_scores(company_pts, fsa_pts, imd, lsoa_ward, innovation)
    total_pop = sum((imd.get(ls) or {}).get("pop") or 0 for ls in (set(lsoa_ward) | set(imd)))
    sectors = sector_summary(company_pts, total_pop)

    # ---- high streets (Local Plan centres) ----
    log("\n[10] High streets (Local Plan centres)")
    centres = CN.load_centres(S)
    cidx = CN.CentreIndex(centres)
    n_ct = 0
    for c in company_pts:
        c["ct"] = cidx.assign(c["lat"], c["lon"])
        n_ct += 1 if c["ct"] else 0
    n_ct_f = 0
    for p in fsa_pts:
        p["ct"] = cidx.assign(p["lat"], p["lon"])
        n_ct_f += 1 if p["ct"] else 0
    log(f"    {len(centres)} centres; {n_ct:,} companies + {n_ct_f:,} FSA premises inside a centre (+{CN.BUFFER_M:.0f}m)")
    n_chain, n_multi = HS.flag_chains(fsa_pts)
    log(f"    chain heuristic: {n_chain} of {len(fsa_pts)} premises flagged ({n_multi} multi-site names)")
    events, reg_meta = HS.update_register(company_pts, snapshot, warn)
    now = dt.date.today()
    hs_rows, avg_share = HS.centre_rollups(centres, company_pts, fsa_pts, imd, lsoa_feats, events, now, warn)
    # official employment/age context (publish-safe subset exported by the
    # retail-centres analysis; disclosure rules applied at export)
    ctx_path = Path(__file__).resolve().parent / "data" / "centre_context.json"
    centre_ctx = {"meta": None, "centres": {}}
    if ctx_path.exists():
        centre_ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
        for r in hs_rows:
            r["ctx"] = centre_ctx["centres"].get(r["name"])
        log(f"    official context attached for {sum(1 for r in hs_rows if r.get('ctx'))} centres")
    else:
        warn("centre_context.json missing — high-street official context omitted")
    borough_trend = HS.startup_series(company_pts, now, 12)
    footfall = HS.load_footfall(S, warn)
    for d in per_lsoa.values():
        d["s12"] = 0
    for c in company_pts:
        if c.get("im") and HS._months_ago(c["im"], now) < 12 and c["lsoa"] in per_lsoa:
            per_lsoa[c["lsoa"]]["s12"] += 1

    active = sum(1 for c in company_pts if "active" in c["st"].lower())
    distress_total = sum(c["ds"] for c in company_pts)
    data = {
        "meta": {
            "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "ch_snapshot": snapshot, "lad": C.LAD_CODE, "lad_name": C.LAD_NAME,
            "imd_vintage": "IoD2025 (LSOA 2021)", "ward_vintage": "December 2024",
            "weights": {"intervention": iv_w, "investment": inv_w},
            "warnings": WARN,
        },
        "headline": {
            "companies": len(company_pts), "active": active, "distress": distress_total,
            "fsa": len(fsa_pts), "lsoas": len(lsoa_ward), "wards": len(ward_nm),
            "population": total_pop, "employees": employment.get("employees"),
            "uk": C.UK_OVERALL,
        },
        "companies": company_pts,
        "fsa": fsa_pts,
        "lsoa_scores": per_lsoa,
        "ward_scores": per_ward,
        "ward_names": ward_nm,
        "sectors": sectors,
        "innovation": innovation,
        "highstreets": {
            "centres": hs_rows, "avg_share": avg_share,
            "trend": borough_trend, "footfall": footfall,
            "events": events[-400:],
            "register": {"snapshots": reg_meta["snapshots"], "seeded": reg_meta["seeded"]},
            "buffer_m": CN.BUFFER_M, "catchment_m": HS.CATCHMENT_M,
            "tier_labels": CN.TIER_LABEL,
            "context_meta": centre_ctx.get("meta"),
        },
        "boundaries": {"lsoa": {"type": "FeatureCollection", "features": lsoa_feats},
                       "ward": {"type": "FeatureCollection", "features": ward_feats},
                       "centres": CN.centres_geojson(centres)},
        "section_labels": C.SECTION_LABELS,
    }
    outp = C.CACHE_DIR / "dashboard_data.json"
    outp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    log(f"\n[done] {outp} ({outp.stat().st_size/1e6:,.1f} MB) in {time.time()-t0:,.0f}s; warnings={len(WARN)}")


if __name__ == "__main__":
    main()
