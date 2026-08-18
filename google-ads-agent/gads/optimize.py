"""The decisions themselves: what to change, and the evidence for it.

The rules here are deliberately conservative and deliberately explicit.  Two
things ruin a dental account faster than bad copy: acting on ten clicks, and
moving bids in big steps.  So every rule states its own minimum evidence, and
every proposal it returns carries the numbers that justified it into the audit
log.

Nothing in this module talks to Google directly except through
:mod:`gads.reports`; nothing here applies anything - :class:`gads.mutations.Executor`
and the guardrails decide what actually happens.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import mutations, reports
from .client import GadsClient
from .gaql import Query, from_micros, safe_div
from .reports import Report

NEGATIVES_PATH = Path(__file__).resolve().parents[1] / "config" / "dental_negatives_master.txt"


# ---------------------------------------------------------------------------
# results
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    """Something a human should know, whether or not the agent acted on it."""

    kind: str
    severity: str  # "info" | "watch" | "act"
    summary: str
    detail: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def line(self) -> str:
        icon = {"act": "!", "watch": "~", "info": "-"}.get(self.severity, "-")
        text = f"{icon} **{self.summary}**"
        if self.detail:
            text += f" - {self.detail}"
        return text


@dataclass
class RoutineResult:
    name: str
    findings: list[Finding] = field(default_factory=list)
    proposals: list[Any] = field(default_factory=list)
    tables: dict[str, Report] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def extend(self, other: "RoutineResult") -> "RoutineResult":
        self.findings.extend(other.findings)
        self.proposals.extend(other.proposals)
        self.tables.update(other.tables)
        self.notes.extend(other.notes)
        return self

    def markdown(self, *, include_tables: bool = True) -> str:
        lines = [f"## {self.name}", ""]
        for severity in ("act", "watch", "info"):
            group = [f for f in self.findings if f.severity == severity]
            if not group:
                continue
            heading = {"act": "Needs action", "watch": "Worth watching",
                       "info": "For the record"}[severity]
            lines += [f"**{heading}**", *[f.line() for f in group], ""]
        if self.proposals:
            lines += [f"**Proposed changes ({len(self.proposals)})**"]
            lines += [f"- {p.change.describe()}" for p in self.proposals]
            lines.append("")
        if not self.findings and not self.proposals:
            lines += ["Nothing to do - the account is inside its rules today.", ""]
        for note in self.notes:
            lines.append(f"> {note}\n")
        if include_tables:
            for table in self.tables.values():
                lines += [table.markdown(limit=15), ""]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# account metadata
# ---------------------------------------------------------------------------


def campaign_settings(client: GadsClient, customer_id: str | None = None) -> dict[int, dict[str, Any]]:
    """Current bidding, budget and age for every live campaign."""
    query = (
        Query("campaign")
        .select("campaign.id", "campaign.name", "campaign.status",
                "campaign.bidding_strategy_type",
                "campaign.maximize_conversions.target_cpa_micros",
                "campaign.target_cpa.target_cpa_micros",
                "campaign.start_date_time",
                "campaign_budget.id", "campaign_budget.amount_micros")
        .where("campaign.status != 'REMOVED'")
    )
    try:
        rows = client.search(customer_id, query.build())
    except Exception:
        # Older API surfaces spell it campaign.start_date.
        rows = client.search(customer_id, query.build().replace(
            "campaign.start_date_time", "campaign.start_date"))

    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        campaign_id = row.get("campaign.id")
        target = (row.get("campaign.maximize_conversions.target_cpa_micros")
                  or row.get("campaign.target_cpa.target_cpa_micros") or 0)
        started = row.get("campaign.start_date_time") or row.get("campaign.start_date") or ""
        out[campaign_id] = {
            "id": campaign_id,
            "name": row.get("campaign.name"),
            "status": row.get("campaign.status"),
            "strategy": row.get("campaign.bidding_strategy_type"),
            "target_cpa": from_micros(target) or None,
            "budget_id": row.get("campaign_budget.id"),
            "daily_budget": from_micros(row.get("campaign_budget.amount_micros")),
            "started": started,
            "age_days": _age_days(started),
        }
    return out


def _age_days(started: str) -> int | None:
    import datetime as dt

    if not started:
        return None
    try:
        date = dt.date.fromisoformat(str(started)[:10])
    except ValueError:
        return None
    return (dt.date.today() - date).days


def target_cpa_for(campaign_name: str, account: dict[str, Any],
                   fallback: float | None = None) -> float | None:
    """Pick the service-line target CPA that matches a campaign's name."""
    targets = ((account.get("goals") or {}).get("target_cpa") or {})
    name = (campaign_name or "").lower()
    for line, value in targets.items():
        if line.lower() in name:
            return float(value)
    aliases = {"emergency": ["emergency", "urgent", "24-7", "24/7", "tooth pain"],
               "implants": ["implant"],
               "ortho": ["ortho", "invisalign", "braces", "aligner"],
               "cosmetic": ["cosmetic", "veneer", "whitening", "smile makeover"],
               "general": ["general", "family", "cleaning", "checkup", "dentist"]}
    for line, words in aliases.items():
        if line in targets and any(word in name for word in words):
            return float(targets[line])
    return fallback or (float(targets["general"]) if "general" in targets else None)


