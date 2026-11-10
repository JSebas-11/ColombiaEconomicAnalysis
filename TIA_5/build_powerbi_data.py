"""Builds the Power BI input tables for the TIA 5 dashboard.

Run with: python3 TIA_5/build_powerbi_data.py
"""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from datetime import date
from pathlib import Path

TIA5_DIR = Path(__file__).resolve().parent
SOURCE_DIR = TIA5_DIR.parent / "data" / "final"
OUTPUT_DIR = TIA5_DIR / "powerbi" / "data"

WINDOW_START = date(2008, 1, 1)
WINDOW_END = date(2026, 7, 1)
COVERAGE_FIRST_YEAR = 2000

MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


@dataclass(frozen=True)
class SeriesDefinition:
    key: str
    unit: str
    frequency: str
    source_column: str
    pre_window_gap: str
    in_window_treatment: str


@dataclass(frozen=True)
class PresidentialTerm:
    label: str
    president: str
    official_start: date
    official_end: date
    first_month: date
    last_month: date


@dataclass(frozen=True)
class OutlierRule:
    series_key: str
    first_period: date
    last_period: date
    classification: str


@dataclass(frozen=True)
class CorrelationPair:
    x_key: str
    y_key: str
    lag_months: int


NO_EMPTY_CELLS = "No empty cells in the window."

SERIES = (
    SeriesDefinition(
        "Inflation YoY", "%", "Monthly", "InflationYOY",
        "Available since 1955, no gap in the window.", NO_EMPTY_CELLS,
    ),
    SeriesDefinition(
        "Policy Rate", "%", "Monthly", "PolicyRate",
        "The series used starts in April 1999.", NO_EMPTY_CELLS,
    ),
    SeriesDefinition(
        "TRM", "COP per USD", "Monthly", "TRMAvg",
        "The series starts in late 1991, when the TRM was established.", NO_EMPTY_CELLS,
    ),
    SeriesDefinition(
        "COLCAP", "Index points", "Monthly", "ColcapIndex",
        "The index starts in January 2008.", NO_EMPTY_CELLS,
    ),
    SeriesDefinition(
        "COLCAP Monthly Return", "%", "Monthly", "MonthlyReturn",
        "The index starts in January 2008.",
        "January 2008 stays empty: a return needs a prior month, which predates the index.",
    ),
    SeriesDefinition(
        "Unemployment Rate", "%", "Monthly", "UnemploymentRate",
        "The labor series starts in January 2001.", NO_EMPTY_CELLS,
    ),
    SeriesDefinition(
        "Occupation Rate", "%", "Monthly", "OccupationRate",
        "The labor series starts in January 2001.", NO_EMPTY_CELLS,
    ),
    SeriesDefinition(
        "Real GDP Growth", "%", "Quarterly", "RealGDPGrowth",
        "The quarterly series starts in 2006.", NO_EMPTY_CELLS,
    ),
)

TERMS = (
    PresidentialTerm(
        "Uribe II (partial)", "Alvaro Uribe",
        date(2006, 8, 7), date(2010, 8, 7), WINDOW_START, date(2010, 7, 1),
    ),
    PresidentialTerm(
        "Santos I", "Juan Manuel Santos",
        date(2010, 8, 7), date(2014, 8, 7), date(2010, 8, 1), date(2014, 7, 1),
    ),
    PresidentialTerm(
        "Santos II", "Juan Manuel Santos",
        date(2014, 8, 7), date(2018, 8, 7), date(2014, 8, 1), date(2018, 7, 1),
    ),
    PresidentialTerm(
        "Duque", "Ivan Duque",
        date(2018, 8, 7), date(2022, 8, 7), date(2018, 8, 1), date(2022, 7, 1),
    ),
    PresidentialTerm(
        "Petro", "Gustavo Petro",
        date(2022, 8, 7), date(2026, 8, 7), date(2022, 8, 1), WINDOW_END,
    ),
)

