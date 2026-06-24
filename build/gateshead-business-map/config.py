"""
Configuration for the Gateshead Business Map build pipeline.

Everything here is free + public and needs NO API key. The only secret-bearing
source (the Companies House *API*) is deliberately avoided in favour of the
keyless Companies House *Free Company Data Product* bulk download.

Edit the SCORE_WEIGHTS to re-tune the intervention / investment indices, or the
boundary vintages to refresh geography from the ONS Open Geography Portal.
"""
from __future__ import annotations
import datetime as _dt
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
BUILD_DIR = Path(__file__).resolve().parent
REPO_ROOT = BUILD_DIR.parent.parent                      # Economic-Intelligence/
CACHE_DIR = BUILD_DIR / ".cache"                         # gitignored
OUTPUT_HTML = REPO_ROOT / "business-industry-trade" / "gateshead-business-map.html"
CACHE_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------- #
# Study area — Gateshead Metropolitan Borough
# --------------------------------------------------------------------------- #
LAD_CODE = "E08000037"
LAD_NAME = "Gateshead"

# Generous postcode pre-filter for the Companies House bulk file. This only
# narrows the set we bother to geocode; the *authoritative* in-borough test is
# postcodes.io admin_district == LAD_CODE. NB Birtley (in Gateshead borough)
# uses DH3 Durham postcodes, so DH3 must be included.
GATESHEAD_OUTCODE_PREFIXES = {
    "NE8", "NE9", "NE10", "NE11", "NE16", "NE17", "NE21", "NE39", "NE40", "DH3",
}

# --------------------------------------------------------------------------- #
# Data vintages
# --------------------------------------------------------------------------- #
# Companies House Free Company Data Product is published within 5 working days
# of month-end, dated YYYY-MM-01. We try the current month then walk back.
def companies_house_candidate_dates(today: _dt.date | None = None) -> list[str]:
    today = today or _dt.date.today()
    first = today.replace(day=1)
    out = []
    for back in range(0, 4):                              # this month .. 3 back
        y, m = first.year, first.month - back
        while m <= 0:
            m += 12
            y -= 1
        out.append(f"{y:04d}-{m:02d}-01")
    return out

CH_ONEFILE_URL = "https://download.companieshouse.gov.uk/BasicCompanyDataAsOneFile-{date}.zip"

# ONS Open Geography Portal (ArcGIS org id for ONS). Service names carry a
# version suffix; these were resolved from the services directory (see probe2.py)
# and can be re-pointed to bump the geography vintage.
OGP_ARCGIS_ORG = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services"
LSOA_VINTAGE = "2021"        # LSOA boundary vintage
WARD_VINTAGE = "2024"        # electoral ward vintage (LSOA21 -> WD24 -> LAD24)
OGP_LSOA21_BSC = "Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4"
OGP_WARD24 = "Wards_December_2024_Boundaries_UK_BGC"  # BSC variant is empty; BGC is populated
OGP_LSOA_WD_LAD_LU = "LSOA21_WD24_LAD24_EW_LU"   # LSOA21 -> Ward2024 -> LAD2024 best-fit lookup

# Other keyless sources
POSTCODES_IO_BULK = "https://api.postcodes.io/postcodes"          # POST, <=100/req
FSA_BASE = "https://api.ratings.food.gov.uk"                      # header x-api-version: 2
GTR_BASE = "https://gtr.ukri.org/gtr/api"                         # Gateway to Research
NOMIS_BASE = "https://www.nomisweb.co.uk/api/v01/dataset"         # UK Business Counts / BRES

# IMD 2025 (IoD2025) — MHCLG file 1 (IMD rank + decile) at LSOA 2021. Resolved
# at runtime from the GOV.UK collection page; this is the expected asset name.
IMD2025_COLLECTION = "https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025"

# ONS Business Demography 2024 — births / deaths / 5yr survival by LA x SIC.
BUSINESS_DEMOGRAPHY_PAGE = (
    "https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation/"
    "bulletins/businessdemography/2024"
)

