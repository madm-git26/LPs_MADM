"""Every write the agent can make, as reviewable proposals.

A builder never talks to Google.  It returns a :class:`Proposal`: the business
description of the change (for the guardrails and the audit log), the protobuf
operations that would carry it out, and an undo plan.  :class:`Executor` is the
only thing that sends anything, and it always validates first.

    proposals = [mutations.pause_keywords(client, cid, dead)]
    result = Executor(client, policy, audit).submit(proposals)
    print(result.markdown())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from .audit import AuditLog, AuditRecord
from .client import GadsClient
from .errors import ApiError
from .gaql import to_micros
from .guardrails import Change, Decision, GuardrailPolicy, Verdict

# ---------------------------------------------------------------------------
# resource names
# ---------------------------------------------------------------------------


def campaign_path(cid: str, campaign_id: int | str) -> str:
    return f"customers/{cid}/campaigns/{campaign_id}"


def budget_path(cid: str, budget_id: int | str) -> str:
    return f"customers/{cid}/campaignBudgets/{budget_id}"


def ad_group_path(cid: str, ad_group_id: int | str) -> str:
    return f"customers/{cid}/adGroups/{ad_group_id}"


def ad_group_criterion_path(cid: str, ad_group_id: int | str, criterion_id: int | str) -> str:
    return f"customers/{cid}/adGroupCriteria/{ad_group_id}~{criterion_id}"


def campaign_criterion_path(cid: str, campaign_id: int | str, criterion_id: int | str) -> str:
    return f"customers/{cid}/campaignCriteria/{campaign_id}~{criterion_id}"


def ad_group_ad_path(cid: str, ad_group_id: int | str, ad_id: int | str) -> str:
    return f"customers/{cid}/adGroupAds/{ad_group_id}~{ad_id}"


def shared_set_path(cid: str, shared_set_id: int | str) -> str:
    return f"customers/{cid}/sharedSets/{shared_set_id}"


def geo_target_path(geo_target_id: int | str) -> str:
    return f"geoTargetConstants/{geo_target_id}"


# ---------------------------------------------------------------------------
# proposals
# ---------------------------------------------------------------------------


@dataclass
class Proposal:
    """A change plus the operations that would make it happen."""

    change: Change
    operations: list[Any] = field(default_factory=list)
    undo: dict[str, Any] | None = None
    # When the undo plan can only be written once Google hands back resource
    # names (anything created), the executor fills this key in afterwards.
    undo_needs_resource_names: bool = False
    # A few operations (applying a Google recommendation) are not expressible as
    # MutateOperations; they carry a callable instead: fn(client, validate_only).
    service_call: Any = None


def _field_mask(client: GadsClient, message: Any) -> Any:
    from google.api_core import protobuf_helpers

    return protobuf_helpers.field_mask(None, message._pb)


def _pct(before: float | None, after: float | None) -> float | None:
    if not before:
        return None
    return round(((after - before) / before) * 100, 2)


# ---------------------------------------------------------------------------
# negatives and keywords
# ---------------------------------------------------------------------------


def add_negative_keywords(
    client: GadsClient,
    customer_id: str,
    keywords: Sequence[tuple[str, str] | str],
    *,
    campaign_id: int | None = None,
    ad_group_id: int | None = None,
    shared_set_id: int | None = None,
    default_match: str = "PHRASE",
    reason: str = "",
) -> Proposal:
    """Add negatives at campaign, ad group or shared-list level.

    ``keywords`` items are either ``"free dental"`` or ``("free dental", "PHRASE")``.
    Exactly one of campaign_id / ad_group_id / shared_set_id must be given.
    """
    targets = [t for t in (campaign_id, ad_group_id, shared_set_id) if t is not None]
    if len(targets) != 1:
        raise ValueError("Pass exactly one of campaign_id, ad_group_id or shared_set_id.")

    cid = client.customer_id(customer_id)
    pairs = [(k, default_match) if isinstance(k, str) else (k[0], k[1]) for k in keywords]
    operations = []
    for text, match in pairs:
        if shared_set_id is not None:
            wrapper, op = client.operation("shared_criterion")
            criterion = op.create
            criterion.shared_set = shared_set_path(cid, shared_set_id)
        elif campaign_id is not None:
            wrapper, op = client.operation("campaign_criterion")
            criterion = op.create
            criterion.campaign = campaign_path(cid, campaign_id)
            criterion.negative = True
        else:
            wrapper, op = client.operation("ad_group_criterion")
            criterion = op.create
            criterion.ad_group = ad_group_path(cid, ad_group_id)
            criterion.negative = True
        criterion.keyword.text = text
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match.upper()]
        operations.append(wrapper)

    level = ("shared list" if shared_set_id else "campaign" if campaign_id else "ad group")
    where = shared_set_id or campaign_id or ad_group_id
    change = Change(
        action="add_negative_keywords",
        entity=f"{len(pairs)} negatives on {level} {where}",
        customer_id=cid,
        campaign_id=campaign_id,
        entity_count=len(pairs),
        after=[f"{m.lower()}: {t}" for t, m in pairs][:20],
        evidence={"keywords": [[t, m] for t, m in pairs]},
        reason=reason or "Search terms that cannot become patients.",
    )
    return Proposal(change, operations, undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


def add_keywords(
    client: GadsClient,
    customer_id: str,
    ad_group_id: int,
    keywords: Sequence[tuple[str, str] | str],
    *,
    default_match: str = "PHRASE",
    cpc_bid: float | None = None,
    final_url: str | None = None,
    reason: str = "",
) -> Proposal:
    cid = client.customer_id(customer_id)
    pairs = [(k, default_match) if isinstance(k, str) else (k[0], k[1]) for k in keywords]
    operations = []
    for text, match in pairs:
        wrapper, op = client.operation("ad_group_criterion")
        criterion = op.create
        criterion.ad_group = ad_group_path(cid, ad_group_id)
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = text
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match.upper()]
        if cpc_bid:
            criterion.cpc_bid_micros = to_micros(cpc_bid)
        if final_url:
            criterion.final_urls.append(final_url)
        operations.append(wrapper)

    change = Change(
        action="add_keywords",
        entity=f"{len(pairs)} keywords into ad group {ad_group_id}",
        customer_id=cid,
        entity_count=len(pairs),
        after=[f"{m.lower()}: {t}" for t, m in pairs][:20],
        evidence={"keywords": [[t, m] for t, m in pairs], "ad_group_id": ad_group_id},
        reason=reason or "Converting search terms promoted to keywords.",
    )
    return Proposal(change, operations, undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


def set_keyword_status(
    client: GadsClient,
    customer_id: str,
    targets: Sequence[tuple[int, int]],
    status: str = "PAUSED",
    *,
    labels: Sequence[str] = (),
    reason: str = "",
) -> Proposal:
    """Pause or re-enable keywords. ``targets`` are ``(ad_group_id, criterion_id)``."""
    cid = client.customer_id(customer_id)
    status = status.upper()
    operations = []
    for ad_group_id, criterion_id in targets:
        wrapper, op = client.operation("ad_group_criterion")
        criterion = op.update
        criterion.resource_name = ad_group_criterion_path(cid, ad_group_id, criterion_id)
        criterion.status = client.enums.AdGroupCriterionStatusEnum[status]
        op.update_mask.CopyFrom(_field_mask(client, criterion))
        operations.append(wrapper)

    action = "pause_keywords" if status == "PAUSED" else "set_keyword_status"
    shown = ", ".join(labels[:6]) if labels else f"{len(targets)} keywords"
    change = Change(
        action=action,
        entity=f"{status.lower()} {shown}",
        customer_id=cid,
        entity_count=len(targets),
        before="ENABLED" if status == "PAUSED" else status,
        after=status,
        reason=reason or "Spend with no conversions past the decision threshold.",
    )
    return Proposal(
        change,
        operations,
        undo={
            "action": "set_keyword_status",
            "targets": [list(t) for t in targets],
            "status": "ENABLED" if status == "PAUSED" else "PAUSED",
        },
    )


def pause_keywords(client: GadsClient, customer_id: str,
                   targets: Sequence[tuple[int, int]], *, labels: Sequence[str] = (),
                   reason: str = "") -> Proposal:
    return set_keyword_status(client, customer_id, targets, "PAUSED",
                              labels=labels, reason=reason)


def set_keyword_bid(client: GadsClient, customer_id: str, ad_group_id: int,
                    criterion_id: int, new_bid: float, current_bid: float | None = None,
                    *, reason: str = "") -> Proposal:
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("ad_group_criterion")
    criterion = op.update
    criterion.resource_name = ad_group_criterion_path(cid, ad_group_id, criterion_id)
    criterion.cpc_bid_micros = to_micros(new_bid)
    op.update_mask.CopyFrom(_field_mask(client, criterion))
    change = Change(
        action="set_keyword_bid",
        entity=f"keyword {criterion_id} max CPC",
        customer_id=cid,
        before=current_bid,
        after=new_bid,
        pct_change=_pct(current_bid, new_bid),
        reason=reason,
    )
    undo = ({"action": "set_keyword_bid", "ad_group_id": ad_group_id,
             "criterion_id": criterion_id, "value": current_bid} if current_bid else None)
    return Proposal(change, [wrapper], undo=undo)


def pause_ads(client: GadsClient, customer_id: str, targets: Sequence[tuple[int, int]],
              *, reason: str = "") -> Proposal:
    """``targets`` are ``(ad_group_id, ad_id)``."""
    cid = client.customer_id(customer_id)
    operations = []
    for ad_group_id, ad_id in targets:
        wrapper, op = client.operation("ad_group_ad")
        ad = op.update
        ad.resource_name = ad_group_ad_path(cid, ad_group_id, ad_id)
        ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        op.update_mask.CopyFrom(_field_mask(client, ad))
        operations.append(wrapper)
    change = Change(
        action="pause_ads",
        entity=f"{len(targets)} ads",
        customer_id=cid,
        entity_count=len(targets),
        before="ENABLED",
        after="PAUSED",
        reason=reason or "Disapproved or clearly out-performed by its siblings.",
    )
    return Proposal(change, operations, undo={
        "action": "set_ad_status",
        "targets": [list(t) for t in targets],
        "status": "ENABLED",
    })


# ---------------------------------------------------------------------------
# shared negative lists
# ---------------------------------------------------------------------------


def create_shared_negative_list(client: GadsClient, customer_id: str, name: str,
                                keywords: Sequence[tuple[str, str] | str],
                                *, default_match: str = "PHRASE",
                                reason: str = "") -> Proposal:
    """Create a negative list and fill it in one atomic request."""
    cid = client.customer_id(customer_id)
    temp = shared_set_path(cid, -1)
    wrapper, op = client.operation("shared_set")
    shared = op.create
    shared.resource_name = temp
    shared.name = name
    shared.type_ = client.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS
    operations = [wrapper]

    pairs = [(k, default_match) if isinstance(k, str) else (k[0], k[1]) for k in keywords]
    for text, match in pairs:
        sub_wrapper, sub_op = client.operation("shared_criterion")
        criterion = sub_op.create
        criterion.shared_set = temp
        criterion.keyword.text = text
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match.upper()]
        operations.append(sub_wrapper)

    change = Change(
        action="create_shared_negative_list",
        entity=f"shared negative list '{name}' with {len(pairs)} terms",
        customer_id=cid,
        entity_count=len(pairs) + 1,
        after=name,
        evidence={"keywords": [[t, m] for t, m in pairs], "list_name": name},
        reason=reason or "One list every campaign inherits, so waste is blocked once.",
    )
    return Proposal(change, operations, undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


def attach_shared_negative_list(client: GadsClient, customer_id: str, campaign_id: int,
                                shared_set_id: int, *, reason: str = "") -> Proposal:
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("campaign_shared_set")
    link = op.create
    link.campaign = campaign_path(cid, campaign_id)
    link.shared_set = shared_set_path(cid, shared_set_id)
    change = Change(
        action="attach_shared_negative_list",
        entity=f"list {shared_set_id} -> campaign {campaign_id}",
        customer_id=cid,
        campaign_id=campaign_id,
        reason=reason,
    )
    return Proposal(change, [wrapper], undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


# ---------------------------------------------------------------------------
# bidding and budget
# ---------------------------------------------------------------------------


def set_target_cpa(client: GadsClient, customer_id: str, campaign_id: int,
                   new_target: float, current_target: float | None = None,
                   *, strategy_type: str = "MAXIMIZE_CONVERSIONS",
                   campaign_age_days: int | None = None, reason: str = "") -> Proposal:
    """Move a campaign's target CPA.

    Most dental accounts run Maximize Conversions with a target CPA, where the
    target lives on ``maximize_conversions``; older accounts on the standalone
    Target CPA strategy keep it on ``target_cpa``.
    """
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("campaign")
    campaign = op.update
    campaign.resource_name = campaign_path(cid, campaign_id)
    if strategy_type.upper() == "TARGET_CPA":
        campaign.target_cpa.target_cpa_micros = to_micros(new_target)
    else:
        campaign.maximize_conversions.target_cpa_micros = to_micros(new_target)
    op.update_mask.CopyFrom(_field_mask(client, campaign))

    change = Change(
        action="set_target_cpa",
        entity=f"campaign {campaign_id} target CPA",
        customer_id=cid,
        campaign_id=campaign_id,
        before=current_target,
        after=new_target,
        pct_change=_pct(current_target, new_target),
        campaign_age_days=campaign_age_days,
        reason=reason,
    )
    undo = ({"action": "set_target_cpa", "campaign_id": campaign_id,
             "value": current_target, "strategy_type": strategy_type}
            if current_target else None)
    return Proposal(change, [wrapper], undo=undo)


def set_target_roas(client: GadsClient, customer_id: str, campaign_id: int,
                    new_target: float, current_target: float | None = None,
                    *, reason: str = "") -> Proposal:
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("campaign")
    campaign = op.update
    campaign.resource_name = campaign_path(cid, campaign_id)
    campaign.maximize_conversion_value.target_roas = new_target
    op.update_mask.CopyFrom(_field_mask(client, campaign))
    change = Change(
        action="set_target_cpa",  # same risk class as a tCPA move
        entity=f"campaign {campaign_id} target ROAS",
        customer_id=cid, campaign_id=campaign_id,
        before=current_target, after=new_target,
        pct_change=_pct(current_target, new_target), reason=reason,
    )
    return Proposal(change, [wrapper], undo=(
        {"action": "set_target_roas", "campaign_id": campaign_id, "value": current_target}
        if current_target else None))


def update_budget(client: GadsClient, customer_id: str, budget_id: int,
                  new_amount: float, current_amount: float | None = None,
                  *, campaign_id: int | None = None, campaign_age_days: int | None = None,
                  reason: str = "") -> Proposal:
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("campaign_budget")
    budget = op.update
    budget.resource_name = budget_path(cid, budget_id)
    budget.amount_micros = to_micros(new_amount)
    op.update_mask.CopyFrom(_field_mask(client, budget))

    change = Change(
        action="update_budget",
        entity=f"budget {budget_id} daily amount",
        customer_id=cid,
        campaign_id=campaign_id,
        before=current_amount,
        after=new_amount,
        pct_change=_pct(current_amount, new_amount),
        daily_spend_delta=round(new_amount - (current_amount or 0), 2),
        campaign_age_days=campaign_age_days,
        reason=reason,
    )
    undo = ({"action": "update_budget", "budget_id": budget_id, "value": current_amount}
            if current_amount else None)
    return Proposal(change, [wrapper], undo=undo)


# ---------------------------------------------------------------------------
# targeting: geography, schedule, demographics
# ---------------------------------------------------------------------------

# Google's income-range criteria are fixed ids shared by every account.
INCOME_RANGE_CRITERION_IDS = {
    "INCOME_RANGE_0_50": 510001,
    "INCOME_RANGE_50_60": 510002,
    "INCOME_RANGE_60_70": 510003,
    "INCOME_RANGE_70_80": 510004,
    "INCOME_RANGE_80_90": 510005,
    "INCOME_RANGE_90_UP": 510006,
}

DEVICE_CRITERION_IDS = {"MOBILE": 30001, "TABLET": 30002, "DESKTOP": 30000}


def add_location_targets(client: GadsClient, customer_id: str, campaign_id: int,
                         geo_target_ids: Sequence[int | str], *,
                         bid_modifier: float | None = None,
                         negative: bool = False, reason: str = "") -> Proposal:
    """Target (or exclude) locations - postal codes, cities, counties."""
    cid = client.customer_id(customer_id)
    operations = []
    for geo_id in geo_target_ids:
        wrapper, op = client.operation("campaign_criterion")
        criterion = op.create
        criterion.campaign = campaign_path(cid, campaign_id)
        criterion.location.geo_target_constant = geo_target_path(geo_id)
        if negative:
            criterion.negative = True
        elif bid_modifier is not None:
            criterion.bid_modifier = bid_modifier
        operations.append(wrapper)

    change = Change(
        action="exclude_locations" if negative else "add_location_targets",
        entity=f"{len(geo_target_ids)} locations on campaign {campaign_id}",
        customer_id=cid,
        campaign_id=campaign_id,
        entity_count=len(geo_target_ids),
        after=[str(g) for g in geo_target_ids][:20],
        reason=reason,
    )
    return Proposal(change, operations, undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


def set_location_bid_modifier(client: GadsClient, customer_id: str, campaign_id: int,
                              criterion_id: int, modifier: float,
                              current_modifier: float | None = None,
                              *, label: str = "", reason: str = "") -> Proposal:
    """Bid up the postal codes that book, bid down the ones that only click."""
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("campaign_criterion")
    criterion = op.update
    criterion.resource_name = campaign_criterion_path(cid, campaign_id, criterion_id)
    criterion.bid_modifier = modifier
    op.update_mask.CopyFrom(_field_mask(client, criterion))
    change = Change(
        action="set_location_bid_modifier",
        entity=f"location {label or criterion_id} on campaign {campaign_id}",
        customer_id=cid, campaign_id=campaign_id,
        before=current_modifier, after=modifier,
        pct_change=_pct(current_modifier, modifier), reason=reason,
    )
    return Proposal(change, [wrapper], undo=(
        {"action": "set_campaign_criterion_bid_modifier", "campaign_id": campaign_id,
         "criterion_id": criterion_id, "value": current_modifier}
        if current_modifier is not None else None))


def set_proximity_target(client: GadsClient, customer_id: str, campaign_id: int,
                         latitude: float, longitude: float, radius_miles: float,
                         *, reason: str = "") -> Proposal:
    """A radius around the practice - the simplest targeting a local office needs."""
    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("campaign_criterion")
    criterion = op.create
    criterion.campaign = campaign_path(cid, campaign_id)
    criterion.proximity.radius = radius_miles
    criterion.proximity.radius_units = client.enums.ProximityRadiusUnitsEnum.MILES
    criterion.proximity.geo_point.latitude_in_micro_degrees = int(latitude * 1_000_000)
    criterion.proximity.geo_point.longitude_in_micro_degrees = int(longitude * 1_000_000)
    change = Change(
        action="add_location_targets",
        entity=f"{radius_miles} mile radius on campaign {campaign_id}",
        customer_id=cid, campaign_id=campaign_id, reason=reason,
    )
    return Proposal(change, [wrapper], undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


def set_income_bid_modifier(client: GadsClient, customer_id: str, campaign_id: int,
                            bucket: str, modifier: float | None = None,
                            *, exclude: bool = False,
                            current_modifier: float | None = None,
                            create: bool = False, reason: str = "") -> Proposal:
    """Bid on (or exclude) a household-income decile. US accounts only.

    ``bucket`` is an ``INCOME_RANGE_*`` name; ``exclude=True`` removes that
    decile from the campaign entirely, which is what implants and cosmetic
    campaigns usually want for the bottom deciles.
    """
    cid = client.customer_id(customer_id)
    bucket = bucket.upper()
    if bucket not in INCOME_RANGE_CRITERION_IDS:
        raise ValueError(f"bucket must be one of {sorted(INCOME_RANGE_CRITERION_IDS)}")
    criterion_id = INCOME_RANGE_CRITERION_IDS[bucket]

    wrapper, op = client.operation("campaign_criterion")
    if create or exclude:
        criterion = op.create
        criterion.campaign = campaign_path(cid, campaign_id)
        criterion.income_range.type_ = client.enums.IncomeRangeTypeEnum[bucket]
        if exclude:
            criterion.negative = True
        elif modifier is not None:
            criterion.bid_modifier = modifier
        undo = {"action": "remove_criteria"}
        needs_names = True
    else:
        criterion = op.update
        criterion.resource_name = campaign_criterion_path(cid, campaign_id, criterion_id)
        criterion.bid_modifier = modifier
        op.update_mask.CopyFrom(_field_mask(client, criterion))
        undo = {"action": "set_campaign_criterion_bid_modifier", "campaign_id": campaign_id,
                "criterion_id": criterion_id, "value": current_modifier}
        needs_names = False

    change = Change(
        action="set_income_bid_modifier",
        entity=f"{bucket} on campaign {campaign_id}",
        customer_id=cid, campaign_id=campaign_id,
        before=current_modifier, after="excluded" if exclude else modifier,
        pct_change=_pct(current_modifier, modifier) if modifier is not None else None,
        reason=reason,
    )
    return Proposal(change, [wrapper], undo=undo, undo_needs_resource_names=needs_names)


def set_device_bid_modifier(client: GadsClient, customer_id: str, campaign_id: int,
                            device: str, modifier: float,
                            current_modifier: float | None = None,
                            *, reason: str = "") -> Proposal:
    cid = client.customer_id(customer_id)
    device = device.upper()
    if device not in DEVICE_CRITERION_IDS:
        raise ValueError(f"device must be one of {sorted(DEVICE_CRITERION_IDS)}")
    wrapper, op = client.operation("campaign_criterion")
    criterion = op.update
    criterion.resource_name = campaign_criterion_path(
        cid, campaign_id, DEVICE_CRITERION_IDS[device])
    criterion.bid_modifier = modifier
    op.update_mask.CopyFrom(_field_mask(client, criterion))
    change = Change(
        action="set_device_bid_modifier",
        entity=f"{device} bid modifier on campaign {campaign_id}",
        customer_id=cid, campaign_id=campaign_id,
        before=current_modifier, after=modifier,
        pct_change=_pct(current_modifier, modifier), reason=reason,
    )
    return Proposal(change, [wrapper], undo=(
        {"action": "set_campaign_criterion_bid_modifier", "campaign_id": campaign_id,
         "criterion_id": DEVICE_CRITERION_IDS[device], "value": current_modifier}
        if current_modifier is not None else None))


def set_ad_schedule(client: GadsClient, customer_id: str, campaign_id: int,
                    schedule: Sequence[dict[str, Any]],
                    *, replace_criterion_ids: Sequence[int] = (),
                    reason: str = "") -> Proposal:
    """Set the hours a campaign runs, with optional per-slot bid modifiers.

    Each slot: ``{"day": "MONDAY", "start_hour": 8, "end_hour": 18,
    "bid_modifier": 1.2}``.  Passing ``replace_criterion_ids`` removes the
    existing schedule in the same atomic request, so the campaign is never
    briefly unscheduled.
    """
    cid = client.customer_id(customer_id)
    operations = []
    for criterion_id in replace_criterion_ids:
        wrapper, op = client.operation("campaign_criterion")
        op.remove = campaign_criterion_path(cid, campaign_id, criterion_id)
        operations.append(wrapper)

    minute = client.enums.MinuteOfHourEnum
    for slot in schedule:
        wrapper, op = client.operation("campaign_criterion")
        criterion = op.create
        criterion.campaign = campaign_path(cid, campaign_id)
        criterion.ad_schedule.day_of_week = client.enums.DayOfWeekEnum[slot["day"].upper()]
        criterion.ad_schedule.start_hour = int(slot.get("start_hour", 0))
        criterion.ad_schedule.end_hour = int(slot.get("end_hour", 24))
        criterion.ad_schedule.start_minute = minute[slot.get("start_minute", "ZERO")]
        criterion.ad_schedule.end_minute = minute[slot.get("end_minute", "ZERO")]
        if slot.get("bid_modifier") is not None:
            criterion.bid_modifier = float(slot["bid_modifier"])
        operations.append(wrapper)

    change = Change(
        action="set_ad_schedule",
        entity=f"{len(schedule)} schedule slots on campaign {campaign_id}",
        customer_id=cid, campaign_id=campaign_id,
        entity_count=len(operations),
        after=[f"{s['day'][:3]} {s.get('start_hour', 0)}-{s.get('end_hour', 24)}"
               for s in schedule],
        reason=reason or "Aligning serving hours with when the phone is answered.",
    )
    return Proposal(change, operations, undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


# ---------------------------------------------------------------------------
# building new structure
# ---------------------------------------------------------------------------

LANGUAGE_CONSTANTS = {"en": 1000, "es": 1003, "fr": 1002}


def create_search_campaign(client: GadsClient, customer_id: str, spec: dict[str, Any]) -> Proposal:
    """Build a Search campaign - budget, settings, targeting - in one request.

    Recognised keys::

        name, daily_budget, target_cpa, status ("PAUSED" by default),
        geo_target_ids, proximity {latitude, longitude, radius_miles},
        languages ["en", "es"], ad_schedule [...], final_url_suffix,
        search_partners (False), display_expansion (False),
        presence_only (True)

    The campaign is created PAUSED unless told otherwise: nothing this agent
    builds starts spending before a human has looked at it.
    """
    cid = client.customer_id(customer_id)
    name = spec["name"]
    daily_budget = float(spec["daily_budget"])
    temp_budget = budget_path(cid, -1)
    temp_campaign = campaign_path(cid, -2)

    operations = []
    wrapper, op = client.operation("campaign_budget")
    budget = op.create
    budget.resource_name = temp_budget
    budget.name = f"{name} - budget"
    budget.amount_micros = to_micros(daily_budget)
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.explicitly_shared = False
    operations.append(wrapper)

    wrapper, op = client.operation("campaign")
    campaign = op.create
    campaign.resource_name = temp_campaign
    campaign.name = name
    campaign.campaign_budget = temp_budget
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.status = client.enums.CampaignStatusEnum[spec.get("status", "PAUSED").upper()]
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = bool(spec.get("search_partners", False))
    campaign.network_settings.target_content_network = bool(spec.get("display_expansion", False))
    campaign.network_settings.target_partner_search_network = False
    # PRESENCE, not PRESENCE_OR_INTEREST: a practice wants people who are here,
    # not people reading about here.
    presence = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
    campaign.geo_target_type_setting.positive_geo_target_type = (
        presence if spec.get("presence_only", True)
        else client.enums.PositiveGeoTargetTypeEnum.PRESENCE_OR_INTEREST
    )
    campaign.geo_target_type_setting.negative_geo_target_type = (
        client.enums.NegativeGeoTargetTypeEnum.PRESENCE)
    if spec.get("target_cpa"):
        campaign.maximize_conversions.target_cpa_micros = to_micros(spec["target_cpa"])
    else:
        campaign.maximize_conversions.target_cpa_micros = 0
    if spec.get("final_url_suffix"):
        campaign.final_url_suffix = spec["final_url_suffix"]
    operations.append(wrapper)

    for geo_id in spec.get("geo_target_ids", []) or []:
        wrapper, op = client.operation("campaign_criterion")
        criterion = op.create
        criterion.campaign = temp_campaign
        criterion.location.geo_target_constant = geo_target_path(geo_id)
        operations.append(wrapper)

    proximity = spec.get("proximity")
    if proximity:
        wrapper, op = client.operation("campaign_criterion")
        criterion = op.create
        criterion.campaign = temp_campaign
        criterion.proximity.radius = float(proximity["radius_miles"])
        criterion.proximity.radius_units = client.enums.ProximityRadiusUnitsEnum.MILES
        criterion.proximity.geo_point.latitude_in_micro_degrees = int(
            float(proximity["latitude"]) * 1_000_000)
        criterion.proximity.geo_point.longitude_in_micro_degrees = int(
            float(proximity["longitude"]) * 1_000_000)
        operations.append(wrapper)

    for language in spec.get("languages", []) or []:
        constant = LANGUAGE_CONSTANTS.get(str(language).lower())
        if not constant:
            continue
        wrapper, op = client.operation("campaign_criterion")
        criterion = op.create
        criterion.campaign = temp_campaign
        criterion.language.language_constant = f"languageConstants/{constant}"
        operations.append(wrapper)

    minute = client.enums.MinuteOfHourEnum
    for slot in spec.get("ad_schedule", []) or []:
        wrapper, op = client.operation("campaign_criterion")
        criterion = op.create
        criterion.campaign = temp_campaign
        criterion.ad_schedule.day_of_week = client.enums.DayOfWeekEnum[slot["day"].upper()]
        criterion.ad_schedule.start_hour = int(slot.get("start_hour", 0))
        criterion.ad_schedule.end_hour = int(slot.get("end_hour", 24))
        criterion.ad_schedule.start_minute = minute["ZERO"]
        criterion.ad_schedule.end_minute = minute["ZERO"]
        if slot.get("bid_modifier") is not None:
            criterion.bid_modifier = float(slot["bid_modifier"])
        operations.append(wrapper)

    change = Change(
        action="create_campaign",
        entity=f"Search campaign '{name}'",
        customer_id=cid,
        entity_count=len(operations),
        after={"budget": daily_budget, "target_cpa": spec.get("target_cpa"),
               "status": spec.get("status", "PAUSED")},
        daily_spend_delta=daily_budget if spec.get("status", "PAUSED") == "ENABLED" else 0.0,
        reason=spec.get("reason", ""),
    )
    return Proposal(change, operations, undo={"action": "remove_created_campaign"},
                    undo_needs_resource_names=True)


def create_ad_group(client: GadsClient, customer_id: str, campaign_id: int, name: str,
                    *, cpc_bid: float | None = None,
                    keywords: Sequence[tuple[str, str] | str] = (),
                    default_match: str = "PHRASE", reason: str = "") -> Proposal:
    cid = client.customer_id(customer_id)
    temp_ad_group = ad_group_path(cid, -1)
    operations = []

    wrapper, op = client.operation("ad_group")
    ad_group = op.create
    ad_group.resource_name = temp_ad_group
    ad_group.name = name
    ad_group.campaign = campaign_path(cid, campaign_id)
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    if cpc_bid:
        ad_group.cpc_bid_micros = to_micros(cpc_bid)
    operations.append(wrapper)

    pairs = [(k, default_match) if isinstance(k, str) else (k[0], k[1]) for k in keywords]
    for text, match in pairs:
        wrapper, op = client.operation("ad_group_criterion")
        criterion = op.create
        criterion.ad_group = temp_ad_group
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = text
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match.upper()]
        operations.append(wrapper)

    change = Change(
        action="create_ad_group",
        entity=f"ad group '{name}' with {len(pairs)} keywords",
        customer_id=cid, campaign_id=campaign_id, entity_count=len(operations),
        after=name, reason=reason,
    )
    return Proposal(change, operations, undo={"action": "remove_criteria"},
                    undo_needs_resource_names=True)


MAX_HEADLINE_CHARS = 30
MAX_DESCRIPTION_CHARS = 90


def create_rsa(client: GadsClient, customer_id: str, ad_group_id: int,
               headlines: Sequence[str | tuple[str, str]],
               descriptions: Sequence[str | tuple[str, str]],
               final_url: str, *, path1: str = "", path2: str = "",
               reason: str = "") -> Proposal:
    """Create a responsive search ad, checking Google's limits before sending.

    Headlines and descriptions may be ``"text"`` or ``("text", "HEADLINE_1")``
    to pin.  Pin sparingly: a pinned asset stops Google testing that position.
    """
    if not 3 <= len(headlines) <= 15:
        raise ValueError(f"An RSA needs 3-15 headlines, got {len(headlines)}.")
    if not 2 <= len(descriptions) <= 4:
        raise ValueError(f"An RSA needs 2-4 descriptions, got {len(descriptions)}.")

    def unpack(item):
        return (item, None) if isinstance(item, str) else (item[0], item[1])

    for item in headlines:
        text, _ = unpack(item)
        if len(text) > MAX_HEADLINE_CHARS:
            raise ValueError(f"Headline over {MAX_HEADLINE_CHARS} chars: {text!r}")
    for item in descriptions:
        text, _ = unpack(item)
        if len(text) > MAX_DESCRIPTION_CHARS:
            raise ValueError(f"Description over {MAX_DESCRIPTION_CHARS} chars: {text!r}")

    cid = client.customer_id(customer_id)
    wrapper, op = client.operation("ad_group_ad")
    ad_group_ad = op.create
    ad_group_ad.ad_group = ad_group_path(cid, ad_group_id)
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad_group_ad.ad.final_urls.append(final_url)
    if path1:
        ad_group_ad.ad.responsive_search_ad.path1 = path1
    if path2:
        ad_group_ad.ad.responsive_search_ad.path2 = path2

    for item in headlines:
        text, pinned = unpack(item)
        asset = client.get_type("AdTextAsset")
        asset.text = text
        if pinned:
            asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[pinned.upper()]
        ad_group_ad.ad.responsive_search_ad.headlines.append(asset)
    for item in descriptions:
        text, pinned = unpack(item)
        asset = client.get_type("AdTextAsset")
        asset.text = text
        if pinned:
            asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[pinned.upper()]
        ad_group_ad.ad.responsive_search_ad.descriptions.append(asset)

    change = Change(
        action="create_rsa",
        entity=f"RSA in ad group {ad_group_id} ({len(headlines)}H/{len(descriptions)}D)",
        customer_id=cid,
        after={"final_url": final_url, "headlines": [unpack(h)[0] for h in headlines]},
        reason=reason or "New ad variant; created paused so it can be read first.",
    )
    return Proposal(change, [wrapper], undo={"action": "remove_ad"},
                    undo_needs_resource_names=True)


def apply_recommendation(client: GadsClient, customer_id: str, resource_name: str,
                         *, recommendation_type: str = "", reason: str = "") -> Proposal:
    """Apply one specific Google recommendation. Never used in bulk."""
    cid = client.customer_id(customer_id)

    def call(gads: GadsClient, validate_only: bool) -> list[str]:
        if validate_only or gads.mock:
            return []
        service = gads.service("RecommendationService")
        operation = gads.get_type("ApplyRecommendationOperation")
        operation.resource_name = resource_name
        response = service.apply_recommendation(customer_id=cid, operations=[operation])
        return [result.resource_name for result in response.results]

    change = Change(
        action="apply_recommendation",
        entity=f"{recommendation_type or 'recommendation'} {resource_name.split('/')[-1]}",
        customer_id=cid, reason=reason,
    )
    return Proposal(change, [], undo=None, service_call=call)


# ---------------------------------------------------------------------------
# applying: validate -> decide -> apply -> log
# ---------------------------------------------------------------------------


@dataclass
class ExecutionResult:
    run_id: str
    applied: list[AuditRecord] = field(default_factory=list)
    pending: list[AuditRecord] = field(default_factory=list)
    blocked: list[AuditRecord] = field(default_factory=list)
    failed: list[AuditRecord] = field(default_factory=list)

    @property
    def all_records(self) -> list[AuditRecord]:
        return [*self.applied, *self.pending, *self.blocked, *self.failed]

    def markdown(self) -> str:
        lines = [f"### Change run `{self.run_id}`", ""]
        if self.applied:
            lines.append(f"**Applied ({len(self.applied)})**")
            lines += [f"- {r.action}: {r.entity}"
                      + (f" - {r.reason}" if r.reason else "") for r in self.applied]
            lines.append("")
        if self.pending:
            lines.append(f"**Waiting for your approval ({len(self.pending)})**")
            lines += [f"- {r.action}: {r.entity} ({r.before} -> {r.after}) - {r.message}"
                      for r in self.pending]
            lines.append("")
        if self.blocked:
            lines.append(f"**Blocked ({len(self.blocked)})**")
            lines += [f"- {r.action}: {r.message}" for r in self.blocked]
            lines.append("")
        if self.failed:
            lines.append(f"**Rejected by Google ({len(self.failed)})**")
            lines += [f"- {r.action}: {r.error}" for r in self.failed]
            lines.append("")
        if not self.all_records:
            lines.append("_Nothing to change._")
        else:
            lines.append(f"Undo this run with: `python scripts/rollback.py --run-id {self.run_id}`")
        return "\n".join(lines)


class Executor:
    """Turns proposals into changes, in the one order that is safe.

    For every proposal: ask the guardrails, validate against Google with
    ``validate_only=True``, apply only what is auto-approved, and write down
    what happened either way.
    """

    def __init__(self, client: GadsClient, policy: GuardrailPolicy | None = None,
                 audit: AuditLog | None = None):
        self.client = client
        self.policy = policy or GuardrailPolicy(read_only=client.read_only)
        self.audit = audit or AuditLog(client.settings.audit_dir)

    def submit(self, proposals: Iterable[Proposal], *, apply: bool = True,
               label: str = "agent-run") -> ExecutionResult:
        import datetime as _dt

        proposals = [p for p in proposals if p is not None]
        run_id = self.audit.start_run(label)
        result = ExecutionResult(run_id=run_id)
        if not proposals:
            return result

        customer_id = proposals[0].change.customer_id or self.client.customer_id(None)
        ops_today = self.audit.ops_today(customer_id)
        decisions = self.policy.evaluate_all([p.change for p in proposals],
                                             ops_today=ops_today)

        for proposal, decision in zip(proposals, decisions):
            record = self._record(run_id, decision)
            if decision.verdict is Verdict.BLOCKED:
                result.blocked.append(record)
                self.audit.write(record)
                continue

            # Ask Google whether the request is even legal before deciding to
            # apply it - a validation failure is not a change, it is a bug.
            try:
                if proposal.operations:
                    self.client.mutate(decision.change.customer_id, proposal.operations,
                                       validate_only=True)
                record.validated = True
            except ApiError as exc:
                record.error = str(exc)
                result.failed.append(record)
                self.audit.write(record)
                continue

            if not (decision.auto and apply):
                if decision.auto and not apply:
                    record.message = ("Dry run - validated against Google and logged, "
                                      "not applied. Would have been applied automatically.")
                result.pending.append(record)
                self.audit.write(record)
                continue

            try:
                names: list[str] = []
                if proposal.operations:
                    names = self.client.mutate(decision.change.customer_id,
                                               proposal.operations, validate_only=False)
                if proposal.service_call:
                    names += proposal.service_call(self.client, False) or []
                record.applied = True
                record.resource_names = [n for n in names if n]
                record.undo = self._undo_plan(proposal, record.resource_names)
            except Exception as exc:
                record.error = str(exc)
                result.failed.append(record)
                self.audit.write(record)
                continue

            result.applied.append(record)
            self.audit.write(record)

        self.audit.write_run(run_id, result.all_records, meta={
            "customer_id": customer_id,
            "label": label,
            "mock": self.client.mock,
            "applied": len(result.applied),
        })
        return result

    # -- internals ---------------------------------------------------------

    def _record(self, run_id: str, decision: Decision) -> AuditRecord:
        import datetime as _dt

        change = decision.change
        return AuditRecord(
            run_id=run_id,
            timestamp=_dt.datetime.now().isoformat(timespec="seconds"),
            customer_id=change.customer_id,
            action=change.action,
            entity=change.entity,
            verdict=decision.verdict.value,
            rule=decision.rule,
            message=decision.message,
            entity_count=change.entity_count,
            before=change.before,
            after=change.after,
            reason=change.reason,
        )

    @staticmethod
    def _undo_plan(proposal: Proposal, resource_names: list[str]) -> dict[str, Any] | None:
        if not proposal.undo:
            return None
        undo = dict(proposal.undo)
        if proposal.undo_needs_resource_names:
            undo["resource_names"] = resource_names
        return undo


# ---------------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------------

_REMOVE_OPERATION_BY_SEGMENT = {
    "adGroupCriteria": "ad_group_criterion",
    "campaignCriteria": "campaign_criterion",
    "sharedCriteria": "shared_criterion",
    "sharedSets": "shared_set",
    "campaignSharedSets": "campaign_shared_set",
    "adGroupAds": "ad_group_ad",
    "adGroups": "ad_group",
    "campaigns": "campaign",
    "campaignBudgets": "campaign_budget",
}


def undo_proposals(client: GadsClient, undo: dict[str, Any], customer_id: str) -> list[Proposal]:
    """Turn a stored undo plan back into proposals that reverse the change."""
    action = undo.get("action")
    cid = client.customer_id(customer_id)

    if action in {"remove_criteria", "remove_ad", "remove_created_campaign"}:
        operations = []
        # Reverse order so children (criteria, ads) go before their parents.
        for resource_name in reversed(undo.get("resource_names") or []):
            parts = resource_name.split("/")
            if len(parts) < 4:
                continue
            kind = _REMOVE_OPERATION_BY_SEGMENT.get(parts[2])
            if not kind:
                continue
            wrapper, op = client.operation(kind)
            op.remove = resource_name
            operations.append(wrapper)
        if not operations:
            return []
        change = Change(action="rollback_remove", customer_id=cid,
                        entity=f"remove {len(operations)} entities created by that run",
                        entity_count=len(operations), reason="rollback")
        return [Proposal(change, operations)]

    if action == "set_keyword_status":
        targets = [tuple(t) for t in undo.get("targets", [])]
        return [set_keyword_status(client, cid, targets, undo.get("status", "ENABLED"),
                                   reason="rollback")]

    if action == "set_ad_status":
        targets = [tuple(t) for t in undo.get("targets", [])]
        operations = []
        for ad_group_id, ad_id in targets:
            wrapper, op = client.operation("ad_group_ad")
            ad = op.update
            ad.resource_name = ad_group_ad_path(cid, ad_group_id, ad_id)
            ad.status = client.enums.AdGroupAdStatusEnum[undo.get("status", "ENABLED")]
            op.update_mask.CopyFrom(_field_mask(client, ad))
            operations.append(wrapper)
        change = Change(action="rollback_ad_status", customer_id=cid,
                        entity=f"{len(targets)} ads", entity_count=len(targets),
                        reason="rollback")
        return [Proposal(change, operations)]

    if action == "set_target_cpa" and undo.get("value"):
        return [set_target_cpa(client, cid, undo["campaign_id"], float(undo["value"]),
                               strategy_type=undo.get("strategy_type", "MAXIMIZE_CONVERSIONS"),
                               reason="rollback")]

    if action == "set_target_roas" and undo.get("value"):
        return [set_target_roas(client, cid, undo["campaign_id"], float(undo["value"]),
                                reason="rollback")]

    if action == "update_budget" and undo.get("value"):
        return [update_budget(client, cid, undo["budget_id"], float(undo["value"]),
                              reason="rollback")]

    if action == "set_keyword_bid" and undo.get("value"):
        return [set_keyword_bid(client, cid, undo["ad_group_id"], undo["criterion_id"],
                                float(undo["value"]), reason="rollback")]

    if action == "set_campaign_criterion_bid_modifier" and undo.get("value") is not None:
        return [set_location_bid_modifier(client, cid, undo["campaign_id"],
                                          undo["criterion_id"], float(undo["value"]),
                                          reason="rollback")]

    return []


def rollback_run(client: GadsClient, run_id: str, *, audit: AuditLog | None = None,
                 apply: bool = True) -> ExecutionResult:
    """Reverse everything that was applied in a run."""
    audit = audit or AuditLog(client.settings.audit_dir)
    data = audit.read_run(run_id)
    customer_id = data.get("meta", {}).get("customer_id") or client.customer_id(None)

    proposals: list[Proposal] = []
    for record in reversed(data["records"]):
        if not record.get("applied") or not record.get("undo"):
            continue
        proposals.extend(undo_proposals(client, record["undo"], customer_id))

    # A rollback is authorised by the human running it, so it does not go
    # through the same approval gate - restoring a previous value must not be
    # blocked by the same step limits that governed the change. It is still
    # validated against Google and written to the audit log.
    policy = GuardrailPolicy(
        {
            "actions": {p.change.action: "auto" for p in proposals},
            "limits": {
                "target_cpa_change_pct": 1e9,
                "bid_modifier_change_pct": 1e9,
                "budget_change_pct": 1e9,
                "max_daily_budget": 1e9,
                "max_daily_spend_delta": 1e9,
                "max_entities_per_batch": 10_000,
                "max_negatives_per_batch": 10_000,
                "max_ops_per_day": 100_000,
                "learning_period_days": 0,
            },
        },
        read_only=client.read_only,
    )
    return Executor(client, policy, audit).submit(proposals, apply=apply,
                                                  label=f"rollback-{run_id}")
