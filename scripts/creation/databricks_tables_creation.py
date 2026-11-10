# Databricks notebook source
import pandas as pd

# COMMAND ----------

# MAGIC %md
# MAGIC ## GLOBAL TABLES

# COMMAND ----------

MONTHLY_PATH = "/Workspace/bi_subject/economics_project/assignment1/ColombiaEconomicAnalysis/data/final/economics_monthly.csv"
QUARTERLY_PATH = "/Workspace/bi_subject/economics_project/assignment1/ColombiaEconomicAnalysis/data/final/economics_quarterly.csv"

monthly_pd = pd.read_csv(MONTHLY_PATH)
quarterly_pd = pd.read_csv(QUARTERLY_PATH)

monthly = spark.createDataFrame(monthly_pd)
quarterly = spark.createDataFrame(quarterly_pd)

monthly.write.format("delta").mode("overwrite").saveAsTable("bi_subject.colombia_economics.monthly")
quarterly.write.format("delta").mode("overwrite").saveAsTable("bi_subject.colombia_economics.quarterly")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ASSIGNMENT 1 TABLES

# COMMAND ----------

FILTERED_MONTHLY_PATH = "/Workspace/bi_subject/economics_project/assignment1/ColombiaEconomicAnalysis/data/assignment/ass1/economics_filtered_monthly.csv"
FILTERED_QUARTERLY_PATH = "/Workspace/bi_subject/economics_project/assignment1/ColombiaEconomicAnalysis/data/assignment/ass1/economics_filtered_quarteryly.csv"

filtered_monthly_pd = pd.read_csv(FILTERED_MONTHLY_PATH)
filtered_quarterly_pd = pd.read_csv(FILTERED_QUARTERLY_PATH)

filtered_monthly = spark.createDataFrame(filtered_monthly_pd)
filtered_quarterly = spark.createDataFrame(filtered_quarterly_pd)

filtered_monthly.write.format("delta").mode("overwrite").saveAsTable("bi_subject.colombia_economics.filtered_monthly")
filtered_quarterly.write.format("delta").mode("overwrite").saveAsTable("bi_subject.colombia_economics.filtered_quarterly")

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN bi_subject.colombia_economics;