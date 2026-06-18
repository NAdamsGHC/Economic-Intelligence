# Economic Intelligence — Gateshead & the North East

Interactive HTML dashboards exploring open ONS datasets for **Gateshead borough** and the wider **North East of England**. Catalogued by ONS topic.

Each dashboard is a single self-contained HTML file — open it directly in any modern browser, or browse the live versions via [GitHub Pages](#enabling-github-pages) once enabled. The site's landing page is [`index.html`](index.html).

## Catalogue

| ONS topic | Dashboard | Theme | Size |
|---|---|---|---|
| **Economy** | [GDHI 2010–2023](economy/gdhi.html) | Gross Disposable Household Income — UK regional accounts, LSOA choropleth, inequality | 9.1 MB |
| **Business, industry and trade** | [Creative Industries (CCIS)](business-industry-trade/creative-industries.html) | DCMS creative sector businesses / employment / GVA across the 7 NECA local authorities | 92 KB |
| **People, population and community** | [Gateshead Built-Up Areas](people-population-community/built-up-areas.html) | Population, house prices, employment, visitor economy for 7 BUAs inside Gateshead | 1.35 MB |
| **People, population and community** | [Gateshead Deprivation (IMD 2025)](people-population-community/indices-of-deprivation-2025.html) | Indices of Deprivation 2025 — 22 wards & 126 neighbourhoods ranked, domain ranks, social-value targeting matrix | 0.66 MB |
| **Employment and labour market** | _no dashboards yet_ | | |

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
