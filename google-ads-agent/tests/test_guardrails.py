import pytest

from gads.guardrails import Change, GuardrailPolicy, Verdict


def change(**kwargs) -> Change:
    base = dict(action="add_negative_keywords", entity="x", customer_id="1234567890")
    base.update(kwargs)
    return Change(**base)


def test_routine_work_is_automatic(policy):
    assert policy.evaluate(change()).verdict is Verdict.AUTO
    assert policy.evaluate(change(action="pause_keywords")).verdict is Verdict.AUTO


def test_structural_work_needs_approval(policy):
    for action in ("create_campaign", "create_rsa", "add_location_targets",
                   "pause_campaign", "apply_recommendation"):
        assert policy.evaluate(change(action=action)).verdict is Verdict.APPROVAL, action


def test_dangerous_work_is_blocked(policy):
    for action in ("remove_campaign", "change_account_settings",
                   "bulk_apply_recommendations"):
        assert policy.evaluate(change(action=action)).verdict is Verdict.BLOCKED, action


def test_big_target_cpa_step_escalates(policy):
    small = policy.evaluate(change(action="set_target_cpa", before=100, after=110,
                                   pct_change=10.0))
    big = policy.evaluate(change(action="set_target_cpa", before=100, after=160,
                                 pct_change=60.0))
    assert small.verdict is Verdict.AUTO
    assert big.verdict is Verdict.APPROVAL
    assert big.rule == "limits.pct_change"


def test_budget_above_ceiling_escalates(policy):
    decision = policy.evaluate(change(action="update_budget", before=240, after=300,
                                      pct_change=8.0, daily_spend_delta=20))
    assert decision.verdict is Verdict.APPROVAL
    assert decision.rule == "limits.max_daily_budget"


def test_large_spend_delta_escalates(policy):
    decision = policy.evaluate(change(action="update_budget", before=100, after=110,
                                      pct_change=10.0, daily_spend_delta=90))
    assert decision.verdict is Verdict.APPROVAL
    assert decision.rule == "limits.max_daily_spend_delta"


def test_batch_size_limits_differ_for_negatives(policy):
    assert policy.evaluate(change(entity_count=150)).verdict is Verdict.AUTO
    assert policy.evaluate(change(action="pause_keywords",
                                  entity_count=150)).verdict is Verdict.APPROVAL


def test_learning_period_protects_new_campaigns_except_negatives(policy):
    assert policy.evaluate(change(action="set_target_cpa", pct_change=5.0,
                                  campaign_age_days=3)).verdict is Verdict.APPROVAL
    assert policy.evaluate(change(campaign_age_days=3)).verdict is Verdict.AUTO


def test_daily_operation_ceiling(policy):
    decision = policy.evaluate(change(entity_count=10), ops_today=499)
    assert decision.verdict is Verdict.APPROVAL
    assert decision.rule == "limits.max_ops_per_day"


def test_read_only_mode_proposes_everything():
    policy = GuardrailPolicy(read_only=True)
    assert policy.evaluate(change()).verdict is Verdict.APPROVAL


def test_freeze_stops_automatic_changes():
    policy = GuardrailPolicy({"freeze": {"enabled": True, "reason": "practice closed"}})
    decision = policy.evaluate(change())
    assert decision.verdict is Verdict.APPROVAL
    assert "practice closed" in decision.message


def test_expired_freeze_is_ignored():
    policy = GuardrailPolicy({"freeze": {"enabled": True, "until": "2020-01-01"}})
    assert policy.evaluate(change()).verdict is Verdict.AUTO


def test_per_account_overrides_are_applied(tmp_path):
    config = tmp_path / "guardrails.yaml"
    config.write_text(
        "default:\n"
        "  actions:\n"
        "    update_budget: auto\n"
        "accounts:\n"
        "  '1234567890':\n"
        "    actions:\n"
        "      update_budget: approval\n",
        encoding="utf-8")
    strict = GuardrailPolicy.load(config, account="1234567890")
    relaxed = GuardrailPolicy.load(config, account="9999999999")
    assert strict.evaluate(change(action="update_budget")).verdict is Verdict.APPROVAL
    assert relaxed.evaluate(change(action="update_budget")).verdict is Verdict.AUTO


def test_evaluate_all_accumulates_towards_the_daily_ceiling(policy):
    # 200 negatives at a time: the third batch crosses the 500 ops/day ceiling.
    decisions = policy.evaluate_all([change(entity_count=200) for _ in range(3)])
    assert [d.verdict for d in decisions] == [Verdict.AUTO, Verdict.AUTO, Verdict.APPROVAL]
    assert decisions[2].rule == "limits.max_ops_per_day"