# ---------------------------------------------------------------------------
# negative keyword mining
# ---------------------------------------------------------------------------


@dataclass
class NegativeRule:
    category: str
    mode: str
    match: str
    terms: list[str]


def load_negative_rules(path: str | Path | None = None) -> list[NegativeRule]:
    """Parse config/dental_negatives_master.txt."""
    path = Path(path or NEGATIVES_PATH)
    rules: list[NegativeRule] = []
    current: NegativeRule | None = None
    header = re.compile(r"^\[(?P<category>[^\]]+)\]\s*(?P<attrs>.*)$")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = header.match(line)
        if match:
            attrs = dict(
                part.split("=", 1) for part in match.group("attrs").split() if "=" in part
            )
            current = NegativeRule(category=match.group("category"),
                                   mode=attrs.get("mode", "review"),
                                   match=attrs.get("match", "PHRASE"), terms=[])
            rules.append(current)
            continue
        if current is not None:
            current.terms.append(line.lower())
    return rules


def _contains_term(search_term: str, term: str) -> bool:
    """Word-boundary containment, so "job" does not fire on "jobst"."""
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", search_term) is not None


def mine_negatives(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
                   *, date_range: str = "LAST_30_DAYS",
                   shared_set_id: int | None = None,
                   negatives_path: str | Path | None = None,
                   waste_multiple: float = 2.0) -> RoutineResult:
    """Find search terms that cannot become patients, and block them.

    Two sources of negatives:

    1. The master list - categories every dental account wants gone, plus the
       services this practice does not offer and the insurance it does not take.
    2. Pure waste - a term that spent more than ``waste_multiple`` x target CPA
       and booked nobody gets blocked as an exact negative.
    """
    account = account or {}
    result = RoutineResult(name="Negative keyword mining")
    terms_report = reports.search_terms(client, customer_id, date_range=date_range)
    result.tables["search_terms"] = terms_report
    if not terms_report.rows:
        result.notes.append("No search term data in this window.")
        return result

    rules = load_negative_rules(negatives_path)
    auto_terms: dict[str, str] = {}
    review_terms: dict[str, str] = {}
    for rule in rules:
        bucket = auto_terms if rule.mode == "auto" else review_terms
        for term in rule.terms:
            bucket.setdefault(term, rule.category)

    # Practice-specific negatives beat any generic list.
    for service in account.get("services_not_offered", []) or []:
        auto_terms.setdefault(str(service).lower(), "service not offered")
    for payer in ((account.get("insurance") or {}).get("not_accepted") or []):
        auto_terms.setdefault(str(payer).lower(), "insurance not accepted")

    existing = {
        str(row.get("text", "")).lower()
        for row in reports.negative_keywords(client, customer_id).rows
    }

    matched: dict[str, dict[str, Any]] = {}
    flagged: list[tuple[str, str, str]] = []
    waste: list[dict[str, Any]] = []
    default_target = target_cpa_for("", account) or 100.0

    for row in terms_report.rows:
        term = str(row.get("search_term_view.search_term") or "").lower()
        if not term:
            continue
        cost = row.get("cost") or 0.0
        conversions = row.get("metrics.conversions") or 0

        hit = next((t for t in auto_terms if _contains_term(term, t)), None)
        if hit and hit not in existing:
            entry = matched.setdefault(hit, {"category": auto_terms[hit], "cost": 0.0,
                                             "terms": [], "clicks": 0})
            entry["cost"] += cost
            entry["clicks"] += row.get("metrics.clicks") or 0
            entry["terms"].append(term)
            continue
        if hit:
            continue

        review_hit = next((t for t in review_terms if _contains_term(term, t)), None)
        if review_hit and review_hit not in existing:
            flagged.append((term, review_hit, review_terms[review_hit]))
            continue

        if conversions == 0 and cost >= waste_multiple * default_target and term not in existing:
            waste.append({"term": term, "cost": cost, "clicks": row.get("metrics.clicks")})

    if matched:
        keywords = [(term, "PHRASE") for term in sorted(matched)]
        wasted = sum(entry["cost"] for entry in matched.values())
        reason = (f"{len(keywords)} master-list matches; "
                  f"${wasted:,.0f} spent on them in {date_range.lower().replace('_', ' ')}")
        if shared_set_id:
            result.proposals.append(mutations.add_negative_keywords(
                client, customer_id, keywords, shared_set_id=shared_set_id, reason=reason))
        else:
            result.notes.append(
                "No shared negative list configured - negatives would have to go on "
                "each campaign. Create one with mutations.create_shared_negative_list "
                "so every campaign inherits the same block list.")
            result.proposals.append(mutations.create_shared_negative_list(
                client, customer_id, "Dental - master negatives", keywords, reason=reason))
        for term, entry in sorted(matched.items(), key=lambda kv: -kv[1]["cost"])[:10]:
            result.findings.append(Finding(
                kind="negative", severity="act",
                summary=f"'{term}' ({entry['category']})",
                detail=f"${entry['cost']:,.0f} on {len(entry['terms'])} search terms, "
                       f"{entry['clicks']} clicks",
                evidence=entry))

    if waste:
        waste.sort(key=lambda item: -item["cost"])
        # A wasteful term is blocked exactly, in the campaign that served it -
        # the same words can be perfectly good traffic elsewhere in the account.
        wasted_terms = {item["term"] for item in waste}
        by_campaign: dict[int, list[str]] = {}
        for row in terms_report.rows:
            term = str(row.get("search_term_view.search_term") or "").lower()
            if term in wasted_terms:
                campaign_id = row.get("campaign.id")
                if campaign_id:
                    by_campaign.setdefault(campaign_id, []).append(term)
        for campaign_id, terms in by_campaign.items():
            result.proposals.append(mutations.add_negative_keywords(
                client, customer_id, [(t, "EXACT") for t in sorted(set(terms))],
                campaign_id=campaign_id,
                reason=f"spent over {waste_multiple:.0f}x target CPA with no bookings"))
        for item in waste[:10]:
            result.findings.append(Finding(
                kind="waste", severity="act",
                summary=f"'{item['term']}' spent ${item['cost']:,.0f}, booked nobody",
                detail=f"{item['clicks']} clicks and no conversions",
                evidence=item))

    for term, hit, category in flagged[:25]:
        result.findings.append(Finding(
            kind="negative-review", severity="watch",
            summary=f"'{term}' matches the '{category}' list",
            detail=f"Blocked only if this practice does not want it ('{hit}'). "
                   "Decide once and it moves to the auto list."))

    return result


