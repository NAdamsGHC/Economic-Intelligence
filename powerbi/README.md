# Power BI — Gateshead Economic Intelligence

**Download one file: `Gateshead-Economic-Intelligence.pbit`.** Nothing else here
is needed to open it.

1. Download it, double-click it. Power BI Desktop builds the model and runs the
   queries.
2. When prompted, choose **Anonymous** access and privacy level **Public** —
   the only data source is the NOMIS open API, which is keyless and free.
3. **File → Save As → .pbix.** That is the working draft file from then on.

No Power BI Service, no workspace, no gateway, no scheduled refresh, no
licensing. Press Refresh in Desktop when you want current numbers.

## Why a .pbit and not a .pbix

A .pbix stores its data model in a binary Analysis Services part that only
Power BI Desktop can write, so it cannot be generated outside Desktop. A .pbit
holds the same model as plain JSON and carries no data — opening it and saving
produces the .pbix.

## What's in it

| Page | What it answers |
|---|---|
| Data freshness | Which datasets NOMIS most recently released, and which have gone stale |
| Labour market | APS employment, activity and inactivity rates with confidence intervals; claimant count monthly |
| Earnings | ASHE median pay, resident and workplace, weekly and annual, by sex |
| Business base | BRES employee jobs by SIC section, active enterprises, population |

Nine tables, filtered to Gateshead, the six other NECA authorities, the five
Tees Valley authorities and England.

## Caveats worth knowing before you build on it

- **Not yet opened in Power BI Desktop.** The package structure, TMSL and report
  JSON were validated programmatically and every query was run against the live
  API, but no visual has been seen rendering. A chart that opens empty is a
  re-bind, not a rebuild.
- **BRES totals don't reconcile by design.** Open-access BRES is disclosure-
  rounded; summing the 21 SIC sections gives 93,130 employee jobs for Gateshead
  2024 against 95,000 from the API's own `Total` code. The model uses the
  section sum throughout — don't mix the two on one page.
- **"North East" means at least two different pools.** NECA is seven
  authorities, the ITL1 region is twelve. The `Geography` table carries explicit
  flags — slice by the flag, never a text label, and say which pool in the title.
- **Survey estimates carry confidence intervals and they are in the data.**
  Gateshead's APS rates carry margins of about ±4 percentage points; smaller
  differences are not real.
- **The claimant count is not seasonally adjusted.** Only same-month
  comparisons carry meaning.

The generating source (`build_pbip.py`, the .pbip project and the standalone
`.pq` query files) lives outside this repo in the working folder. Edit there and
regenerate — changes made to generated output are lost on the next build.
