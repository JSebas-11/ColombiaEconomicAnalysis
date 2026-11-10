# Databricks notebook source
import pandas as pd

# COMMAND ----------

FINAL_DATA_FOLDER = "../data/final"

monthly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_monthly.csv")
quarterly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_quarterly.csv")

# COMMAND ----------

columns = [
    "InflationYOY",
    "TRMAvg",
    "OccupationRate",
    "UnemploymentRate",
    "PolicyRate",
    "ColcapIndex",
    "MonthlyReturn"
]

stats = monthly_set[columns].agg(
    ["count", "mean", "median", "std", "min", "max"]
).T

print(stats.round(2))

# COMMAND ----------

gdp_stats = quarterly_set[["RealGDPGrowth"]].agg(
    ["count", "mean", "median", "std", "min", "max"]
).T

print(gdp_stats.round(2))

# COMMAND ----------

def iqr_outlier_summary(df, columns):
    rows = []

    for col in columns:
        s = df[col].dropna()
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = s[(s < lower) | (s > upper)]

        rows.append({
            "Variable": col,
            "Q1": q1,
            "Q3": q3,
            "IQR": iqr,
            "LowerFence": lower,
            "UpperFence": upper,
            "OutlierCount": len(outliers),
            "OutlierPercent": 100 * len(outliers) / len(s),
        })

    return pd.DataFrame(rows).set_index("Variable")



def find_outliers(df, date_col, variables):
    findings = []

    for variable in variables:
        values = df[variable].dropna()
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        mask = df[variable].notna() & (
            (df[variable] < lower) | (df[variable] > upper)
        )

        for _, row in df.loc[mask].iterrows():
            value = row[variable]
            findings.append({
                "Date": row[date_col],
                "Variable": variable,
                "Value": value,
                "LowerFence": round(lower, 3),
                "UpperFence": round(upper, 3),
                "Direction": "Below lower fence" if value < lower
                             else "Above upper fence"
            })

    return pd.DataFrame(findings)

# COMMAND ----------



monthly_columns = [
    "InflationYOY", "TRMAvg", "OccupationRate",
    "UnemploymentRate", "PolicyRate",
    "ColcapIndex", "MonthlyReturn"
]

print(iqr_outlier_summary(monthly_set, monthly_columns).round(2))
print(iqr_outlier_summary(quarterly_set, ["RealGDPGrowth"]).round(2))

# COMMAND ----------

monthly_variables = [
    "InflationYOY", "TRMAvg", "OccupationRate",
    "UnemploymentRate", "PolicyRate",
    "ColcapIndex", "MonthlyReturn"
]

monthly_outliers = find_outliers(
    monthly_set, "MonthlyDate", monthly_variables
)

gdp_outliers = find_outliers(
    quarterly_set, "Quarter", ["RealGDPGrowth"]
)

print("MONTHLY OUTLIERS")
print(monthly_outliers.to_string(index=False))

print("\nQUARTERLY GDP OUTLIERS")
print(gdp_outliers.to_string(index=False))