# --------------------------------------------------------------------------- #
# Scoring weights — normalised 0..1 inputs, weights need not sum to 1 (the
# composite is re-normalised). Tune freely; the dashboard shows these.
# --------------------------------------------------------------------------- #
SCORE_WEIGHTS = {
    "intervention": {
        "deprivation": 0.40,        # IMD2025 (higher = more deprived)
        "live_distress": 0.20,      # share of local live cos in liquidation/administration
        "sector_fragility": 0.25,   # local mix weighted by low survival + high death rate
        "vacancy": 0.15,            # empty-premises rate (0 + flagged if NNDR unavailable)
    },
    "investment": {
        "growth_sectors": 0.30,     # local mix weighted by high birth rate / survival
        "innovation": 0.25,         # UKRI / Innovate UK grant density
        "dynamism": 0.20,           # recent incorporations + churn
        "agglomeration": 0.15,      # density of related-SIC firms
        "underserved_demand": 0.10, # residents-per-premises gap (consumer sectors)
    },
}

# Consumer-facing SIC section letters used for the saturation / demand views.
CONSUMER_SIC_SECTIONS = {"G", "I", "S"}   # retail, accommodation & food, other services

# --------------------------------------------------------------------------- #
# ONS Business Demography 2024 — REAL published birth & death rates (%) by broad
# industry group. Per-industry 5yr survival is not published in the bulletin;
# the overall UK 5yr survival rate (businesses born 2019) is 38.4%. We use the
# published DEATH RATE by industry as the closure/fragility signal.
# Source: ONS Business demography, UK: 2024.
# --------------------------------------------------------------------------- #
UK_OVERALL = {"birth_rate": 11.1, "death_rate": 9.8, "survival_5yr": 38.4}

# SIC section letter -> (birth_rate %, death_rate %). Sections not separately
# published by ONS fall back to the UK overall (11.1 / 9.8).
SECTION_CHURN = {
    "A": (11.1, 9.8),                                    # Agriculture (overall)
    "B": (7.6, 7.8), "C": (7.6, 7.8), "D": (7.6, 7.8), "E": (7.6, 7.8),  # Production
    "F": (10.6, 8.8),                                    # Construction
    "G": (11.4, 10.9),                                   # Wholesale/Retail/Motor
    "H": (15.6, 16.5),                                   # Transport & Storage (highest death)
    "I": (14.9, 12.9),                                   # Accommodation & Food ("pizza shops")
    "J": (10.7, 9.8),                                    # Information & Communication
    "K": (6.6, 6.7),                                     # Finance & Insurance
    "L": (11.1, 9.8),                                    # Real estate (overall)
    "M": (10.5, 9.2),                                    # Professional/Scientific/Technical
    "N": (14.4, 13.5),                                   # Business Admin & Support
    "O": (11.1, 9.8), "P": (11.1, 9.8),                  # Public admin / Education (overall)
    "Q": (9.4, 6.5),                                     # Health
    "R": (11.1, 9.8), "S": (11.1, 9.8),                  # Arts / Other services (overall)
    "T": (11.1, 9.8), "U": (11.1, 9.8),
}

# SIC 2007 section letter -> human label.
SECTION_LABELS = {
    "A": "Agriculture, forestry & fishing", "B": "Mining & quarrying",
    "C": "Manufacturing", "D": "Energy supply", "E": "Water & waste",
    "F": "Construction", "G": "Wholesale & retail", "H": "Transport & storage",
    "I": "Accommodation & food", "J": "Information & communication",
    "K": "Finance & insurance", "L": "Real estate", "M": "Professional & technical",
    "N": "Business admin & support", "O": "Public administration", "P": "Education",
    "Q": "Health & social work", "R": "Arts & recreation", "S": "Other services",
    "T": "Household employers", "U": "Extraterritorial", "X": "Not classified",
}

# SIC 2007 division (first 2 digits) -> section letter.
def sic_section(sic_code: str) -> str:
    digits = "".join(ch for ch in str(sic_code) if ch.isdigit())
    if len(digits) < 2:
        return "X"
    d = int(digits[:2])
    ranges = [
        (1, 3, "A"), (5, 9, "B"), (10, 33, "C"), (35, 35, "D"), (36, 39, "E"),
        (41, 43, "F"), (45, 47, "G"), (49, 53, "H"), (55, 56, "I"), (58, 63, "J"),
        (64, 66, "K"), (68, 68, "L"), (69, 75, "M"), (77, 82, "N"), (84, 84, "O"),
        (85, 85, "P"), (86, 88, "Q"), (90, 93, "R"), (94, 96, "S"), (97, 98, "T"),
        (99, 99, "U"),
    ]
    for lo, hi, sec in ranges:
        if lo <= d <= hi:
            return sec
    return "X"

HTTP_HEADERS = {"User-Agent": "EconomicIntelligence-GatesheadBusinessMap/1.0 (+github.com/NAdamsGHC)"}
HTTP_TIMEOUT = 60
