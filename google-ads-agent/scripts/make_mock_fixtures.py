#!/usr/bin/env python3
"""Generate the mock fixtures used when GADS_MOCK=1.

The data models a real single-location dental practice: four Search campaigns,
a dominant emergency campaign, a leaky broad-match ad group, some wasted spend
on job-seeker and DIY search terms, and a spread of postal codes.  It is meant
to be *realistic enough that the optimisation rules fire*, so the whole daily
routine can be rehearsed before a developer token exists.

Re-run after adding a report:  python scripts/make_mock_fixtures.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "gads" / "mock"
CID = "1234567890"
rng = random.Random(20260818)

CAMPAIGNS = [
    (2001, "ETFD | Search | Emergency Dentist | Miami | 24-7", "MAXIMIZE_CONVERSIONS", 120.0),
    (2002, "ETFD | Search | General Dentist | Miami", "MAXIMIZE_CONVERSIONS", 90.0),
    (2003, "ETFD | Search | Dental Implants | Miami", "MAXIMIZE_CONVERSIONS", 75.0),
    (2004, "ETFD | Search | Espanol | General + Emergency", "MAXIMIZE_CONVERSIONS", 45.0),
]

AD_GROUPS = [
    (3001, 2001, "Emergency Dentist - Exact"),
    (3002, 2001, "Tooth Pain - Phrase"),
    (3003, 2002, "Dentist Near Me - Exact"),
    (3004, 2002, "New Patient Special - Phrase"),
    (3005, 2002, "General Dentistry - Broad"),
    (3006, 2003, "Dental Implants - Exact"),
    (3007, 2004, "Dentista Cerca de Mi"),
]

KEYWORDS = [
    # (ad_group, text, match, impressions, clicks, cost, conversions, quality score)
    (3001, "emergency dentist", "EXACT", 4120, 512, 1890.0, 41, 8),
    (3001, "emergency dentist near me", "EXACT", 3380, 447, 1720.0, 38, 8),
    (3001, "24 hour dentist", "EXACT", 1210, 138, 610.0, 9, 7),
    (3002, "tooth pain relief", "PHRASE", 2650, 210, 780.0, 6, 5),
    (3002, "broken tooth", "PHRASE", 980, 96, 402.0, 7, 7),
    (3003, "dentist near me", "EXACT", 5300, 604, 2110.0, 44, 8),
    (3003, "dental office near me", "EXACT", 2210, 233, 902.0, 15, 7),
    (3004, "new patient dental special", "PHRASE", 860, 74, 288.0, 8, 8),
    (3005, "dentist", "BROAD", 9400, 421, 1655.0, 4, 4),
    (3005, "teeth cleaning", "BROAD", 3120, 188, 690.0, 3, 5),
    (3006, "dental implants", "EXACT", 1980, 176, 1580.0, 7, 7),
    (3006, "full mouth dental implants cost", "EXACT", 740, 61, 690.0, 2, 6),
    (3007, "dentista cerca de mi", "EXACT", 1740, 201, 620.0, 17, 8),
]

SEARCH_TERMS = [
    # (ad_group, term, matched_as, status, impr, clicks, cost, conv)
    (3005, "dental assistant jobs miami", "BROAD", "NONE", 420, 38, 121.0, 0),
    (3005, "how to pull your own tooth", "BROAD", "NONE", 260, 21, 63.0, 0),
    (3005, "free dental clinic miami", "BROAD", "NONE", 610, 55, 168.0, 0),
    (3005, "dental hygienist school", "BROAD", "NONE", 180, 14, 44.0, 0),
    (3005, "medicaid dentist miami", "BROAD", "NONE", 390, 41, 128.0, 0),
    (3005, "dentist open now near me", "BROAD", "NONE", 340, 47, 158.0, 5),
    (3005, "walk in dentist miami", "BROAD", "NONE", 290, 39, 141.0, 4),
    (3002, "cracked molar hurts", "PHRASE", "NONE", 150, 19, 71.0, 2),
    (3001, "emergency dentist near me open now", "EXACT", "ADDED", 880, 121, 470.0, 12),
    (3006, "veneers cost miami", "EXACT", "NONE", 210, 18, 152.0, 1),
    (3006, "dental implants for dogs", "EXACT", "NONE", 60, 4, 33.0, 0),
    (3003, "dentist salary florida", "EXACT", "NONE", 130, 9, 27.0, 0),
]

# geoTargetConstant id -> (zip, median household income)
POSTAL = [
    ("9060601", "33131", 118000), ("9060602", "33130", 96000),
    ("9060603", "33133", 132000), ("9060604", "33125", 47000),
    ("9060605", "33135", 42000), ("9060606", "33143", 141000),
    ("9060607", "33156", 168000), ("9060608", "33176", 89000),
    ("9060609", "33186", 78000), ("9060610", "33172", 55000),
]


def money(dollars: float) -> int:
    return int(round(dollars * 1_000_000))


def metrics(impr, clicks, cost, conv, value=None):
    return {
        "metrics.impressions": impr,
        "metrics.clicks": clicks,
        "metrics.cost_micros": money(cost),
        "metrics.conversions": float(conv),
        "metrics.conversions_value": float(value if value is not None else conv * 350),
    }


def write(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"  {name}.json  ({len(rows)} rows)")


def campaign_totals(campaign_id: int) -> tuple[int, int, float, float]:
    impr = clicks = 0
    cost = conv = 0.0
    for ag_id, camp_id, _ in AD_GROUPS:
        if camp_id != campaign_id:
            continue
        for kw in KEYWORDS:
            if kw[0] == ag_id:
                impr += kw[3]
                clicks += kw[4]
                cost += kw[5]
                conv += kw[6]
    return impr, clicks, cost, conv


def build() -> None:
    print("Writing mock fixtures to", OUT)

    # --- campaigns -------------------------------------------------------
    campaigns = []
    for cid, name, strategy, budget in CAMPAIGNS:
        impr, clicks, cost, conv = campaign_totals(cid)
        lost_budget = 0.18 if "Emergency" in name else 0.04
        campaigns.append({
            "campaign.id": cid, "campaign.name": name, "campaign.status": "ENABLED",
            "campaign.advertising_channel_type": "SEARCH",
            "campaign.bidding_strategy_type": strategy,
            "campaign_budget.id": 7000 + (cid - 2000),
            "campaign_budget.amount_micros": money(budget),
            "campaign.maximize_conversions.target_cpa_micros": money(
                {2001: 75, 2002: 90, 2003: 300, 2004: 80}[cid]),
            "campaign.target_cpa.target_cpa_micros": 0,
            "campaign.start_date_time": "2026-01-15",
            **metrics(impr, clicks, cost, conv),
            "metrics.search_impression_share": round(0.62 if lost_budget > 0.1 else 0.71, 4),
            "metrics.search_rank_lost_impression_share": 0.2,
            "metrics.search_budget_lost_impression_share": lost_budget,
            "metrics.search_absolute_top_impression_share": 0.31,
        })
    write("campaign", campaigns)

    # --- ad groups -------------------------------------------------------
    ad_groups = []
    for ag_id, camp_id, ag_name in AD_GROUPS:
        camp_name = next(c[1] for c in CAMPAIGNS if c[0] == camp_id)
        impr = clicks = 0
        cost = conv = 0.0
        for kw in KEYWORDS:
            if kw[0] == ag_id:
                impr += kw[3]; clicks += kw[4]; cost += kw[5]; conv += kw[6]
        ad_groups.append({
            "campaign.id": camp_id, "campaign.name": camp_name,
            "ad_group.id": ag_id, "ad_group.name": ag_name, "ad_group.status": "ENABLED",
            **metrics(impr, clicks, cost, conv),
        })
    write("ad_group", ad_groups)

    # --- keywords --------------------------------------------------------
    keywords = []
    for i, (ag_id, text, match, impr, clicks, cost, conv, qs) in enumerate(KEYWORDS):
        camp_id = next(a[1] for a in AD_GROUPS if a[0] == ag_id)
        keywords.append({
            "campaign.id": camp_id,
            "campaign.name": next(c[1] for c in CAMPAIGNS if c[0] == camp_id),
            "ad_group.id": ag_id,
            "ad_group.name": next(a[2] for a in AD_GROUPS if a[0] == ag_id),
            "ad_group_criterion.criterion_id": 400000 + i,
            "ad_group_criterion.keyword.text": text,
            "ad_group_criterion.keyword.match_type": match,
            "ad_group_criterion.status": "ENABLED",
            "ad_group_criterion.quality_info.quality_score": qs,
            **metrics(impr, clicks, cost, conv),
        })
    write("keyword_view", keywords)

    # --- search terms ----------------------------------------------------
    terms = []
    for ag_id, term, matched, status, impr, clicks, cost, conv in SEARCH_TERMS:
        camp_id = next(a[1] for a in AD_GROUPS if a[0] == ag_id)
        terms.append({
            "campaign.id": camp_id,
            "campaign.name": next(c[1] for c in CAMPAIGNS if c[0] == camp_id),
            "ad_group.name": next(a[2] for a in AD_GROUPS if a[0] == ag_id),
            "search_term_view.search_term": term,
            "search_term_view.status": status,
            "segments.search_term_match_type": matched,
            **metrics(impr, clicks, cost, conv),
        })
    write("search_term_view", terms)

    # --- geography -------------------------------------------------------
    geo = []
    for gid, zip_code, income in POSTAL:
        clicks = rng.randint(40, 260)
        conv = round(clicks * rng.uniform(0.03, 0.14), 1)
        geo.append({
            "campaign.name": CAMPAIGNS[0][1],
            "segments.geo_target_postal_code": f"geoTargetConstants/{gid}",
            "geographic_view.location_type": "LOCATION_OF_PRESENCE",
            **metrics(clicks * 9, clicks, clicks * rng.uniform(3.1, 5.4), conv),
        })
    write("geographic_view", geo)

    write("location_view", [{
        "campaign.name": CAMPAIGNS[0][1],
        "campaign_criterion.location.geo_target_constant": f"geoTargetConstants/{gid}",
        "campaign_criterion.bid_modifier": 1.0,
        "campaign_criterion.negative": False,
        **metrics(900, 88, 320.0, 6),
    } for gid, _, _ in POSTAL[:5]])

    write("distance_view", [{
        "campaign.name": CAMPAIGNS[0][1],
        "distance_view.distance_bucket": bucket,
        **metrics(impr, clicks, cost, conv),
    } for bucket, impr, clicks, cost, conv in [
        ("WITHIN_1_MILE", 3200, 410, 1420.0, 52),
        ("WITHIN_5_MILES", 4100, 452, 1690.0, 41),
        ("WITHIN_10_MILES", 2600, 240, 940.0, 12),
        ("WITHIN_15_MILES", 1400, 96, 402.0, 2),
    ]])

    # --- audience / schedule / device ------------------------------------
    write("income_range_view", [{
        "campaign.name": CAMPAIGNS[2][1], "ad_group.name": "Dental Implants - Exact",
        "ad_group_criterion.income_range.type": bucket,
        "ad_group_criterion.bid_modifier": 1.0,
        **metrics(impr, clicks, cost, conv),
    } for bucket, impr, clicks, cost, conv in [
        ("INCOME_RANGE_90_UP", 620, 74, 690.0, 6),
        ("INCOME_RANGE_80_90", 410, 44, 402.0, 3),
        ("INCOME_RANGE_70_80", 380, 39, 358.0, 1),
        ("INCOME_RANGE_50_60", 290, 26, 240.0, 0),
        ("INCOME_RANGE_0_50", 480, 41, 372.0, 0),
    ]])

    write("age_range_view", [{
        "campaign.name": CAMPAIGNS[1][1], "ad_group.name": "Dentist Near Me - Exact",
        "ad_group_criterion.age_range.type": bucket,
        "ad_group_criterion.bid_modifier": 1.0,
        **metrics(impr, clicks, cost, conv),
    } for bucket, impr, clicks, cost, conv in [
        ("AGE_RANGE_25_34", 1900, 220, 760.0, 18),
        ("AGE_RANGE_35_44", 1700, 205, 720.0, 21),
        ("AGE_RANGE_45_54", 1200, 141, 502.0, 13),
        ("AGE_RANGE_55_64", 900, 96, 340.0, 7),
        ("AGE_RANGE_18_24", 700, 62, 210.0, 2),
    ]])

    hours = []
    for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]:
        for hour in range(24):
            open_hours = 8 <= hour <= 18 and day != "SUNDAY"
            clicks = rng.randint(6, 40) if open_hours else rng.randint(0, 9)
            conv = round(clicks * (0.11 if open_hours else 0.03), 1)
            hours.append({
                "campaign.name": CAMPAIGNS[0][1],
                "segments.day_of_week": day, "segments.hour": hour,
                **metrics(clicks * 8, clicks, clicks * 3.9, conv),
            })
    write("campaign+day_of_week-hour", hours)

    write("campaign+device", [{
        "campaign.name": name, "segments.device": device,
        **metrics(impr, clicks, cost, conv),
    } for name, device, impr, clicks, cost, conv in [
        (CAMPAIGNS[0][1], "MOBILE", 7400, 890, 3210.0, 74),
        (CAMPAIGNS[0][1], "DESKTOP", 2100, 190, 780.0, 11),
        (CAMPAIGNS[0][1], "TABLET", 310, 21, 88.0, 1),
        (CAMPAIGNS[1][1], "MOBILE", 8200, 810, 2890.0, 52),
        (CAMPAIGNS[1][1], "DESKTOP", 3400, 290, 1120.0, 14),
    ]])

    write("campaign+auction_insight_domain", [{
        "campaign.name": CAMPAIGNS[0][1],
        "segments.auction_insight_domain": domain,
        "metrics.auction_insight_search_impression_share": is_,
        "metrics.auction_insight_search_absolute_top_impression_share": abs_top,
        "metrics.auction_insight_search_overlap_rate": overlap,
        "metrics.auction_insight_search_outranking_share": outrank,
    } for domain, is_, abs_top, overlap, outrank in [
        ("you", 0.62, 0.31, 1.0, 1.0),
        ("smilemiamidental.com", 0.48, 0.22, 0.61, 0.44),
        ("brickellsmiles.com", 0.41, 0.19, 0.55, 0.38),
        ("emergencydentistmiami.net", 0.37, 0.24, 0.49, 0.51),
        ("coralwaydental.com", 0.22, 0.08, 0.30, 0.19),
    ]])

    write("campaign+conversion_action_name", [{
        "campaign.name": CAMPAIGNS[i][1],
        "segments.conversion_action_name": action,
        "metrics.conversions": conv, "metrics.conversions_value": conv * value,
        "metrics.cost_micros": money(cost), "metrics.clicks": clicks,
        "metrics.impressions": clicks * 9,
    } for i, action, conv, value, cost, clicks in [
        (0, "Call from ad (60s+)", 61.0, 420, 2400.0, 620),
        (0, "Click to call - LP", 34.0, 300, 1200.0, 310),
        (1, "Book online - Modento", 29.0, 380, 1600.0, 410),
        (1, "Click to call - LP", 26.0, 300, 1100.0, 290),
        (2, "Booked appointment (offline)", 5.0, 3200, 1900.0, 210),
    ]])

    # --- ads and assets --------------------------------------------------
    write("ad_group_ad", [{
        "campaign.name": next(c[1] for c in CAMPAIGNS if c[0] == camp_id),
        "ad_group.name": ag_name, "ad_group_ad.ad.id": 5000 + i,
        "ad_group_ad.status": "ENABLED",
        "ad_group_ad.ad_strength": strength,
        "ad_group_ad.policy_summary.approval_status": approval,
        "ad_group_ad.policy_summary.review_status": "REVIEWED",
        "ad_group_ad.policy_summary.policy_topic_entries": policy,
        **metrics(impr, clicks, cost, conv),
    } for i, (camp_id, ag_name, strength, approval, policy, impr, clicks, cost, conv) in enumerate([
        (2001, "Emergency Dentist - Exact", "EXCELLENT", "APPROVED", "", 6400, 780, 2900.0, 68),
        (2001, "Tooth Pain - Phrase", "GOOD", "APPROVED", "", 3200, 280, 1080.0, 13),
        (2002, "Dentist Near Me - Exact", "GOOD", "APPROVED", "", 7100, 760, 2800.0, 55),
        (2003, "Dental Implants - Exact", "AVERAGE", "DISAPPROVED", "HEALTHCARE_CLAIM", 900, 0, 0.0, 0),
        (2004, "Dentista Cerca de Mi", "GOOD", "APPROVED", "", 1700, 200, 615.0, 17),
    ])])

    write("ad_group_ad_asset_view", [{
        "campaign.name": CAMPAIGNS[0][1], "ad_group.name": "Emergency Dentist - Exact",
        "asset.text_asset.text": text,
        "ad_group_ad_asset_view.field_type": field_type,
        "ad_group_ad_asset_view.performance_label": label,
        "ad_group_ad_asset_view.pinned_field": pinned,
        **metrics(impr, clicks, cost, conv),
    } for text, field_type, label, pinned, impr, clicks, conv, cost in [
        ("Emergency Dentist Open Now", "HEADLINE", "BEST", "HEADLINE_1", 5200, 610, 58, 2100.0),
        ("Same-Day Tooth Pain Relief", "HEADLINE", "GOOD", "UNSPECIFIED", 4100, 420, 34, 1500.0),
        ("Miami Dentist Since 2009", "HEADLINE", "LOW", "UNSPECIFIED", 3800, 190, 6, 700.0),
        ("Walk-Ins Welcome 7 Days", "HEADLINE", "GOOD", "UNSPECIFIED", 3400, 360, 29, 1300.0),
        ("Call now - we answer 24/7 and see emergencies today.", "DESCRIPTION", "BEST", "UNSPECIFIED", 5000, 540, 51, 1900.0),
        ("Financing available. Most insurance accepted.", "DESCRIPTION", "LOW", "UNSPECIFIED", 3000, 140, 4, 520.0),
    ]])

    write("landing_page_view", [{
        "landing_page_view.unexpanded_final_url": url,
        "campaign.name": name,
        "metrics.mobile_friendly_clicks_percentage": 1.0,
        **metrics(impr, clicks, cost, conv),
    } for url, name, impr, clicks, cost, conv in [
        ("https://everythingteeth.com/emergency-dentist-en", CAMPAIGNS[0][1], 9800, 1100, 4100.0, 88),
        ("https://everythingteeth.com/general-dentist-en", CAMPAIGNS[1][1], 11200, 1050, 3980.0, 62),
        ("https://everythingteeth.com/general-dentist-es", CAMPAIGNS[3][1], 1740, 201, 620.0, 17),
    ]])

    # --- calls, conversions, health --------------------------------------
    calls = []
    for i in range(40):
        duration = rng.choice([8, 14, 22, 45, 63, 92, 140, 210, 305])
        calls.append({
            "campaign.name": CAMPAIGNS[0][1] if i % 2 else CAMPAIGNS[1][1],
            "call_view.start_call_date_time": f"2026-08-{10 + i % 8:02d} {9 + i % 9:02d}:15:00",
            "call_view.call_duration_seconds": duration,
            "call_view.call_status": "RECEIVED" if duration > 5 else "MISSED",
            "call_view.caller_area_code": rng.choice(["305", "786", "954"]),
            "call_view.type": "MANUALLY_DIALED",
        })
    write("call_view", calls)

    write("conversion_action", [{
        "conversion_action.id": 900 + i, "conversion_action.name": name,
        "conversion_action.category": category, "conversion_action.type": type_,
        "conversion_action.status": "ENABLED",
        "conversion_action.primary_for_goal": primary,
        "conversion_action.counting_type": counting,
        "conversion_action.click_through_lookback_window_days": 30,
        "conversion_action.value_settings.default_value": value,
    } for i, (name, category, type_, primary, counting, value) in enumerate([
        ("Call from ad (60s+)", "PHONE_CALL_LEAD", "AD_CALL", True, "ONE_PER_CLICK", 0.0),
        ("Click to call - LP", "PHONE_CALL_LEAD", "WEBPAGE", True, "ONE_PER_CLICK", 0.0),
        ("Book online - Modento", "BOOK_APPOINTMENT", "WEBPAGE", True, "ONE_PER_CLICK", 0.0),
        ("Directions click", "DEFAULT", "WEBPAGE", False, "MANY_PER_CLICK", 0.0),
        ("Booked appointment (offline)", "BOOK_APPOINTMENT", "UPLOAD_CLICKS", False, "ONE_PER_CLICK", 0.0),
        ("Patient showed (offline)", "BOOK_APPOINTMENT", "UPLOAD_CLICKS", False, "ONE_PER_CLICK", 0.0),
    ])])

    write("change_event", [{
        "change_event.change_date_time": f"2026-08-{12 + i:02d} 10:0{i}:00",
        "change_event.user_email": email,
        "change_event.client_type": client_type,
        "change_event.change_resource_type": resource,
        "change_event.resource_change_operation": op,
        "change_event.changed_fields": fields,
        "change_event.campaign": f"customers/{CID}/campaigns/2001",
        "change_event.ad_group": "",
    } for i, (email, client_type, resource, op, fields) in enumerate([
        ("agent@relevanceonlinemarketing.com", "GOOGLE_ADS_API", "AD_GROUP_CRITERION", "CREATE", "negative,keyword.text"),
        ("agent@relevanceonlinemarketing.com", "GOOGLE_ADS_API", "AD_GROUP_CRITERION", "UPDATE", "status"),
        ("owner@everythingteeth.com", "GOOGLE_ADS_WEB_CLIENT", "CAMPAIGN_BUDGET", "UPDATE", "amount_micros"),
    ])])

    write("recommendation", [{
        "recommendation.type": rec_type,
        "recommendation.campaign": f"customers/{CID}/campaigns/{camp}",
        "recommendation.resource_name": f"customers/{CID}/recommendations/{800 + i}",
        "recommendation.impact.potential_metrics.impressions": 5200,
        "recommendation.impact.potential_metrics.clicks": 610,
        "recommendation.impact.potential_metrics.conversions": pot_conv,
        "recommendation.impact.potential_metrics.cost_micros": money(pot_cost),
        "recommendation.impact.base_metrics.conversions": base_conv,
        "recommendation.impact.base_metrics.cost_micros": money(base_cost),
    } for i, (rec_type, camp, base_conv, pot_conv, base_cost, pot_cost) in enumerate([
        ("CAMPAIGN_BUDGET", 2001, 68.0, 79.0, 3600.0, 4900.0),
        ("KEYWORD", 2002, 55.0, 61.0, 2800.0, 3100.0),
        ("SEARCH_PARTNERS_OPT_IN", 2002, 55.0, 58.0, 2800.0, 3300.0),
    ])])

    write("geo_target_constant", [{
        "geo_target_constant.resource_name": f"geoTargetConstants/{gid}",
        "geo_target_constant.id": int(gid),
        "geo_target_constant.name": zip_code,
        "geo_target_constant.canonical_name": f"{zip_code},Florida,United States",
        "geo_target_constant.target_type": "Postal Code",
    } for gid, zip_code, _ in POSTAL])

    write("customer_client", [{
        "customer_client.client_customer": f"customers/{CID}",
        "customer_client.id": int(CID),
        "customer_client.descriptive_name": "Everything Teeth Family Dental (mock)",
        "customer_client.currency_code": "USD",
        "customer_client.time_zone": "America/New_York",
        "customer_client.manager": False,
        "customer_client.status": "ENABLED",
        "customer_client.level": 1,
    }])

    write("campaign_criterion", [{
        "campaign.name": CAMPAIGNS[1][1],
        "campaign_criterion.criterion_id": 700 + i,
        "campaign_criterion.keyword.text": text,
        "campaign_criterion.keyword.match_type": "PHRASE",
    } for i, text in enumerate(["jobs", "salary", "school"])])

    write("ad_group_criterion", [{
        "campaign.name": CAMPAIGNS[1][1], "ad_group.name": "General Dentistry - Broad",
        "ad_group_criterion.criterion_id": 710 + i,
        "ad_group_criterion.keyword.text": text,
        "ad_group_criterion.keyword.match_type": "PHRASE",
    } for i, text in enumerate(["free", "cheap"])])

    write("shared_criterion", [{
        "shared_set.name": "ETFD - Master dental negatives",
        "shared_set.id": 6001,
        "shared_criterion.criterion_id": 720 + i,
        "shared_criterion.keyword.text": text,
        "shared_criterion.keyword.match_type": "PHRASE",
    } for i, text in enumerate(["dental assistant", "hygienist", "for dogs", "medicaid"])])

    print("Done.")


if __name__ == "__main__":
    build()
