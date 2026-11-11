# Databricks notebook source
# Power BI table FactMetricLong: every series in long format (one row per series and period),
# flagged with the IQR outlier rule.
# Output: TIA_5/powerbi/data/fact_metric_long.csv
import pandas as pd

FINAL_DATA_FOLDER = "../../data/final"
POWERBI_DATA_FOLDER = "../../TIA_5/powerbi/data"

WINDOW_START = pd.Timestamp("2008-01-01")
WINDOW_END = pd.Timestamp("2026-07-01")


def round_values(values: pd.Series, digits: int) -> pd.Series:
    """Python's round() on each value. Empty cells stay empty."""
    return values.map(lambda value: round(value, digits))

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

# LONG TABLE
fact_metric_long = pd.DataFrame({
    "Date": in_window["Date"].dt.strftime("%Y-%m-%d"),
    "SeriesKey": in_window["SeriesKey"],
    "Value": round_values(in_window["Value"], 4),
    "IsOutlier": in_window["IsOutlier"],
})

fact_metric_long.groupby("SeriesKey", sort=False)["IsOutlier"].agg(["count", "sum"])

# COMMAND ----------

# EXPORTATION
fact_metric_long.to_csv(f"{POWERBI_DATA_FOLDER}/fact_metric_long.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
