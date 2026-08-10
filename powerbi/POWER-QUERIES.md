# Power Queries — Gateshead Economic Intelligence

Nine queries against the NOMIS open API. Keyless, free, anonymous.

**To use each one:** Power BI Desktop → Home → Transform data → New Source →
Blank Query → Home → Advanced Editor → select all, paste, Done. Then rename the
query to the heading name exactly (the report visuals bind to these names).

When prompted for credentials choose **Anonymous**, and privacy level **Public**.

---

## Geography

```m
let
    // Comparator pools as an explicit dimension. "North East" is ambiguous:
    // the Combined Authority is seven authorities, the ITL1 region is twelve.
    // Slice by the flag you mean; never by a text label.
    Source = #table(
        type table [
            #"Area code" = text, #"Area name" = text,
            #"Is Gateshead" = Int64.Type, #"In NECA 7" = Int64.Type,
            #"In North East 12" = Int64.Type
        ],
        {
        {"E08000037", "Gateshead", 1, 1, 1},
        {"E06000047", "County Durham", 0, 1, 1},
        {"E08000021", "Newcastle upon Tyne", 0, 1, 1},
        {"E08000022", "North Tyneside", 0, 1, 1},
        {"E06000057", "Northumberland", 0, 1, 1},
        {"E08000023", "South Tyneside", 0, 1, 1},
        {"E08000024", "Sunderland", 0, 1, 1},
        {"E06000005", "Darlington", 0, 0, 1},
        {"E06000001", "Hartlepool", 0, 0, 1},
        {"E06000002", "Middlesbrough", 0, 0, 1},
        {"E06000003", "Redcar and Cleveland", 0, 0, 1},
        {"E06000004", "Stockton-on-Tees", 0, 0, 1},
        {"E92000001", "England", 0, 0, 0}
        }
    )
in
    Source
```

## Dataset freshness

```m
let
    // The point of this table. NOMIS publishes release metadata per dataset at
    // the .def.sdmx.json endpoint: Status, FirstReleased and LastUpdated.
    // Verified working 10 Aug 2026.
    //
    // Note that "last updated" and "newest period in the data" are different
    // things. A dataset can be actively maintained while its most recent data
    // period is two years old - the ONS compendium's labour market rates did
    // exactly that. Both are surfaced; the gap between them is the signal.
    Registry = #table(
        type table [#"Dataset ID" = text, #"Dataset" = text],
        {
            {"NM_17_5", "Annual Population Survey - labour market and qualifications"},
            {"NM_162_1", "Claimant count"},
            {"NM_30_1", "ASHE - resident analysis"},
            {"NM_99_1", "ASHE - workplace analysis"},
            {"NM_189_1", "Business Register and Employment Survey (open access)"},
            {"NM_142_1", "UK Business Counts - enterprises"},
            {"NM_31_1", "Mid-year population estimates"},
            {"NM_2006_1", "Subnational population projections"}
        }
    ),
    Fetch = (id as text) as record =>
        let
            Raw  = Json.Document(
                Web.Contents(
                    "https://www.nomisweb.co.uk",
                    [RelativePath = "api/v01/dataset/" & id & ".def.sdmx.json"]
                )
            ),
            KF   = Raw[structure][keyfamilies][keyfamily],
            One  = if Value.Is(KF, type list) then KF{0} else KF,
            Anns = try One[annotations][annotation] otherwise {},
            Get  = (title as text) as nullable text =>
                let
                    Hit = List.Select(
                        Anns,
                        each Record.FieldOrDefault(_, "annotationtitle", "") = title
                    )
                in
                    if List.Count(Hit) > 0
                    then Record.FieldOrDefault(Hit{0}, "annotationtext", null)
                    else null
        in
            [
                Status        = Get("Status"),
                LastUpdatedRaw= Get("LastUpdated"),
                FirstReleased = Get("FirstReleased")
            ],
    WithMeta = Table.AddColumn(Registry, "Meta", each Fetch([#"Dataset ID"])),
    Expanded = Table.ExpandRecordColumn(
        WithMeta, "Meta",
        {"Status", "LastUpdatedRaw", "FirstReleased"},
        {"Status", "LastUpdatedRaw", "First released"}
    ),
    LastUpd  = Table.AddColumn(
        Expanded, "Last updated",
        each try DateTime.FromText(
            Text.Replace(Text.From([LastUpdatedRaw]), " ", "T")
        ) otherwise null,
        type nullable datetime
    ),
    Days = Table.AddColumn(
        LastUpd, "Days since update",
        each try Duration.Days(DateTime.LocalNow() - [#"Last updated"])
             otherwise null,
        Int64.Type
    ),
    Band = Table.AddColumn(
        Days, "Freshness",
        each if [#"Days since update"] = null then "Unknown"
             else if [#"Days since update"] <= 31  then "1 - Within a month"
             else if [#"Days since update"] <= 92  then "2 - Within a quarter"
             else if [#"Days since update"] <= 366 then "3 - Within a year"
             else "4 - Over a year old",
        type text
    ),
    Clean = Table.RemoveColumns(Band, {"LastUpdatedRaw"})
in
    Clean
```