# ---------------------------------------------------------------------------
# keywords
# ---------------------------------------------------------------------------


def dead_keywords(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
                  *, date_range: str = "LAST_30_DAYS", min_clicks: int = 100,
                  spend_multiple: float = 3.0) -> RoutineResult:
    """Pause keywords that have had a fair chance and produced nothing.

    A keyword is dead when it has spent more than ``spend_multiple`` x its
    campaign's target CPA, or taken ``min_clicks`` clicks, without a single
    conversion.  Anything short of that is noise, not a verdict.
    """
    account = account or {}
    result = RoutineResult(name="Dead keyword sweep")
    report = reports.keyword_performance(client, customer_id, date_range=date_range)
    result.tables["keywords"] = report
    settings = campaign_settings(client, customer_id)

    to_pause: list[tuple[int, int]] = []
    labels: list[str] = []
    wasted = 0.0
    for row in report.rows:
        if row.get("ad_group_criterion.status") != "ENABLED":
            continue
        conversions = row.get("metrics.conversions") or 0
        clicks = row.get("metrics.clicks") or 0
        cost = row.get("cost") or 0.0
        campaign_name = row.get("campaign.name") or ""
        target = target_cpa_for(campaign_name, account) or 100.0
        keyword = row.get("ad_group_criterion.keyword.text")

        if conversions == 0 and (clicks >= min_clicks or cost >= spend_multiple * target):
            ad_group_id = row.get("ad_group.id")
            criterion_id = row.get("ad_group_criterion.criterion_id")
            if ad_group_id and criterion_id:
                to_pause.append((ad_group_id, criterion_id))
                labels.append(f"{keyword} [{row.get('ad_group_criterion.keyword.match_type')}]")
                wasted += cost
                result.findings.append(Finding(
                    kind="dead-keyword", severity="act",
                    summary=f"'{keyword}' - ${cost:,.0f}, {clicks} clicks, 0 bookings",
                    detail=f"target CPA ${target:,.0f} in {campaign_name}",
                    evidence={"keyword": keyword, "cost": cost, "clicks": clicks}))
        elif conversions and cost / conversions > 2 * target and cost >= 2 * target:
            result.findings.append(Finding(
                kind="expensive-keyword", severity="watch",
                summary=f"'{keyword}' CPA ${cost / conversions:,.0f} vs target ${target:,.0f}",
                detail="Not dead, but twice the target - tighten the match type, "
                       "check the landing page, or move it to its own ad group.",
                evidence={"keyword": keyword, "cpa": round(cost / conversions, 2)}))

        quality = row.get("ad_group_criterion.quality_info.quality_score")
        if quality and quality <= 4 and clicks >= 25:
            result.findings.append(Finding(
                kind="quality-score", severity="watch",
                summary=f"'{keyword}' Quality Score {quality}",
                detail="Low QS on a keyword with real traffic means the ad or the "
                       "landing page does not match the search - fix that before bidding more."))

    if to_pause:
        result.proposals.append(mutations.pause_keywords(
            client, customer_id, to_pause, labels=labels,
            reason=f"no conversions on ${wasted:,.0f} of spend in "
                   f"{date_range.lower().replace('_', ' ')}"))
    return result


