# TIA 5 Plan: Colombia Macro Dashboard (Power BI)

## Current Status

- Linux prep is done: data tables, DAX measures, theme and page-by-page spec are in `TIA_5/powerbi/`.
- The Power BI report is not built yet. The DAX and theme have not been run in Power BI, because Desktop needs Windows.
- Analysis window: January 2008 to July 2026, 223 months and 74 quarters.

## Critical Decisions

| Decision | Reason |
| --- | --- |
| Reuse the TIA4 dataset and analysis | The activity allows continuing with an existing dataset. |
| Window 2008-01 to 2026-07 | First month every indicator exists, through the last full presidential term. |
| Build in Power BI Desktop on the Windows partition | Power BI Desktop has no Linux version. |
| Build visuals by hand, prepare everything else from Linux | Visuals are the graded part and the official MCP server doesn't touch them. |
| Presidential terms as a filter, data stays monthly | Aggregating to terms leaves 5 points per metric and hides the shocks. |
| Term comparison shows start and end, not only averages | Averages hide direction, for example inflation under Duque and Petro. |
| August belongs to the incoming president | Terms change on August 7. Q3 GDP follows its last month. |
| Term slicer replaces event bookmarks | One control covers the main episodes. |
| No imputation | The only empty cell is structural. Filling it invents data. |
| Keep all outliers | They are real events, no entry errors found. |
| No slide deck | The dashboard is the deliverable. Pages 1 to 3 do the job slides would do. |
| Reuse the TIA4 deck's layout ideas, not its numbers | Its timeline, sample strip, treatment steps and style fit pages 2 and 3. Its statistics and outlier counts use full history. |
| No dual-axis charts | Two scales imply relationships that depend on arbitrary axis choices. |
| Standard-library build script | No new dependencies needed. |
| Everything in English | +0.3 on the final grade. |

## Deliverables So Far

| File | Purpose |
| --- | --- |
| `build_powerbi_data.py` | Regenerates every CSV from `data/final` |
| `powerbi/data/*.csv` | Power BI input tables |
| `powerbi/measures.dax` | DAX measures |
| `powerbi/theme.json` | Validated color theme |
| `powerbi/DASHBOARD_SPEC.md` | Setup, model, page-by-page build with final English text, reconciliation values |

## Rubric Coverage

| Criterion | Points | Where it lands |
| --- | ---: | --- |
| Context | 20 | Page 1 |
| Missing data | 20 | Page 2 |
| Outliers | 20 | Page 3 |
| Charts and interpretation | 25 | Pages 4 to 7, plus a written takeaway on every page |
| Time and communication | 15 | 7-minute script below |

## Key Results (2008-01 to 2026-07)

Full detail is in `powerbi/data/`, and the final wording is in the spec.

- **Missing data:** 1 of 1,561 monthly cells is empty (0.06%), the January 2008 return. GDP has none.
- **Outliers:** 50 in total, 43 monthly and 7 GDP. TIA4 had 30 and 5, because it used full history, so its outlier text can't be reused.
- **Rates:** inflation vs policy rate correlates 0.80 in the same month, 0.88 six months later, 0.76 twelve months later.
- **Markets:** TRM vs COLCAP -0.14. Monthly returns vs inflation -0.05 and vs policy rate 0.03.
- **Terms:** inflation rose from 3.10% to 10.21% under Duque and fell from 10.84% to 6.03% under Petro.

## Presentation (7 Minutes, From the Dashboard)

No slides. Keep a PDF export as backup in case the live demo fails. The professor can choose who presents which part, so every group member has to know all of it.

Default split, swap freely:

| Member | Pages | Time | Length |
| --- | --- | --- | --- |
| Juan Sebastian Delgado | 1 to 3: context, data quality, outliers | 0:00 to 2:30 | 2:30 |
| Breinner Fernely Silva | 4 and 5: rates, FX and markets | 2:30 to 4:25 | 1:55 |
| Brayan Stid Jimenez | 6, 7 and back to 1: real economy, terms, recommendation | 4:25 to 6:40 | 2:15 |