OUTLIER_RULES = (
    OutlierRule("Inflation YoY", date(2022, 1, 1), date(2023, 12, 1), "2022-23 inflation episode"),
    OutlierRule("Occupation Rate", date(2020, 3, 1), date(2021, 12, 1), "COVID-19 labor shock"),
    OutlierRule("Unemployment Rate", date(2020, 3, 1), date(2021, 12, 1), "COVID-19 labor shock"),
    OutlierRule("COLCAP", date(2026, 1, 1), date(2026, 7, 1), "New highs on a trending index"),
    OutlierRule("COLCAP Monthly Return", date(2008, 10, 1), date(2008, 10, 1), "Global financial crisis"),
    OutlierRule("COLCAP Monthly Return", date(2020, 3, 1), date(2020, 3, 1), "COVID-19 market crash"),
    OutlierRule("COLCAP Monthly Return", date(2020, 12, 1), date(2020, 12, 1), "Post-vaccine recovery rally"),
    OutlierRule("COLCAP Monthly Return", date(2022, 6, 1), date(2022, 6, 1), "Sell-off around the presidential election"),
    OutlierRule("COLCAP Monthly Return", date(2026, 1, 1), date(2026, 1, 1), "Rally to record highs, driver not sourced"),
    OutlierRule("Real GDP Growth", date(2020, 6, 1), date(2020, 12, 1), "COVID-19 contraction"),
    OutlierRule("Real GDP Growth", date(2021, 6, 1), date(2022, 6, 1), "Post-COVID rebound"),
)

CORRELATION_PAIRS = (
    CorrelationPair("Inflation YoY", "Policy Rate", 0),
    CorrelationPair("Inflation YoY", "Policy Rate", 3),
    CorrelationPair("Inflation YoY", "Policy Rate", 6),
    CorrelationPair("Inflation YoY", "Policy Rate", 9),
    CorrelationPair("Inflation YoY", "Policy Rate", 12),
    CorrelationPair("Policy Rate", "Inflation YoY", 12),
    CorrelationPair("TRM", "Inflation YoY", 0),
    CorrelationPair("TRM", "COLCAP", 0),
    CorrelationPair("Policy Rate", "COLCAP", 0),
    CorrelationPair("Inflation YoY", "COLCAP Monthly Return", 0),
    CorrelationPair("Policy Rate", "COLCAP Monthly Return", 0),
    CorrelationPair("Unemployment Rate", "Occupation Rate", 0),
)


