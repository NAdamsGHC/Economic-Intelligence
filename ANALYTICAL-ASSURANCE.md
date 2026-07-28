# Analytical assurance note — ELS scorecard, GDHI and productivity dashboards

**Status: experimental analytical products, not official statistics.** Built from published official statistics, but the derived measures (ranks, quartiles, indices, better/worse directions) are the author's analytical judgements. Treat with caution and verify figures against the source releases before using them to inform decisions.

This note applies the **Aqua Book (2025)** framework — proportionate quality assurance, verification vs validation, an assumptions log, and named roles — to:

- [`economy/els-scorecard.html`](economy/els-scorecard.html) — all 88 ONS Explore Local Statistics indicators covering Gateshead
- [`economy/gdhi.html`](economy/gdhi.html) — GDHI per head benchmarking, 1997–2023, and the small-area GDHI explorer, 2010–2023 (the per-head benchmarking previously sat in a separate `gdhi-per-head.html`, merged into this product in July 2026)
- [`economy/productivity.html`](economy/productivity.html) — GVA and productivity position, 1998–2023, with the statistical-neighbour scorecard and UK league table

Last updated: 28 July 2026.

---

## 1. Purpose, use and proportionality

These are **descriptive monitoring and benchmarking products**: they answer *"where does Gateshead stand, against whom, on what definition?"* They make no causal claims, no forecasts, and no appraisal of interventions.

**Assurance tier** (Aqua Book proportionality): *dashboard / published brief* — definitions block, caveats section, manifest provenance, structured review, and (this document) an assumptions log.

**Not sufficient for:** business cases, funding bids or investment decisions. Under the **Green Book (2026)**, evidence feeding an options appraisal needs a step-up this work has not had: a named **independent assurer**, sensitivity analysis of key assumptions, optimism-bias treatment, and additionality discipline (deadweight, displacement, substitution, leakage) applied to any claimed benefits. If a figure from these dashboards is carried into a business case, re-assure it at that tier first.

## 2. Roles (Aqua Book four-role model)

| Role | Who | Notes |
|---|---|---|
| Commissioner | N. Adams (author, personal capacity) | Set the requirement: all ELS indicators, house comparator sets |
| Analyst | Claude (AI-assisted build), sessions of 7 July 2026 | Built pipeline, dashboards and this log; self-assured |
| Assurer | **Not yet independently assured** | Structured self-review performed (§4); an independent review by a colleague (or a separate structured AI-assisted review session) is recommended before high-stakes use |
| Approver | N. Adams | Publication to the repository constitutes approval of the products as *experimental* |

## 3. Assumptions log