# ---------------------------------------------------------------------------
# bidding and budget
# ---------------------------------------------------------------------------


def bid_review(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
               *, date_range: str = "LAST_30_DAYS", min_conversions: int = 30,
               step_pct: float = 0.10) -> RoutineResult:
    """Nudge target CPA where there is enough evidence to justify a step.

    Raise when the campaign is hitting its target but losing impression share to
    rank - that is demand it can afford.  Lower when it is over target with
    enough conversions to be sure.  Never more than one step at a time.
    """
    account = account or {}
    result = RoutineResult(name="Target CPA review")
    summary = reports.account_summary(client, customer_id, date_range=date_range)
    result.tables["campaigns"] = summary
    settings = campaign_settings(client, customer_id)

    for row in summary.rows:
        campaign_id = row.get("campaign.id")
        name = row.get("campaign.name") or ""
        meta = settings.get(campaign_id, {})
        conversions = row.get("metrics.conversions") or 0
        cost = row.get("cost") or 0.0
        cpa = row.get("cpa") or 0.0
        lost_rank = row.get("metrics.search_rank_lost_impression_share") or 0.0
        target = meta.get("target_cpa") or target_cpa_for(name, account)
        age = meta.get("age_days")

        if not target:
            result.findings.append(Finding(
                kind="no-target", severity="watch",
                summary=f"{name} has no target CPA set",
                detail="Maximize Conversions without a target spends the budget "
                       "whatever a booking costs. Set one from the practice's "
                       "patient value."))
            continue
        if age is not None and age < 14:
            result.findings.append(Finding(
                kind="learning", severity="info",
                summary=f"{name} is {age} days old - leaving bidding alone",
                detail="Changing the target during learning restarts it."))
            continue
        if conversions < min_conversions:
            result.findings.append(Finding(
                kind="thin-data", severity="info",
                summary=f"{name}: {conversions:.0f} conversions - below the "
                        f"{min_conversions} needed to move the target",
                detail=f"CPA ${cpa:,.0f} vs target ${target:,.0f}. Watch, do not touch."))
            continue

        if cpa > target * 1.3:
            new_target = round(target * (1 - step_pct), 2)
            result.proposals.append(mutations.set_target_cpa(
                client, customer_id, campaign_id, new_target, target,
                strategy_type=str(meta.get("strategy") or "MAXIMIZE_CONVERSIONS"),
                campaign_age_days=age,
                reason=f"CPA ${cpa:,.0f} is {cpa / target:.1f}x target on "
                       f"{conversions:.0f} conversions"))
            result.findings.append(Finding(
                kind="tcpa-down", severity="act",
                summary=f"{name}: CPA ${cpa:,.0f} vs target ${target:,.0f}",
                detail=f"Stepping the target down to ${new_target:,.0f}."))
        elif cpa <= target and lost_rank > 0.20:
            new_target = round(target * (1 + step_pct), 2)
            result.proposals.append(mutations.set_target_cpa(
                client, customer_id, campaign_id, new_target, target,
                strategy_type=str(meta.get("strategy") or "MAXIMIZE_CONVERSIONS"),
                campaign_age_days=age,
                reason=f"CPA ${cpa:,.0f} under target with {lost_rank:.0%} of "
                       "impression share lost to rank"))
            result.findings.append(Finding(
                kind="tcpa-up", severity="act",
                summary=f"{name} is under target and losing {lost_rank:.0%} to rank",
                detail=f"Stepping the target up to ${new_target:,.0f} to buy the "
                       "impressions it is already earning."))
    return result


