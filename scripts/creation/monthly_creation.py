# Databricks notebook source
import pandas as pd

RAW_DATA_FOLDER = "../../data/raw"
FINAL_DATA_FOLDER = "../../data/final"

# COMMAND ----------

# CPI SET
cpi_set = pd.read_csv(f"{RAW_DATA_FOLDER}/ConsumerPriceIndex.csv")
total_expense_cpi = (
    cpi_set[cpi_set['División del gasto'] == "Total"]
    .rename(columns={'Fecha (Mes año)': 'Date', 'Variación anual (%)': 'InflationYOY'})
    .copy()
)
total_expense_cpi["MonthlyDate"] = pd.to_datetime(total_expense_cpi["Date"]).dt.to_period("M")
total_expense_cpi = total_expense_cpi.drop(columns=[
    "Fecha sistema", "Date", "Índice", "Variación mensual (%)", "Variación año corrido (%)", "Orden_División", "División del gasto"
])

total_expense_cpi = total_expense_cpi[["MonthlyDate", "InflationYOY"]]

total_expense_cpi

# COMMAND ----------

# TRM SET
trm_set = pd.read_csv(f"{RAW_DATA_FOLDER}/COP_TRM.csv")
trm_monthly_avg = (
    trm_set.rename(columns={
        'Periodo(MMM DD, AAAA)': 'Period', 
        'Tasa Representativa del Mercado (TRM)': 'TRMAvg'
    })
    .assign(Period=lambda df: pd.to_datetime(df['Period']).dt.to_period("M"))
    .groupby('Period')['TRMAvg']
    .mean()
    .round(2)
    .reset_index()
    .rename(columns={'Period': 'MonthlyDate'})
)

trm_monthly_avg

# COMMAND ----------

# OCCUPATION & UNEMPLOYEMENT SET
occ_unem_set = pd.read_csv(f"{RAW_DATA_FOLDER}/OccupationAndUnemployement.csv")
occ_unem_total_set = (
    occ_unem_set[occ_unem_set['Cobertura geográfica'] == "Total nacional"]
    .rename(columns={
        'Fecha (Mes año)': 'Date', 'Tasa de ocupación (%)': 'OccupationRate', 'Tasa de desempleo (%)': 'UnemploymentRate'
    })
    .drop(columns=["Fecha sistema", "Metodología", "Cobertura geográfica"])
    .reset_index(drop=True)
    .copy()
)
occ_unem_total_set["MonthlyDate"] = pd.to_datetime(occ_unem_total_set["Date"]).dt.to_period("M")
occ_unem_total_set = occ_unem_total_set.drop(columns=["Date"])

occ_unem_total_set

# COMMAND ----------

# POLICY RATE SET
policy_rate_set = pd.read_excel(f"{RAW_DATA_FOLDER}/policy_rate.xlsx")
policy_rate_monthly_last = (
    policy_rate_set.rename(columns={
        'Fecha (dd/mm/aaaa)': 'Date', 
        'Tasa de política monetaria (%)': 'PolicyRate'
    })
    .assign(Date=lambda df: pd.to_datetime(df['Date'], dayfirst=True))
    .sort_values('Date')
    .assign(Period=lambda df: df['Date'].dt.to_period("M"))
    .groupby('Period')
    .last()
    .reset_index()
    .rename(columns={'Period': 'MonthlyDate'})
)
policy_rate_monthly_last = policy_rate_monthly_last.drop(columns=["Date"])

policy_rate_monthly_last


# COMMAND ----------

# COLCAP SET
colcap_set = pd.read_csv(f"{RAW_DATA_FOLDER}/stock_market_colcap.csv")
colcap_monthly_set = (
    colcap_set.rename(columns={'Fecha (DD/MM/AAAA)': 'Date', 'Índice': 'ColcapIndex'})
    .assign(Date=lambda df: pd.to_datetime(df['Date'], dayfirst=True))
    .sort_values("Date")
    .set_index("Date")["ColcapIndex"]
    .resample("ME")
    .last()
    .dropna()
    .reset_index()
)
colcap_monthly_set["MonthlyReturn"] = colcap_monthly_set["ColcapIndex"].pct_change() * 100
colcap_monthly_set["MonthlyDate"] = colcap_monthly_set["Date"].dt.to_period("M")
colcap_monthly_set = colcap_monthly_set.drop(columns=["Date"])

colcap_monthly_set


# COMMAND ----------

# UNIFICATION
monthly_dataset = (
    total_expense_cpi
    .merge(trm_monthly_avg, on="MonthlyDate", how="left")
    .merge(occ_unem_total_set, on="MonthlyDate", how="left")
    .merge(policy_rate_monthly_last, on="MonthlyDate", how="left")
    .merge(colcap_monthly_set, on="MonthlyDate", how="left")
)

monthly_dataset

# COMMAND ----------

# EXPORTATION
monthly_dataset.to_csv(f"{FINAL_DATA_FOLDER}/economics_monthly.csv", index=False)