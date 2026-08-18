import pytest

from gads import mutations
from gads.audit import AuditLog
from gads.guardrails import GuardrailPolicy
from tests.conftest import CUSTOMER_ID


def _sub(proposal, index=0):
    """The sub-operation inside a MutateOperation wrapper."""
    wrapper = proposal.operations[index]
    which = wrapper._pb.WhichOneof("operation")
    return getattr(wrapper, which)


def test_negatives_build_one_operation_each(client):
    proposal = mutations.add_negative_keywords(
        client, CUSTOMER_ID, ["jobs", ("free dental", "EXACT")], campaign_id=2002)
    assert len(proposal.operations) == 2
    first = _sub(proposal).create
    assert first.keyword.text == "jobs"
    assert first.negative is True
    assert first.campaign.endswith("/campaigns/2002")
    second = _sub(proposal, 1).create
    assert second.keyword.match_type == client.enums.KeywordMatchTypeEnum.EXACT
    assert proposal.change.entity_count == 2


def test_negatives_require_exactly_one_level(client):
    with pytest.raises(ValueError):
        mutations.add_negative_keywords(client, CUSTOMER_ID, ["jobs"])
    with pytest.raises(ValueError):
        mutations.add_negative_keywords(client, CUSTOMER_ID, ["jobs"],
                                        campaign_id=1, ad_group_id=2)


def test_pause_keywords_sets_status_and_update_mask(client):
    proposal = mutations.pause_keywords(client, CUSTOMER_ID, [(3005, 400008)])
    operation = _sub(proposal)
    assert operation.update.status == client.enums.AdGroupCriterionStatusEnum.PAUSED
    assert "status" in list(operation.update_mask.paths)
    assert proposal.undo["status"] == "ENABLED"


def test_target_cpa_goes_on_the_right_strategy(client):
    smart = mutations.set_target_cpa(client, CUSTOMER_ID, 2001, 82.0, 75.0)
    assert _sub(smart).update.maximize_conversions.target_cpa_micros == 82_000_000
    legacy = mutations.set_target_cpa(client, CUSTOMER_ID, 2001, 82.0, 75.0,
                                      strategy_type="TARGET_CPA")
    assert _sub(legacy).update.target_cpa.target_cpa_micros == 82_000_000
    assert smart.change.pct_change == pytest.approx(9.33, abs=0.01)


def test_budget_change_reports_spend_delta(client):
    proposal = mutations.update_budget(client, CUSTOMER_ID, 7001, 140.0, 120.0)
    assert proposal.change.daily_spend_delta == 20.0
    assert _sub(proposal).update.amount_micros == 140_000_000


def test_shared_list_is_created_and_filled_atomically(client):
    proposal = mutations.create_shared_negative_list(
        client, CUSTOMER_ID, "Master", ["jobs", "free"])
    assert len(proposal.operations) == 3  # the list plus two criteria
    temp = _sub(proposal).create.resource_name
    assert _sub(proposal, 1).create.shared_set == temp


def test_campaign_build_is_one_atomic_request(client):
    proposal = mutations.create_search_campaign(client, CUSTOMER_ID, {
        "name": "ETFD | Search | Implants",
        "daily_budget": 75,
        "target_cpa": 300,
        "geo_target_ids": [9060601, 9060603],
        "proximity": {"latitude": 25.7651, "longitude": -80.2131, "radius_miles": 12},
        "languages": ["en", "es"],
        "ad_schedule": [{"day": "MONDAY", "start_hour": 8, "end_hour": 18}],
    })
    # budget + campaign + 2 geo + proximity + 2 languages + 1 schedule
    assert len(proposal.operations) == 8
    campaign = _sub(proposal, 1).create
    assert campaign.status == client.enums.CampaignStatusEnum.PAUSED
    assert campaign.network_settings.target_search_network is False
    assert campaign.network_settings.target_content_network is False
    assert (campaign.geo_target_type_setting.positive_geo_target_type
            == client.enums.PositiveGeoTargetTypeEnum.PRESENCE)
    assert campaign.maximize_conversions.target_cpa_micros == 300_000_000


