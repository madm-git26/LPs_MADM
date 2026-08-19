import pytest

from gads.gaql import (Query, derive_metrics, escape, from_micros, literal,
                       safe_div, sum_rows, to_micros)


def test_query_builds_in_order():
    sql = (Query("campaign")
           .select("campaign.name", ["metrics.clicks", "metrics.cost_micros"])
           .equals("campaign.status", "ENABLED")
           .during("LAST_7_DAYS")
           .order_by("metrics.cost_micros")
           .limit(10)
           .build())
    assert sql == (
        "SELECT campaign.name, metrics.clicks, metrics.cost_micros FROM campaign "
        "WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_7_DAYS "
        "ORDER BY metrics.cost_micros DESC LIMIT 10")


def test_custom_date_range():
    sql = Query("campaign").select("campaign.id").during("2026-01-01,2026-01-31").build()
    assert "segments.date BETWEEN '2026-01-01' AND '2026-01-31'" in sql


def test_unknown_date_range_is_rejected():
    with pytest.raises(ValueError):
        Query("campaign").select("campaign.id").during("LAST_FORTNIGHT")


def test_query_needs_fields():
    with pytest.raises(ValueError):
        Query("campaign").build()


def test_literals_are_escaped():
    assert escape("O'Brien Dental") == "O\\'Brien Dental"
    assert literal(["A", "B"]) == "('A', 'B')"
    assert literal(True) == "TRUE"


def test_micros_round_trip():
    assert to_micros(12.34) == 12_340_000
    assert from_micros(12_340_000) == 12.34
    assert to_micros(0.1) == 100_000  # no float drift


def test_derived_metrics():
    row = derive_metrics({"metrics.cost_micros": 900_000_000, "metrics.clicks": 300,
                          "metrics.impressions": 3000, "metrics.conversions": 10,
                          "metrics.conversions_value": 4500})
    assert row["cost"] == 900.0
    assert row["ctr"] == 10.0
    assert row["avg_cpc"] == 3.0
    assert row["cpa"] == 90.0
    assert row["conv_rate"] == pytest.approx(3.33, abs=0.01)
    assert row["roas"] == 5.0


def test_ratios_are_recomputed_from_totals_not_averaged():
    rows = [
        {"metrics.cost_micros": 100_000_000, "metrics.clicks": 100,
         "metrics.impressions": 1000, "metrics.conversions": 1,
         "metrics.conversions_value": 0},
        {"metrics.cost_micros": 900_000_000, "metrics.clicks": 100,
         "metrics.impressions": 1000, "metrics.conversions": 9,
         "metrics.conversions_value": 0},
    ]
    totals = sum_rows(rows)
    assert totals["cost"] == 1000.0
    assert totals["cpa"] == 100.0  # not the mean of 100 and 100


def test_safe_div_handles_zero():
    assert safe_div(1, 0) == 0.0