def budget_review(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
                  *, date_range: str = "LAST_30_DAYS", step_pct: float = 0.20,
                  lost_is_threshold: float = 0.10) -> RoutineResult:
    """Raise budget only where the money is already working.

    Budget-lost impression share says "there was more demand than money".  That
    is only worth buying when CPA is at or under target - otherwise the same
    change just buys more of a losing auction.
    """
    account = account or {}
    result = RoutineResult(name="Budget review")
    pacing = reports.budget_pacing(client, customer_id, date_range="LAST_30_DAYS")
    result.tables["pacing"] = pacing
    settings = campaign_settings(client, customer_id)
    ceiling = float(((account.get("goals") or {}).get("monthly_budget") or 0)) / 30 or None

    for row in pacing.rows:
        campaign_id = row.get("campaign.id")
        name = row.get("campaign.name") or ""
        meta = settings.get(campaign_id, {})
        lost_budget = row.get("metrics.search_budget_lost_impression_share") or 0.0
        cpa = row.get("cpa") or 0.0
        conversions = row.get("metrics.conversions") or 0
        target = meta.get("target_cpa") or target_cpa_for(name, account)
        current = meta.get("daily_budget") or row.get("daily_budget") or 0.0

        if lost_budget >= lost_is_threshold and target and conversions >= 10 and cpa <= target:
            new_budget = round(current * (1 + step_pct), 2)
            if ceiling and new_budget > ceiling:
                result.findings.append(Finding(
                    kind="budget-capped", severity="watch",
                    summary=f"{name} deserves more budget but the account cap is in the way",
                    detail=f"Would go to ${new_budget:,.0f}/day; the practice's monthly "
                           f"budget implies ${ceiling:,.0f}/day. A decision for the owner."))
                continue
            result.proposals.append(mutations.update_budget(
                client, customer_id, meta.get("budget_id"), new_budget, current,
                campaign_id=campaign_id, campaign_age_days=meta.get("age_days"),
                reason=f"losing {lost_budget:.0%} of impressions to budget at "
                       f"${cpa:,.0f} CPA against a ${target:,.0f} target"))
            result.findings.append(Finding(
                kind="budget-up", severity="act",
                summary=f"{name} is losing {lost_budget:.0%} of impressions to budget",
                detail=f"CPA ${cpa:,.0f} is at or under target - raising "
                       f"${current:,.0f} to ${new_budget:,.0f}/day."))
        elif lost_budget >= lost_is_threshold and target and cpa > target:
            result.findings.append(Finding(
                kind="budget-hold", severity="watch",
                summary=f"{name} is budget-limited but over target",
                detail=f"CPA ${cpa:,.0f} vs ${target:,.0f}. Fix efficiency first - "
                       "more budget here just buys more expensive clicks."))
        elif row.get("budget_used_pct", 100) < 70:
            result.findings.append(Finding(
                kind="budget-underspend", severity="info",
                summary=f"{name} is using {row.get('budget_used_pct')}% of its budget",
                detail="Not a budget problem - look at impression share, bids and "
                       "keyword coverage."))
    return result


# ---------------------------------------------------------------------------
# schedule, geography, ads
# ---------------------------------------------------------------------------

_DAY_ORDER = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def schedule_review(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
                    *, date_range: str = "LAST_30_DAYS", min_clicks: int = 40) -> RoutineResult:
    """Compare when the ads spend with when the practice can answer the phone.

    The classic local-dental leak: 20% of the budget goes out after the front
    desk has gone home, into voicemail.
    """
    account = account or {}
    result = RoutineResult(name="Schedule review")
    report = reports.schedule_performance(client, customer_id, date_range=date_range)
    result.tables["schedule"] = report
    if not report.rows:
        return result

    hours = account.get("hours") or {}
    after_hours_ok = bool(account.get("after_hours_answering"))

    buckets: dict[tuple[str, int], dict[str, float]] = {}
    for row in report.rows:
        key = (str(row.get("segments.day_of_week")), int(row.get("segments.hour") or 0))
        bucket = buckets.setdefault(key, {"clicks": 0.0, "cost": 0.0, "conv": 0.0})
        bucket["clicks"] += row.get("metrics.clicks") or 0
        bucket["cost"] += row.get("cost") or 0.0
        bucket["conv"] += row.get("metrics.conversions") or 0

    total_clicks = sum(b["clicks"] for b in buckets.values())
    total_conv = sum(b["conv"] for b in buckets.values())
    account_cvr = safe_div(total_conv, total_clicks)

    closed_cost = closed_clicks = closed_conv = 0.0
    weak_slots: list[tuple[str, int, dict[str, float]]] = []
    for (day, hour), bucket in buckets.items():
        open_now = _is_open(hours, day, hour)
        if not open_now:
            closed_cost += bucket["cost"]
            closed_clicks += bucket["clicks"]
            closed_conv += bucket["conv"]
        if bucket["clicks"] >= min_clicks:
            cvr = safe_div(bucket["conv"], bucket["clicks"])
            if account_cvr and cvr < account_cvr * 0.5:
                weak_slots.append((day, hour, {**bucket, "cvr": cvr}))

    if closed_cost and total_clicks:
        share = closed_cost / sum(b["cost"] for b in buckets.values())
        closed_cvr = safe_div(closed_conv, closed_clicks)
        severity = "act" if share > 0.15 and not after_hours_ok else "watch"
        result.findings.append(Finding(
            kind="after-hours", severity=severity,
            summary=f"{share:.0%} of spend lands when the practice is closed",
            detail=(f"${closed_cost:,.0f}, conversion rate {closed_cvr:.1%} vs "
                    f"{account_cvr:.1%} overall. "
                    + ("An answering service is configured, so this may be fine - check "
                       "that after-hours calls are actually being booked."
                       if after_hours_ok else
                       "Either bid these hours down, or put an answering service behind "
                       "the phone. Emergency campaigns are the exception - pain does not "
                       "keep office hours.")),
            evidence={"closed_cost": round(closed_cost, 2), "share": round(share, 3)}))

    for day, hour, bucket in sorted(weak_slots, key=lambda item: -item[2]["cost"])[:8]:
        result.findings.append(Finding(
            kind="weak-hour", severity="watch",
            summary=f"{day.title()} {hour:02d}:00 converts at {bucket['cvr']:.1%}",
            detail=f"${bucket['cost']:,.0f} spent, {bucket['clicks']:.0f} clicks, "
                   f"against an account average of {account_cvr:.1%}"))
    if weak_slots:
        result.notes.append(
            "Hour-level bid modifiers are proposed only after two consecutive weeks "
            "show the same pattern - single-week hour data is mostly noise.")
    return result


