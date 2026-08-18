#!/usr/bin/env python3
"""Deterministic Google Ads account health score for dental accounts (0-100).

Usage:
    python3 health_score.py metrics.json
    python3 health_score.py --example        # print a fully populated input template
    python3 health_score.py --self-test      # verify the scoring rules

The score exists so the same account state always produces the same number, and so a
score can be defended input by input. It is not a substitute for the diagnosis -- it
summarises it.

Every input is optional. Inputs that are absent are reported as unscored rather than
guessed, and the final score is renormalised over the dimensions that could be scored.
A score computed from partial data always reports its own coverage.

See ../references/health-score.md for the rubric these rules implement.
"""

import json
import sys

# (key, display name, weight). Weights sum to 100.
DIMENSIONS = [
    ("tracking", "Tracking health", 20),
    ("lead_quality", "Lead quality", 15),
    ("cost_efficiency", "Cost efficiency", 15),
    ("search_quality", "Search quality", 12),
    ("traffic", "Traffic health", 10),
    ("location", "Location quality", 8),
    ("structure", "Campaign structure", 8),
    ("conversion", "Landing page / conversion", 7),
    ("budget_bidding", "Budget & bidding", 5),
]


def lin(value, zero_at, one_at):
    """Linear score in [0,1]. Handles ascending and descending scales.

    lin(v, 30, 70)  -> 0 at v<=30, 1 at v>=70   (higher is better)
    lin(v, 15, 0)   -> 0 at v>=15, 1 at v<=0    (lower is better)
    """
    if zero_at == one_at:
        raise ValueError("zero_at and one_at must differ")
    frac = (value - zero_at) / (one_at - zero_at)
    return max(0.0, min(1.0, frac))


def steps(value, table, default):
    """First matching threshold wins. table = [(predicate, score), ...]."""
    for predicate, score in table:
        if predicate(value):
            return score
    return default


def boolean(value):
    return 1.0 if value else 0.0


def score_dimension(data, rules):
    """Score one dimension from its sub-rules, renormalising over present inputs.

    rules = [(input_key, sub_weight, scorer), ...]
    Returns (fraction, detail_list) or (None, detail_list) when nothing was scorable.
    """
    total_weight = 0.0
    earned = 0.0
    detail = []
    for key, weight, scorer in rules:
        if key not in data or data[key] is None:
            detail.append((key, None, weight))
            continue
        sub = max(0.0, min(1.0, float(scorer(data[key]))))
        earned += sub * weight
        total_weight += weight
        detail.append((key, sub, weight))
    if total_weight == 0.0:
        return None, detail
    return earned / total_weight, detail


