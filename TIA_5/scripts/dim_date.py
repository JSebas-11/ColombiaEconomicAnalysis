# Databricks notebook source
# Power BI table DimDate: one row per month of the analysis window, with its presidential term.
# Output: TIA_5/powerbi/data/dim_date.csv
import pandas as pd

POWERBI_DATA_FOLDER = "../../TIA_5/powerbi/data"

WINDOW_START = pd.Timestamp("2008-01-01")
WINDOW_END = pd.Timestamp("2026-07-01")

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# COMMAND ----------

# PRESIDENTIAL TERMS
# Terms change on August 7, so every month from August belongs to the incoming president.
terms = pd.DataFrame(
    [
        ("Uribe II (partial)", "Alvaro Uribe", "2006-08-07", "2010-08-07", "2008-01-01", "2010-07-01"),
        ("Santos I", "Juan Manuel Santos", "2010-08-07", "2014-08-07", "2010-08-01", "2014-07-01"),
        ("Santos II", "Juan Manuel Santos", "2014-08-07", "2018-08-07", "2014-08-01", "2018-07-01"),
        ("Duque", "Ivan Duque", "2018-08-07", "2022-08-07", "2018-08-01", "2022-07-01"),
        ("Petro", "Gustavo Petro", "2022-08-07", "2026-08-07", "2022-08-01", "2026-07-01"),
    ],
    columns=["TermLabel", "President", "OfficialTermStart", "OfficialTermEnd", "FirstMonth", "LastMonth"],
)
terms["TermOrder"] = range(1, len(terms) + 1)
terms["FirstMonth"] = pd.to_datetime(terms["FirstMonth"])
terms["LastMonth"] = pd.to_datetime(terms["LastMonth"])

terms

# COMMAND ----------

# CALENDAR
calendar = pd.DataFrame({"Date": pd.date_range(WINDOW_START, WINDOW_END, freq="MS")})
calendar = calendar.assign(
    Year=lambda df: df["Date"].dt.year,
    Quarter=lambda df: df["Date"].dt.year.astype(str) + "-Q" + df["Date"].dt.quarter.astype(str),
    MonthNumber=lambda df: df["Date"].dt.month,
    MonthLabel=lambda df: df["Date"].dt.month.map(lambda month: MONTH_NAMES[month - 1]) + " " + df["Date"].dt.year.astype(str),
)


def term_for(date: pd.Timestamp) -> pd.Series:
    """The single term whose first and last month contain this month."""
    match = terms[(terms["FirstMonth"] <= date) & (terms["LastMonth"] >= date)]
    assert len(match) == 1, f"{date:%Y-%m} is not covered by exactly one term"
    return match.iloc[0]


term_columns = pd.DataFrame([term_for(date) for date in calendar["Date"]]).reset_index(drop=True)
dim_date = pd.concat([calendar, term_columns], axis=1)

dim_date["Date"] = dim_date["Date"].dt.strftime("%Y-%m-%d")
dim_date = dim_date[[
    "Date", "Year", "Quarter", "MonthNumber", "MonthLabel",
    "TermOrder", "TermLabel", "President", "OfficialTermStart", "OfficialTermEnd",
]]

dim_date.info()

# COMMAND ----------

# EXPORTATION
dim_date.to_csv(f"{POWERBI_DATA_FOLDER}/dim_date.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