def _is_open(hours: dict[str, Any], day: str, hour: int) -> bool:
    window = str(hours.get(day.lower(), "")).strip().lower()
    if not window or window in {"closed", "-"}:
        return False
    try:
        start, _, end = window.partition("-")
        return int(start.split(":")[0]) <= hour < int(end.split(":")[0])
    except (ValueError, IndexError):
        return True


def geo_review(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
               *, date_range: str = "LAST_30_DAYS", min_clicks: int = 25) -> RoutineResult:
    """Postal codes that spend and never book, and the ones worth paying more for."""
    from . import zips as zips_module

    account = account or {}
    result = RoutineResult(name="Geography review")
    report = reports.zip_performance(client, customer_id, date_range=date_range)
    result.tables["zips"] = report
    if not report.rows:
        return result

    names = [r.get("segments.geo_target_postal_code") for r in report.rows]
    lookup = zips_module.resolve_postal_codes(client, [n for n in names if n], customer_id)

    default_target = target_cpa_for("", account) or 100.0
    for row in report.rows:
        resource = row.get("segments.geo_target_postal_code") or ""
        zip_code = lookup.get(resource, resource.split("/")[-1])
        row["postal_code"] = zip_code
        clicks = row.get("metrics.clicks") or 0
        conversions = row.get("metrics.conversions") or 0
        cost = row.get("cost") or 0.0
        if clicks < min_clicks:
            continue
        if conversions == 0 and cost >= 2 * default_target:
            result.findings.append(Finding(
                kind="zip-waste", severity="act",
                summary=f"ZIP {zip_code}: ${cost:,.0f}, {clicks} clicks, no bookings",
                detail="Candidate for exclusion or a -30% modifier. Check drive time "
                       "before excluding - a ZIP can be close on the map and awkward "
                       "to reach.",
                evidence={"zip": zip_code, "cost": cost}))
        elif conversions and cost / conversions <= default_target * 0.7:
            result.findings.append(Finding(
                kind="zip-win", severity="info",
                summary=f"ZIP {zip_code} books at ${cost / conversions:,.0f}",
                detail=f"vs a ${default_target:,.0f} target - worth a positive bid "
                       "modifier, and worth knowing for direct mail too.",
                evidence={"zip": zip_code, "cpa": round(cost / conversions, 2)}))
    return result


def ad_review(client: GadsClient, customer_id: str, *,
              date_range: str = "LAST_30_DAYS", min_impressions: int = 1000) -> RoutineResult:
    """Disapprovals, weak ad strength, and the assets Google says are not working."""
    result = RoutineResult(name="Ad and asset review")

    rejected = reports.disapprovals(client, customer_id)
    result.tables["disapprovals"] = rejected
    for row in rejected.rows:
        result.findings.append(Finding(
            kind="disapproval", severity="act",
            summary=f"Ad {row.get('ad_group_ad.ad.id')} is disapproved",
            detail=f"{row.get('campaign.name')} / {row.get('ad_group.name')}: "
                   f"{row.get('ad_group_ad.policy_summary.policy_topic_entries')}. "
                   "Dental copy trips the healthcare policy easily - avoid superlatives, "
                   "guarantees and before/after claims.",
            evidence=row))

    ads = reports.ad_performance(client, customer_id, date_range=date_range)
    result.tables["ads"] = ads
    for row in ads.rows:
        strength = str(row.get("ad_group_ad.ad_strength") or "")
        if strength in {"POOR", "AVERAGE"}:
            result.findings.append(Finding(
                kind="ad-strength", severity="watch",
                summary=f"Ad strength {strength} in {row.get('ad_group.name')}",
                detail="Add distinct headlines - offer, urgency, insurance/financing, "
                       "location, and one proof point."))

    assets = reports.rsa_asset_performance(client, customer_id, date_range=date_range)
    result.tables["assets"] = assets
    for row in assets.rows:
        if (row.get("ad_group_ad_asset_view.performance_label") == "LOW"
                and (row.get("metrics.impressions") or 0) >= min_impressions):
            result.findings.append(Finding(
                kind="weak-asset", severity="act",
                summary=f"Replace: \"{row.get('asset.text_asset.text')}\"",
                detail=f"{row.get('ad_group_ad_asset_view.field_type')} labelled LOW "
                       f"after {row.get('metrics.impressions'):,} impressions in "
                       f"{row.get('ad_group.name')}",
                evidence=row))
    return result


