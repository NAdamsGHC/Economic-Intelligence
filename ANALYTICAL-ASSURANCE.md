# Analytical assurance note — ELS scorecard, GDHI, productivity and Local Outcomes Framework dashboards

**Status: experimental analytical products, not official statistics.** Built from published official statistics, but the derived measures (ranks, quartiles, indices, better/worse directions) are the author's analytical judgements. Treat with caution and verify figures against the source releases before using them to inform decisions.

This note applies the **Aqua Book (2025)** framework — proportionate quality assurance, verification vs validation, an assumptions log, and named roles — to:

- [`economy/els-scorecard.html`](economy/els-scorecard.html) — all 88 ONS Explore Local Statistics indicators covering Gateshead
- [`economy/gdhi.html`](economy/gdhi.html) — GDHI per head benchmarking, 1997–2023, and the small-area GDHI explorer, 2010–2023 (the per-head benchmarking previously sat in a separate `gdhi-per-head.html`, merged into this product in July 2026)
- [`economy/productivity.html`](economy/productivity.html) — GVA and productivity position, 1998–2023, with the statistical-neighbour scorecard and UK league table
- [`performance-outcomes/lgof-comparator.html`](performance-outcomes/lgof-comparator.html) — Gateshead's position on MHCLG's Local Outcomes Framework (first edition, 1 July 2026), 112 live metrics rendered as 137 series against six comparator groups (added 30 July 2026)

Last updated: 30 July 2026.

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

### Local Outcomes Framework comparator (added 30 July 2026)

