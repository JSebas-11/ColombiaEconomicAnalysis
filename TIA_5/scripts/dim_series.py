# Databricks notebook source
# Power BI table DimSeries: one row per series with its unit, descriptive statistics and IQR fences.
# Output: TIA_5/powerbi/data/dim_series.csv
import pandas as pd

FINAL_DATA_FOLDER = "../../data/final"
POWERBI_DATA_FOLDER = "../../TIA_5/powerbi/data"

WINDOW_START = pd.Timestamp("2008-01-01")
WINDOW_END = pd.Timestamp("2026-07-01")

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def period_label(series_key: str, date: pd.Timestamp) -> str:
    """Quarter label for GDP (2020-Q2), month label for everything else (Nov 2020)."""
    if series_key == "Real GDP Growth":
        return f"{date.year}-Q{(date.month - 1) // 3 + 1}"
    return f"{MONTH_NAMES[date.month - 1]} {date.year}"

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

in_window.info()

# COMMAND ----------

# IQR FENCES: 1.5 x IQR beyond the quartiles, computed per series on the analysis window
fences = in_window.groupby("SeriesKey")["Value"].quantile([0.25, 0.75]).unstack()
fences.columns = ["Q1", "Q3"]
fences = fences.assign(
    IQR=lambda df: df["Q3"] - df["Q1"],
    LowerFence=lambda df: df["Q1"] - 1.5 * df["IQR"],
    UpperFence=lambda df: df["Q3"] + 1.5 * df["IQR"],
)
in_window = in_window.join(fences, on="SeriesKey")
in_window["IsOutlier"] = (
    (in_window["Value"] < in_window["LowerFence"]) | (in_window["Value"] > in_window["UpperFence"])
).astype(int)

fences

# COMMAND ----------

# DESCRIPTIVE STATISTICS PER SERIES
SERIES_INFO = [
    ("Inflation YoY", "%", "Monthly"),
    ("Policy Rate", "%", "Monthly"),
    ("TRM", "COP per USD", "Monthly"),
    ("COLCAP", "Index points", "Monthly"),
    ("COLCAP Monthly Return", "%", "Monthly"),
    ("Unemployment Rate", "%", "Monthly"),
    ("Occupation Rate", "%", "Monthly"),
    ("Real GDP Growth", "%", "Quarterly"),
]

rows = []
for order, (key, unit, frequency) in enumerate(SERIES_INFO, start=1):
    series = in_window[in_window["SeriesKey"] == key]
    values = series["Value"]
    fence = fences.loc[key]
    lowest = series.loc[values.idxmin(), "Date"]   # first period with the minimum
    highest = series.loc[values.idxmax(), "Date"]  # first period with the maximum
    outliers = int(series["IsOutlier"].sum())
    rows.append({
        "SeriesKey": key,
        "SeriesOrder": order,
        "Unit": unit,
        "Frequency": frequency,
        "Observations": len(values),
        "Mean": round(values.mean(), 2),
        "Median": round(values.median(), 2),
        "StdDev": round(values.std(), 2),
        "Min": round(values.min(), 2),
        "MinPeriod": period_label(key, lowest),
        "Max": round(values.max(), 2),
        "MaxPeriod": period_label(key, highest),
        "Q1": round(fence["Q1"], 2),
        "Q3": round(fence["Q3"], 2),
        "IQR": round(fence["IQR"], 2),
        "LowerFence": round(fence["LowerFence"], 2),
        "UpperFence": round(fence["UpperFence"], 2),
        "OutlierCount": outliers,
        "OutlierPercent": round(100 * outliers / len(values), 2),
    })
dim_series = pd.DataFrame(rows)

dim_series

# COMMAND ----------

# EXPORTATION
dim_series.to_csv(f"{POWERBI_DATA_FOLDER}/dim_series.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