RULES = {
    "tracking": [
        ("has_primary_conversion", 0.30, boolean),
        ("crm_variance_pct", 0.20, lambda v: steps(
            abs(v), [(lambda x: x <= 10, 1.0), (lambda x: x <= 25, 0.7),
                     (lambda x: x <= 50, 0.35)], 0.0)),
        ("days_with_zero_conversions_last_30", 0.15, lambda v: steps(
            v, [(lambda x: x == 0, 1.0), (lambda x: x <= 2, 0.6),
                (lambda x: x <= 6, 0.3)], 0.0)),
        ("duplicate_conversion_actions", 0.15, lambda v: steps(
            v, [(lambda x: x == 0, 1.0), (lambda x: x == 1, 0.5)], 0.0)),
        ("auto_tagging_enabled", 0.10, boolean),
        ("call_conversion_threshold_seconds", 0.10, lambda v: steps(
            v, [(lambda x: x >= 60, 1.0), (lambda x: x >= 30, 0.6)], 0.2)),
    ],
    "lead_quality": [
        ("qualified_lead_rate_pct", 0.40, lambda v: lin(v, 30, 70)),
        ("booked_rate_pct", 0.40, lambda v: lin(v, 20, 60)),
        ("spam_rate_pct", 0.20, lambda v: lin(v, 25, 0)),
    ],
    "cost_efficiency": [
        ("cost_per_qualified_lead_ratio", 0.70, lambda v: lin(v, 2.0, 0.8)),
        ("cpa_trend_pct", 0.30, lambda v: lin(v, 50, 0)),
    ],
    "search_quality": [
        ("high_intent_spend_pct", 0.50, lambda v: lin(v, 30, 70)),
        ("wasted_spend_pct", 0.35, lambda v: lin(v, 15, 0)),
        ("negative_list_present", 0.15, boolean),
    ],
    "traffic": [
        ("search_impression_share_pct", 0.40, lambda v: lin(v, 20, 65)),
        ("lost_is_budget_pct", 0.20, lambda v: lin(v, 30, 0)),
        ("lost_is_rank_pct", 0.20, lambda v: lin(v, 60, 15)),
        ("clicks_trend_pct", 0.20, lambda v: lin(v, -30, 0)),
    ],
    "location": [
        ("in_area_spend_pct", 0.50, lambda v: lin(v, 60, 95)),
        ("presence_only_targeting", 0.30, boolean),
        ("top_zip_spend_concentration_pct", 0.20, lambda v: lin(v, 50, 25)),
    ],
    "structure": [
        ("services_segmented", 0.30, boolean),
        ("brand_separated", 0.25, boolean),
        ("single_keyword_spend_share_pct", 0.25, lambda v: lin(v, 50, 20)),
        ("pmax_search_cannibalization", 0.20, lambda v: boolean(not v)),
    ],
    "conversion": [
        ("conversion_rate_ratio", 0.50, lambda v: lin(v, 0.25, 1.25)),
        ("mobile_desktop_cvr_ratio", 0.30, lambda v: lin(v, 0.3, 0.9)),
        ("dedicated_landing_pages", 0.20, boolean),
    ],
    "budget_bidding": [
        ("budget_limited_campaigns_with_good_cpa", 0.40, lambda v: steps(
            v, [(lambda x: x == 0, 1.0), (lambda x: x == 1, 0.6),
                (lambda x: x == 2, 0.3)], 0.0)),
        ("strategy_appropriate", 0.40, boolean),
        ("underspend_pct", 0.20, lambda v: lin(v, 40, 10)),
    ],
}


def compute(metrics):
    results = []
    scored_weight = 0.0
    earned_points = 0.0

    for key, name, weight in DIMENSIONS:
        data = metrics.get(key) or {}
        fraction, detail = score_dimension(data, RULES[key])
        if fraction is None:
            results.append({"key": key, "name": name, "weight": weight,
                            "fraction": None, "points": None, "detail": detail})
            continue
        points = fraction * weight
        scored_weight += weight
        earned_points += points
        results.append({"key": key, "name": name, "weight": weight,
                        "fraction": fraction, "points": points, "detail": detail})

    if scored_weight == 0.0:
        return {"score": None, "coverage_pct": 0.0, "dimensions": results}

    # Renormalise so a partially-scored account is not penalised for missing data.
    score = round(earned_points / scored_weight * 100)
    return {"score": score, "coverage_pct": round(scored_weight, 1),
            "raw_points": round(earned_points, 2), "dimensions": results}


def band(score):
    if score >= 85:
        return "HEALTHY"
    if score >= 70:
        return "STABLE - fixable gaps"
    if score >= 50:
        return "AT RISK"
    if score >= 30:
        return "POOR"
    return "CRITICAL"


def render(result):
    if result["score"] is None:
        return ("ACCOUNT HEALTH: DATA NOT AVAILABLE - CANNOT CONFIRM\n"
                "No scorable inputs were supplied.")

    out = [f"ACCOUNT HEALTH: {result['score']}/100  ({band(result['score'])})",
           f"Scored on {result['coverage_pct']:.0f}% of the rubric by weight.",
           "",
           f"{'Dimension':<28}{'Score':>10}{'Weight':>9}{'Lost':>8}",
           "-" * 55]

    losses = []
    for dim in result["dimensions"]:
        if dim["fraction"] is None:
            out.append(f"{dim['name']:<28}{'not scored':>10}{dim['weight']:>9}{'-':>8}")
            continue
        lost = dim["weight"] - dim["points"]
        losses.append((lost, dim))
        out.append(f"{dim['name']:<28}{dim['fraction'] * 100:>9.0f}%"
                   f"{dim['weight']:>9}{lost:>8.1f}")

    unscored = [d["name"] for d in result["dimensions"] if d["fraction"] is None]
    if unscored:
        out.append("")
        out.append("DATA NOT AVAILABLE - CANNOT CONFIRM: " + ", ".join(unscored))

    losses.sort(key=lambda pair: pair[0], reverse=True)
    top = [pair for pair in losses if pair[0] >= 0.5][:3]
    if top:
        out.append("")
        out.append("Biggest point losses:")
        for lost, dim in top:
            weak = [k for k, sub, _w in dim["detail"] if sub is not None and sub < 0.6]
            because = ("  <- " + ", ".join(weak)) if weak else ""
            out.append(f"  -{lost:.1f} pts  {dim['name']}{because}")

    return "\n".join(out)