def conversion_health(client: GadsClient, customer_id: str,
                      account: dict[str, Any] | None = None) -> RoutineResult:
    """Is the account even measuring the right thing?

    Everything downstream - bidding, budget, the whole optimisation loop - is
    only as good as what counts as a conversion.
    """
    account = account or {}
    result = RoutineResult(name="Conversion tracking health")
    actions = reports.conversion_actions(client, customer_id)
    result.tables["conversion_actions"] = actions
    if not actions.rows:
        result.findings.append(Finding(
            kind="no-conversions", severity="act",
            summary="No conversion actions found",
            detail="Nothing can be optimised until a booked patient is measurable."))
        return result

    primary = [r for r in actions.rows if r.get("conversion_action.primary_for_goal")]
    expected = {str(n).lower() for n in (account.get("primary_conversions") or [])}

    if not primary:
        result.findings.append(Finding(
            kind="no-primary", severity="act",
            summary="No primary conversion actions",
            detail="Smart bidding has nothing to optimise towards."))
    if len(primary) > 4:
        result.findings.append(Finding(
            kind="too-many-primary", severity="watch",
            summary=f"{len(primary)} primary conversion actions",
            detail="Every soft click counted as primary teaches bidding to buy "
                   "clicks, not patients. Keep calls, bookings and form submits "
                   "primary; make everything else secondary."))
    for row in primary:
        name = str(row.get("conversion_action.name") or "")
        if expected and name.lower() not in expected:
            result.findings.append(Finding(
                kind="unexpected-primary", severity="watch",
                summary=f"'{name}' is primary but is not on the practice's list",
                detail="Either add it to primary_conversions in the account config "
                       "or demote it to secondary."))
        if row.get("conversion_action.counting_type") == "MANY_PER_CLICK" and \
                "call" not in name.lower():
            result.findings.append(Finding(
                kind="counting", severity="watch",
                summary=f"'{name}' counts every conversion per click",
                detail="For new-patient actions this inflates the count - one click "
                       "should book one patient."))

    has_offline = any("UPLOAD" in str(r.get("conversion_action.type") or "")
                      for r in actions.rows)
    if not has_offline:
        result.findings.append(Finding(
            kind="no-offline", severity="watch",
            summary="No offline conversion import is set up",
            detail="Without it, bidding optimises for calls that ring, not for "
                   "patients who sit in the chair. gads.offline builds the upload."))
    return result


def call_quality(client: GadsClient, customer_id: str, account: dict[str, Any] | None = None,
                 *, date_range: str = "LAST_30_DAYS") -> RoutineResult:
    """How many of the calls being paid for are long enough to be a patient."""
    account = account or {}
    threshold = int(account.get("qualified_call_seconds") or 60)
    result = RoutineResult(name="Call quality")
    report = reports.calls(client, customer_id, date_range=date_range)
    result.tables["calls"] = report
    rows = report.rows
    if not rows:
        result.notes.append("No call data - call reporting may be off, or all calls "
                            "go through a tracking number outside Google.")
        return result

    qualified = [r for r in rows
                 if (r.get("call_view.call_duration_seconds") or 0) >= threshold]
    missed = [r for r in rows if str(r.get("call_view.call_status")) == "MISSED"]
    share = safe_div(len(qualified), len(rows))
    result.findings.append(Finding(
        kind="call-quality",
        severity="act" if share < 0.4 else "info",
        summary=f"{len(qualified)}/{len(rows)} calls ran {threshold}s or longer "
                f"({share:.0%})",
        detail=("Short calls are usually wrong-number traffic, price shoppers or "
                "a front desk that is not converting. Listen to five before changing "
                "anything in the account." if share < 0.4 else
                "Healthy - the traffic is reaching people who want an appointment.")))
    if missed:
        result.findings.append(Finding(
            kind="missed-calls", severity="act",
            summary=f"{len(missed)} calls were missed",
            detail="Paid for and not answered. This is the cheapest fix in the "
                   "whole account."))
    return result


# ---------------------------------------------------------------------------
# routines
# ---------------------------------------------------------------------------


