# Databricks notebook source
import pandas as pd

# COMMAND ----------

RAW_DATA_FOLDER = "../data/raw"
FINAL_DATA_FOLDER = "../data/final"

cpi_set = pd.read_csv(f"{RAW_DATA_FOLDER}/ConsumerPriceIndex.csv")
trm_set = pd.read_csv(f"{RAW_DATA_FOLDER}/COP_TRM.csv")
gdp_set = pd.read_excel(f"{RAW_DATA_FOLDER}/GDP.xlsx")
occ_unem_set = pd.read_csv(f"{RAW_DATA_FOLDER}/OccupationAndUnemployement.csv")
policy_rate_set = pd.read_excel(f"{RAW_DATA_FOLDER}/policy_rate.xlsx")
colcap_set = pd.read_csv(f"{RAW_DATA_FOLDER}/stock_market_colcap.csv")

monthly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_monthly.csv")
quarterly_set = pd.read_csv(f"{FINAL_DATA_FOLDER}/economics_quarterly.csv")

# COMMAND ----------

# MAGIC %md
# MAGIC ## CPI Dataset (RAW)

# COMMAND ----------

cpi_set.info()

# COMMAND ----------

print("FILTERED BY División del gasto: Total")
cpi_set[cpi_set['División del gasto'] == 'Total'].info()

print("-----------------------------------------------")
print("FILTERED BY División del gasto: Total AND Fecha < 1956")
cpi_set[(cpi_set['División del gasto'] == 'Total') & (cpi_set['Fecha (Mes año)'] < '1956-01-01')].info()

print("-----------------------------------------------")
print("FILTERED BY División del gasto diferente Total")
cpi_set[cpi_set['División del gasto'] != 'Total'].info()

# COMMAND ----------

cpi_set['División del gasto'].unique()

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRM Dataset (RAW)

# COMMAND ----------

trm_set.info()

# COMMAND ----------

# MAGIC %md
# MAGIC ## GDP Dataset (RAW) 

# COMMAND ----------

gdp_set.info()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Occupation & Unemployement Dataset (RAW)

# COMMAND ----------

occ_unem_set.info()

# COMMAND ----------

for col in ['Metodología', 'Cobertura geográfica']:
    print(f"Valores unicos en {col}:")
    print(occ_unem_set[col].unique())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Policy Rate Dataset (RAW)

# COMMAND ----------

policy_rate_set.info()

# COMMAND ----------

# MAGIC %md
# MAGIC ## COLCAP Dataset (RAW)

# COMMAND ----------

colcap_set.info()

# COMMAND ----------

colcap_set['Nombre del índice'].unique()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Economics Monthly (CONSOLIDATED)

# COMMAND ----------

monthly_set.info()

# COMMAND ----------

print("FILTERED BY MonthlyDate: 1956")
monthly_set[(monthly_set['MonthlyDate'] > '2002-01-01')].info()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Economics Quarterly (CONSOLIDATED)

# COMMAND ----------

quarterly_set.info()