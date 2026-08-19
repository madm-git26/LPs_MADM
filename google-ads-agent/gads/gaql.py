"""GAQL query building, money conversion and metric derivation.

Reports never hand-roll query strings: they use :class:`Query`, which escapes
literals and keeps the selected field list in one place so results can be
flattened by field path.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

MICROS = 1_000_000

# Date ranges Google accepts directly in `DURING`.
DATE_RANGES = {
    "TODAY",
    "YESTERDAY",
    "LAST_7_DAYS",
    "LAST_14_DAYS",
    "LAST_30_DAYS",
    "LAST_BUSINESS_WEEK",
    "LAST_MONTH",
    "LAST_WEEK_MON_SUN",
    "LAST_WEEK_SUN_SAT",
    "THIS_MONTH",
    "THIS_WEEK_MON_TODAY",
    "THIS_WEEK_SUN_TODAY",
}

# Metric columns almost every report wants.
CORE_METRICS = [
    "metrics.impressions",
    "metrics.clicks",
    "metrics.cost_micros",
    "metrics.conversions",
    "metrics.conversions_value",
]

IMPRESSION_SHARE_METRICS = [
    "metrics.search_impression_share",
    "metrics.search_rank_lost_impression_share",
    "metrics.search_budget_lost_impression_share",
    "metrics.search_absolute_top_impression_share",
]


# ---------------------------------------------------------------------------
# money + math
# ---------------------------------------------------------------------------


def to_micros(amount: float) -> int:
    """Currency units -> micros, rounded the way Google expects."""
    return int(round(float(amount) * MICROS))


def from_micros(micros: Any) -> float:
    return round((micros or 0) / MICROS, 2)


def safe_div(numerator: float, denominator: float) -> float:
    return (numerator / denominator) if denominator else 0.0


def derive_metrics(row: dict[str, Any]) -> dict[str, Any]:
    """Add the derived columns a human actually reads: cost, CPC, CPA, CVR, CTR.

    Derived in Python rather than pulled from the API so every report computes
    them identically, and so ratios stay correct after rows are aggregated.
    """
    cost = from_micros(row.get("metrics.cost_micros"))
    clicks = row.get("metrics.clicks") or 0
    impressions = row.get("metrics.impressions") or 0
    conversions = row.get("metrics.conversions") or 0.0
    value = row.get("metrics.conversions_value") or 0.0
    row["cost"] = cost
    row["ctr"] = round(safe_div(clicks, impressions) * 100, 2)
    row["avg_cpc"] = round(safe_div(cost, clicks), 2)
    row["cpa"] = round(safe_div(cost, conversions), 2)
    row["conv_rate"] = round(safe_div(conversions, clicks) * 100, 2)
    row["roas"] = round(safe_div(value, cost), 2)
    return row


def sum_rows(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate raw metric columns, then re-derive ratios from the totals."""
    total = {key: 0 for key in CORE_METRICS}
    for row in rows:
        for key in CORE_METRICS:
            total[key] = (total[key] or 0) + (row.get(key) or 0)
    return derive_metrics(total)


# ---------------------------------------------------------------------------
# query building
# ---------------------------------------------------------------------------


def escape(value: str) -> str:
    """Escape a string literal for use inside a GAQL condition."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def literal(value: Any) -> str:
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return "(" + ", ".join(literal(v) for v in value) + ")"
    if isinstance(value, (_dt.date, _dt.datetime)):
        return f"'{value.isoformat()}'"
    return f"'{escape(value)}'"


@dataclass
class Query:
    """A GAQL query built from parts.

    >>> str(Query("campaign").select("campaign.name").during("LAST_30_DAYS"))
    "SELECT campaign.name FROM campaign WHERE segments.date DURING LAST_30_DAYS"
    """

    resource: str
    fields: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    ordering: list[str] = field(default_factory=list)
    row_limit: int | None = None

    def select(self, *fields: str | Sequence[str]) -> "Query":
        for item in fields:
            if isinstance(item, str):
                self.fields.append(item)
            else:
                self.fields.extend(item)
        return self

    def where(self, condition: str) -> "Query":
        self.conditions.append(condition)
        return self

    def equals(self, field_path: str, value: Any) -> "Query":
        return self.where(f"{field_path} = {literal(value)}")

    def one_of(self, field_path: str, values: Sequence[Any]) -> "Query":
        return self.where(f"{field_path} IN {literal(list(values))}")

    def at_least(self, field_path: str, value: float) -> "Query":
        return self.where(f"{field_path} >= {value}")

    def during(self, date_range: str) -> "Query":
        """Restrict to a Google date range constant, or a custom ``start,end``."""
        date_range = (date_range or "LAST_30_DAYS").strip().upper()
        if date_range in DATE_RANGES:
            return self.where(f"segments.date DURING {date_range}")
        if "," in date_range:
            start, _, end = date_range.partition(",")
            return self.where(
                f"segments.date BETWEEN {literal(start.strip())} AND {literal(end.strip())}"
            )
        raise ValueError(
            f"Unknown date range {date_range!r}. Use one of {sorted(DATE_RANGES)} "
            "or 'YYYY-MM-DD,YYYY-MM-DD'."
        )

    def order_by(self, field_path: str, descending: bool = True) -> "Query":
        self.ordering.append(f"{field_path} {'DESC' if descending else 'ASC'}")
        return self

    def limit(self, count: int | None) -> "Query":
        self.row_limit = count
        return self

    def build(self) -> str:
        if not self.fields:
            raise ValueError("A GAQL query needs at least one selected field.")
        parts = [f"SELECT {', '.join(self.fields)}", f"FROM {self.resource}"]
        if self.conditions:
            parts.append("WHERE " + " AND ".join(self.conditions))
        if self.ordering:
            parts.append("ORDER BY " + ", ".join(self.ordering))
        if self.row_limit:
            parts.append(f"LIMIT {int(self.row_limit)}")
        return " ".join(parts)

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.build()


def enabled_only(query: Query, resource: str) -> Query:
    """Common filter: skip removed entities (they cannot be acted on anyway)."""
    return query.where(f"{resource}.status != 'REMOVED'")
