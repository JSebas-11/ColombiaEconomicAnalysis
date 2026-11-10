# Databricks notebook source
import pandas as pd

# COMMAND ----------

RAW_DATA_FOLDER = "../data/raw"

cpi_set = pd.read_csv(f"{RAW_DATA_FOLDER}/ConsumerPriceIndex.csv")
trm_set = pd.read_csv(f"{RAW_DATA_FOLDER}/COP_TRM.csv")
gdp_set = pd.read_excel(f"{RAW_DATA_FOLDER}/GDP.xlsx")
occ_unem_set = pd.read_csv(f"{RAW_DATA_FOLDER}/OccupationAndUnemployement.csv")
policy_rate_set = pd.read_excel(f"{RAW_DATA_FOLDER}/policy_rate.xlsx")
colcap_set = pd.read_csv(f"{RAW_DATA_FOLDER}/stock_market_colcap.csv")

# COMMAND ----------

cpi_set.info()

# COMMAND ----------

trm_set.info()

# COMMAND ----------

gdp_set.info()

# COMMAND ----------

occ_unem_set.info()

# COMMAND ----------


policy_rate_set.info()

# COMMAND ----------

colcap_set.info()