# Databricks notebook source
# Evidence table CorrelationSummary: the Pearson correlations quoted on the dashboard. Not loaded into Power BI.
# A lag of N months pairs variable X in month t with variable Y in month t + N.
# Output: TIA_5/powerbi/data/correlation_summary.csv
import pandas as pd

FINAL_DATA_FOLDER = "../../data/final"
POWERBI_DATA_FOLDER = "../../TIA_5/powerbi/data"

WINDOW_START = pd.Timestamp("2008-01-01")
WINDOW_END = pd.Timestamp("2026-07-01")

# COMMAND ----------

# SOURCE DATA: every non-empty observation, one row per series and period
MONTHLY_COLUMNS = {
    "InflationYOY": "Inflation YoY",
    "PolicyRate": "Policy Rate",
    "TRMAvg": "TRM",
    "ColcapIndex": "COLCAP",
    "MonthlyReturn": "COLCAP Monthly Return",
    "UnemploymentRate": "Unemployment Rate",
    "OccupationRate": "Occupation Rate",
}
SERIES_ORDER = {key: order for order, key in enumerate([*MONTHLY_COLUMNS.values(), "Real GDP Growth"], start=1)}

monthly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_monthly.csv")
monthly_long = (
    monthly_set
    .assign(Date=lambda df: pd.to_datetime(df["MonthlyDate"], format="%Y-%m"))
    .melt(id_vars="Date", value_vars=list(MONTHLY_COLUMNS), var_name="SourceColumn", value_name="Value")
    .assign(SeriesKey=lambda df: df["SourceColumn"].map(MONTHLY_COLUMNS))
)

# Quarters are keyed to their last month so they join the monthly calendar (2008-Q1 -> 2008-03-01)
quarterly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_quarterly.csv")
quarterly_long = pd.DataFrame({
    "Date": pd.to_datetime(pd.DataFrame({
        "year": quarterly_set["Quarter"].str[:4].astype(int),
        "month": quarterly_set["Quarter"].str[-1].astype(int) * 3,
        "day": 1,
    })),
    "SeriesKey": "Real GDP Growth",
    "Value": quarterly_set["RealGDPGrowth"],
})

observations = (
    pd.concat([monthly_long[["Date", "SeriesKey", "Value"]], quarterly_long], ignore_index=True)
    .dropna(subset=["Value"])
    .assign(SeriesOrder=lambda df: df["SeriesKey"].map(SERIES_ORDER))
    .sort_values(["SeriesOrder", "Date"], ignore_index=True)
)
in_window = observations[observations["Date"].between(WINDOW_START, WINDOW_END)].reset_index(drop=True)

# One column per series, one row per month
wide = in_window.pivot(index="Date", columns="SeriesKey", values="Value")

wide.info()

# COMMAND ----------

# CORRELATIONS
CORRELATION_PAIRS = [
    ("Inflation YoY", "Policy Rate", 0),
    ("Inflation YoY", "Policy Rate", 3),
    ("Inflation YoY", "Policy Rate", 6),
    ("Inflation YoY", "Policy Rate", 9),
    ("Inflation YoY", "Policy Rate", 12),
    ("Policy Rate", "Inflation YoY", 12),
    ("TRM", "Inflation YoY", 0),
    ("TRM", "COLCAP", 0),
    ("Policy Rate", "COLCAP", 0),
    ("Inflation YoY", "COLCAP Monthly Return", 0),
    ("Policy Rate", "COLCAP Monthly Return", 0),
    ("Unemployment Rate", "Occupation Rate", 0),
]

rows = []
for x_key, y_key, lag in CORRELATION_PAIRS:
    x_values = wide[x_key].dropna().rename("X")
    # Shift Y back by the lag so that Y(t + lag) lines up with X(t); only months inside the window pair up
    y_later = wide[y_key].dropna().rename("Y")
    y_later.index = y_later.index - pd.DateOffset(months=lag)
    matched = pd.concat([x_values, y_later], axis=1, join="inner").dropna()
    rows.append({
        "VariableX": x_key,
        "VariableY": y_key,
        "LagMonths": lag,
        "Correlation": round(matched["X"].corr(matched["Y"]), 2),
        "Observations": len(matched),
    })
correlation_summary = pd.DataFrame(rows)

correlation_summary

# COMMAND ----------

# EXPORTATION
correlation_summary.to_csv(f"{POWERBI_DATA_FOLDER}/correlation_summary.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