EXAMPLE = {
    "tracking": {
        "has_primary_conversion": True,
        "crm_variance_pct": 12.0,
        "days_with_zero_conversions_last_30": 0,
        "duplicate_conversion_actions": 0,
        "auto_tagging_enabled": True,
        "call_conversion_threshold_seconds": 60,
    },
    "lead_quality": {
        "qualified_lead_rate_pct": 55.0,
        "booked_rate_pct": 38.0,
        "spam_rate_pct": 9.0,
    },
    "cost_efficiency": {
        "cost_per_qualified_lead_ratio": 0.95,
        "cpa_trend_pct": 6.0,
    },
    "search_quality": {
        "high_intent_spend_pct": 61.0,
        "wasted_spend_pct": 5.0,
        "negative_list_present": True,
    },
    "traffic": {
        "search_impression_share_pct": 44.0,
        "lost_is_budget_pct": 14.0,
        "lost_is_rank_pct": 42.0,
        "clicks_trend_pct": -4.0,
    },
    "location": {
        "in_area_spend_pct": 86.0,
        "presence_only_targeting": True,
        "top_zip_spend_concentration_pct": 24.0,
    },
    "structure": {
        "services_segmented": True,
        "brand_separated": True,
        "single_keyword_spend_share_pct": 19.0,
        "pmax_search_cannibalization": False,
    },
    "conversion": {
        "conversion_rate_ratio": 1.05,
        "mobile_desktop_cvr_ratio": 0.88,
        "dedicated_landing_pages": True,
    },
    "budget_bidding": {
        "budget_limited_campaigns_with_good_cpa": 1,
        "strategy_appropriate": True,
        "underspend_pct": 6.0,
    },
}

PERFECT = {
    "tracking": {"has_primary_conversion": True, "crm_variance_pct": 0,
                 "days_with_zero_conversions_last_30": 0,
                 "duplicate_conversion_actions": 0, "auto_tagging_enabled": True,
                 "call_conversion_threshold_seconds": 90},
    "lead_quality": {"qualified_lead_rate_pct": 80, "booked_rate_pct": 70,
                     "spam_rate_pct": 0},
    "cost_efficiency": {"cost_per_qualified_lead_ratio": 0.5, "cpa_trend_pct": -10},
    "search_quality": {"high_intent_spend_pct": 80, "wasted_spend_pct": 0,
                       "negative_list_present": True},
    "traffic": {"search_impression_share_pct": 70, "lost_is_budget_pct": 0,
                "lost_is_rank_pct": 10, "clicks_trend_pct": 5},
    "location": {"in_area_spend_pct": 99, "presence_only_targeting": True,
                 "top_zip_spend_concentration_pct": 20},
    "structure": {"services_segmented": True, "brand_separated": True,
                  "single_keyword_spend_share_pct": 15,
                  "pmax_search_cannibalization": False},
    "conversion": {"conversion_rate_ratio": 1.4, "mobile_desktop_cvr_ratio": 1.0,
                   "dedicated_landing_pages": True},
    "budget_bidding": {"budget_limited_campaigns_with_good_cpa": 0,
                       "strategy_appropriate": True, "underspend_pct": 0},
}

