# Databricks notebook source
# Power BI table FactMonthly: the monthly indicators in the analysis window, plus derived columns.
# Output: TIA_5/powerbi/data/fact_monthly.csv
import pandas as pd

FINAL_DATA_FOLDER = "../../data/final"
POWERBI_DATA_FOLDER = "../../TIA_5/powerbi/data"

WINDOW_START = pd.Timestamp("2008-01-01")
WINDOW_END = pd.Timestamp("2026-07-01")


def round_values(values: pd.Series, digits: int) -> pd.Series:
    """Python's round() on each value. Empty cells stay empty."""
    return values.map(lambda value: round(value, digits))

# COMMAND ----------

# MONTHLY SET IN THE WINDOW
monthly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_monthly.csv")
window = (
    monthly_set
    .assign(Date=lambda df: pd.to_datetime(df["MonthlyDate"], format="%Y-%m"))
    .loc[lambda df: df["Date"].between(WINDOW_START, WINDOW_END)]
    .reset_index(drop=True)
)
# January 2008 is the base month for the rebased series
base = window.iloc[0]
assert base["Date"] == WINDOW_START

window.info()

# COMMAND ----------

# DERIVED COLUMNS
# Real policy rate = policy rate minus inflation. Rebased series: January 2008 = 100.
fact_monthly = pd.DataFrame({
    "Date": window["Date"].dt.strftime("%Y-%m-%d"),
    "InflationYoY": round_values(window["InflationYOY"], 4),
    "PolicyRate": round_values(window["PolicyRate"], 4),
    "RealPolicyRate": round_values(window["PolicyRate"] - window["InflationYOY"], 4),
    "TrmAverage": round_values(window["TRMAvg"], 2),
    "TrmRebased": round_values(100 * window["TRMAvg"] / base["TRMAvg"], 2),
    "ColcapIndex": round_values(window["ColcapIndex"], 2),
    "ColcapRebased": round_values(100 * window["ColcapIndex"] / base["ColcapIndex"], 2),
    # January 2008 stays empty: a return needs the previous month, which predates the index
    "ColcapMonthlyReturn": round_values(window["MonthlyReturn"], 4),
    "UnemploymentRate": round_values(window["UnemploymentRate"], 4),
    "OccupationRate": round_values(window["OccupationRate"], 4),
})

fact_monthly.info()

# COMMAND ----------

# EXPORTATION
fact_monthly.to_csv(f"{POWERBI_DATA_FOLDER}/fact_monthly.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
