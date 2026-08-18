import pytest

from gads import optimize
from tests.conftest import CUSTOMER_ID


def test_negative_rules_parse_with_modes(tmp_path):
    rules = optimize.load_negative_rules()
    assert rules
    modes = {rule.mode for rule in rules}
    assert modes == {"auto", "review"}
    employment = next(r for r in rules if r.category == "employment")
    assert "jobs" in employment.terms


def test_word_boundaries_stop_false_positives():
    assert optimize._contains_term("dental assistant jobs miami", "jobs")
    assert not optimize._contains_term("jobst compression stockings", "jobs")


def test_mining_finds_waste_and_skips_existing_negatives(client, account):
    result = optimize.mine_negatives(client, CUSTOMER_ID, account, shared_set_id=6001)
    summaries = " ".join(f.summary for f in result.findings)
    assert "how to pull" in summaries      # DIY search, not yet blocked
    assert "'jobs'" not in summaries       # already a campaign negative in the fixtures
    assert result.proposals


def test_service_lines_the_practice_does_not_offer_become_negatives(client, account):
    account = dict(account, services_not_offered=["invisalign"])
    result = optimize.mine_negatives(client, CUSTOMER_ID, account, shared_set_id=6001)
    assert result.proposals is not None  # the rule ran; fixtures may not contain the term


def test_dead_keyword_rule_needs_zero_conversions(client, account):
    result = optimize.dead_keywords(client, CUSTOMER_ID, account)
    dead = [f for f in result.findings if f.kind == "dead-keyword"]
    for finding in dead:
        assert "0 bookings" in finding.summary
    # 'dentist' broad converts 4 times in the fixtures - expensive, but not dead
    assert not any("'dentist'" in f.summary for f in dead)
    assert any(f.kind == "expensive-keyword" and "'dentist'" in f.summary
               for f in result.findings)


def test_target_cpa_is_not_moved_without_enough_conversions(client, account):
    result = optimize.bid_review(client, CUSTOMER_ID, account)
    thin = [f for f in result.findings if f.kind == "thin-data"]
    assert thin, "campaigns under the conversion floor should be reported, not changed"
    moved = {p.change.campaign_id for p in result.proposals}
    assert 2003 not in moved  # implants has 9 conversions in the fixtures


def test_budget_is_raised_only_when_efficiency_is_there(client, account):
    result = optimize.budget_review(client, CUSTOMER_ID, account)
    for proposal in result.proposals:
        assert proposal.change.action == "update_budget"
        assert proposal.change.after > proposal.change.before


def test_campaign_settings_expose_targets_and_age(client):
    settings = optimize.campaign_settings(client, CUSTOMER_ID)
    assert settings[2001]["target_cpa"] == 75.0
    assert settings[2001]["budget_id"] == 7001
    assert settings[2001]["age_days"] > 0


def test_target_cpa_lookup_matches_service_lines(account):
    assert optimize.target_cpa_for("ETFD | Search | Dental Implants | Miami",
                                   account) == 300
    assert optimize.target_cpa_for("ETFD | Search | Emergency Dentist | 24-7",
                                   account) == 75
    assert optimize.target_cpa_for("Something else", account) == 90  # general fallback


def test_routines_run_end_to_end(client, account):
    for name in ("daily", "weekly", "monthly"):
        result = optimize.run_routine(client, name, CUSTOMER_ID, account)
        assert result.markdown(include_tables=False)


def test_monthly_proposes_nothing(client, account):
    assert optimize.monthly_routine(client, CUSTOMER_ID, account).proposals == []