def months_between(first: date, last: date) -> list[date]:
    first_index = first.year * 12 + first.month - 1
    last_index = last.year * 12 + last.month - 1
    return [
        date(index // 12, index % 12 + 1, 1)
        for index in range(first_index, last_index + 1)
    ]


def add_months(period: date, months: int) -> date:
    index = period.year * 12 + period.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def month_label(period: date) -> str:
    return f"{MONTH_NAMES[period.month - 1]} {period.year}"


def quarter_label(period: date) -> str:
    return f"{period.year}-Q{(period.month - 1) // 3 + 1}"


def quantile(sorted_values: list[float], probability: float) -> float:
    """Linear interpolation, matching the pandas default used in TIA 4."""
    position = (len(sorted_values) - 1) * probability
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    weight = position - lower_index
    return sorted_values[lower_index] + (sorted_values[upper_index] - sorted_values[lower_index]) * weight


@dataclass(frozen=True)
class IqrFences:
    q1: float
    q3: float

    @property
    def iqr(self) -> float:
        return self.q3 - self.q1

    @property
    def lower(self) -> float:
        return self.q1 - 1.5 * self.iqr

    @property
    def upper(self) -> float:
        return self.q3 + 1.5 * self.iqr

    def is_outlier(self, value: float) -> bool:
        return value < self.lower or value > self.upper

    @classmethod
    def from_values(cls, values: list[float]) -> IqrFences:
        ordered = sorted(values)
        return cls(quantile(ordered, 0.25), quantile(ordered, 0.75))


class MacroDataset:
    """Holds every non-empty observation, keyed by series and period."""

    def __init__(self, source_dir: Path) -> None:
        self.observations: dict[str, dict[date, float]] = {
            series.key: {} for series in SERIES
        }
        self.window_months = months_between(WINDOW_START, WINDOW_END)
        self.window_quarters: list[date] = []
        self._load_monthly(source_dir / "economics_monthly.csv")
        self._load_quarterly(source_dir / "economics_quarterly.csv")

    def _load_monthly(self, path: Path) -> None:
        monthly_series = [s for s in SERIES if s.frequency == "Monthly"]
        with path.open(encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                year, month = row["MonthlyDate"].split("-")
                period = date(int(year), int(month), 1)
                for series in monthly_series:
                    if row[series.source_column].strip():
                        self.observations[series.key][period] = float(row[series.source_column])

    def _load_quarterly(self, path: Path) -> None:
        """Quarters are keyed to their last month so they join the monthly calendar."""
        with path.open(encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                year, quarter = row["Quarter"].split("-Q")
                period = date(int(year), int(quarter) * 3, 1)
                self.observations["Real GDP Growth"][period] = float(row["RealGDPGrowth"])
                if WINDOW_START <= period <= WINDOW_END:
                    self.window_quarters.append(period)
        self.window_quarters.sort()

    def in_window(self, series_key: str) -> dict[date, float]:
        return {
            period: value
            for period, value in sorted(self.observations[series_key].items())
            if WINDOW_START <= period <= WINDOW_END
        }

    def expected_periods(self, series: SeriesDefinition) -> list[date]:
        return self.window_quarters if series.frequency == "Quarterly" else self.window_months


class PowerBiTables:
    """Builds each table of the Power BI model as a list of rows."""

    def __init__(self, dataset: MacroDataset) -> None:
        self.dataset = dataset
        self.fences = {
            series.key: IqrFences.from_values(list(dataset.in_window(series.key).values()))
            for series in SERIES
        }

    @staticmethod
    def term_for(period: date) -> tuple[int, PresidentialTerm]:
        for order, term in enumerate(TERMS, start=1):
            if term.first_month <= period <= term.last_month:
                return order, term
        raise ValueError(f"No presidential term covers {period}")

    @staticmethod
    def period_label(series: SeriesDefinition, period: date) -> str:
        return quarter_label(period) if series.frequency == "Quarterly" else month_label(period)

    def dim_date(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for period in self.dataset.window_months:
            order, term = self.term_for(period)
            rows.append({
                "Date": period.isoformat(),
                "Year": period.year,
                "Quarter": quarter_label(period),
                "MonthNumber": period.month,
                "MonthLabel": month_label(period),
                "TermOrder": order,
                "TermLabel": term.label,
                "President": term.president,
                "OfficialTermStart": term.official_start.isoformat(),
                "OfficialTermEnd": term.official_end.isoformat(),
            })
        return rows

    def dim_series(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for order, series in enumerate(SERIES, start=1):
            observed = self.dataset.in_window(series.key)
            values = list(observed.values())
            fences = self.fences[series.key]
            lowest = min(observed, key=lambda period: observed[period])
            highest = max(observed, key=lambda period: observed[period])
            outliers = sum(fences.is_outlier(value) for value in values)
            rows.append({
                "SeriesKey": series.key,
                "SeriesOrder": order,
                "Unit": series.unit,
                "Frequency": series.frequency,
                "Observations": len(values),
                "Mean": round(statistics.mean(values), 2),
                "Median": round(statistics.median(values), 2),
                "StdDev": round(statistics.stdev(values), 2),
                "Min": round(observed[lowest], 2),
                "MinPeriod": self.period_label(series, lowest),
                "Max": round(observed[highest], 2),
                "MaxPeriod": self.period_label(series, highest),
                "Q1": round(fences.q1, 2),
                "Q3": round(fences.q3, 2),
                "IQR": round(fences.iqr, 2),
                "LowerFence": round(fences.lower, 2),
                "UpperFence": round(fences.upper, 2),
                "OutlierCount": outliers,
                "OutlierPercent": round(100 * outliers / len(values), 2),
            })
        return rows

    def fact_monthly(self) -> list[dict[str, object]]:
        inflation = self.dataset.in_window("Inflation YoY")
        policy = self.dataset.in_window("Policy Rate")
        trm = self.dataset.in_window("TRM")
        colcap = self.dataset.in_window("COLCAP")
        returns = self.dataset.in_window("COLCAP Monthly Return")
        unemployment = self.dataset.in_window("Unemployment Rate")
        occupation = self.dataset.in_window("Occupation Rate")
        trm_base = trm[WINDOW_START]
        colcap_base = colcap[WINDOW_START]
        return [
            {
                "Date": period.isoformat(),
                "InflationYoY": round(inflation[period], 4),
                "PolicyRate": round(policy[period], 4),
                "RealPolicyRate": round(policy[period] - inflation[period], 4),
                "TrmAverage": round(trm[period], 2),
                "TrmRebased": round(100 * trm[period] / trm_base, 2),
                "ColcapIndex": round(colcap[period], 2),
                "ColcapRebased": round(100 * colcap[period] / colcap_base, 2),
                "ColcapMonthlyReturn": round(returns[period], 4) if period in returns else "",
                "UnemploymentRate": round(unemployment[period], 4),
                "OccupationRate": round(occupation[period], 4),
            }
            for period in self.dataset.window_months
        ]

    def fact_quarterly(self) -> list[dict[str, object]]:
        return [
            {
                "Date": period.isoformat(),
                "QuarterLabel": quarter_label(period),
                "RealGdpGrowth": value,
            }
            for period, value in self.dataset.in_window("Real GDP Growth").items()
        ]

    def fact_metric_long(self) -> list[dict[str, object]]:
        return [
            {
                "Date": period.isoformat(),
                "SeriesKey": series.key,
                "Value": round(value, 4),
                "IsOutlier": int(self.fences[series.key].is_outlier(value)),
            }
            for series in SERIES
            for period, value in self.dataset.in_window(series.key).items()
        ]

    @staticmethod
    def classify_outlier(series_key: str, period: date) -> str:
        for rule in OUTLIER_RULES:
            if rule.series_key == series_key and rule.first_period <= period <= rule.last_period:
                return rule.classification
        raise ValueError(f"No classification for outlier {series_key} at {period}")

    def fact_outliers(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for series in SERIES:
            fences = self.fences[series.key]
            for period, value in self.dataset.in_window(series.key).items():
                if fences.is_outlier(value):
                    rows.append({
                        "Date": period.isoformat(),
                        "Period": self.period_label(series, period),
                        "SeriesKey": series.key,
                        "Value": round(value, 2),
                        "LowerFence": round(fences.lower, 2),
                        "UpperFence": round(fences.upper, 2),
                        "Direction": "Below lower fence" if value < fences.lower else "Above upper fence",
                        "Classification": self.classify_outlier(series.key, period),
                        "Treatment": "Kept",
                    })
        return rows

    def correlation_summary(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for pair in CORRELATION_PAIRS:
            x_values = self.dataset.in_window(pair.x_key)
            y_values = self.dataset.in_window(pair.y_key)
            matched = [
                (value, y_values[add_months(period, pair.lag_months)])
                for period, value in x_values.items()
                if add_months(period, pair.lag_months) in y_values
            ]
            x_series, y_series = zip(*matched)
            rows.append({
                "VariableX": pair.x_key,
                "VariableY": pair.y_key,
                "LagMonths": pair.lag_months,
                "Correlation": round(statistics.correlation(x_series, y_series), 2),
                "Observations": len(matched),
            })
        return rows

    def coverage_by_year(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for series in SERIES:
            quarterly = series.frequency == "Quarterly"
            all_periods = months_between(date(COVERAGE_FIRST_YEAR, 1, 1), WINDOW_END)
            for year in range(COVERAGE_FIRST_YEAR, WINDOW_END.year + 1):
                expected = [
                    period for period in all_periods
                    if period.year == year and (not quarterly or period.month % 3 == 0)
                ]
                observed = sum(period in self.dataset.observations[series.key] for period in expected)
                rows.append({
                    "SeriesKey": series.key,
                    "Year": year,
                    "ExpectedPeriods": len(expected),
                    "ObservedPeriods": observed,
                    "CoveragePercent": round(100 * observed / len(expected), 1),
                    "InAnalysisWindow": int(year >= WINDOW_START.year),
                })
        return rows

    def missing_data_summary(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for series in SERIES:
            expected = len(self.dataset.expected_periods(series))
            observed = len(self.dataset.in_window(series.key))
            rows.append({
                "SeriesKey": series.key,
                "FirstAvailable": self.period_label(series, min(self.dataset.observations[series.key])),
                "ExpectedInWindow": expected,
                "ObservedInWindow": observed,
                "EmptyInWindow": expected - observed,
                "PreWindowGap": series.pre_window_gap,
                "TreatmentInWindow": series.in_window_treatment,
            })
        return rows

    def term_summary_expected(self) -> list[dict[str, object]]:
        """Reconciliation values for the DAX measures. Not imported into the model."""
        rows: list[dict[str, object]] = []
        for term in TERMS:
            months = months_between(term.first_month, term.last_month)
            metric = lambda key: [
                self.dataset.observations[key][period]
                for period in months if period in self.dataset.observations[key]
            ]
            inflation, policy, trm = metric("Inflation YoY"), metric("Policy Rate"), metric("TRM")
            colcap, unemployment = metric("COLCAP"), metric("Unemployment Rate")
            gdp = metric("Real GDP Growth")
            rows.append({
                "Term": term.label,
                "President": term.president,
                "Months": len(months),
                "InflationAvg": round(statistics.mean(inflation), 2),
                "InflationStart": round(inflation[0], 2),
                "InflationEnd": round(inflation[-1], 2),
                "PolicyAvg": round(statistics.mean(policy), 2),
                "PolicyStart": round(policy[0], 2),
                "PolicyEnd": round(policy[-1], 2),
                "TrmAvg": round(statistics.mean(trm), 2),
                "TrmChangePercent": round(100 * (trm[-1] / trm[0] - 1), 1),
                "ColcapChangePercent": round(100 * (colcap[-1] / colcap[0] - 1), 1),
                "UnemploymentAvg": round(statistics.mean(unemployment), 2),
                "GdpGrowthAvg": round(statistics.mean(gdp), 2),
                "GdpQuarters": len(gdp),
            })
        return rows


def write_table(name: str, rows: list[dict[str, object]]) -> None:
    """Writes UTF-8 with BOM so Power BI detects the encoding."""
    with (OUTPUT_DIR / f"{name}.csv").open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tables = PowerBiTables(MacroDataset(SOURCE_DIR))
    write_table("dim_date", tables.dim_date())
    write_table("dim_series", tables.dim_series())
    write_table("fact_monthly", tables.fact_monthly())
    write_table("fact_quarterly", tables.fact_quarterly())
    write_table("fact_metric_long", tables.fact_metric_long())
    write_table("fact_outliers", tables.fact_outliers())
    write_table("correlation_summary", tables.correlation_summary())
    write_table("coverage_by_year", tables.coverage_by_year())
    write_table("missing_data_summary", tables.missing_data_summary())
    write_table("term_summary_expected", tables.term_summary_expected())


if __name__ == "__main__":
    main()
