# Colombia Economic Analysis 2018–2026

---

## Objective

Analyze the evolution and relationships between inflation, exchange rates, economic growth, employment, monetary policy, and the Colombian stock market between 2018 and 2026 using economic data from the Banco de la República's statistical database.

---

## Period

**January 2018 → latest available observation in 2026**

> Note: 2026 is an incomplete year. Therefore, results for 2026 represent the period available up to the latest observation, not the full year.

---

# Datasets

## CPI — Consumer Price Index

**Definition:**
The Consumer Price Index (CPI) measures the change over time in the prices of a representative basket of goods and services consumed by households. Its annual percentage variation is used as the country's inflation indicator.

**Table:**

```text
system_date
date (M, Y)
index
monthlyVar (%)
annualVar (%)
currentYearVar (%)
expenseDivision
```

**Used columns:**

```text
date
annualVar
```

**Available data range:** 1954 → August 2026

**Plan:**
The data is already monthly. Filter `expenseDivision = Total` and use the annual percentage variation as the monthly inflation indicator for the 2018–2026 study period.

---

## TRM — Representative Market Rate

**Definition:**
The Representative Market Rate (TRM) is the official exchange rate of the US dollar against the Colombian peso (COP), representing how many Colombian pesos are equivalent to one US dollar.

**Table:**

```text
period
trm
```

**Available data range:** 1991 → September 8, 2026

**Plan:**
The original data is daily. Group observations by month and calculate the **monthly average TRM**.

Final variable:

```text
trm_avg
```

---

## GDP — Gross Domestic Product

**Definition:**
GDP measures the monetary value of final goods and services produced within a country's economy during a given period.

**Table:**

```text
date
real_gdp_growth
```

**Available data range:** 2006 → June 30, 2026

**Plan:**
Use the quarterly real GDP growth series, seasonally adjusted. The data is already expressed as a growth rate, so no additional growth calculation is required.

Final variable:

```text
gdp_growth_yoy
```

GDP remains **quarterly** rather than being converted to monthly data.

---

## Occupation & Unemployment Rates

**Definition:**
The occupation rate represents the proportion of the working-age population that is employed. The unemployment rate represents the percentage of the labor force that does not have a job but is available for and actively seeking employment.

**Table:**

```text
data_system
methodology
geo_scope
date (M, Y)
occupation_rate (%)
unemployment_rate (%)
```

**Available data range:** 2001 → 2026

**Plan:**
Use the **Total National** series. The data is already monthly, so no frequency conversion is required.

Final variables:

```text
occupation_rate
unemployment_rate
```

---

## Policy Rate

**Definition:**
The monetary policy rate is a short-term benchmark interest rate set by the country's central bank. The central bank can raise the rate to reduce demand and inflationary pressure or lower it to stimulate borrowing and economic activity.

**Table:**

```text
date (D, M, Y)
rate (%)
```

**Available data range:** 1995 → 2026

**Plan:**
The original data is daily. Since the policy rate represents a policy decision rather than a continuously fluctuating market price, use the **last available rate of each month**.

Final variable:

```text
policy_rate
```

---

## Colombian Stock Market — MSCI COLCAP

**Definition:**
The MSCI COLCAP is a benchmark index of the Colombian stock market calculated by MSCI. It tracks the performance of 20 issuers and 25 of the most liquid Colombian stocks.

**Table:**

```text
date_system
date (D, M, Y)
indexName
index
index_abs_var
percent_var
```

**Used columns:**

```text
date
index
```

**Available data range:** 2008 → September 2026

**Plan:**
The original data is daily.

First, obtain the **last index value of each month**. Then calculate the monthly return:

```text
monthly_return =
    (current_month_end_index / previous_month_end_index - 1) × 100
```

Final variables:

```text
colcap_index
colcap_monthly_return
```

---

# Final Data Structure

## Monthly Dataset

### `economic_monthly`

| Variable                | Description                           |
| ----------------------- | ------------------------------------- |
| `date`                  | Month                                 |
| `inflation_yoy`         | Annual CPI variation (%)              |
| `trm_avg`               | Monthly average COP/USD               |
| `occupation_rate`       | National occupation rate (%)          |
| `unemployment_rate`     | National unemployment rate (%)        |
| `policy_rate`           | End-of-month monetary policy rate (%) |
| `colcap_index`          | End-of-month MSCI COLCAP level        |
| `colcap_monthly_return` | Monthly MSCI COLCAP return (%)        |

---

## Quarterly Dataset

### `economic_quarterly`

| Variable         | Description                              |
| ---------------- | ---------------------------------------- |
| `quarter`        | Quarter                                  |
| `gdp_growth_yoy` | Real GDP growth, seasonally adjusted (%) |

BanRep's current statistics show the seasonally adjusted real GDP growth series through **Q2 2026**.

---

# Frequency Transformation Summary

| Variable     | Original frequency | Final frequency | Transformation             |
| ------------ | ------------------ | --------------- | -------------------------- |
| Inflation    | Monthly            | Monthly         | Keep                       |
| TRM          | Daily              | Monthly         | Monthly average            |
| Unemployment | Monthly            | Monthly         | Keep                       |
| Occupation   | Monthly            | Monthly         | Keep                       |
| Policy rate  | Daily              | Monthly         | Last observation           |
| MSCI COLCAP  | Daily              | Monthly         | Month-end + monthly return |
| GDP growth   | Quarterly          | Quarterly       | Keep                       |

---

## Methodological Principle

**Normalize the structure, not the economics.**

Daily financial/economic variables are aggregated to monthly observations when appropriate, while variables that are naturally monthly or quarterly remain at their original frequency.

GDP will therefore remain quarterly rather than being artificially converted into monthly observations.

---

## QUERIES

- Inflation: How did inflation evolve between 2018 and 2026, and when were its major peaks?
- Exchange rate: How did the TRM evolve between 2018 and 2026, particularly around major economic shocks?
- Monetary policy: How did Banco de la República's policy rate respond to changes in inflation?
- Labor market & GDP: How did unemployment, occupation, and economic growth evolve before and after COVID-19?
- Stock market: Which periods produced the strongest and weakest MSCI COLCAP monthly returns?
- Relationships: Is there an observable relationship between inflation, the policy rate, TRM, and MSCI COLCAP returns?