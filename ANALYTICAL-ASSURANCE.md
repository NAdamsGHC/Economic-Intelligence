# Analytical assurance note — ELS scorecard & GDHI per head dashboards

**Status: experimental analytical products, not official statistics.** Built from published official statistics, but the derived measures (ranks, quartiles, indices, better/worse directions) are the author's analytical judgements. Treat with caution and verify figures against the source releases before using them to inform decisions.

This note applies the **Aqua Book (2025)** framework — proportionate quality assurance, verification vs validation, an assumptions log, and named roles — to:

- [`economy/els-scorecard.html`](economy/els-scorecard.html) — all 88 ONS Explore Local Statistics indicators covering Gateshead
- [`economy/gdhi-per-head.html`](economy/gdhi-per-head.html) — GDHI per head benchmarking, 1997–2023

Last updated: 7 July 2026.

---

## 1. Purpose, use and proportionality

These are **descriptive monitoring and benchmarking products**: they answer *"where does Gateshead stand, against whom, on what definition?"* They make no causal claims, no forecasts, and no appraisal of interventions.

**Assurance tier** (Aqua Book proportionality): *dashboard / published brief* — definitions block, caveats section, manifest provenance, structured review, and (this document) an assumptions log.

**Not sufficient for:** business cases, funding bids or investment decisions. Under the **Green Book (2026)**, evidence feeding an options appraisal needs a step-up this work has not had: a named **independent assurer**, sensitivity analysis of key assumptions, optimism-bias treatment, and additionality discipline (deadweight, displacement, substitution, leakage) applied to any claimed benefits. If a figure from these dashboards is carried into a business case, re-assure it at that tier first.

## 2. Roles (Aqua Book four-role model)

| Role | Who | Notes |
|---|---|---|
| Commissioner | N. Adams (Gateshead Council economic intelligence) | Set the requirement: all ELS indicators, house comparator sets |
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

### GDHI per head dashboard

| # | Assumption / judgement | Basis and risk |
|---|---|---|
| B1 | GDHI per head = ONS-published figure (current prices, residence-based, all-ages denominator), quoted directly — this is the official series behind the £19,127 (2023) figure; the companion `gdhi.html` per-head figures are derived with a different (MYPE) denominator and labelled as such. | Reconciliation note in the README. |
| B2 | **UK = 100 index** used as the inflation-free read of relative position (no LAD-level real GDHI exists); nominal growth always labelled nominal. | A falling index can coincide with rising real income — stated in the dashboard. |
| B3 | Ranks among the 361 UK LADs in the workbook (2023 boundaries), 1 = highest income; National Accounts estimates carry **no CIs but are revised through the whole back series each release** — nearby ranks treated as equivalent. | 2024 release (~autumn 2026) will revise history; rebuild, don't append. |
| B4 | Comparator sets as A7. | — |

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
