# Dashboard Spec: Colombia Macro 2008-2026

Build guide for Power BI Desktop on Windows. All text below is final English copy, so paste it as written.

Copy the whole `TIA_5/powerbi` folder to Windows first.

## 1. Setup

1. Install Power BI Desktop from the Microsoft Store. Then go to File > Options > Global > Regional Settings: application language English, model language English (United States).
2. File > Options > Current File > Data Load: turn off Auto date/time.
3. File > Options > Current File > Regional Settings: locale for import English (United States). Do this before importing, because the CSVs use decimal points and ISO dates.
4. View > Themes > Browse for themes: load `theme.json`.

## 2. Model

The model is predefined as TMDL in `ColombiaMacro.SemanticModel/definition/`: every import, type, relationship, sort-by and measure below already exists, so refresh and run the checks instead of building it. The steps below document it and serve as a manual fallback. The CSV folder is the `DataFolder` parameter (Transform data > Manage parameters), so change it if the project moves.

Two sets of CSV columns are renamed in the model because their names clash with measures: `DimSeries` `Observations`, `Mean`, `Median`, `StdDev`, `Min`, `Max` become `WindowObservations`, `WindowMean`, `WindowMedian`, `WindowStdDev`, `WindowMin`, `WindowMax`, and `CorrelationSummary[Observations]` becomes `PairedObservations`. Fact `Date` columns and the fact-side keys are hidden, so always slice by `DimDate` and `DimSeries`.

Import every CSV in `data/` except `term_summary_expected.csv`.

| Table | File |
| --- | --- |
| DimDate | `dim_date.csv` |
| DimSeries | `dim_series.csv` |
| FactMonthly | `fact_monthly.csv` |
| FactQuarterly | `fact_quarterly.csv` |
| FactMetricLong | `fact_metric_long.csv` |
| FactOutliers | `fact_outliers.csv` |
| CorrelationSummary | `correlation_summary.csv` |
| CoverageByYear | `coverage_by_year.csv` |
| MissingDataSummary | `missing_data_summary.csv` |

After import, confirm every `Date` column has the Date type and `FactMonthly[InflationYoY]` shows values like 6.03, not 60263.

**Relationships (one to many, single direction)**

- `DimDate[Date]` to `FactMonthly[Date]`, `FactQuarterly[Date]`, `FactMetricLong[Date]`, `FactOutliers[Date]`
- `DimSeries[SeriesKey]` to `FactMetricLong[SeriesKey]`, `FactOutliers[SeriesKey]`, `CoverageByYear[SeriesKey]`, `MissingDataSummary[SeriesKey]`

Leave `CorrelationSummary` and `CoverageByYear[Year]` unrelated to the calendar on purpose. They show full-window facts and shouldn't react to the slicers. Don't mark `DimDate` as a date table, it has one row per month.

**Sort by column**

- `DimDate[TermLabel]` by `DimDate[TermOrder]`
- `DimDate[MonthLabel]` by `DimDate[Date]`
- `DimSeries[SeriesKey]` by `DimSeries[SeriesOrder]`

**Measures.** Create a table named `_Measures` (`Measures` is a reserved name in Analysis Services and fails to load) and add everything in `measures.dax`. Format rates with 2 decimals and a literal `%` suffix (format string `0.00\%`, because the data stores 6.03, not 0.0603), and `TRM Change %` and `COLCAP Change %` as percentages with 1 decimal.

## 3. Global Interaction

Put these on every page, synced with View > Sync slicers:

- `DimDate[TermLabel]`, multi-select list with Select all.
- `DimDate[Date]`, between slider.

Add page navigation buttons. Outlier fences and correlations stay fixed when filtering, which is intentional.

## 4. Visual Rules

| Variable | Color |
| --- | --- |
| Policy Rate | `#2a78d6` blue |
| Inflation YoY | `#eb6834` orange |
| Real GDP Growth | `#1baf7a` aqua |
| Occupation Rate | `#e87ba4` magenta |
| TRM | `#008300` green |
| COLCAP and monthly return | `#6250d6` violet |
| Unemployment Rate | `#e34948` red |
| Outlier markers | `#0b0b0b` ink, in every chart |