def test_rsa_limits_are_checked_before_sending(client):
    with pytest.raises(ValueError, match="3-15 headlines"):
        mutations.create_rsa(client, CUSTOMER_ID, 1, ["a", "b"], ["c", "d"], "https://x")
    with pytest.raises(ValueError, match="2-4 descriptions"):
        mutations.create_rsa(client, CUSTOMER_ID, 1, ["a", "b", "c"], ["only one"],
                             "https://x")
    with pytest.raises(ValueError, match="over 30 chars"):
        mutations.create_rsa(client, CUSTOMER_ID, 1,
                             ["a" * 31, "b", "c"], ["d", "e"], "https://x")


def test_rsa_pins_and_is_created_paused(client):
    proposal = mutations.create_rsa(
        client, CUSTOMER_ID, 3006,
        ["Dental Implants Miami", ("Free Consult", "HEADLINE_1"), "Financing Available"],
        ["Replace missing teeth.", "Most insurance accepted."],
        "https://everythingteeth.com/implants")
    ad = _sub(proposal).create
    assert ad.status == client.enums.AdGroupAdStatusEnum.PAUSED
    headlines = ad.ad.responsive_search_ad.headlines
    assert headlines[1].pinned_field == client.enums.ServedAssetFieldTypeEnum.HEADLINE_1


def test_income_bucket_must_be_valid(client):
    with pytest.raises(ValueError):
        mutations.set_income_bid_modifier(client, CUSTOMER_ID, 2003, "RICH_PEOPLE", 1.2)


def test_executor_applies_auto_and_holds_approval(client, audit_dir):
    proposals = [
        mutations.add_negative_keywords(client, CUSTOMER_ID, ["jobs"], campaign_id=2002),
        mutations.create_search_campaign(client, CUSTOMER_ID,
                                         {"name": "New", "daily_budget": 50}),
    ]
    executor = mutations.Executor(client, GuardrailPolicy.load(), AuditLog(audit_dir))
    result = executor.submit(proposals, label="test")
    assert len(result.applied) == 1
    assert len(result.pending) == 1
    assert result.applied[0].action == "add_negative_keywords"
    assert result.applied[0].validated is True
    assert result.pending[0].action == "create_campaign"


def test_dry_run_applies_nothing_but_still_validates(client, audit_dir):
    proposal = mutations.add_negative_keywords(client, CUSTOMER_ID, ["jobs"],
                                               campaign_id=2002)
    executor = mutations.Executor(client, GuardrailPolicy.load(), AuditLog(audit_dir))
    result = executor.submit([proposal], apply=False, label="dry")
    assert not result.applied
    assert result.pending[0].validated is True
    assert "Dry run" in result.pending[0].message


def test_run_is_recorded_with_an_undo_plan(client, audit_dir):
    audit = AuditLog(audit_dir)
    executor = mutations.Executor(client, GuardrailPolicy.load(), audit)
    result = executor.submit(
        [mutations.pause_keywords(client, CUSTOMER_ID, [(3005, 400008)])], label="test")
    stored = audit.read_run(result.run_id)
    assert stored["records"][0]["undo"]["action"] == "set_keyword_status"
    assert audit.ops_today(CUSTOMER_ID) == 1


def test_rollback_reverses_what_was_applied(client, audit_dir):
    audit = AuditLog(audit_dir)
    executor = mutations.Executor(client, GuardrailPolicy.load(), audit)
    forward = executor.submit([
        mutations.pause_keywords(client, CUSTOMER_ID, [(3005, 400008)]),
        mutations.update_budget(client, CUSTOMER_ID, 7001, 140.0, 120.0),
        mutations.add_negative_keywords(client, CUSTOMER_ID, ["jobs"], campaign_id=2002),
    ], label="forward")
    assert len(forward.applied) == 3

    back = mutations.rollback_run(client, forward.run_id, audit=audit)
    actions = {record.action for record in back.applied}
    assert "set_keyword_status" in actions      # re-enabled
    assert "update_budget" in actions           # restored to 120
    assert "rollback_remove" in actions         # negative removed
    assert not back.pending, "a rollback must not be held back by step limits"


def test_read_only_mode_refuses_to_apply(client, audit_dir, monkeypatch):
    monkeypatch.setattr(client.settings, "read_only", True)
    executor = mutations.Executor(client, GuardrailPolicy(read_only=True),
                                  AuditLog(audit_dir))
    result = executor.submit(
        [mutations.add_negative_keywords(client, CUSTOMER_ID, ["jobs"], campaign_id=2002)])
    assert not result.applied
    assert result.pending[0].rule == "read_only"
