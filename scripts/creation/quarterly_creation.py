# Databricks notebook source
import pandas as pd

RAW_DATA_FOLDER = "../../data/raw"
FINAL_DATA_FOLDER = "../../data/final"

# COMMAND ----------

# GDP SET
gdp_set = pd.read_excel(f"{RAW_DATA_FOLDER}/GDP.xlsx")
quarterly_dataset = (
    gdp_set
    .rename(columns=
        {'Fecha (dd/mm/aaaa/)': 'QuarterDate', 'Crecimiento PIB real trimestral (%)': 'RealGDPGrowth'}
    ).assign(
        QuarterDate=lambda df: pd.to_datetime(df['QuarterDate'], dayfirst=True),
        Quarter=lambda df: (df['QuarterDate'].dt.to_period("Q").astype(str)).str.replace("Q", "-Q", regex=False)
    )
    .drop(columns=["QuarterDate"])
)
quarterly_dataset["RealGDPGrowth"] = quarterly_dataset["RealGDPGrowth"].str.replace(",", ".").astype(float)
quarterly_dataset = quarterly_dataset[["Quarter", "RealGDPGrowth"]]

quarterly_dataset.info()

# COMMAND ----------

# EXPORTATION
quarterly_dataset.to_csv(f"{FINAL_DATA_FOLDER}/economics_quarterly.csv", index=False)