- Set each color per series, so a variable keeps its color on every page.
- Every chart has one Y axis, a title stating what it shows, and a unit on the axis.
- Show a legend when a chart has 2 or more series.
- Aqua and magenta have low contrast on the page background, so keep tooltips on and add a text callout with the peak or trough value.
- Keep default tooltips on, they give every point a readable value.

**Page style (from the TIA4 deck)**

- **Header row:** a small uppercase label on the left, such as `PART 2 · DATA QUALITY`, and the page number on the right, such as `02 / 07`. Use Segoe UI 9 pt in secondary ink `#52514e`.
- **Title:** under the header row, the page title in Segoe UI Semibold 20 pt, primary ink.
- **Section labels:** small uppercase text above each visual group, such as `MISSING DATA` or `TREATMENT DECISION`.
- **Accent bar:** a thin rectangle, 4 px, at the left edge of the takeaway box. Use ink `#0b0b0b`, not blue, because blue already means Policy Rate.
- **Takeaway box:** a rectangle filled `#f0efec` behind the takeaway text, labeled `KEY TAKEAWAY`.
- **Decimals:** points everywhere (13.34%, 4,926.66). The TIA4 deck mixed commas and points.

## 5. Pages

Each page has a title, the visuals, and one takeaway text box.

### Page 1: Overview

**Title:** Inflation leads rates, COLCAP moves on events

**Text box (decision):** A Colombian asset manager's investment committee must decide how to adjust exposure to fixed income, Colombian equities and USD across the macro cycle. Data: Banco de la República statistics, January 2008 to July 2026.

**Visuals:** 6 cards with the latest value and the window average as a subtitle.

| Card | Measure | Window average | Unit |
| --- | --- | --- | --- |
| Inflation | `Inflation Latest` | `Inflation Window Avg` | % YoY |
| Policy rate | `Policy Rate Latest` | `Policy Rate Window Avg` | % |
| TRM | `TRM Latest` | `TRM Window Avg` | COP per USD |
| Unemployment | `Unemployment Latest` | `Unemployment Window Avg` | % |
| Real GDP growth | `GDP Growth Latest` | `GDP Growth Window Avg` | % YoY |
| COLCAP | `COLCAP Latest` | `COLCAP Window Avg` | points |

**Text box (recommendation):**

- Use inflation as an early signal for the rate cycle and fixed income positioning. The policy rate tracks inflation most closely about six months later.
- Decide USD exposure separately from COLCAP exposure. The two barely move together.
- Size equity positions for shocks rather than timing them with macro levels. Extreme COLCAP months are event-driven.

### Page 2: Data Quality

**Title:** January 2008 is the first month every series exists

**Number strip (top of page):** section label `OBSERVATIONS IN THE WINDOW: 223 MONTHS, 74 QUARTERS`, then 8 cards in one row. Each card uses the `Observations` measure with a visual filter on one `DimSeries[SeriesKey]`, and the series name as its label. With no filter, the expected values are:

| Card | Value |
| --- | ---: |
| Inflation | 223 |
| Policy Rate | 223 |
| TRM | 223 |
| COLCAP | 223 |
| Returns | 222 |
| Unemployment | 223 |
| Occupation | 223 |
| GDP (quarters) | 74 |

The cards follow the term slicer, so they also show how many months each term covers.

**Visuals:**

- Matrix: rows `DimSeries[SeriesKey]`, columns `CoverageByYear[Year]`, values `CoveragePercent` with a white-to-blue background scale.
- Table: `SeriesKey`, `FirstAvailable`, `ObservedInWindow`, `EmptyInWindow`, `PreWindowGap`, `TreatmentInWindow` from `MissingDataSummary`.
- Matrix: rows `DimSeries[SeriesKey]`, values `Observations`, `Mean`, `Median`, `Std Dev`, `Minimum`, `Maximum`, plus `DimSeries[Unit]`.

