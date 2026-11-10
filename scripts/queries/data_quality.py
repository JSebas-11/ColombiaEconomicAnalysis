# Databricks notebook source
import pandas as pd

MONTHLY_PATH = "../../data/final/economics_monthly.csv"
QUARTERLY_PATH = "../../data/final/economics_quarterly.csv"

RAW_DATA_FOLDER = "../../data/war"
ASSIGN_DATA_FOLDER = "../../data/assignment/ass1"

# COMMAND ----------

# MAGIC %md
# MAGIC ## MONTHLY DATASET

# COMMAND ----------

monthly_set = pd.read_csv(MONTHLY_PATH)

monthly_set["MonthlyDate"] = pd.to_datetime(monthly_set["MonthlyDate"]).dt.to_period("M")
start_period = pd.Period("2018-01", freq="M")
end_period = pd.Period("2026-08", freq="M")

filtered_monthly = monthly_set[monthly_set["MonthlyDate"].between(start_period, end_period)]

filtered_monthly


# COMMAND ----------

filtered_monthly.info()

# COMMAND ----------

filtered_monthly.describe()

# COMMAND ----------

filtered_monthly.to_csv(f"{ASSIGN_DATA_FOLDER}/economics_filtered_monthly.csv", index=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## QUARTERLY DATASET

# COMMAND ----------

quarterly_set = pd.read_csv(QUARTERLY_PATH)

start_quarter = "2018-Q1"
end_quarter = "2026-Q2"

filtered_quarteryly = quarterly_set[(quarterly_set['Quarter'] >= start_quarter) & (quarterly_set['Quarter'] <= end_quarter)]

filtered_quarteryly


# COMMAND ----------

filtered_quarteryly.info()

# COMMAND ----------

filtered_quarteryly.describe()

# COMMAND ----------

filtered_quarteryly.to_csv(f"{ASSIGN_DATA_FOLDER}/economics_filtered_quarteryly.csv", index=False)