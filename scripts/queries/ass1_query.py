# Databricks notebook source
# MAGIC %sql
# MAGIC SELECT * FROM bi_subject.colombia_economics.filtered_monthly LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ## INFLATION: How did inflation evolve between 2018 and 2026, and when were its major peaks?

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     YEAR(MonthlyDate) AS Year, AVG(InflationYOY) AS AvgInflation, 
# MAGIC     MAX(InflationYOY) AS MaxInflation, MIN(InflationYOY) AS MinInflation
# MAGIC FROM bi_subject.colombia_economics.filtered_monthly
# MAGIC WHERE InflationYOY IS NOT NULL
# MAGIC GROUP BY YEAR(MonthlyDate)
# MAGIC ORDER BY Year;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exchange rate: How did the TRM evolve between 2018 and 2026, particularly around major economic shocks?

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     YEAR(TO_DATE(MonthlyDate, 'yyyy-MM')) AS Year,
# MAGIC     ROUND(AVG(TRMAvg), 2) AS AverageTRM,
# MAGIC     ROUND(MIN(TRMAvg), 2) AS MinimumTRM,
# MAGIC     ROUND(MAX(TRMAvg), 2) AS MaximumTRM
# MAGIC FROM bi_subject.colombia_economics.filtered_monthly
# MAGIC WHERE TRMAvg IS NOT NULL
# MAGIC GROUP BY YEAR(TO_DATE(MonthlyDate, 'yyyy-MM'))
# MAGIC ORDER BY Year;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Monetary policy: How did Banco de la República's policy rate respond to changes in inflation?

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     CASE
# MAGIC         WHEN InflationYOY < 3 THEN 'Low Inflation'
# MAGIC         WHEN InflationYOY < 5 THEN 'Moderate Inflation'
# MAGIC         ELSE 'High Inflation'
# MAGIC     END AS InflationLevel,
# MAGIC     COUNT(*) AS Months,
# MAGIC     ROUND(AVG(InflationYOY), 2) AS AverageInflation, ROUND(AVG(PolicyRate), 2) AS AveragePolicyRate,
# MAGIC     ROUND(MIN(PolicyRate), 2) AS MinimumPolicyRate, ROUND(MAX(PolicyRate), 2) AS MaximumPolicyRate
# MAGIC FROM bi_subject.colombia_economics.filtered_monthly
# MAGIC WHERE InflationYOY IS NOT NULL
# MAGIC   AND PolicyRate IS NOT NULL
# MAGIC GROUP BY
# MAGIC     CASE
# MAGIC         WHEN InflationYOY < 3 THEN 'Low Inflation'
# MAGIC         WHEN InflationYOY < 5 THEN 'Moderate Inflation'
# MAGIC         ELSE 'High Inflation'
# MAGIC     END
# MAGIC ORDER BY AverageInflation;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Labor market & GDP: How did unemployment, occupation, and economic growth evolve before and after COVID-19?

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH labor AS (
# MAGIC     SELECT
# MAGIC         CASE
# MAGIC             WHEN YEAR(TO_DATE(MonthlyDate, 'yyyy-MM')) <= 2019
# MAGIC                 THEN 'Pre-COVID'
# MAGIC             WHEN YEAR(TO_DATE(MonthlyDate, 'yyyy-MM')) = 2020
# MAGIC                 THEN 'COVID'
# MAGIC             ELSE 'Post-COVID'
# MAGIC         END AS Period,
# MAGIC         OccupationRate,
# MAGIC         UnemploymentRate
# MAGIC     FROM bi_subject.colombia_economics.filtered_monthly
# MAGIC ),
# MAGIC
# MAGIC labor_summary AS (
# MAGIC     SELECT
# MAGIC         Period,
# MAGIC         ROUND(AVG(OccupationRate), 2) AS AvgOccupationRate,
# MAGIC         ROUND(AVG(UnemploymentRate), 2) AS AvgUnemploymentRate
# MAGIC     FROM labor
# MAGIC     GROUP BY Period
# MAGIC ),
# MAGIC
# MAGIC gdp_summary AS (
# MAGIC     SELECT
# MAGIC         CASE
# MAGIC             WHEN SUBSTRING(Quarter, 1, 4) <= '2019'
# MAGIC                 THEN 'Pre-COVID'
# MAGIC             WHEN SUBSTRING(Quarter, 1, 4) = '2020'
# MAGIC                 THEN 'COVID'
# MAGIC             ELSE 'Post-COVID'
# MAGIC         END AS Period,
# MAGIC         ROUND(AVG(RealGDPGrowth), 2) AS AvgGDPGrowth
# MAGIC     FROM bi_subject.colombia_economics.filtered_quarterly
# MAGIC     GROUP BY
# MAGIC         CASE
# MAGIC             WHEN SUBSTRING(Quarter, 1, 4) <= '2019'
# MAGIC                 THEN 'Pre-COVID'
# MAGIC             WHEN SUBSTRING(Quarter, 1, 4) = '2020'
# MAGIC                 THEN 'COVID'
# MAGIC             ELSE 'Post-COVID'
# MAGIC         END
# MAGIC )
# MAGIC
# MAGIC SELECT
# MAGIC     l.Period,
# MAGIC     l.AvgOccupationRate,
# MAGIC     l.AvgUnemploymentRate,
# MAGIC     g.AvgGDPGrowth
# MAGIC FROM labor_summary l
# MAGIC JOIN gdp_summary g
# MAGIC     ON l.Period = g.Period
# MAGIC ORDER BY
# MAGIC     CASE l.Period
# MAGIC         WHEN 'Pre-COVID' THEN 1
# MAGIC         WHEN 'COVID' THEN 2
# MAGIC         WHEN 'Post-COVID' THEN 3
# MAGIC     END;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stock market: Which periods produced the strongest and weakest MSCI COLCAP monthly returns?

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH ranked_returns AS (
# MAGIC     SELECT
# MAGIC         MonthlyDate,
# MAGIC         ROUND(MonthlyReturn, 2) AS MonthlyReturn,
# MAGIC         ROW_NUMBER() OVER (ORDER BY MonthlyReturn DESC) AS BestRank,
# MAGIC         ROW_NUMBER() OVER (ORDER BY MonthlyReturn ASC) AS WorstRank
# MAGIC     FROM bi_subject.colombia_economics.filtered_monthly
# MAGIC     WHERE MonthlyReturn IS NOT NULL
# MAGIC )
# MAGIC
# MAGIC SELECT
# MAGIC     CASE
# MAGIC         WHEN BestRank <= 5 THEN 'Strongest'
# MAGIC         WHEN WorstRank <= 5 THEN 'Weakest'
# MAGIC     END AS ReturnType,
# MAGIC     MonthlyDate,
# MAGIC     MonthlyReturn
# MAGIC FROM ranked_returns
# MAGIC WHERE BestRank <= 5
# MAGIC    OR WorstRank <= 5
# MAGIC ORDER BY
# MAGIC     CASE WHEN ReturnType = 'Strongest' THEN 1 ELSE 2 END,
# MAGIC     MonthlyReturn DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Relationships: Is there an observable relationship between inflation, the policy rate, TRM, and MSCI COLCAP returns?

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     ROUND(CORR(InflationYOY, PolicyRate), 3) AS Inflation_PolicyRate,
# MAGIC     ROUND(CORR(InflationYOY, TRMAvg), 3) AS Inflation_TRM,
# MAGIC     ROUND(CORR(InflationYOY, MonthlyReturn), 3) AS Inflation_COLCAPReturn,
# MAGIC     ROUND(CORR(PolicyRate, TRMAvg), 3) AS PolicyRate_TRM,
# MAGIC     ROUND(CORR(PolicyRate, MonthlyReturn), 3) AS PolicyRate_COLCAPReturn,
# MAGIC     ROUND(CORR(TRMAvg, MonthlyReturn), 3) AS TRM_COLCAPReturn
# MAGIC FROM bi_subject.colombia_economics.filtered_monthly
# MAGIC WHERE InflationYOY IS NOT NULL
# MAGIC   AND PolicyRate IS NOT NULL
# MAGIC   AND TRMAvg IS NOT NULL
# MAGIC   AND MonthlyReturn IS NOT NULL;