BROKEN = {
    "tracking": {"has_primary_conversion": False, "crm_variance_pct": 200,
                 "days_with_zero_conversions_last_30": 30,
                 "duplicate_conversion_actions": 4, "auto_tagging_enabled": False,
                 "call_conversion_threshold_seconds": 0},
    "lead_quality": {"qualified_lead_rate_pct": 5, "booked_rate_pct": 0,
                     "spam_rate_pct": 90},
    "cost_efficiency": {"cost_per_qualified_lead_ratio": 5.0, "cpa_trend_pct": 200},
    "search_quality": {"high_intent_spend_pct": 5, "wasted_spend_pct": 60,
                       "negative_list_present": False},
    "traffic": {"search_impression_share_pct": 3, "lost_is_budget_pct": 80,
                "lost_is_rank_pct": 90, "clicks_trend_pct": -90},
    "location": {"in_area_spend_pct": 20, "presence_only_targeting": False,
                 "top_zip_spend_concentration_pct": 95},
    "structure": {"services_segmented": False, "brand_separated": False,
                  "single_keyword_spend_share_pct": 90,
                  "pmax_search_cannibalization": True},
    "conversion": {"conversion_rate_ratio": 0.05, "mobile_desktop_cvr_ratio": 0.0,
                   "dedicated_landing_pages": False},
    "budget_bidding": {"budget_limited_campaigns_with_good_cpa": 9,
                       "strategy_appropriate": False, "underspend_pct": 90},
}


def self_test():
    checks = []

    def check(label, condition):
        checks.append((label, bool(condition)))

    # lin() in both directions, including clamping.
    check("lin ascending low clamp", lin(10, 30, 70) == 0.0)
    check("lin ascending high clamp", lin(90, 30, 70) == 1.0)
    check("lin ascending midpoint", abs(lin(50, 30, 70) - 0.5) < 1e-9)
    check("lin descending low is best", lin(0, 15, 0) == 1.0)
    check("lin descending high clamp", lin(20, 15, 0) == 0.0)
    check("lin descending midpoint", abs(lin(7.5, 15, 0) - 0.5) < 1e-9)

    check("perfect account scores 100", compute(PERFECT)["score"] == 100)
    check("perfect account is fully covered", compute(PERFECT)["coverage_pct"] == 100)
    check("broken account scores 0", compute(BROKEN)["score"] == 0)

    # Missing data is excluded, never guessed.
    partial = compute({"tracking": PERFECT["tracking"]})
    check("partial score renormalises to 100", partial["score"] == 100)
    check("partial coverage reports 20%", partial["coverage_pct"] == 20)
    check("unscored dimensions are flagged",
          sum(1 for d in partial["dimensions"] if d["fraction"] is None) == 8)

    # Empty input refuses to invent a score.
    check("empty input has no score", compute({})["score"] is None)
    check("empty input renders DATA NOT AVAILABLE",
          "DATA NOT AVAILABLE" in render(compute({})))

    # A single missing sub-input renormalises within its dimension.
    no_crm = dict(PERFECT["tracking"])
    del no_crm["crm_variance_pct"]
    check("dimension renormalises over present sub-inputs",
          compute({"tracking": no_crm})["score"] == 100)

    # An explicit null is treated as unknown, not as zero.
    null_crm = dict(PERFECT["tracking"])
    null_crm["crm_variance_pct"] = None
    check("explicit null is unknown, not zero",
          compute({"tracking": null_crm})["score"] == 100)

    # Tracking failure alone must be able to sink the score materially.
    tracking_broken = dict(PERFECT)
    tracking_broken["tracking"] = BROKEN["tracking"]
    check("tracking failure costs the full 20 points",
          compute(tracking_broken)["score"] == 80)

    # Out-of-range inputs clamp rather than escaping [0,100].
    silly = {"traffic": {"search_impression_share_pct": 999, "lost_is_budget_pct": -50,
                         "lost_is_rank_pct": -50, "clicks_trend_pct": 500}}
    check("out-of-range inputs clamp high", compute(silly)["score"] == 100)

    check("weights sum to 100", sum(w for _k, _n, w in DIMENSIONS) == 100)
    for key, _name, _weight in DIMENSIONS:
        check(f"rules exist for {key}", key in RULES and len(RULES[key]) > 0)
        check(f"sub-weights sum to 1.0 for {key}",
              abs(sum(w for _k, w, _s in RULES[key]) - 1.0) < 1e-9)

    example_result = compute(EXAMPLE)
    check("example scores in range", 0 <= example_result["score"] <= 100)
    check("example is fully covered", example_result["coverage_pct"] == 100)
    check("example renders a band", band(example_result["score"]) in
          {"HEALTHY", "STABLE - fixable gaps", "AT RISK", "POOR", "CRITICAL"})

    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    if argv[1] == "--self-test":
        return self_test()
    if argv[1] == "--example":
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    try:
        with open(argv[1]) as handle:
            metrics = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {argv[1]}: {exc}", file=sys.stderr)
        return 1
    print(render(compute(metrics)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
