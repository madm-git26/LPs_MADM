"""The line between what the agent may do on its own and what needs a human.

The agent is allowed to run the account day to day - mining negatives, pausing
keywords that have proven themselves dead, nudging target CPA - because those
changes are small, reversible and evidence-driven.  It is not allowed to invent
campaigns, move budgets in big steps, or touch anything structural without
someone saying yes.

Every proposed change is classified by :class:`GuardrailPolicy` into one of

    AUTO       apply it, log it, mention it in the daily report
    APPROVAL   show the human the numbers and wait
    BLOCKED    never, regardless of who asks

Configuration lives in ``config/guardrails.yaml`` so the limits can be tuned per
account without touching code.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .errors import ConfigError

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "guardrails.yaml"


class Verdict(str, Enum):
    AUTO = "auto"
    APPROVAL = "approval"
    BLOCKED = "blocked"


@dataclass
class Change:
    """A proposed change, described in business terms rather than protobufs."""

    action: str
    entity: str
    customer_id: str = ""
    campaign_id: int | None = None
    entity_count: int = 1
    before: Any = None
    after: Any = None
    pct_change: float | None = None
    daily_spend_delta: float = 0.0
    campaign_age_days: int | None = None
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        parts = [f"**{self.action}** - {self.entity}"]
        if self.before is not None or self.after is not None:
            parts.append(f"{self.before} -> {self.after}")
        if self.entity_count > 1:
            parts.append(f"({self.entity_count} entities)")
        if self.daily_spend_delta:
            parts.append(f"[{self.daily_spend_delta:+.2f}/day]")
        if self.reason:
            parts.append(f"- {self.reason}")
        return " ".join(parts)


@dataclass
class Decision:
    change: Change
    verdict: Verdict
    rule: str
    message: str

    @property
    def auto(self) -> bool:
        return self.verdict is Verdict.AUTO


DEFAULT_POLICY: dict[str, Any] = {
    "limits": {
        "target_cpa_change_pct": 15.0,
        "bid_modifier_change_pct": 30.0,
        "budget_change_pct": 20.0,
        "max_daily_budget": 250.0,
        "max_entities_per_batch": 50,
        "max_negatives_per_batch": 200,
        "max_ops_per_day": 500,
        "max_daily_spend_delta": 50.0,
        "learning_period_days": 14,
    },
    "actions": {
        # day-to-day hygiene the agent owns
        "add_negative_keywords": "auto",
        "create_shared_negative_list": "auto",
        "attach_shared_negative_list": "auto",
        "pause_keywords": "auto",
        "pause_ads": "auto",
        "set_keyword_bid": "auto",
        "set_target_cpa": "auto",
        "update_budget": "auto",
        "set_location_bid_modifier": "auto",
        "set_device_bid_modifier": "auto",
        "set_income_bid_modifier": "auto",
        "set_demographic_bid_modifier": "auto",
        "set_ad_schedule": "auto",
        "add_keywords": "auto",
        # structural: the human decides
        "create_campaign": "approval",
        "create_ad_group": "approval",
        "create_rsa": "approval",
        "pause_campaign": "approval",
        "pause_ad_group": "approval",
        "add_location_targets": "approval",
        "exclude_locations": "approval",
        "set_bidding_strategy": "approval",
        "apply_recommendation": "approval",
        "upload_offline_conversions": "approval",
        # never
        "remove_campaign": "blocked",
        "remove_ad_group": "blocked",
        "remove_conversion_action": "blocked",
        "change_account_settings": "blocked",
        "bulk_apply_recommendations": "blocked",
    },
    "freeze": {"enabled": False, "until": None, "reason": ""},
}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("PyYAML is required to read guardrail config.") from exc
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class GuardrailPolicy:
    """Classifies changes. Holds no state beyond configuration."""

    def __init__(self, config: dict[str, Any] | None = None, *, read_only: bool = False):
        self.config = _merge(DEFAULT_POLICY, config or {})
        self.read_only = read_only

    @classmethod
    def load(cls, path: str | Path | None = None, *, account: str | None = None,
             read_only: bool = False) -> "GuardrailPolicy":
        """Load the shared policy, then apply this account's overrides on top."""
        data = _load_yaml(Path(path or DEFAULT_CONFIG_PATH))
        config = _merge({}, data.get("default", data))
        if account:
            overrides = (data.get("accounts") or {}).get(str(account))
            if overrides:
                config = _merge(config, overrides)
        return cls(config, read_only=read_only)

    # -- helpers -----------------------------------------------------------

    @property
    def limits(self) -> dict[str, Any]:
        return self.config["limits"]

    def mode(self, action: str) -> str:
        return self.config["actions"].get(action, "approval")

    def frozen(self) -> tuple[bool, str]:
        freeze = self.config.get("freeze") or {}
        if not freeze.get("enabled"):
            return False, ""
        until = freeze.get("until")
        if until:
            try:
                if _dt.date.fromisoformat(str(until)) < _dt.date.today():
                    return False, ""
            except ValueError:
                pass
        return True, freeze.get("reason") or "Account is frozen in guardrails.yaml."

    # -- the decision ------------------------------------------------------

    def evaluate(self, change: Change, *, ops_today: int = 0) -> Decision:
        limits = self.limits
        mode = self.mode(change.action)

        if mode == "blocked":
            return Decision(change, Verdict.BLOCKED, f"actions.{change.action}",
                            f"{change.action} is never done automatically by this agent.")

        if self.read_only:
            return Decision(change, Verdict.APPROVAL, "read_only",
                            "GADS_READ_ONLY=1 - proposing only, nothing will be applied.")

        frozen, why = self.frozen()
        if frozen:
            return Decision(change, Verdict.APPROVAL, "freeze", why)

        if mode == "approval":
            return Decision(change, Verdict.APPROVAL, f"actions.{change.action}",
                            f"{change.action} is a structural change - needs a yes.")

        # From here the action is auto-eligible; numeric limits can still
        # escalate an individual change to approval.
        max_batch = (limits["max_negatives_per_batch"]
                     if "negative" in change.action else limits["max_entities_per_batch"])
        if change.entity_count > max_batch:
            return Decision(change, Verdict.APPROVAL, "limits.max_entities_per_batch",
                            f"{change.entity_count} entities in one batch is above the "
                            f"limit of {max_batch}.")

        if ops_today + change.entity_count > limits["max_ops_per_day"]:
            return Decision(change, Verdict.APPROVAL, "limits.max_ops_per_day",
                            f"Would exceed the daily ceiling of {limits['max_ops_per_day']} "
                            "operations for this account.")

        if (change.campaign_age_days is not None
                and change.campaign_age_days < limits["learning_period_days"]
                and "negative" not in change.action):
            return Decision(change, Verdict.APPROVAL, "limits.learning_period_days",
                            f"Campaign is {change.campaign_age_days} days old; bidding is "
                            f"still learning. Only negatives are applied automatically in "
                            f"the first {limits['learning_period_days']} days.")

        if abs(change.daily_spend_delta) > limits["max_daily_spend_delta"]:
            return Decision(change, Verdict.APPROVAL, "limits.max_daily_spend_delta",
                            f"Changes daily spend by {change.daily_spend_delta:+.2f}, above "
                            f"the {limits['max_daily_spend_delta']:.0f}/day limit.")

        pct_limit = {
            "set_target_cpa": limits["target_cpa_change_pct"],
            "update_budget": limits["budget_change_pct"],
            "set_location_bid_modifier": limits["bid_modifier_change_pct"],
            "set_device_bid_modifier": limits["bid_modifier_change_pct"],
            "set_income_bid_modifier": limits["bid_modifier_change_pct"],
            "set_demographic_bid_modifier": limits["bid_modifier_change_pct"],
        }.get(change.action)
        if pct_limit is not None and change.pct_change is not None:
            if abs(change.pct_change) > pct_limit:
                return Decision(change, Verdict.APPROVAL, "limits.pct_change",
                                f"{change.pct_change:+.1f}% is a bigger move than the "
                                f"{pct_limit:.0f}% step this agent takes on its own.")

        if change.action == "update_budget" and isinstance(change.after, (int, float)):
            if change.after > limits["max_daily_budget"]:
                return Decision(change, Verdict.APPROVAL, "limits.max_daily_budget",
                                f"{change.after:.2f}/day is above the configured ceiling of "
                                f"{limits['max_daily_budget']:.2f}/day.")

        return Decision(change, Verdict.AUTO, f"actions.{change.action}",
                        "Within the limits the agent operates in.")

    def evaluate_all(self, changes: list[Change], *, ops_today: int = 0) -> list[Decision]:
        decisions = []
        running = ops_today
        for change in changes:
            decision = self.evaluate(change, ops_today=running)
            if decision.auto:
                running += change.entity_count
            decisions.append(decision)
        return decisions
