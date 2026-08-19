"""The reports the agent reads before it changes anything.

Each function returns a :class:`Report`: flat rows keyed by GAQL field path,
derived money/ratio columns, totals, the query that produced it, and a
``markdown()`` rendering so Claude reads a table instead of a protobuf dump.

Every report is registered in :data:`REPORTS` and exposed as an MCP tool.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from .client import GadsClient
from .gaql import (
    CORE_METRICS,
    IMPRESSION_SHARE_METRICS,
    Query,
    derive_metrics,
    from_micros,
    sum_rows,
)

# Short, human labels for the columns that show up in tables.
LABELS = {
    "campaign.name": "campaign",
    "campaign.id": "campaign_id",
    "campaign.status": "status",
    "campaign.advertising_channel_type": "channel",
    "campaign.bidding_strategy_type": "bid_strategy",
    "ad_group.name": "ad_group",
    "ad_group.id": "ad_group_id",
    "ad_group.status": "ag_status",
    "ad_group_criterion.keyword.text": "keyword",
    "ad_group_criterion.keyword.match_type": "match",
    "ad_group_criterion.criterion_id": "criterion_id",
    "ad_group_criterion.status": "kw_status",
    "ad_group_criterion.quality_info.quality_score": "qs",
    "search_term_view.search_term": "search_term",
    "search_term_view.status": "term_status",
    "segments.search_term_match_type": "matched_as",
    "segments.geo_target_postal_code": "postal_code",
    "segments.geo_target_city": "city",
    "segments.device": "device",
    "segments.hour": "hour",
    "segments.day_of_week": "day",
    "segments.date": "date",
    "segments.auction_insight_domain": "competitor",
    "metrics.impressions": "impr",
    "metrics.clicks": "clicks",
    "metrics.conversions": "conv",
    "metrics.conversions_value": "conv_value",
    "metrics.search_impression_share": "impr_share",
    "metrics.search_rank_lost_impression_share": "lost_is_rank",
    "metrics.search_budget_lost_impression_share": "lost_is_budget",
    "metrics.search_absolute_top_impression_share": "abs_top_share",
    "metrics.auction_insight_search_impression_share": "their_is",
    "metrics.auction_insight_search_absolute_top_impression_share": "their_abs_top",
    "asset.text_asset.text": "asset",
    "ad_group_ad_asset_view.field_type": "type",
    "ad_group_ad_asset_view.performance_label": "label",
    "ad_group_ad_asset_view.pinned_field": "pinned",
    "ad_group_ad.ad.id": "ad_id",
    "ad_group_ad.ad_strength": "strength",
    "ad_group_ad.policy_summary.approval_status": "approval",
    "ad_group_criterion.income_range.type": "income_decile",
    "ad_group_criterion.age_range.type": "age",
    "ad_group_criterion.gender.type": "gender",
    "ad_group_criterion.bid_modifier": "bid_mod",
    "campaign_criterion.location.geo_target_constant": "location",
    "campaign_criterion.bid_modifier": "bid_mod",
    "distance_view.distance_bucket": "distance",
    "landing_page_view.unexpanded_final_url": "landing_page",
    "conversion_action.name": "conversion_action",
    "conversion_action.primary_for_goal": "primary",
    "conversion_action.counting_type": "counting",
    "segments.conversion_action_name": "conversion_action",
    "call_view.call_duration_seconds": "seconds",
    "call_view.call_status": "call_status",
    "call_view.caller_area_code": "area_code",
    "call_view.start_call_date_time": "when",
    "change_event.change_date_time": "when",
    "change_event.user_email": "who",
    "change_event.client_type": "via",
    "change_event.change_resource_type": "what",
    "change_event.resource_change_operation": "op",
    "change_event.changed_fields": "fields",
    "recommendation.type": "recommendation",
    "recommendation.campaign": "campaign",
    "metrics.auction_insight_search_overlap_rate": "overlap",
    "metrics.auction_insight_search_outranking_share": "you_outrank",
    "cost": "cost",
    "ctr": "ctr%",
    "avg_cpc": "cpc",
    "cpa": "cpa",
    "conv_rate": "cvr%",
    "roas": "roas",
}

DEFAULT_COLUMNS = ["metrics.impressions", "metrics.clicks", "cost", "ctr", "avg_cpc",
                   "metrics.conversions", "cpa", "conv_rate"]


@dataclass
class Report:
    """A table of numbers plus the query that produced it."""

    name: str
    rows: list[dict[str, Any]]
    columns: list[str]
    query: str
    date_range: str = ""
    totals: dict[str, Any] | None = None
    notes: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.rows)

    def markdown(self, limit: int = 40) -> str:
        header = f"### {self.name}"
        if self.date_range:
            header += f"  ({self.date_range})"
        if not self.rows:
            return f"{header}\n\n_No rows._"
        cols = self.columns
        head = "| " + " | ".join(LABELS.get(c, c) for c in cols) + " |"
        rule = "|" + "|".join("---" for _ in cols) + "|"
        body = [
            "| " + " | ".join(_cell(row.get(c)) for c in cols) + " |"
            for row in self.rows[:limit]
        ]
        table = "\n".join([header, "", head, rule, *body])
        if len(self.rows) > limit:
            table += f"\n\n_{len(self.rows) - limit} more rows not shown._"
        if self.totals:
            table += "\n\n**Totals:** " + ", ".join(
                f"{LABELS.get(k, k)}={_cell(self.totals.get(k))}"
                for k in ("metrics.impressions", "metrics.clicks", "cost",
                          "metrics.conversions", "cpa")
                if k in self.totals
            )
        for note in self.notes:
            table += f"\n\n> {note}"
        return table

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "date_range": self.date_range,
            "row_count": len(self.rows),
            "columns": self.columns,
            "rows": self.rows,
            "totals": self.totals,
            "query": self.query,
            "notes": self.notes,
        }


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".") if value % 1 else f"{value:,.0f}"
    if isinstance(value, int):
        return f"{value:,}"
    # Campaign names in this account convention contain pipes ("Brand | Search
    # | Emergency"), which would otherwise split the markdown row.
    return str(value).replace("|", "\\|")


def _run(
    client: GadsClient,
    customer_id: str | int | None,
    query: Query,
    *,
    name: str,
    dimensions: Sequence[str],
    metrics: Sequence[str] = DEFAULT_COLUMNS,
    date_range: str = "",
    notes: Sequence[str] = (),
    totals: bool = True,
) -> Report:
    sql = query.build()
    rows = [derive_metrics(row) for row in client.search(customer_id, sql)]
    return Report(
        name=name,
        rows=rows,
        columns=[*dimensions, *metrics],
        query=sql,
        date_range=date_range,
        totals=sum_rows(rows) if totals and rows else None,
        notes=list(notes),
    )


# ---------------------------------------------------------------------------
# account level
# ---------------------------------------------------------------------------


def account_summary(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """One row per campaign plus account totals - the first thing to look at."""
    query = (
        Query("campaign")
        .select("campaign.id", "campaign.name", "campaign.status",
                "campaign.advertising_channel_type", "campaign.bidding_strategy_type",
                CORE_METRICS, IMPRESSION_SHARE_METRICS)
        .where("campaign.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(
        client, customer_id, query,
        name="Account summary by campaign",
        dimensions=["campaign.name", "campaign.status", "campaign.bidding_strategy_type"],
        metrics=[*DEFAULT_COLUMNS, "metrics.search_impression_share",
                 "metrics.search_rank_lost_impression_share",
                 "metrics.search_budget_lost_impression_share"],
        date_range=date_range,
    )


def campaign_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS",
                         campaign_ids: Sequence[int] | None = None) -> Report:
    """Spend, clicks and bookings by campaign."""
    query = (
        Query("campaign")
        .select("campaign.id", "campaign.name", "campaign.status", CORE_METRICS)
        .where("campaign.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    if campaign_ids:
        query.one_of("campaign.id", list(campaign_ids))
    return _run(client, customer_id, query, name="Campaign performance",
                dimensions=["campaign.name", "campaign.status"], date_range=date_range)


def ad_group_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS",
                         campaign_ids: Sequence[int] | None = None) -> Report:
    """The same numbers one level down - where a campaign's CPA actually comes from."""
    query = (
        Query("ad_group")
        .select("campaign.name", "ad_group.id", "ad_group.name", "ad_group.status", CORE_METRICS)
        .where("ad_group.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    if campaign_ids:
        query.one_of("campaign.id", list(campaign_ids))
    return _run(client, customer_id, query, name="Ad group performance",
                dimensions=["campaign.name", "ad_group.name", "ad_group.status"],
                date_range=date_range)


def budget_pacing(client: GadsClient, customer_id=None, date_range="THIS_MONTH") -> Report:
    """Daily budget vs. what each campaign is actually spending."""
    query = (
        Query("campaign")
        .select("campaign.id", "campaign.name", "campaign.status",
                "campaign_budget.amount_micros", CORE_METRICS,
                "metrics.search_budget_lost_impression_share")
        .where("campaign.status = 'ENABLED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    report = _run(
        client, customer_id, query, name="Budget pacing",
        dimensions=["campaign.name", "daily_budget", "avg_daily_spend", "budget_used_pct"],
        metrics=["cost", "metrics.conversions", "cpa",
                 "metrics.search_budget_lost_impression_share"],
        date_range=date_range,
        notes=["Lost IS (budget) above 10% with CPA at or under target is the "
               "signal to raise budget - not raw spend."],
    )
    days = _days_in_range(date_range)
    for row in report.rows:
        budget = from_micros(row.get("campaign_budget.amount_micros"))
        spend_per_day = round(row["cost"] / days, 2) if days else 0.0
        row["daily_budget"] = budget
        row["avg_daily_spend"] = spend_per_day
        row["budget_used_pct"] = round((spend_per_day / budget) * 100, 1) if budget else 0.0
    return report


def _days_in_range(date_range: str) -> int:
    import datetime as dt

    mapping = {"TODAY": 1, "YESTERDAY": 1, "LAST_7_DAYS": 7, "LAST_14_DAYS": 14,
               "LAST_30_DAYS": 30, "LAST_WEEK_MON_SUN": 7, "LAST_WEEK_SUN_SAT": 7,
               "LAST_BUSINESS_WEEK": 5}
    key = (date_range or "").upper()
    if key in mapping:
        return mapping[key]
    today = dt.date.today()
    if key == "THIS_MONTH":
        return today.day
    if key == "LAST_MONTH":
        first = today.replace(day=1)
        return (first - dt.timedelta(days=1)).day
    if "," in key:
        start, _, end = key.partition(",")
        try:
            return max(
                (dt.date.fromisoformat(end.strip()) - dt.date.fromisoformat(start.strip())).days + 1,
                1,
            )
        except ValueError:
            return 30
    return 30


# ---------------------------------------------------------------------------
# keywords and search terms
# ---------------------------------------------------------------------------


def keyword_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS",
                        campaign_ids: Sequence[int] | None = None,
                        min_clicks: int = 0) -> Report:
    """Every enabled keyword with its Quality Score - the dead-keyword sweep reads this."""
    query = (
        Query("keyword_view")
        .select("campaign.name", "ad_group.name",
                "ad_group_criterion.criterion_id",
                "ad_group_criterion.keyword.text",
                "ad_group_criterion.keyword.match_type",
                "ad_group_criterion.status",
                "ad_group_criterion.quality_info.quality_score",
                CORE_METRICS)
        .where("ad_group_criterion.status != 'REMOVED'")
        .where("ad_group_criterion.negative = FALSE")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    if campaign_ids:
        query.one_of("campaign.id", list(campaign_ids))
    if min_clicks:
        query.at_least("metrics.clicks", min_clicks)
    return _run(
        client, customer_id, query, name="Keyword performance",
        dimensions=["campaign.name", "ad_group.name", "ad_group_criterion.keyword.text",
                    "ad_group_criterion.keyword.match_type", "ad_group_criterion.status",
                    "ad_group_criterion.quality_info.quality_score"],
        date_range=date_range,
    )


def search_terms(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS",
                 campaign_ids: Sequence[int] | None = None,
                 min_impressions: int = 1, only_unmapped: bool = False) -> Report:
    """What people actually typed - the raw material for negatives and new keywords."""
    query = (
        Query("search_term_view")
        .select("campaign.name", "ad_group.name",
                "search_term_view.search_term", "search_term_view.status",
                "segments.search_term_match_type", CORE_METRICS)
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    if campaign_ids:
        query.one_of("campaign.id", list(campaign_ids))
    if min_impressions > 1:
        query.at_least("metrics.impressions", min_impressions)
    if only_unmapped:
        # NONE = the term is neither an added keyword nor an added negative yet.
        query.equals("search_term_view.status", "NONE")
    return _run(
        client, customer_id, query, name="Search terms",
        dimensions=["search_term_view.search_term", "campaign.name", "ad_group.name",
                    "segments.search_term_match_type", "search_term_view.status"],
        date_range=date_range,
        notes=["Terms with status NONE are not yet added as keywords or negatives - "
               "that is the weekly mining queue."],
    )


def negative_keywords(client: GadsClient, customer_id=None) -> Report:
    """Every negative already in place, so the agent never adds a duplicate."""
    campaign_level = client.search(customer_id, (
        Query("campaign_criterion")
        .select("campaign.name", "campaign_criterion.criterion_id",
                "campaign_criterion.keyword.text", "campaign_criterion.keyword.match_type")
        .where("campaign_criterion.negative = TRUE")
        .where("campaign_criterion.type = 'KEYWORD'")
        .build()
    ))
    ad_group_level = client.search(customer_id, (
        Query("ad_group_criterion")
        .select("campaign.name", "ad_group.name", "ad_group_criterion.criterion_id",
                "ad_group_criterion.keyword.text", "ad_group_criterion.keyword.match_type")
        .where("ad_group_criterion.negative = TRUE")
        .where("ad_group_criterion.type = 'KEYWORD'")
        .build()
    ))
    shared = client.search(customer_id, (
        Query("shared_criterion")
        .select("shared_set.name", "shared_set.id", "shared_criterion.criterion_id",
                "shared_criterion.keyword.text", "shared_criterion.keyword.match_type")
        .where("shared_set.type = 'NEGATIVE_KEYWORDS'")
        .build()
    ))
    rows = []
    for row in campaign_level:
        rows.append({"level": "campaign", "where": row.get("campaign.name"),
                     "text": row.get("campaign_criterion.keyword.text"),
                     "match": row.get("campaign_criterion.keyword.match_type"),
                     "criterion_id": row.get("campaign_criterion.criterion_id")})
    for row in ad_group_level:
        rows.append({"level": "ad_group",
                     "where": f"{row.get('campaign.name')} / {row.get('ad_group.name')}",
                     "text": row.get("ad_group_criterion.keyword.text"),
                     "match": row.get("ad_group_criterion.keyword.match_type"),
                     "criterion_id": row.get("ad_group_criterion.criterion_id")})
    for row in shared:
        rows.append({"level": "shared_list", "where": row.get("shared_set.name"),
                     "text": row.get("shared_criterion.keyword.text"),
                     "match": row.get("shared_criterion.keyword.match_type"),
                     "criterion_id": row.get("shared_criterion.criterion_id")})
    return Report(name="Negative keywords in place", rows=rows,
                  columns=["level", "where", "text", "match"],
                  query="campaign_criterion + ad_group_criterion + shared_criterion",
                  totals=None)


# ---------------------------------------------------------------------------
# geography
# ---------------------------------------------------------------------------


def zip_performance(client: GadsClient, customer_id=None, date_range="LAST_90_DAYS",
                    campaign_ids: Sequence[int] | None = None) -> Report:
    """Performance by postal code of the person searching.

    LOCATION_OF_PRESENCE means "where they physically were", which is the only
    thing that matters for a practice patients have to drive to.
    """
    date_range = "LAST_30_DAYS" if date_range == "LAST_90_DAYS" else date_range
    query = (
        Query("geographic_view")
        .select("campaign.name", "segments.geo_target_postal_code",
                "geographic_view.location_type", CORE_METRICS)
        .equals("geographic_view.location_type", "LOCATION_OF_PRESENCE")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    if campaign_ids:
        query.one_of("campaign.id", list(campaign_ids))
    return _run(
        client, customer_id, query, name="Performance by postal code",
        dimensions=["segments.geo_target_postal_code", "campaign.name"],
        date_range=date_range,
        notes=["Postal codes come back as geoTargetConstants/<id>; "
               "gads.zips.resolve_postal_codes() turns them into ZIPs."],
    )


def city_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """Results by the city the searcher was in."""
    query = (
        Query("geographic_view")
        .select("campaign.name", "segments.geo_target_city", CORE_METRICS)
        .equals("geographic_view.location_type", "LOCATION_OF_PRESENCE")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Performance by city",
                dimensions=["segments.geo_target_city", "campaign.name"], date_range=date_range)


def targeted_locations(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """The locations currently targeted, with their bid modifiers and results."""
    query = (
        Query("location_view")
        .select("campaign.name", "campaign_criterion.location.geo_target_constant",
                "campaign_criterion.bid_modifier", "campaign_criterion.negative",
                CORE_METRICS)
        .where("campaign_criterion.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Targeted locations",
                dimensions=["campaign.name", "campaign_criterion.location.geo_target_constant",
                            "campaign_criterion.bid_modifier", "campaign_criterion.negative"],
                date_range=date_range)


def distance_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """How results decay with distance from the practice (needs location assets)."""
    query = (
        Query("distance_view")
        .select("campaign.name", "distance_view.distance_bucket", CORE_METRICS)
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Performance by distance from practice",
                dimensions=["distance_view.distance_bucket", "campaign.name"],
                date_range=date_range,
                notes=["Requires location assets on the account."])


# ---------------------------------------------------------------------------
# audience, schedule, device
# ---------------------------------------------------------------------------


def income_performance(client: GadsClient, customer_id=None, date_range="LAST_90_DAYS") -> Report:
    """Results by household income decile (US only)."""
    date_range = "LAST_30_DAYS" if date_range == "LAST_90_DAYS" else date_range
    query = (
        Query("income_range_view")
        .select("campaign.name", "ad_group.name",
                "ad_group_criterion.income_range.type",
                "ad_group_criterion.bid_modifier", CORE_METRICS)
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Performance by household income",
                dimensions=["ad_group_criterion.income_range.type", "campaign.name",
                            "ad_group_criterion.bid_modifier"],
                date_range=date_range,
                notes=["Income targeting is US-only and uses Google's own decile "
                       "estimate for the searcher's area, not a declared income."])


def demographic_performance(client: GadsClient, customer_id=None,
                            date_range="LAST_30_DAYS", dimension: str = "age") -> Report:
    """Results by age, gender or parental status."""
    resources = {
        "age": ("age_range_view", "ad_group_criterion.age_range.type"),
        "gender": ("gender_view", "ad_group_criterion.gender.type"),
        "parental": ("parental_status_view", "ad_group_criterion.parental_status.type"),
    }
    if dimension not in resources:
        raise ValueError(f"dimension must be one of {sorted(resources)}")
    resource, field_path = resources[dimension]
    query = (
        Query(resource)
        .select("campaign.name", "ad_group.name", field_path,
                "ad_group_criterion.bid_modifier", CORE_METRICS)
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name=f"Performance by {dimension}",
                dimensions=[field_path, "campaign.name", "ad_group_criterion.bid_modifier"],
                date_range=date_range)


def schedule_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """Hour x day - the input for dayparting around the practice's opening hours."""
    query = (
        Query("campaign")
        .select("campaign.name", "segments.day_of_week", "segments.hour", CORE_METRICS)
        .where("campaign.status = 'ENABLED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Performance by day and hour",
                dimensions=["segments.day_of_week", "segments.hour", "campaign.name"],
                date_range=date_range,
                notes=["Compare against front-desk hours: clicks that land when "
                       "nobody answers the phone are the cheapest thing to fix."])


def device_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """Mobile vs desktop vs tablet - dental emergency traffic is overwhelmingly mobile."""
    query = (
        Query("campaign")
        .select("campaign.name", "segments.device", CORE_METRICS)
        .where("campaign.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Performance by device",
                dimensions=["segments.device", "campaign.name"], date_range=date_range)


# ---------------------------------------------------------------------------
# ads, assets, competition
# ---------------------------------------------------------------------------


def ad_performance(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """Ads with their strength and approval status."""
    query = (
        Query("ad_group_ad")
        .select("campaign.name", "ad_group.name", "ad_group_ad.ad.id",
                "ad_group_ad.status", "ad_group_ad.ad_strength",
                "ad_group_ad.policy_summary.approval_status", CORE_METRICS)
        .where("ad_group_ad.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Ad performance",
                dimensions=["campaign.name", "ad_group.name", "ad_group_ad.ad.id",
                            "ad_group_ad.status", "ad_group_ad.ad_strength",
                            "ad_group_ad.policy_summary.approval_status"],
                date_range=date_range)


def rsa_asset_performance(client: GadsClient, customer_id=None,
                          date_range="LAST_30_DAYS") -> Report:
    """Headline/description level results, with Google's LOW/GOOD/BEST label."""
    query = (
        Query("ad_group_ad_asset_view")
        .select("campaign.name", "ad_group.name", "asset.text_asset.text",
                "ad_group_ad_asset_view.field_type",
                "ad_group_ad_asset_view.performance_label",
                "ad_group_ad_asset_view.pinned_field", CORE_METRICS)
        .where("ad_group_ad_asset_view.enabled = TRUE")
        .during(date_range)
        .order_by("metrics.impressions")
    )
    return _run(client, customer_id, query, name="RSA asset performance",
                dimensions=["asset.text_asset.text", "ad_group_ad_asset_view.field_type",
                            "ad_group_ad_asset_view.performance_label",
                            "ad_group_ad_asset_view.pinned_field", "ad_group.name"],
                metrics=["metrics.impressions", "metrics.clicks", "ctr",
                         "metrics.conversions"],
                date_range=date_range,
                notes=["Replace LOW assets; a label only appears once the asset has "
                       "enough serving history, so LEARNING is not a problem."])


def auction_insights(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS",
                     campaign_ids: Sequence[int] | None = None) -> Report:
    """Who else is showing on your dental searches, and how often they beat you."""
    query = (
        Query("campaign")
        .select("campaign.name", "segments.auction_insight_domain",
                "metrics.auction_insight_search_impression_share",
                "metrics.auction_insight_search_absolute_top_impression_share",
                "metrics.auction_insight_search_overlap_rate",
                "metrics.auction_insight_search_outranking_share")
        .where("campaign.status = 'ENABLED'")
        .during(date_range)
        .order_by("metrics.auction_insight_search_impression_share")
    )
    if campaign_ids:
        query.one_of("campaign.id", list(campaign_ids))
    return _run(client, customer_id, query, name="Auction insights",
                dimensions=["segments.auction_insight_domain", "campaign.name"],
                metrics=["metrics.auction_insight_search_impression_share",
                         "metrics.auction_insight_search_absolute_top_impression_share",
                         "metrics.auction_insight_search_overlap_rate",
                         "metrics.auction_insight_search_outranking_share"],
                date_range=date_range, totals=False,
                notes=["Track month over month: a new domain climbing your impression "
                       "share is usually a new practice or an agency change nearby."])


def landing_pages(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS") -> Report:
    """Which pages the traffic lands on, and what happens there."""
    query = (
        Query("landing_page_view")
        .select("landing_page_view.unexpanded_final_url", "campaign.name",
                CORE_METRICS, "metrics.mobile_friendly_clicks_percentage")
        .during(date_range)
        .order_by("metrics.cost_micros")
    )
    return _run(client, customer_id, query, name="Landing page performance",
                dimensions=["landing_page_view.unexpanded_final_url", "campaign.name"],
                date_range=date_range)


# ---------------------------------------------------------------------------
# calls, conversions, health
# ---------------------------------------------------------------------------


def calls(client: GadsClient, customer_id=None, date_range="LAST_30_DAYS",
          min_duration_seconds: int = 0) -> Report:
    """Individual calls from call assets / call-only ads, with duration."""
    query = (
        Query("call_view")
        .select("campaign.name", "call_view.start_call_date_time",
                "call_view.call_duration_seconds", "call_view.call_status",
                "call_view.caller_area_code", "call_view.type")
        .during(date_range)
        .order_by("call_view.start_call_date_time")
    )
    if min_duration_seconds:
        query.at_least("call_view.call_duration_seconds", min_duration_seconds)
    return _run(client, customer_id, query, name="Calls",
                dimensions=["call_view.start_call_date_time", "campaign.name",
                            "call_view.call_duration_seconds", "call_view.call_status",
                            "call_view.caller_area_code"],
                metrics=[], date_range=date_range, totals=False,
                notes=["Calls under ~60 seconds rarely become booked appointments; "
                       "that is the qualified-call threshold the agent optimises to."])


def conversion_actions(client: GadsClient, customer_id=None) -> Report:
    """Every conversion action, whether it is primary, and how it counts."""
    query = (
        Query("conversion_action")
        .select("conversion_action.id", "conversion_action.name",
                "conversion_action.category", "conversion_action.type",
                "conversion_action.status", "conversion_action.primary_for_goal",
                "conversion_action.counting_type",
                "conversion_action.click_through_lookback_window_days",
                "conversion_action.value_settings.default_value")
        .where("conversion_action.status != 'REMOVED'")
    )
    return _run(client, customer_id, query, name="Conversion actions",
                dimensions=["conversion_action.name", "conversion_action.category",
                            "conversion_action.type", "conversion_action.status",
                            "conversion_action.primary_for_goal",
                            "conversion_action.counting_type"],
                metrics=[], totals=False,
                notes=["Only primary actions drive bidding. A practice that counts "
                       "every button click as primary is bidding on noise."])


def conversion_breakdown(client: GadsClient, customer_id=None,
                         date_range="LAST_30_DAYS") -> Report:
    """Which conversion action is producing the numbers - calls, bookings or clicks."""
    query = (
        Query("campaign")
        .select("campaign.name", "segments.conversion_action_name",
                "metrics.conversions", "metrics.conversions_value",
                "metrics.cost_micros", "metrics.clicks", "metrics.impressions")
        .where("campaign.status != 'REMOVED'")
        .during(date_range)
        .order_by("metrics.conversions")
    )
    return _run(client, customer_id, query, name="Conversions by action",
                dimensions=["segments.conversion_action_name", "campaign.name"],
                metrics=["metrics.conversions", "metrics.conversions_value", "cpa"],
                date_range=date_range)


def disapprovals(client: GadsClient, customer_id=None) -> Report:
    """Ads that are not running because Google rejected them."""
    query = (
        Query("ad_group_ad")
        .select("campaign.name", "ad_group.name", "ad_group_ad.ad.id",
                "ad_group_ad.policy_summary.approval_status",
                "ad_group_ad.policy_summary.review_status",
                "ad_group_ad.policy_summary.policy_topic_entries")
        .where("ad_group_ad.status != 'REMOVED'")
        .one_of("ad_group_ad.policy_summary.approval_status",
                ["DISAPPROVED", "AREA_OF_INTEREST_ONLY"])
    )
    return _run(client, customer_id, query, name="Disapproved ads",
                dimensions=["campaign.name", "ad_group.name", "ad_group_ad.ad.id",
                            "ad_group_ad.policy_summary.approval_status",
                            "ad_group_ad.policy_summary.policy_topic_entries"],
                metrics=[], totals=False)


def change_history(client: GadsClient, customer_id=None, days: int = 14,
                   limit: int = 500) -> Report:
    """Who changed what recently - including changes this agent made.

    The API only keeps 30 days of change events and requires both a date filter
    and a LIMIT.
    """
    import datetime as dt

    days = max(1, min(days, 29))
    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    query = (
        Query("change_event")
        .select("change_event.change_date_time", "change_event.user_email",
                "change_event.client_type", "change_event.change_resource_type",
                "change_event.resource_change_operation", "change_event.changed_fields",
                "change_event.campaign", "change_event.ad_group")
        .where(f"change_event.change_date_time >= '{start}'")
        .order_by("change_event.change_date_time")
        .limit(limit)
    )
    return _run(client, customer_id, query, name=f"Change history (last {days} days)",
                dimensions=["change_event.change_date_time", "change_event.user_email",
                            "change_event.client_type", "change_event.change_resource_type",
                            "change_event.resource_change_operation",
                            "change_event.changed_fields"],
                metrics=[], totals=False)


def recommendations(client: GadsClient, customer_id=None) -> Report:
    """Google's own suggestions - read them, apply selectively, never in bulk."""
    query = (
        Query("recommendation")
        .select("recommendation.type", "recommendation.campaign",
                "recommendation.resource_name",
                "recommendation.impact.potential_metrics.impressions",
                "recommendation.impact.potential_metrics.clicks",
                "recommendation.impact.potential_metrics.conversions",
                "recommendation.impact.potential_metrics.cost_micros",
                "recommendation.impact.base_metrics.conversions",
                "recommendation.impact.base_metrics.cost_micros")
    )
    report = _run(client, customer_id, query, name="Google recommendations",
                  dimensions=["recommendation.type", "recommendation.campaign"],
                  metrics=["potential_extra_conversions", "potential_extra_cost"],
                  totals=False,
                  notes=["Auto-apply is off for a reason: broad-match and budget "
                         "recommendations routinely raise spend faster than bookings."])
    for row in report.rows:
        base_conv = row.get("recommendation.impact.base_metrics.conversions") or 0
        pot_conv = row.get("recommendation.impact.potential_metrics.conversions") or 0
        base_cost = from_micros(row.get("recommendation.impact.base_metrics.cost_micros"))
        pot_cost = from_micros(row.get("recommendation.impact.potential_metrics.cost_micros"))
        row["potential_extra_conversions"] = round(pot_conv - base_conv, 2)
        row["potential_extra_cost"] = round(pot_cost - base_cost, 2)
    return report


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

REPORTS: dict[str, Callable[..., Report]] = {
    "account_summary": account_summary,
    "campaign_performance": campaign_performance,
    "ad_group_performance": ad_group_performance,
    "budget_pacing": budget_pacing,
    "keyword_performance": keyword_performance,
    "search_terms": search_terms,
    "negative_keywords": negative_keywords,
    "zip_performance": zip_performance,
    "city_performance": city_performance,
    "targeted_locations": targeted_locations,
    "distance_performance": distance_performance,
    "income_performance": income_performance,
    "demographic_performance": demographic_performance,
    "schedule_performance": schedule_performance,
    "device_performance": device_performance,
    "ad_performance": ad_performance,
    "rsa_asset_performance": rsa_asset_performance,
    "auction_insights": auction_insights,
    "landing_pages": landing_pages,
    "calls": calls,
    "conversion_actions": conversion_actions,
    "conversion_breakdown": conversion_breakdown,
    "disapprovals": disapprovals,
    "change_history": change_history,
    "recommendations": recommendations,
}


def run_report(client: GadsClient, name: str, customer_id=None, **kwargs) -> Report:
    if name not in REPORTS:
        raise ValueError(f"Unknown report {name!r}. Available: {', '.join(sorted(REPORTS))}")
    return REPORTS[name](client, customer_id=customer_id, **kwargs)
