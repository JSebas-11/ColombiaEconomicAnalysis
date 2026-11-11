# Databricks notebook source
# Evidence table FactOutliers: the 50 IQR outliers with the event each one matches. Not loaded into Power BI.
# Output: TIA_5/powerbi/data/fact_outliers.csv
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

# EVENT CLASSIFICATION
# Each outlier was matched to a documented event (press and DANE reports). A rule covers one series
# over a period range; an outlier with no matching rule stops the script.
OUTLIER_RULES = [
    ("Inflation YoY", "2022-01-01", "2023-12-01", "2022-23 inflation episode"),
    ("Occupation Rate", "2020-03-01", "2021-12-01", "COVID-19 labor shock"),
    ("Unemployment Rate", "2020-03-01", "2021-12-01", "COVID-19 labor shock"),
    ("COLCAP", "2026-01-01", "2026-07-01", "New highs on a trending index"),
    ("COLCAP Monthly Return", "2008-10-01", "2008-10-01", "Global financial crisis"),
    ("COLCAP Monthly Return", "2020-03-01", "2020-03-01", "COVID-19 market crash"),
    ("COLCAP Monthly Return", "2020-12-01", "2020-12-01", "Post-vaccine recovery rally"),
    ("COLCAP Monthly Return", "2022-06-01", "2022-06-01", "Sell-off around the presidential election"),
    ("COLCAP Monthly Return", "2026-01-01", "2026-01-01", "Rally to record highs, driver not sourced"),
    ("Real GDP Growth", "2020-06-01", "2020-12-01", "COVID-19 contraction"),
    ("Real GDP Growth", "2021-06-01", "2022-06-01", "Post-COVID rebound"),
]


def classify(series_key: str, date: pd.Timestamp) -> str:
    for key, first, last, classification in OUTLIER_RULES:
        if key == series_key and pd.Timestamp(first) <= date <= pd.Timestamp(last):
            return classification
    raise ValueError(f"No classification for outlier {series_key} at {date:%Y-%m}")


outliers = in_window[in_window["IsOutlier"] == 1]
fact_outliers = pd.DataFrame({
    "Date": outliers["Date"].dt.strftime("%Y-%m-%d"),
    "Period": [period_label(key, date) for key, date in zip(outliers["SeriesKey"], outliers["Date"])],
    "SeriesKey": outliers["SeriesKey"],
    "Value": outliers["Value"].map(lambda value: round(value, 2)),
    "LowerFence": outliers["LowerFence"].map(lambda value: round(value, 2)),
    "UpperFence": outliers["UpperFence"].map(lambda value: round(value, 2)),
    "Direction": (outliers["Value"] < outliers["LowerFence"]).map({True: "Below lower fence", False: "Above upper fence"}),
    "Classification": [classify(key, date) for key, date in zip(outliers["SeriesKey"], outliers["Date"])],
    "Treatment": "Kept",
})

fact_outliers.groupby(["SeriesKey", "Classification"], sort=False).size()

# COMMAND ----------

# EXPORTATION
fact_outliers.to_csv(f"{POWERBI_DATA_FOLDER}/fact_outliers.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