### ELS scorecard

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| A1 | **Indicator direction (polarity)** — each of the 88 indicators is classed *higher-is-better* (+), *lower-is-better* (−) or *context* (no direction). 70 ranked, 18 context. | Author's analytical judgement, stated on every Explore page. Full classification in `build/els-scorecard/parse_all.py` (`POL`). Contentious calls documented in A2. Misclassification would invert a rank; the direction is printed beside every rank so a reader can challenge it. |
| A2 | Contentious direction calls: **amenity rates** (supermarkets, sports facilities, museums, library/rail access, cultural participation) = higher-better, as access-to-services measures; **domestic electricity & gas consumption** = context (lower use is efficiency *or* fuel poverty — ambiguous); **house prices, population size/structure/change, traffic flow, food outlets, short-term lets, active-business counts, ecosystem-service £ values** = context (level reflects size, geography or preference, not performance); **business births** = higher-better and **deaths** = lower-better (churn's dynamism value is acknowledged but net framing preferred); **net housing additions** = higher-better (supply-side framing); **child underweight** = lower-better (alongside obesity/overweight). | Where a direction is genuinely arguable the indicator was placed in *context* rather than forced. |
| A3 | **National benchmark preference**: England > UK > Great Britain > England & Wales — the first with data on the indicator's latest period. Matches each source's coverage; the chosen benchmark is named on every row. | Comparing an England-only DfE measure with a UK average would mix coverages. |
| A4 | **Rank basis**: latest period column only, among local authorities with data on it (n stated per indicator); rank = 1 + count(strictly better); quartile = ⌈4·rank/n⌉. Legacy/dissolved LAD codes drop out because they have no latest-period value. | Ties share the better rank. n varies from 132 (persistent absence) to 382 — ranks are not comparable across indicators, only within. |
| A5 | **Direction-adjusted % vs benchmark** = polarity × (Gateshead ÷ benchmark − 1). A deliberate relative scale across mixed units; it says nothing about absolute importance. | Used only for the "furthest above/below benchmark" chart; labelled as author's calculation. |
| A6 | **Survey estimates**: 25 indicators carry published 95% CIs (marked ≈). Gateshead's latest-period CI is shown; ranks on these indicators are treated as soft and differences within the CI as not meaningful. APS-based local estimates are ONS **"official statistics in development"** — that designation travels with anything built on them. | CI series (beyond latest period) not embedded — a simplification. |
| A7 | **Comparator sets**: NECA 7; ONS economic statistical nearest neighbours (2026 release, economic set, similarity order). England-only sources lose the 6 Welsh/Scottish/NI neighbours — stated on each Explore page, never silently shrunk. | Sets fixed as of the 2026 releases; refresh when ONS re-clusters. |
| A8 | **Monthly series** (average house price) downsampled to one observation per year plus the latest month for the trend chart; ranks use the latest month. | Cosmetic only; no derived statistic uses the dropped months. |
| A9 | **Excluded tables** (20 of 108): no Gateshead row — NI/Wales/Scotland-specific variants, region-level FDI/R&D/exports, travel-time-to-employment, homicide (police-force areas). Population-by-age-and-sex detail summarised by the five structure indicators instead. | Listed in the dashboard's About tab. |
| A10 | **Values quoted as published** (rounded to ≤4 significant figures for embedding); no deflation applied anywhere — money values are current prices except GDP per head CVM (real, as published) and ecosystem values (2024 prices, as published). | Definitions discipline: nominal never presented as real. |
| A11 | **Reference periods differ by indicator** (Sept 2021 – Apr 2026) and are labelled on every row; the scorecard is a compendium, not a snapshot. | The single biggest misreading risk; flagged in the header caveat. |

### Business Map — high streets & centres (added 7 July 2026)

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| C1 | **Centre definitions are the statutory Local Plan designations** (MSGP Policy 6) fetched live from Gateshead Council's public GIS server: Primary Shopping Area ("Gateshead town centre"), 8 District and 15 Local Shopping Centres. | The most defensible definition available; changes when the council revises the policies map. |
| C2 | **Centre membership** = registered-office/premises point inside the designated polygon or within **150m** of its boundary (walkable fringe — judgement). MetroCentre and Retail World are published as label points, approximated by **500m/350m circles** (judgement) and treated as out-of-centre context, excluded from high-street aggregates. | Buffer widens centres slightly; stated on the dashboard. |
| C3 | **Registered office ≠ trading address** (inherited caveat): company counts per centre include firms registered at accountants/home addresses inside the centre; FSA-rated premises are the trading ground truth and drive the composition, takeaway and independents measures. | |
| C4 | **Start-ups** = incorporations of *currently-live* companies (the free CH product is live-only), so older quarters undercount (survivorship). Read recent levels, not long slopes — stated on the chart. | |
| C5 | **Openings/closures** are month-on-month diffs of CH snapshots via a persistent register (`build/gateshead-business-map/data/company_register.json`, committed so the Action accumulates history). "Gone" = dissolved, moved or de-registered — not necessarily a shopfront closure. Register seeded 1 July 2026; history builds from August 2026. | |
| C6 | **Independents vs chains** is a heuristic on FSA-rated premises: national brand list (~120 names) + any name at 3+ Gateshead premises. Applied to food-rated premises only; non-food chains (e.g. betting shops without food rating) may be missed. | Judgement; flagged on the dashboard. |
| C7 | **Walk-in catchment** = residents of LSOAs whose (boundary-approximated) centroid lies within **800m** of the centre centroid; income-deprivation from IMD 2025 (share of catchment population in England's most-deprived 30% of LSOAs). | Centroid-based, so edge LSOAs may be in/excluded; adequate for comparative context. |
| C8 | **Footfall** is the ONS/BT experimental index for the **North East region by site type** — no per-town footfall is published free anywhere; presented as regional context only, never as a Gateshead measurement. | |
| C9 | **VOA rating-list data was investigated and deliberately not used**: the bulk download is keyless but under a restricted (non-OGL) licence unsuitable for republication on a public site, and it still lacks a vacancy flag. The intervention score's vacancy signal therefore remains unwired; the recommended route is the council's internal NNDR empty-property data. | |

### GDHI per head dashboard

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| B1 | GDHI per head = ONS-published figure (current prices, residence-based, all-ages denominator), quoted directly — this is the official series behind the £19,127 (2023) figure; the companion `gdhi.html` per-head figures are derived with a different (MYPE) denominator and labelled as such. | Reconciliation note in the README. |
| B2 | **UK = 100 index** used as the inflation-free read of relative position (no LAD-level real GDHI exists); nominal growth always labelled nominal. | A falling index can coincide with rising real income — stated in the dashboard. |
| B3 | Ranks among the 361 UK LADs in the workbook (2023 boundaries), 1 = highest income; National Accounts estimates carry **no CIs but are revised through the whole back series each release** — nearby ranks treated as equivalent. | 2024 release (~autumn 2026) will revise history; rebuild, don't append. |
| B4 | Comparator sets as A7. | — |

### GDHI small-area explorer (added 28 July 2026)

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| C1 | The **LAD, ITL-region and national aggregates in the explorer are derived by the build**, not published by ONS: they sum the LSOA / Data Zone / SOA building blocks in the "other geographic areas" release. | Sums of modelled apportionments; use the per-head tab's published series for any quoted LAD figure. |
| C2 | Those derived aggregates cover **Great Britain, not the UK** — the building blocks are English and Welsh LSOAs and Scottish Data Zones, so Northern Ireland's 11 districts are absent. The national row is labelled Great Britain (2023 total £1,656,256m against an official UK £1,695,436m; the £39,180m difference is Northern Ireland). | Corrected 28 July 2026 after the July verification pass found the row labelled United Kingdom. Coverage is stated in the About tab and on the affected chart descriptions. |
| C3 | Area counts quoted in the interface are **3,425 areas, 350 GB local authorities and 11 ITL regions**, after two source header rows ingested as areas were removed from the data. | Corrected 28 July 2026 (the counts previously read 3,427 / 351 / 12, and one panel carried a stale 1,946 from an earlier build). |

### Productivity & GVA dashboard (added 28 July 2026)

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| D1 | GVA and productivity series quoted **exactly as published** by ONS — regional GVA (balanced) by industry for local authorities (April 2025 release, data to 2023) and subregional productivity by local authority district (19 June 2025 release, data to 2023). No re-derivation where an official figure exists. | Next vintages: LAD GVA 2024 around September 2026, subregional productivity 2024 on 5 November 2026, both with back-series revisions — rebuild, don't append. |
| D2 | The **business base total is the published UKBC figure** (5,580 enterprises, 2025), not the sum of the disclosure-rounded size bands (5,575). Size-band shares are computed on the band sum, so they remain internally consistent. | Corrected 28 July 2026; the difference is disclosure rounding, not error. |
| D3 | The statistical-neighbour scorecard resolves **all 20 economic neighbours**, including Barnsley (E08000016) and Newry, Mourne and Down (N09000010), both added from source on 28 July 2026 after the July verification pass found Barnsley carried a non-existent code (E08000038) and Newry missing from the areas dictionary. | Newry's 2023 per-job and jobs values are suppressed at source; the series ends 2022 for those two measures and the table shows the last published value. |

## 4. Verification and validation record

**Verification (built right):**

- Parse totals reconciled against the workbook: 108 tables read, 88 with Gateshead data, LAD counts per table checked against expected geography counts (361 UK LADs; 296 England).
- Spot checks against independently known official figures: GDHI per head £19,127 (2023); employment rate 76.3% with CI 72.0–80.6 (matches the known ±4.3pp APS interval); GVA per hour £32.16 (matches the productivity dashboard's source); average house price vs UK HPI.
- GDHI dashboard figures cross-checked against the standalone GDHI extract parsed independently earlier the same day (identical values).
- Pipeline no-change gate tested: consecutive runs on the same workbook produce no diff (and a key-type comparison bug found and fixed in that test); the first live GitHub Action run correctly took the no-commit path.
- Browser QA: zero console errors; all charts render; table sorting, search, domain filter, row-click navigation and CI display verified against computed values; mobile layout checked.

**Validation (right thing built):** the products answer the commissioned question — Gateshead's standing on all available ELS indicators against the house comparator sets — and explicitly do not answer causal ("why"), predictive ("what next") or appraisal ("what should we fund") questions. Findings sentences are generated from the data, so they cannot drift from the figures they describe.

**Reproducibility (through-life QA):** source workbooks, tidy extracts and `manifest.json` provenance records; the full pipeline is in `build/els-scorecard/` and re-runs monthly via GitHub Action, committing only on real data changes; every number visible in prose is computed from the embedded data object at load.

## 5. Code of Practice for Statistics

Applied voluntarily: definitions and methods published (About tabs + this note); estimates labelled honestly (CIs shown, "official statistics in development" respected for APS-based measures, experimental status declared); revisions explained (back-series revision warnings on regional accounts); sources cited with publication dates on every indicator.

## 6. Known limitations and recommended step-ups

1. **No independent assurer yet** — the single biggest gap against the Aqua Book for anything beyond internal monitoring use.
2. No sensitivity analysis of the polarity classification (e.g. how the quartile-mix chart moves if contested directions flip). Cheap to add if the scorecard starts driving decisions.
3. Amenity per-head rates structurally favour small rural areas; cross-boundary use (Newcastle's amenities) is invisible at LAD level.
4. CI bands are latest-period only; trend charts show point estimates.
5. If any figure feeds a Green Book business case: independent assurance, sensitivity analysis, optimism bias and additionality treatment first (§1).