**Takeaway:** Earlier gaps come from when each series began, not from lost records. Starting in January 2008 leaves 1 of 1,561 monthly cells empty (0.06%), the first COLCAP return, which cannot exist without a prior month. Nothing was imputed, because filling it would invent data. The impact is one fewer observation for returns and the loss of pre-2008 history. Inflation and the policy rate have means above their medians (4.93% vs 3.97% and 6.11% vs 4.50%), pulled up by the 2022-23 cycle.

### Page 3: Outliers

**Title:** Extreme values are real events, with no entry errors found

**Visuals:**

- Table from `DimSeries`: `SeriesKey`, `Q1`, `Q3`, `IQR`, `LowerFence`, `UpperFence`, `OutlierCount`.
- 6 small line charts, one per series with outliers: Inflation YoY, Unemployment Rate, Occupation Rate, COLCAP, COLCAP Monthly Return, Real GDP Growth. Axis `DimDate[Date]`, values `Series Value` and `Outlier Marker`, with a visual filter on `DimSeries[SeriesKey]`. For `Outlier Marker`, set line width to 0 and show markers in ink.
- Table from `FactOutliers`: `SeriesKey`, `Period`, `Value`, `Direction`, `Classification`, `Treatment`.

**Header counts (top right):** two large numbers, `43` labeled `MONTHLY` and `7` labeled `GDP QUARTERS`.

**Event timeline (top of page):** a horizontal line with 6 dots, one text box under each. Build it from shapes and text boxes.

| Date | Label | Text |
| --- | --- | --- |
| 2008 | Global financial crisis | COLCAP fell 18.98% in October. |
| 2020 | COVID crash | COLCAP fell 27.48% in March, then rose 14.3% in December. |
| 2020-21 | Labor shock | Unemployment peaked at 21.97% in May 2020. GDP fell 16.74% in Q2 2020. |
| 2022 | Election-month sell-off | COLCAP fell 17.49% in June. |
| 2022-23 | Inflation episode | 14 months above the upper fence, peaking at 13.34% in March 2023. |
| 2026 | Record highs | COLCAP rose 19.67% in January, with 5 months above the fence. |

**Text box, labeled `TREATMENT DECISION`:**

1. Not removed automatically. The IQR rule flags candidates, not errors.
2. Matched to documented events. The market and GDP extremes were cross-checked against press and DANE reports.
3. Kept, because they record real episodes. Removing them would understate volatility and erase what the analysis is about.

**Takeaway:** The IQR rule (1.5x) flags 50 observations that cluster in a few episodes: the 2008 crisis, COVID, the 2022 election and the 2022-23 inflation cycle. COLCAP's five level outliers in 2026 are new highs on a rising index, not anomalies. Because they stay in, averages remain sensitive to extremes, so the median is shown beside the mean throughout.

### Page 4: Inflation and Rates

**Title:** The policy rate follows inflation by about six months

**Visuals:**

- Line chart: `DimDate[Date]`, `Inflation YoY` and `Policy Rate`, one % axis.
- Column chart: `DimDate[Date]`, `Real Policy Rate`. Conditional color rules: below 0 `#e34948`, 0 or above `#2a78d6`. Keep the zero baseline.
- Table from `CorrelationSummary`, filtered to `VariableX` Inflation YoY and `VariableY` Policy Rate: `LagMonths`, `Correlation`, `PairedObservations` (rename the header to "Observations").

**Takeaway:** Correlation rises from 0.80 in the same month to 0.88 six months later. In 2022, inflation averaged 10.15% against a 7.46% policy rate, a negative real rate. By 2024 it was 6.63% against 11.33%. This is consistent with a central bank reacting with a delay, but correlation between trending series doesn't prove cause.

### Page 5: FX and Markets

**Title:** The peso and COLCAP are separate decisions

**Visuals:**

