# Databricks notebook source
# Power BI table MissingDataSummary: per series, when it starts, how many cells the window expects,
# how many are empty, and why.
# Output: TIA_5/powerbi/data/missing_data_summary.csv
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

# EXPECTED PERIODS IN THE WINDOW
# Monthly series expect every month; GDP expects every quarter published inside the window.
window_months = len(pd.date_range(WINDOW_START, WINDOW_END, freq="MS"))
window_quarters = int(quarterly_long["Date"].between(WINDOW_START, WINDOW_END).sum())

print(f"Months in the window: {window_months}, quarters: {window_quarters}")

# COMMAND ----------

# MISSING DATA PER SERIES
NO_EMPTY_CELLS = "No empty cells in the window."
SERIES_NOTES = [
    ("Inflation YoY", "Available since 1955, no gap in the window.", NO_EMPTY_CELLS),
    ("Policy Rate", "The series used starts in April 1999.", NO_EMPTY_CELLS),
    ("TRM", "The series starts in late 1991, when the TRM was established.", NO_EMPTY_CELLS),
    ("COLCAP", "The index starts in January 2008.", NO_EMPTY_CELLS),
    ("COLCAP Monthly Return", "The index starts in January 2008.",
     "January 2008 stays empty: a return needs a prior month, which predates the index."),
    ("Unemployment Rate", "The labor series starts in January 2001.", NO_EMPTY_CELLS),
    ("Occupation Rate", "The labor series starts in January 2001.", NO_EMPTY_CELLS),
    ("Real GDP Growth", "The quarterly series starts in 2006.", NO_EMPTY_CELLS),
]

first_available = observations.groupby("SeriesKey")["Date"].min()
observed_in_window = in_window.groupby("SeriesKey").size()

rows = []
for key, pre_window_gap, treatment in SERIES_NOTES:
    expected = window_quarters if key == "Real GDP Growth" else window_months
    observed = int(observed_in_window[key])
    rows.append({
        "SeriesKey": key,
        "FirstAvailable": period_label(key, first_available[key]),
        "ExpectedInWindow": expected,
        "ObservedInWindow": observed,
        "EmptyInWindow": expected - observed,
        "PreWindowGap": pre_window_gap,
        "TreatmentInWindow": treatment,
    })
missing_data_summary = pd.DataFrame(rows)

missing_data_summary

# COMMAND ----------

# EXPORTATION
missing_data_summary.to_csv(f"{POWERBI_DATA_FOLDER}/missing_data_summary.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