def spend_anomalies(client: GadsClient, customer_id: str, *,
                    tolerance: float = 0.4) -> RoutineResult:
    """Yesterday against the previous week, per campaign."""
    result = RoutineResult(name="Spend check")
    yesterday = reports.campaign_performance(client, customer_id, date_range="YESTERDAY")
    week = reports.campaign_performance(client, customer_id, date_range="LAST_7_DAYS")
    result.tables["yesterday"] = yesterday
    baseline = {r.get("campaign.id"): (r.get("cost") or 0.0) / 7 for r in week.rows}

    for row in yesterday.rows:
        campaign_id = row.get("campaign.id")
        cost = row.get("cost") or 0.0
        expected = baseline.get(campaign_id, 0.0)
        if expected < 5:
            continue
        drift = (cost - expected) / expected
        if abs(drift) < tolerance:
            continue
        result.findings.append(Finding(
            kind="spend-anomaly", severity="act" if drift > 0 else "watch",
            summary=f"{row.get('campaign.name')} spent ${cost:,.0f} yesterday "
                    f"({drift:+.0%} vs its daily average)",
            detail="Check for a budget change, a new competitor, or a keyword that "
                   "started matching something new." if drift > 0 else
                   "Check for disapprovals, a paused ad group, or a bid that has "
                   "fallen out of the auction.",
            evidence={"cost": cost, "expected": round(expected, 2)}))
        if cost == 0 and expected > 20:
            result.findings.append(Finding(
                kind="stopped", severity="act",
                summary=f"{row.get('campaign.name')} spent nothing yesterday",
                detail="A live campaign that stops spending is usually a disapproval, "
                       "a billing problem or an accidental pause."))
    return result


def daily_routine(client: GadsClient, customer_id: str,
                  account: dict[str, Any] | None = None, *,
                  shared_set_id: int | None = None) -> RoutineResult:
    """What a good account manager checks before their second coffee.

    Reads a lot, changes little: only negatives are proposed daily, because
    everything else needs more than a day of evidence.
    """
    account = account or {}
    result = RoutineResult(name="Daily check")
    result.extend(spend_anomalies(client, customer_id))
    result.extend(ad_review(client, customer_id, date_range="LAST_7_DAYS"))
    result.extend(mine_negatives(client, customer_id, account, date_range="LAST_7_DAYS",
                                 shared_set_id=shared_set_id))
    result.extend(call_quality(client, customer_id, account, date_range="LAST_7_DAYS"))
    result.name = "Daily check"
    result.notes.append(
        "Daily runs only propose negatives. Bids, budgets and pausing decisions "
        "wait for the weekly run, where there is enough data to be right.")
    return result


def weekly_routine(client: GadsClient, customer_id: str,
                   account: dict[str, Any] | None = None, *,
                   shared_set_id: int | None = None) -> RoutineResult:
    """The full optimisation pass."""
    account = account or {}
    result = RoutineResult(name="Weekly optimisation")
    result.extend(mine_negatives(client, customer_id, account, date_range="LAST_30_DAYS",
                                 shared_set_id=shared_set_id))
    result.extend(dead_keywords(client, customer_id, account, date_range="LAST_30_DAYS"))
    result.extend(bid_review(client, customer_id, account, date_range="LAST_30_DAYS"))
    result.extend(budget_review(client, customer_id, account))
    result.extend(schedule_review(client, customer_id, account))
    result.extend(geo_review(client, customer_id, account))
    result.extend(ad_review(client, customer_id))
    result.name = "Weekly optimisation"
    return result


def monthly_routine(client: GadsClient, customer_id: str,
                    account: dict[str, Any] | None = None) -> RoutineResult:
    """The strategic pass: structure, competition, measurement.

    Proposes nothing on its own - the output is a set of decisions for the
    practice, which is where a month's worth of change belongs.
    """
    account = account or {}
    result = RoutineResult(name="Monthly review")
    result.extend(conversion_health(client, customer_id, account))
    result.tables["auction_insights"] = reports.auction_insights(client, customer_id)
    result.tables["landing_pages"] = reports.landing_pages(client, customer_id)
    result.tables["devices"] = reports.device_performance(client, customer_id)
    result.tables["income"] = reports.income_performance(client, customer_id)
    result.tables["distance"] = reports.distance_performance(client, customer_id)
    result.tables["changes"] = reports.change_history(client, customer_id, days=29)

    insights = result.tables["auction_insights"].rows
    rivals = [r for r in insights
              if str(r.get("segments.auction_insight_domain", "")).lower() not in {"you", ""}]
    if rivals:
        top = max(rivals, key=lambda r: r.get(
            "metrics.auction_insight_search_impression_share") or 0)
        result.findings.append(Finding(
            kind="competition", severity="info",
            summary=f"{top.get('segments.auction_insight_domain')} shows on "
                    f"{top.get('metrics.auction_insight_search_impression_share'):.0%} "
                    "of your auctions",
            detail="Compare with last month. A domain climbing fast is usually a "
                   "practice that just hired an agency - expect CPCs to follow."))
    result.notes.append(
        "Monthly is also when to re-run the ZIP/income plan (gads.zips) against "
        "actual postal-code performance, and to review the offer on the landing pages.")
    return result


ROUTINES = {
    "daily": daily_routine,
    "weekly": weekly_routine,
    "monthly": monthly_routine,
}


def run_routine(client: GadsClient, name: str, customer_id: str,
                account: dict[str, Any] | None = None, **kwargs) -> RoutineResult:
    if name not in ROUTINES:
        raise ValueError(f"Unknown routine {name!r}. Available: {', '.join(ROUTINES)}")
    return ROUTINES[name](client, customer_id, account, **kwargs)