## Labour market

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    // Survey estimates. The confidence interval is pulled alongside every rate so a visual can show it - differences inside the interval are not real.
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_17_5.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS4-latest",
            #"variable" = "18,45,83",
            #"measures" = "20599,21001,21002,21003",
            #"select" = "date_name,geography_name,geography_code,variable_name,measures_name,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```

## Claimant count

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    // NOT seasonally adjusted - only same-month comparisons are meaningful. Every dimension is pinned; unpinned this returns well over 25,000 rows.
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_162_1.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS36-latest",
            #"gender" = "0",
            #"age" = "0",
            #"measure" = "1",
            #"measures" = "20100",
            #"select" = "date_name,geography_name,geography_code,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```

## Earnings - resident

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    // sex 5/6/7 = Male/Female/Total; pay 1/7 = weekly/annual gross; item 2 = median; measures 20100/20701 = value/confidence interval (%).
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_30_1.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS2-latest",
            #"sex" = "5,6,7",
            #"item" = "2",
            #"pay" = "1,7",
            #"measures" = "20100,20701",
            #"select" = "date_name,geography_name,geography_code,sex_name,pay_name,measures_name,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```

## Earnings - workplace

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_99_1.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS2-latest",
            #"sex" = "5,6,7",
            #"item" = "2",
            #"pay" = "1,7",
            #"measures" = "20100,20701",
            #"select" = "date_name,geography_name,geography_code,sex_name,pay_name,measures_name,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```

## BRES employment

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    // employment_status 1 = Employees (NOT 4 = Employment, which includes working proprietors). Open-access BRES is disclosure-rounded: summing these sections gives Gateshead 93,130 for 2024, while the API's own 'Total' industry code returns 95,000. They are rounded independently. This model uses the section sum throughout and never shows both.
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_189_1.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS4-latest",
            #"industry" = "150994945,150994946,150994947,150994948,150994949,150994950,150994951,150994952,150994953,150994954,150994955,150994956,150994957,150994958,150994959,150994960,150994961,150994962,150994963,150994964,150994965",
            #"employment_status" = "1",
            #"measure" = "1",
            #"measures" = "20100",
            #"select" = "date_name,geography_name,geography_code,industry_name,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```

## Business counts

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    // Enterprises, all industries, all sizebands, all legal statuses.
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_142_1.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS4-latest",
            #"industry" = "37748736",
            #"employment_sizeband" = "0",
            #"legal_status" = "0",
            #"measures" = "20100",
            #"select" = "date_name,geography_name,geography_code,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```

## Population

```m
let
    // ---------------------------------------------------------------
    // Source: NOMIS open API (https://www.nomisweb.co.uk/api/v01/).
    // Keyless and free. Anonymous requests cap at 25,000 rows, so every
    // query below pins its dimensions rather than relying on defaults -
    // an unpinned dimension returns the cross-product of all its options.
    // ---------------------------------------------------------------
    // age 0 = All ages, 22 = Aged 16-64. The 16-64 figure is the denominator for the claimant rate and every per-working-age measure.
    Source = Csv.Document(
        Web.Contents(
            "https://www.nomisweb.co.uk",
            [
                RelativePath = "api/v01/dataset/NM_31_1.data.csv",
                Query = [
            #"geography" = "E08000037,E06000047,E08000021,E08000022,E06000057,E08000023,E08000024,E06000005,E06000001,E06000002,E06000003,E06000004,E92000001",
            #"date" = "latestMINUS4-latest",
            #"sex" = "7",
            #"age" = "0,22",
            #"measures" = "20100",
            #"select" = "date_name,geography_name,geography_code,age_name,obs_value"
                ]
            ]
        ),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Value   = Table.TransformColumns(
        Headers,
        {{"OBS_VALUE", each try Number.FromText(Text.From(_)) otherwise null,
          type nullable number}}
    )
in
    Value
```
