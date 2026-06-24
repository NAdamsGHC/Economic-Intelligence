# Economic Intelligence — Gateshead & the North East

Interactive HTML dashboards exploring open ONS datasets for **Gateshead borough** and the wider **North East of England**. Catalogued by ONS topic.

Each dashboard is a single self-contained HTML file — open it directly in any modern browser, or browse the live versions via [GitHub Pages](#enabling-github-pages) once enabled. The site's landing page is [`index.html`](index.html).

## Catalogue

| ONS topic | Dashboard | Theme | Size |
|---|---|---|---|
| **Economy** | [Productivity & GVA](economy/productivity.html) | Balanced GVA (current price & real), output per hour / per job, sectors, concentration risk, benchmarking vs NE / UK / statistical neighbours | 0.49 MB |
| **Economy** | [GDHI 2010–2023](economy/gdhi.html) | Gross Disposable Household Income — UK regional accounts, LSOA choropleth, inequality | 9.1 MB |
| **Business, industry and trade** | [Gateshead Business Map](business-industry-trade/gateshead-business-map.html) ⭐ | Every Companies House business in the borough + IMD 2025, sector churn, FSA premises, BRES jobs, UKRI innovation; intervention/investment scores by LSOA & ward | ~2.9 MB |
| **Business, industry and trade** | [Creative Industries (CCIS)](business-industry-trade/creative-industries.html) | DCMS creative sector businesses / employment / GVA across the 7 NECA local authorities | 92 KB |
| **People, population and community** | [Gateshead Built-Up Areas](people-population-community/built-up-areas.html) | Population, house prices, employment, visitor economy for 7 BUAs inside Gateshead | 1.35 MB |
| **People, population and community** | [Gateshead Deprivation (IMD 2025)](people-population-community/indices-of-deprivation-2025.html) | Indices of Deprivation 2025 — 22 wards & 126 neighbourhoods ranked, domain ranks, social-value targeting matrix | 0.66 MB |
| **Employment and labour market** | [Employer Skills Survey 2024](employment-labour-market/employer-skills-survey-2024.html) | DfE ESS 2024 — North East vs England's 9 regions: vacancies, skills gaps, training, apprenticeships, future skill needs, AI | 36 KB |

---

## Economy — Productivity & GVA dashboard

[`economy/productivity.html`](economy/productivity.html)

Interactive dashboard of **Gateshead's productivity and gross value added**, built to answer where the borough's economy is growing, where it is at risk, what its biggest sectors are, and how it benchmarks against the North East, the UK and its statistical neighbours.

### What's in it

| Tab | What it shows |
|---|---|
| Overview | Headline scorecards (GVA £5.04bn current / £4.66bn real, £32.16 per hour, £49,663 per job, 96,600 jobs), the two-decade relative-decline chart (UK = 100), nominal-vs-real GVA, and six generated key-finding cards |
| GVA & growth | Current prices vs chained-volume (real) GVA, real growth indexed against the NE and UK (1998 = 100), and growth by period — the "growth is mostly inflation" story (real GVA is still below its 2006 peak, +0.4% over the last decade) |
| Sectors | Biggest sectors by GVA, real growth by sector, sector mix vs UK & NE, **sector value-per-job** (GVA ÷ BRES jobs vs England), concentration metrics (top-3 / top-5 share, HHI, public-facing share) and the UKBC business base by size and sector |
| Productivity | GVA per hour and per filled job (£) vs NE average and UK, the UK = 100 index trajectories, jobs & total hours, and the productivity gap expressed in money (~£1.6bn/yr vs UK output-per-job) |
| Benchmarking | ONS **economic** statistical nearest neighbours — productivity scatter (per hour vs per job), per-job ranking, and a sortable scorecard with UK and NE reference rows |
| National & league | Gateshead's place in the national distribution of output-per-job (ranked ~315/361), fastest- and slowest-growing local authorities, and a searchable, region-filterable league table of all 360+ UK LADs |

### Metrics

- **GVA, current prices** — cash value added by industry (£m), includes inflation; for single-year area comparison.
- **GVA, chained volume measures (CVM)** — real value added in 2022 money; for tracking growth over time.
- **GVA per hour worked** and **GVA per filled job** — ONS smoothed, current-price subregional productivity.

### Data sources

- **GVA** — ONS, *Regional gross value added (balanced) by industry: local authorities by ITL1 region* (released 17 Apr 2025; 1998–2023). All twelve ITL1-region workbooks are used to build UK and England aggregates and the national league table.
- **Productivity** — ONS, *Subregional productivity: labour productivity indices by local authority district* (released 19 Jun 2025; output per hour 2004–2023, per job 2002–2023), with the accompanying £-level, jobs and hours tables.
- **Statistical neighbours** — ONS, *Clustering similar local authorities and statistical nearest neighbours in the UK, 2026* (released 18 Mar 2026) — the **economic** nearest-neighbour set.
- **Employment / businesses** — NOMIS: *Business Register and Employment Survey (BRES)* employee jobs by SIC (2023–2024) and *UK Business Counts* (enterprises) by SIC and size band (2025).

### Designed for the 2024 update

GVA and productivity currently run to **2023**; ONS refreshes balanced GVA (spring) and subregional productivity (summer) annually, so 2024 is expected mid-2026. BRES already runs to **2024** and UKBC to **2025**. Every chart reads its latest year from the embedded data and the narrative text is generated from it, so a new vintage drops in by re-running the build — no design changes.

### Notes & caveats

- Current-price growth mixes real growth and inflation — don't read nominal GVA gains as real-terms gains.
- Regional and national GVA aggregates are summed from local-authority building blocks; CVM money values are summed on ONS's 2022 reference-year basis.
- Sector value-per-job divides ONS GVA by BRES employee jobs (Great Britain, excludes most self-employment) — read it as a cross-sector comparison, not a precise wage figure.
- The UK = 100 index is relative: a falling index can coincide with rising absolute productivity if the UK grew faster.

---

## Economy — GDHI dashboard

[`economy/gdhi.html`](economy/gdhi.html)

Interactive dashboard exploring ONS estimates of **Gross Disposable Household Income (GDHI)** for small UK geographic areas, 2010–2023, with a focus on Gateshead borough and the North East.

### What's in it

- **3,427 areas** across 18 geography types — parliamentary constituencies, towns, travel-to-work areas, integrated care boards, health boards, MSOAs, plus derived **Local Authority District** and **ITL region** aggregates and a UK national total
- **126 Gateshead LSOAs** from the ONS small-area GDHI release, with full per-LSOA time series
- **GDHI per head** computed from ONS Mid-Year Population Estimates (NOMIS) — both **total population** and **working-age (16–64)** denominators
- **Interactive choropleth map** of all 126 Gateshead LSOAs with five colour metrics (per-head, total GDHI, growth %, population)
- **14 years** of data (2010–2023), **17 income components** per area
- **Specialty zones** from the ONS dataset — Central Activities Zone, Northern Isle of Dogs, OPDC, Clyde River Region, Clyde River Gateway, Highlands & Islands, West Midlands Metro

### Tabs

| Tab | What it shows |
|---|---|
| Gateshead | Borough headline (£3.81bn / £18,988 per head in 2023), per-head trajectory vs NE and UK, four Westminster constituencies, share-of-borough by constituency, income-component breakdown, all 27 Gateshead MSOAs, comparison with neighbouring boroughs |
| LSOAs & Map | Choropleth of 126 Gateshead LSOAs — switch between per-head GDHI (total or working-age), GDHI £m, growth %, or population. Pan/zoom, hover for detail, click for trajectory. Distribution histogram + ranked league table. Inequality ratio (richest:poorest LSOA) alongside median and mean |
| North East | All NE LADs / constituencies / towns / TTWAs / MSOAs ranked and tabled, switchable by geography type and sort metric |
| UK Context | UK total, 12 ITL regions ranked, indexed growth trajectories, where Gateshead sits in the 350-LAD league table |
| Specialty Areas | CAZ, NIOD, OPDC, Clyde, Highlands & Islands, West Midlands Metro — each compared with Gateshead and the UK total on an indexed basis |
| Compare | Pick any combination of UK areas. Switch component, switch between £m / indexed-to-2010 / YoY %. Presets for Gateshead, NE big cities, NE boroughs, UK regions |
| Explore | Drill into any single area's full 17-component breakdown |

### Data sources

- **GDHI**: [ONS — GDHI estimates for other geographic areas, 2010 to 2023](https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome) (statistics in development, published 28 May 2026). The companion "small-area" workbook supplies LSOA-level England/Wales, Data Zone Scotland, and SOA Northern Ireland figures.
- **Population**: ONS Mid-Year Population Estimates via [NOMIS](https://www.nomisweb.co.uk/) — LAD-level by five-year age band (2010–2023) and small-area (LSOA) by single year of age (2011–2023). Three age bands (0–15, 16–64, 65+) are aggregated to compute total population for the per-head denominator; working-age GDHI per head uses the 16–64 band only.
- **Boundaries**: Gateshead LSOA boundaries (2011 census geography) from [ONS Open Geography Portal](https://geoportal.statistics.gov.uk/) — super-generalised clipped polygons for fast web rendering.

GDHI is the amount of money that all individuals in the household sector have available for spending or saving after direct and indirect taxes and direct benefits. The estimates apportion LSOA / Data Zone / SOA building blocks to wider geographies. All £-million values are **current prices**; per-head figures are £ of current-price GDHI per resident per year.

### Notes & caveats

- Current-price growth combines real growth and inflation — don't read +83% UK growth since 2010 as a real-terms gain.
- Don't sum across geography types (e.g. PCs + Towns). They overlap.
- The four Gateshead-named Westminster constituencies extend into Consett (County Durham) and Washington (Sunderland borough), so their sum (£7.33bn) overstates Gateshead borough. The proper borough figure (£3.81bn) is the LAD aggregate, derived from summing all 27 Gateshead MSOAs.
- The UK total in this dataset excludes Northern Ireland (NI uses a different geography that isn't apportioned in the same way for these "other geographic areas" tables).

---

## Business, industry and trade — Creative Industries (CCIS)

[`business-industry-trade/creative-industries.html`](business-industry-trade/creative-industries.html)

Baseline dashboard of the **DCMS Creative Industries** across the seven local authorities of the **North East Combined Authority** (NECA). Companion to the CCIS Framework Data & Evidence consultation.

### What's in it

- Business counts, employment and Gross Value Added by creative-industry sub-sector
- Local-authority breakdowns across the seven NECA councils
- Sector and area filters, time-series trends, sector mix views

### Data source

**DCMS Creative Industries Sector Economic Estimates** — business counts, employment and GVA by SIC subclasses defined as "creative industries" by DCMS. The underlying business and employment counts come from the ONS Inter-Departmental Business Register (IDBR) and Business Register and Employment Survey (BRES).

---

## Business, industry and trade — Gateshead Business Map

[`business-industry-trade/gateshead-business-map.html`](business-industry-trade/gateshead-business-map.html)

An interactive map of **every company registered in Gateshead borough** (~11,200 from the Companies House Free Company Data Product), geocoded and filtered to LAD **E08000037**, then enriched to help an economic-development team spot where to **intervene** and where to **invest**.

### What's in it

| Tab | What it shows |
|---|---|
| Overview | Borough headline — companies, active vs. in-distress, FSA premises, BRES jobs, residents — with an auto-written narrative and top intervention/investment wards |
| Map | Leaflet map: company points (clustered, coloured by SIC section), FSA food premises, and an LSOA choropleth switchable between **intervention score**, **investment score**, **IMD 2025 decile** and **business density**; ward overlay; filters by sector / status / mass-registration address |
| Sectors & saturation | Bubble chart of businesses-per-1,000-residents (supply) vs. ONS industry death rate (churn) — the "too many that keep failing" lens — plus a full SIC-section table |
| Intervention & investment | Ward league tables for each composite score, with signal composition notes |
| Innovation | UKRI Gateway to Research projects (incl. Innovate UK) associated with Gateshead, by funder |
| About & caveats | Sources, vintages, scoring weights and the honest caveats (registered office ≠ trading address, national-by-industry churn, etc.) |

### Scoring (editable in [`build/gateshead-business-map/config.py`](build/gateshead-business-map/config.py))

- **Intervention** = deprivation (IMD 2025) + live business distress (CH liquidation/administration) + sector fragility (local mix × ONS death rates). *Vacancy omitted until council NNDR data is wired.*
- **Investment** = growth sectors + dynamism (recent incorporations) + agglomeration (business density) + underserved demand (residents per consumer premise). *Per-LSOA innovation omitted until geocoded.*
- Each signal is normalised 0–1 across the 126 LSOAs; weights re-normalise when a signal is unavailable. LSOA scores roll up to ward, population-weighted.

### Data sources (all free + **no API key**)

Companies House Free Company Data Product · postcodes.io (geocoding) · IMD 2025 / IoD2025 (MHCLG) · ONS Business Demography 2024 (industry birth/death rates) · Nomis BRES (employment) · Food Standards Agency · UKRI Gateway to Research · ONS Open Geography Portal (LSOA 2021 + Ward 2024 boundaries).

---

## People, population and community — Gateshead Built-Up Areas

[`people-population-community/built-up-areas.html`](people-population-community/built-up-areas.html)

Profile of the **seven built-up areas inside Gateshead Metropolitan Borough** (Gateshead, Whickham, Blaydon, Birtley, Ryton, Crawcrook & Greenside, Rowlands Gill), benchmarked against the wider North East and all 1,395 England & Wales BUAs.

### What's in it

| Section | What it shows |
|---|---|
| Profile | One scorecard per BUA — classification chips, 2021 population, house price, employment change, inactivity, ageing |
| Map | The seven Gateshead BUAs plotted geographically. Filter by Combined classification / Income deprivation / Job density / Relative access / Coastal / Size / Visitor profile |
| Population | 2001 vs 2021 counts, % change vs national & NE averages, age-band shifts |
| House prices | 2001 / 2011 / 2021 / 2023 median trends with national & NE reference lines |
| Employment | 2015–2024 job change in counts and %, economic-inactivity composition |
| Visitor economy | Per-BUA visitor ratios, hotspot-vs-spread scatter, NE peer benchmark, national distribution, visitor profile by classification |
| Context | Gateshead vs NE region vs class group vs England & Wales totals, distribution plots, classification breakdown |
| Takeaways | Six narrative callouts on what the data says about Gateshead |

### Data source

ONS — *Understanding towns in England and Wales: investigating socioeconomic trends, May 2026*. Source workbook: `00combinedclassificationv5.xlsx`. BUA 2024 geography from Ordnance Survey, with centroids from the [ONS Open Geography Portal](https://geoportal.statistics.gov.uk/) (`main_ONS_BUA_2024_EW_V2`).

Inputs the dashboard draws on:

- 2001, 2011 & 2021 Censuses (population totals + age structure)
- Business Register and Employment Survey (BRES) 2015–2024
- HM Land Registry 2001–2023 (median house prices)
- English IMD 2025 / Welsh IMD 2025 (deprivation flags)
- 2021 Rural Urban Classification (relative access)
- O2 Motion People Counts, Nov 2024 – Nov 2025 (visitor-to-resident ratios — **research data, not official statistics**)

### Notes & caveats

- London is excluded (different BUA methodology).
- Visitor-to-resident ratios are aggregated from LSOA to BUA via an ONS lookup table. Major destinations sitting in zero-resident commercial land (notably the **MetroCentre**) don't fall inside any of the 5,000+ BUA polygons — their footfall is attributed via whichever BUA the containing LSOA is assigned to, the most plausible explanation for Whickham's anomalously high max ratio of 16.8.
- Net employment change across the seven Gateshead BUAs is **−900 jobs (2015→2024)**, despite the main Gateshead BUA gaining +5,000. The satellites collectively lost ~5,900.
- House prices use median sale prices and don't control for accommodation type.
- The map uses CARTO Light tiles and Leaflet — no API key required, but a network connection is needed for tiles. Everything else (data, charts) is embedded.

---

## People, population and community — Gateshead Deprivation (IMD 2025)

[`people-population-community/indices-of-deprivation-2025.html`](people-population-community/indices-of-deprivation-2025.html)

Ward, domain and neighbourhood breakdown of the **English Indices of Deprivation 2025 (IoD2025)** for Gateshead, built to **target social value commitments where need is deepest and reach is widest**.

### What's in it

| Tab | What it shows |
|---|---|
| Overview | Gateshead's national position (53rd most deprived of 296 LADs), the spread of its 126 neighbourhoods across national deprivation deciles, and headline indicators as real headcounts — 55,926 income-deprived residents, 14,697 children in income-deprived families, 22,563 employment-deprived, 12,466 older people |
| Domains | The seven IoD domains ranked by Gateshead's **rank among all 296 English local authorities** (the only fair cross-domain comparison), a borough radar profile, and worst-decile neighbourhood counts per domain |
| Wards | League table of all 22 wards by population-weighted IMD score, with per-ward indicator headcounts; click a ward for its domain radar and full profile |
| Map | Leaflet choropleth of the 126 LSOAs or 22 wards, colourable by 10 measures (overall IMD, income, employment, child poverty, health, crime, older-people income deprivation, education, barriers, living environment) |
| Priorities & targeting | Intensity-vs-reach priority matrix, three priority tiers, and targeting recommendations linking the borough's worst domains to the wards carrying the most need |

### Key findings

- **53rd most deprived of England's 296 local authorities** (top 18%). Worst on **Health & Disability (27th nationally)** and **Employment (36th)**; best on **Barriers to Housing & Services (273rd)** — i.e. good physical access.
- **24 of 126 neighbourhoods (19%) in England's most-deprived 10%; 45 (36%) in the worst 20%** — yet 17 sit in the least-deprived 20%. Deprivation is concentrated, not uniform.
- Five most deprived wards: **Felling, High Fell, Deckham, Saltwell, Bridges**. **Saltwell** carries the most income-deprived residents (4,539) and children in income-deprived families (1,629) — the gap between *intensity* and *reach*.
- **42% of Gateshead's children** live in income-deprived families (England 37%).

### Data sources

- **IoD2025** — Ministry of Housing, Communities & Local Government, *File 7: All ranks, scores, deciles and population denominators* (LSOA 2021 geography). [gov.uk](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025)
- **Geography** — ONS Open Geography Portal: LSOA (2021) → Ward (2024) → LAD (2024) best-fit lookup, plus 2024 ward and 2021 LSOA generalised boundaries (Gateshead's current 22 wards).

### Notes & caveats

- Ward scores are population-weighted averages of constituent LSOA scores; national domain ranks are computed against the same measure for all 296 English LADs (author's calculation from File 7). LSOA→ward assignment is best-fit, so ward edges are approximate.
- **Comparability:** IoD2025's Income and Employment domains use **Universal Credit** data, which captures a broader population than IoD2019's legacy benefits. Absolute rates are therefore higher than 2019 and **must not be read as change over time** — the Indices are designed for *relative* ranking, which is exactly how this dashboard uses them.

---

## Employment and labour market — Employer Skills Survey 2024

[`employment-labour-market/employer-skills-survey-2024.html`](employment-labour-market/employer-skills-survey-2024.html)

Dashboard of the **Department for Education Employer Skills Survey (ESS) 2024**, benchmarking the **North East** against England's nine regions on the demand for, and supply of, workforce skills.

### What's in it

| Tab | What it shows |
|---|---|
| Overview | North East headline scorecards (61,239 employers, 14% with a vacancy, 16% with a skills deficiency, 59% training, 38% apprenticeships, 11% using AI), a rank-of-9 "at a glance" strip, NE-vs-England-weighted comparison, and six generated key-finding cards |
| Skills shortages & gaps | Any-deficiency and vacancy incidence by region, the North East's skills gaps broken down by occupation (skilled trades stands out), and the SSV-vs-skills-gap explainer |
| Training & apprenticeships | Apprenticeship engagement by region (NE is **#1 in England**), training incidence by region, and the mix of training types NE employers provide |
| Future skills, AI & quals | Anticipated upskilling need by region (NE **#1 at 68%**), the drivers behind it, AI current-use vs planned-adoption (NE lowest), and T-Level awareness |
| Regional comparison | Sortable, colour-shaded matrix of all nine regions across eleven measures, with the North East highlighted and an employer-weighted England reference row |
| About | Methodology, the **no-Gateshead-data** caveat, definitions, base sizes and caveats |

### Key findings (North East)

- **Highest apprenticeship engagement in England** — 38% currently offer or have offered apprenticeships in the last three years (England ~26%); 17% currently have apprentices on site (joint-highest).
- **Highest anticipated need for upskilling in England** — 68% expect to need new skills in the next 12 months, driven by new products/services and regulation (both 48%).
- **Lowest AI adoption in England** — 11% use AI now and just 6% of non-users plan to adopt; yet NE's AI adopters are the **most committed to embedding it further** (92%, England's highest).
- **Softest labour demand but a skilled-trades pinch** — lowest vacancy incidence (14%), but the **highest skilled-trades skills gap** of any region (4%, statistically significant).
- **High talent under-utilisation** — 49% report over-qualified staff, the second-highest rate in England.

### Data source

**Department for Education — Employer Skills Survey 2024**, England regional data tables (`Employer_Skills_Survey_2024_England_regional_data_tables.xlsx`), fieldwork by IFF Research. Tables used: 1, 3, 4, 13, 117, 134, 139, 156, 159, 160, 163, 204, 222, 224, 225. All figures are embedded in the HTML; the England reference figures are computed in-browser as the employer-count-weighted mean of the nine regions.

### Notes & caveats

- **Geography.** This is the **regional** table pack — its finest geography is the nine Government Office Regions. It carries **no Gateshead, local-authority or combined-authority breakdown**; the North East region is used as the closest proxy. DfE publishes ESS **local-authority-district** estimates separately on [Explore Education Statistics](https://explore-education-statistics.service.gov.uk/find-statistics/employer-skills-survey), which can be slotted into the same dashboard structure for a true Gateshead build.
- The North East has the **smallest unweighted sample** of the nine regions (342 core interviews; ~84–93 on the apprenticeship and T-Level modules), so its figures — especially module-based ones — carry wider margins of error. Small inter-regional differences are indicative, not definitive.
- ESS surveys **establishments (sites)**, not enterprises; percentages are rounded to whole numbers before ranks and the weighted England average are computed.

---

## Build pipeline & monthly refresh

Unlike the other (hand-built) dashboards, the Business Map is **generated** by a Python pipeline and refreshed automatically.

- Tooling lives in [`build/gateshead-business-map/`](build/gateshead-business-map/): `config.py` (study area, vintages, weights, source URLs), `fetch_ch.py` (downloads the CH bulk file to a gitignored cache), `pipeline.py` (fetch → filter to Gateshead → geocode → enrich → score → `.cache/dashboard_data.json`), `render.py` (bakes the self-contained HTML), and `build.py` (orchestrator).
- **Run locally:** `pip install -r requirements.txt` then `python build.py` (use `python build.py --render` to re-render from cached data).
- **Monthly:** the [`.github/workflows/refresh-business-map.yml`](.github/workflows/refresh-business-map.yml) GitHub Action runs on the 6th of each month (after the CH snapshot publishes), rebuilds, and commits the regenerated HTML. **No secrets** are required — every source is keyless.

---

## Adding a new dashboard

1. Identify which **ONS topic** the dashboard's primary data sits under (see [ons.gov.uk](https://www.ons.gov.uk/)).
2. Drop the HTML file into the matching folder:
   - `economy/` — regional accounts, GDP, GVA, prices, public finance
   - `business-industry-trade/` — sectors, business activity, manufacturing, retail, tourism
   - `employment-labour-market/` — jobs, earnings, skills, unemployment _(create folder when first dashboard lands)_
   - `people-population-community/` — population, housing, deprivation, health, education
3. Use **kebab-case** filenames (`some-dashboard.html`), no spaces.
4. Add a row to the catalogue table at the top of this README, and a card on [`index.html`](index.html).
5. For multi-theme dashboards, file under the **source publication's** ONS topic and tag secondary themes in the catalogue description.

## Enabling GitHub Pages

1. In the repo on github.com, go to **Settings → Pages**.
2. Under "Build and deployment", set **Source: Deploy from a branch**, **Branch: main**, **Folder: / (root)**.
3. Save. After a minute or two, the catalogue will be live at `https://nadamsghc.github.io/Economic-Intelligence/`.
