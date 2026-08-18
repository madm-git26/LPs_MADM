import pytest

from gads import reports
from tests.conftest import CUSTOMER_ID


def test_every_report_runs_against_fixtures(client):
    for name in sorted(reports.REPORTS):
        report = reports.run_report(client, name, customer_id=CUSTOMER_ID)
        assert isinstance(report, reports.Report), name
        assert report.markdown(), name


def test_account_summary_derives_money_and_ratios(client):
    report = reports.account_summary(client, CUSTOMER_ID)
    assert report.rows
    row = report.rows[0]
    assert row["cost"] == row["metrics.cost_micros"] / 1_000_000
    assert report.totals["cost"] == pytest.approx(
        sum(r["cost"] for r in report.rows), abs=0.01)


def _cell_separators(line: str) -> int:
    """Pipes that actually split the row - escaped ones are content."""
    return line.count("|") - line.count("\\|")


def test_campaign_names_with_pipes_do_not_break_the_table(client):
    # Campaign names in this account convention are "ETFD | Search | Emergency".
    table = reports.account_summary(client, CUSTOMER_ID).markdown()
    header_columns = _cell_separators(table.splitlines()[2])
    body = [l for l in table.splitlines()[4:] if l.startswith("|")]
    assert body
    for line in body:
        assert _cell_separators(line) == header_columns


def test_budget_pacing_computes_daily_spend(client):
    report = reports.budget_pacing(client, CUSTOMER_ID, date_range="LAST_30_DAYS")
    row = report.rows[0]
    assert row["daily_budget"] > 0
    assert row["avg_daily_spend"] == pytest.approx(row["cost"] / 30, abs=0.01)


def test_search_terms_can_be_filtered_to_the_mining_queue(client):
    everything = reports.search_terms(client, CUSTOMER_ID)
    unmapped = reports.search_terms(client, CUSTOMER_ID, only_unmapped=True)
    assert len(unmapped.rows) < len(everything.rows)
    assert all(r["search_term_view.status"] == "NONE" for r in unmapped.rows)


def test_disapprovals_only_returns_disapproved_ads(client):
    report = reports.disapprovals(client, CUSTOMER_ID)
    assert report.rows
    assert all(r["ad_group_ad.policy_summary.approval_status"] == "DISAPPROVED"
               for r in report.rows)


def test_negative_keywords_covers_all_three_levels(client):
    report = reports.negative_keywords(client, CUSTOMER_ID)
    assert {r["level"] for r in report.rows} == {"campaign", "ad_group", "shared_list"}


def test_change_history_is_capped_to_the_retention_window(client):
    report = reports.change_history(client, CUSTOMER_ID, days=90)
    assert "LIMIT" in report.query
    assert "29 days" in report.name


def test_unknown_report_name_is_rejected(client):
    with pytest.raises(ValueError):
        reports.run_report(client, "not_a_report", customer_id=CUSTOMER_ID)
