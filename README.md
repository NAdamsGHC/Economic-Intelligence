# UK GDHI Dashboard — Gateshead & the North East

An interactive dashboard exploring ONS estimates of **Gross Disposable Household Income (GDHI)** for small UK geographic areas, 2010-2023, with a focus on **Gateshead borough** and the **North East of England**.

## 👉 Live dashboard

Once GitHub Pages is enabled on this repo, the dashboard is at:

**https://&lt;your-github-username&gt;.github.io/&lt;this-repo-name&gt;/**

Or just open `index.html` directly in any modern browser — the file is self-contained.

## What's in it

- **3,427 areas** across 18 geography types — parliamentary constituencies, towns, travel-to-work areas, integrated care boards, health boards, MSOAs, plus derived **Local Authority District** and **ITL region** aggregates and a UK national total
- **14 years** of data (2010-2023)
- **17 income components** per area (compensation of employees, operating surplus, property income, taxes, social benefits, transfers, etc.)
- **Specialty zones** from the ONS dataset — Central Activities Zone (central London), Northern Isle of Dogs, OPDC, Clyde River Region, Clyde River Gateway, Highlands & Islands, West Midlands Metro

## Tabs

| Tab | What it shows |
|---|---|
| **Gateshead** | Borough headline (£3.81bn in 2023, +54.2% since 2010), the four Westminster constituencies, share-of-borough by constituency, full income-component breakdown, all 27 Gateshead MSOAs, comparison with neighbouring boroughs |
| **North East** | All NE LADs / constituencies / towns / TTWAs / MSOAs ranked and tabled, switchable by geography type and sort metric |
| **UK Context** | UK total, 12 ITL regions ranked, indexed growth trajectories, where Gateshead sits in the 350-LAD league table |
| **Specialty Areas** | CAZ, NIOD, OPDC, Clyde, Highlands & Islands, West Midlands Metro — each compared with Gateshead and the UK total on an indexed basis |
| **Compare** | Pick any combination of UK areas. Switch component, switch between £m / indexed-to-2010 / YoY %. Presets for Gateshead, NE big cities, NE boroughs, and UK regions |
| **Explore** | Drill into any single area's full 17-component breakdown |

## Data source

[ONS — GDHI estimates for other geographic areas, 2010 to 2023](https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome) (statistics in development, published 28 May 2026).

GDHI is the amount of money that all individuals in the household sector have available for spending or saving after direct and indirect taxes and direct benefits. The estimates apportion LSOA / Data Zone / SOA building blocks to wider geographies. All values are **£ millions in current prices** (not chained-volume measures, not per-resident).

## Notes & caveats

- Current-price growth combines real growth and inflation — don't read +83% UK growth since 2010 as a real-terms gain.
- Don't sum across geography types (e.g. PCs + Towns). They overlap.
- The four Gateshead-named Westminster constituencies extend into Consett (County Durham) and Washington (Sunderland borough), so their sum (£7.33bn) overstates Gateshead borough. The proper borough figure (£3.81bn) is the LAD aggregate, derived from summing all 27 Gateshead MSOAs.
- The UK total in this dataset excludes Northern Ireland (NI uses a different geography that isn't apportioned in the same way for these "other geographic areas" tables).

## How to enable GitHub Pages

1. Push this repo to GitHub.
2. In the repo on github.com, go to **Settings → Pages**.
3. Under "Build and deployment", set **Source: Deploy from a branch**, **Branch: main**, **Folder: / (root)**.
4. Save. After a minute or two, your dashboard will be live at `https://<your-username>.github.io/<this-repo-name>/`.