- Line chart: `DimDate[Date]`, `TRM Rebased` and `COLCAP Rebased`, one axis, subtitle "January 2008 = 100".
- Column chart: `DimDate[Date]`, `COLCAP Monthly Return`. Conditional color rules: below -11.92 or above 13.45 in ink, otherwise violet.
- Scatter: X `Inflation YoY`, Y `COLCAP Monthly Return`, Values `DimDate[Date]`.
- Table from `CorrelationSummary`, filtered to the TRM and COLCAP pairs: `VariableX`, `VariableY`, `Correlation`.

**Takeaway:** TRM moves moderately with inflation (0.58) but barely with COLCAP (-0.14). Monthly returns show almost no same-month correlation with inflation (-0.05) or the policy rate (0.03). The five extreme months are tied to events: the 2008 crisis, the COVID crash, the vaccine rally, the sell-off around the 2022 election, and the record highs of January 2026.

### Page 6: Real Economy

**Title:** COVID hit hard, and unemployment was back near its 2019 level by 2023

**Visuals:**

- Line chart: `DimDate[Date]`, `Unemployment Rate`.
- Line chart: `DimDate[Date]`, `Occupation Rate`.
- Column chart: `FactQuarterly[QuarterLabel]`, `GDP Growth`. Quarterly on purpose, never interpolated.

**Takeaway:** Unemployment averaged 10.89% in 2019, 16.67% in 2020 and 10.17% in 2023, peaking at 21.97% in May 2020. Occupation fell to 42.50% in April 2020. GDP growth is year-over-year: -16.74% in Q2 2020, then +18.27% in Q2 2021, a rebound measured against a collapsed base.

### Page 7: Presidential Terms

**Title:** Macro conditions by term, shaped by more than the president

**Visuals:**

- Matrix: rows `DimDate[TermLabel]`, values `Inflation YoY`, `Inflation Start`, `Inflation End`, `Policy Rate`, `TRM Change %`, `COLCAP Change %`, `Unemployment Rate`, `GDP Growth`. Rename the headers to include "Avg", "Start" or "End".
- Column chart: `DimDate[TermLabel]`, `TRM Change %`.
- Column chart: `DimDate[TermLabel]`, `COLCAP Change %`.

**Takeaway:** Averages hide direction. Inflation averaged a mild 4.01% under Duque but rose from 3.10% to 10.21%, then averaged 7.97% under Petro while falling from 10.84% to 6.03%. Unemployment was highest under Duque (13.07%), mostly due to COVID. The peso weakened most in Santos II (+52.0% TRM), during the oil price collapse.

**Footer note:** Terms describe when conditions occurred, not who caused them. Banco de la República sets the policy rate independently, and global shocks fall inside several terms. Uribe II covers January 2008 to July 2010 only. Months are assigned to the incoming president from August.

## 6. Reconciliation

Check page 7 against these values before presenting. Full numbers are in `data/term_summary_expected.csv`.

| Term | Months | Inflation avg | Inflation start | Inflation end | Policy avg | TRM change | COLCAP change | Unemployment avg | GDP avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Uribe II (partial) | 31 | 4.81 | 6.00 | 2.24 | 6.70 | -5.5% | 67.7% | 12.01 | 2.62 |
| Santos I | 48 | 2.80 | 2.31 | 2.89 | 3.92 | 2.0% | 1.8% | 10.50 | 5.24 |
| Santos II | 48 | 5.03 | 3.02 | 3.12 | 5.57 | 52.0% | -13.8% | 9.50 | 2.38 |
| Duque | 48 | 4.01 | 3.10 | 10.21 | 3.45 | 47.6% | -16.0% | 13.07 | 3.41 |
| Petro | 48 | 7.97 | 10.84 | 6.03 | 11.12 | -24.4% | 94.7% | 9.65 | 2.19 |

Page 2's statistics matrix should match `data/dim_series.csv` with no filter applied. Page 1 cards should read 6.03%, 12.00%, 3,268.95, 8.10%, 3.37% and 2,392.10.

## 7. Final Checks

- No Spanish anywhere: titles, axes, tooltips, slicers, month names and field names.
- Every chart has a title, axis labels and units.
- Export to PDF as a presentation backup.