MHCLG publishes no dataset behind the framework and its digital tool is not live, so every metric
is assembled from the original publication the framework names. The registry
(`pipelines/lgof-comparator/src/registry.py`) is the single source of truth for polarity, units,
verdict suppression and every note the product displays.

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| L1 | **Comparison universe includes Gateshead in every group.** MHCLG's fifteen statistical neighbours and the ONS economic twenty are defined as Gateshead's *neighbours* and exclude it; Gateshead is added to both, making 16 and 21, so the median and the rank are computed on the same authorities. | Reporting a rank against one universe and a median against another is not defensible in a footnote. The addition is stated on the group control and in the About tab. It moves a 15-member median slightly. |
| L2 | **Better/similar/worse is a confidence-interval test against the group median** — better or worse where Gateshead's published 95% interval excludes the median, similar where it includes it. This is OHID's own Fingertips convention. Available on 49 of 137 series. | Not a formal test of difference between two estimates: the median is treated as a fixed benchmark, which is how Fingertips treats England. It understates uncertainty because the median itself is estimated. |
| L3 | **Where no interval is published, only position is shown** — rank of N and quintile band, explicitly labelled position and not significance, on 64 series. | Administrative returns have no sampling error but do have recording differences between authorities, which a rank cannot see. Stated on every such metric. |
| L4 | **Quintile bands are not computed below 10 authorities with a value.** NECA 7 would put 1.4 authorities in a band. The rank is still given for every group. | A band on a group of seven would read as precision that is not there. |
| L5 | **Group medians are not computed below 3 authorities with a value** in the period; the trend line drops those periods rather than drawing a median of two. | |
| L6 | **11 metrics carry `no_verdict` from the registry** — tiny counts (rough sleeping, families in B&B), banded denominators (building remediation), mismatched geography (both bus metrics), raw counts not adjusted for population (domestic abuse referrals), a comparator universe too partial to rank against (local sites in positive conservation management), and estimates too imprecise to rank (18–24 employment, ±16pp). **The rank is withheld along with the verdict**, because on these metrics a rank is the thing that would mislead, not merely the significance test; their notes say so in terms. Neutral-polarity metrics are treated differently — the position is meaningful and only the direction is not, so those show "Nth highest of N" without a judgement. | Author's judgement per metric, with the reason printed on the metric. Withholding a rank loses information; giving a misleading one loses trust. The first build printed the rank beside a "not judged" badge on all 18 such series, contradicting the notes on the same page; caught in browser QA. |
| L7 | **7 metrics have no agreed better direction** and render neutral, uncoloured, with position shown and no judgement: the looked-after rate, the placement-type mix, early-help spend share, two adult social care volume measures, business deaths and the fly-tipping enforcement ratio. | Where a direction is genuinely arguable it is not forced. |
| L8 | **Metrics published only as parts are shown as parts.** 11 metrics are rendered as one series per component with no arithmetic between them — placement types, care leavers by age, road condition by class, the two adult social care volume measures, the sex-split life expectancy measures, the 18–24 pair, and the four substance-misuse series. Components carry their own vintage where they differ. | Combining them would publish a total the source does not. The substance-misuse set spans 2014/15 to 2022/23 and is explicitly not a snapshot. |
| L9 | **Unmet need (outcomes 4 and 8) is not published on any free, keyless source and is not estimated.** Four published components ship side by side with no arithmetic between them. | Subtracting all drug clients from opiate-and-crack prevalence would count non-opiate clients as meeting opiate and crack need and would mix a 15–64 base with an 18-plus one — a plausible-looking wrong number, which is worse than an honest gap. |
| L10 | **Derived metrics are labelled as the author's calculation** on the metric and in the scorecard, with the derivation and what the source *does* publish stated. Where the source publishes the figure directly — the killed-or-seriously-injured rate, the bus mileage change — that is said too. | 11 metrics are derived. The temporary accommodation rate takes both its numerator (households in temporary accommodation with children) and its denominator (households in the area) from MHCLG's own table TA1, so only the division is ours; an earlier version summed four TA2 columns over a Census 2021 count and was wrong on both. |
| L11 | **Two metrics ship as the nearest available published measure**, flagged on the metric: active travel (DfT publishes "at least once a month", not "at least twice in 28 days") and assessments not leading to support (DHSC counts requests for support, not assessments). Both are upper bounds on the metric as worded. | The cohort is right in both cases; the event is not. |
| L12 | **A share built from incomplete published parts is never ranked as if complete.** Where a component is suppressed, the authority's value is computed from the published parts, flagged `partial`, and Gateshead's own verdict is withheld when its value is partial; where comparators are partial the group carries a stated caveat. | Affects one metric (special guardianship / family networks), where 55 of 126 comparator values are partial and therefore understated, flattering Gateshead's rank. |
| L13 | **Units are registered per metric, never inferred from the title.** The framework's wording is unreliable: three business metrics titled "number of" are published as percentages, and two adult social care metrics titled "number of people" are published as rates per 100,000. | Title inference was tested and got a dozen metrics wrong. The build stops on a metric with no registered unit. |
| L14 | **Staleness is self-calibrating**, measured against each series' own observed publication cadence plus a grace allowance, not a flat rule — these metrics run from monthly returns to three-year pooled mortality rates. An `inherent_lag_months` allowance is set only where the measure's *design* explains the gap (three-year business survival names a birth cohort), and a cadence override only where the publisher issues one edition at a time (the Indices of Deprivation). | Set per metric in the registry. A wrong override would hide a genuine publication delay; both are used sparingly and listed in the registry. |
| L15 | **Periods are never reformatted**, except where a published label would misstate the vintage — DfT writes `2025` for the year ending March 2025, converted to `2024/25` with the conversion stated in the fetcher. | Otherwise the sweep reads DfT data as nine months fresher than it is. |
| L16 | **Retired GSS codes are mapped** for pure recodes only (Barnsley, Sheffield, Gateshead, Northumberland). Mergers and reorganisations are deliberately absent from the shared map because they are not one-to-one; Defra's use of the abolished Buckinghamshire county code is remapped inside that fetcher only, on rows Defra itself labels unitary. | Unmapped, two of the 132 authorities drop out silently and every group median is computed on the wrong universe. |
| L17 | **Single-period metrics show no trend** rather than a one-point line: the three Indices of Deprivation measures, the connectivity score, EPC, both DHSC volume measures and Skills for Care. IoD2019 is not stitched on, because MHCLG states IoD2025 is not directly comparable with earlier editions. | Stitching would manufacture a trend the publisher says is not there. |
| L18 | **Values are rounded to four decimal places for embedding**, far beyond any precision displayed; the unrounded figures remain in the pipeline's source stores. | |
| L19 | **A tied rank is reported as a block, and a tied block that straddles more than one fifth gets no quintile band.** Competition ranking alone (ties taking the block's best position) is withheld in favour of "joint Nth–Mth of N", and `_band` refuses to name a fifth the block does not sit wholly inside. | Found in verification. Gateshead collects no food waste separately — the joint-lowest figure in England, shared with 73 authorities — and the block's best position put it 59th of 132 and in the **middle fifth** of a distribution it is at the bottom of. Two further series moved a full band on the same mechanism. |
| L20 | **Fingertips category rows are excluded wherever a Fingertips series is read.** Three of the four substance-misuse components are published broken down by deprivation decile against the England area code; keeping those rows left 82 England rows per indicator and the last one written won. | Found in verification. England's adults-in-drug-treatment rate displayed as 2.80 per 1,000 — the least-deprived decile — where the published England figure is 4.48, on six displayed series. Local authority values, medians, ranks and verdicts were not affected. The reader is now shown the published England figure. |
| L21 | **Five ASCOF measures carry DHSC's "official statistics in development" designation** for 2024/25, being newly derived from client level data, with DHSC's own warning that low figures in some authorities reflect data quality rather than practice. | 2A, 2B/2C, 2D(1), 2E(2a)/(2b) and 3D(2a). Previously only 2A said so, while 2E and 2B/2C carried the two most negative readings on the page. |
| L22 | **ASCOF 2E is flagged as unsafe to read as a Gateshead outcome.** Cross-checked against DHSC's adult social care activity return for the same year and the same client level source, 54.4% of Gateshead's 65-and-over long-term support clients receive a community service type against the 41.2% this measure reports as living at home or with family — a 13.2 point gap where England's is 0.9 and the median across 152 authorities is 1.1, placing Gateshead at about the 94th percentile of divergence. | Consistent with an accommodation-status recording gap in Gateshead's first client level return rather than a real difference in support, and it accounts for roughly two thirds of the apparent gap to England. Stated on the metric. |
| L23 | **Children in low income families: the choice of housing-costs basis moves the comparison, not only the level**, and is stated with its positional effect. Before housing costs puts Gateshead 88th of 130 and in the fourth fifth; after housing costs, 63rd and the middle fifth. Three published caveats now travel with it: under-16s only, latest year provisional, and a mid-2024 population denominator DWP itself flags. | The earlier note claimed before-housing-costs was "DWP's own headline local series", which is not supported — the publication and the Child Poverty Strategy both lead on after housing costs. It is the longer series, which is the actual reason for the choice. |

## 4. Verification and validation record

**Verification (built right):**

- Parse totals reconciled against the workbook: 108 tables read, 88 with Gateshead data, LAD counts per table checked against expected geography counts (361 UK LADs; 296 England).
- Spot checks against independently known official figures: GDHI per head £19,127 (2023); employment rate 76.3% with CI 72.0–80.6 (matches the known ±4.3pp APS interval); GVA per hour £32.16 (matches the productivity dashboard's source); average house price vs UK HPI.
- GDHI dashboard figures cross-checked against the standalone GDHI extract parsed independently earlier the same day (identical values).
- Pipeline no-change gate tested: consecutive runs on the same workbook produce no diff (and a key-type comparison bug found and fixed in that test); the first live GitHub Action run correctly took the no-commit path.
- Browser QA: zero console errors; all charts render; table sorting, search, domain filter, row-click navigation and CI display verified against computed values; mobile layout checked.

**Verification — Local Outcomes Framework comparator (30 July 2026):**

- Registry binds 115 entries to 115 parsed framework metrics, zero unregistered, zero errors; a reworded metric fails the build rather than dropping silently.
- Every fetcher re-runs clean from cache; each asserts its source's layout, and several declare an expected England value before reading by position.
- Group statistics reproduced independently in a second implementation: all 137 series × 6 groups checked, and every stored median, rank and verdict recomputed from the embedded cross-section and matched.
- Verdicts re-derived from each series' own interval and the group median: all 39 agree with the stored value.
- Spot checks against independently known figures: EPC band C or above 51.07%; killed or seriously injured 48.56 per billion vehicle miles (2025 edition, which the live URL resolver found had superseded the pinned 2024 file); ASCOF 2E 65+ 41.2% against England 60.3%; RQF Level 4+ 36.6% (30.3–42.9), Jan–Dec 2021, its true vintage.
- **Two defects found and fixed during the build.** The households-with-children-in-temporary-accommodation rate used NOMIS `NM_2026_1` as its denominator, which is *TS006 Population density*, not TS041 Number of Households: Gateshead read 1,378 households against the published 88,999, inflating the rate roughly 67-fold and giving a national median of 104 per 1,000 households — a tenth of every household in England. Corrected to `NM_2059_1`, with an assertion that England's total equals the published 23,436,085 before the denominator is used, and a completeness check that then caught NOMIS filing Census 2021 under retired codes for Barnsley and Sheffield and having no rows at all for the four authorities created in April 2023. Separately, the ASCOF fetcher was reading the authority-level time series to date each measure and then discarding it, leaving nine measures with no trend.
- Narrative gate: every static sentence containing a number is generated in the browser from the embedded data, and the headline counts, the strongest/weakest finding and the currency panel were recomputed in Python from the same file and matched.
- Browser QA: zero console errors; all 137 series rendered across all 6 comparator groups and all 16 outcomes (822 renders) without an exception; confidence whiskers, median reference line, trend panel, group switching and row-click navigation verified.
- Every source landing page fetched at publish and returning 200, except Arts Council England, which returns 403 to any programmatic request including for its own front page.

**Second verification pass — independent review, 30 July 2026.** A structured adversarial review of the derived metrics, the group-statistics code and the framing was run before publication. It returned three findings that would have put a wrong reading in front of a reader, all fixed and re-verified above (L19, L20, and ranks displayed on the 18 series the product itself says must not be ranked), plus the source and caveat corrections at L21–L23 and the temporary accommodation numerator at L10. Two of its findings were checked and confirmed against the source workbooks before acting: MHCLG's table TA1 does publish both the with-children count and a household denominator by authority, and the before/after housing costs rank swing is 88th to 63rd of 130. One brief-compliance gap was accepted and closed: the commissioned analytical read on the economic and place outcomes (12 to 16) was absent and has been added, generated from the data.

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