| Time | Page | Message | Click |
| --- | --- | --- | --- |
| 0:00 to 0:40 | 1 Overview | The decision, the data, the 4 questions | |
| 0:40 to 1:35 | 2 Data Quality | Why 2008, one empty cell, no imputation and its impact | |
| 1:35 to 2:30 | 3 Outliers | IQR method, what the extremes are, why they stay | |
| 2:30 to 3:35 | 4 Inflation and Rates | Rates follow inflation with a delay | Duque + Petro |
| 3:35 to 4:25 | 5 FX and Markets | FX and COLCAP are separate decisions | Uribe II |
| 4:25 to 5:15 | 6 Real Economy | COVID shock and recovery | Duque |
| 5:15 to 6:00 | 7 Terms | Conditions differ, attribution is limited | All |
| 6:00 to 6:40 | 1 Overview | Recommendation to the committee | |
| 6:40 to 7:00 | | Buffer | |

Likely questions to rehearse:

- Why not impute?
- Why did the outlier count change from TIA4?
- Why does IQR flag COLCAP in 2026?
- Is the inflation and rate correlation causal?
- Why is GDP not monthly?
- Are you blaming presidents for these outcomes?

## Open Items

- Confirm with the professor: reuse of the TIA4 analysis, Banco de la República as a source (the activity links to datos abiertos Colombia), and the time limit (7 minutes in the activity, 8 in the rubric).
- Find a source for what drove COLCAP's +19.67% in January 2026. Press confirms record highs that month, so it isn't an entry error, but no January-specific cause was found.

## Outlier Evidence

| Item | Finding | Source |
| --- | --- | --- |
| GDP definition | Year-over-year and seasonally adjusted. The dataset's 2022-Q2 value of 12.55% matches DANE's reported 12.6%. | [DANE press release](https://www.dane.gov.co/files/investigaciones/boletines/pib/cp_PIB_IItrim22.pdf) |
| 2022-Q2 GDP | Classified as post-COVID rebound. A strike-related base effect could not be quantified. | [La República](https://www.larepublica.co/economia/crecimiento-del-pib-para-el-segundo-trimestre-del-ano-fue-de-12-6-segun-el-dane-3425670) |
| 2022-06 return (-17.49%) | Press reports a 17.5% fall in June, with a sharp drop after the election. | [Valora Analitik](https://www.valoraanalitik.com/?p=182152), [Bloomberg Línea](https://www.bloomberglinea.com/2022/06/21/bolsa-de-colombia-es-la-que-mas-cae-a-nivel-mundial-tras-triunfo-de-petro/) |
| 2020-12 return (+14.3%) | Press reports the same monthly rise, and vaccine news brought inflows. | [Valora Analitik](https://www.valoraanalitik.com/bolsa-de-colombia-cerr-2020-con-altibajos-en-medio-de-la-crisis-colcap-cay-13-5/) |
| 2026-01 COLCAP | All-time highs reported in January 2026. | [Trading Economics](https://tradingeconomics.com/colombia/stock-market/news/518814) |
| Term dates | De la Espriella took office on August 7, 2026, ending Petro's term. | [AP](https://www.djournal.com/news/nation-world/colombia-inaugurates-its-new-president-in-cali-in-photos/article_6c210a63-0704-51a8-b1b2-6c87da2780e1.html) |

## Next Steps

1. Copy the whole `ColombiaEconomicAnalysis` project folder to Windows, so this plan, the spec and the data travel together. The repo has no remote and the TIA5 files are uncommitted, so copy the folder rather than relying on git.
2. Install Power BI Desktop from the Microsoft Store, which keeps it updated.
3. Follow `powerbi/DASHBOARD_SPEC.md`, starting with page 4 to settle the visual style. Save the report as `TIA_5/powerbi/ColombiaMacro.pbix`.
4. Reconcile page 7 and the page 1 cards against the spec.
5. Rehearse with a timer and export the PDF.

**Resuming with Claude Code on Windows:** memory doesn't carry across machines. Start the session by asking Claude to read `TIA_5/PLAN.md` and `TIA_5/powerbi/DASHBOARD_SPEC.md`. For DAX or theme errors, paste the exact error message.

## Lessons Learned

- Statistics on full history mix decades that each series doesn't share. Fix the window before computing anything.
- IQR depends on the window: narrowing it changes which points are outliers.
- IQR on a trending level series flags new highs. Use returns to look for market anomalies.
- Period averages hide direction on trending series. Show start and end values too.
- Ending the window on a term boundary removed a one-month term and two empty cells.
