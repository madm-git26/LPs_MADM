#!/usr/bin/env python3
"""MCP server: the Google Ads account, exposed to Claude as tools.

Reads are free.  Writes go through the guardrails in ``config/guardrails.yaml``:
routine optimisation applies itself, structural changes come back as proposals
for a human.  Every write is validated against Google first and written to the
audit log with an undo plan.

Run it directly for a smoke test:

    GADS_MOCK=1 python mcp_server/server.py --list-tools
    GADS_MOCK=1 python mcp_server/server.py --call run_routine '{"routine":"weekly"}'
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gads import mutations, offline, optimize, reports, zips  # noqa: E402
from gads.accounts import account_config, describe, load_accounts  # noqa: E402
from gads.audit import AuditLog  # noqa: E402
from gads.client import GadsClient  # noqa: E402
from gads.errors import GadsError  # noqa: E402
from gads.guardrails import GuardrailPolicy  # noqa: E402

_CLIENT: GadsClient | None = None


def client() -> GadsClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = GadsClient.from_env()
    return _CLIENT


def _cid(args: dict[str, Any]) -> str:
    return client().customer_id(args.get("customer_id"))


def _account(args: dict[str, Any]) -> dict[str, Any]:
    return account_config(_cid(args))


def _execute(proposals: list[Any], customer_id: str, apply: bool, label: str) -> str:
    proposals = [p for p in proposals if p is not None]
    if not proposals:
        return "_No changes proposed._"
    policy = GuardrailPolicy.load(account=customer_id, read_only=client().read_only)
    executor = mutations.Executor(client(), policy, AuditLog(client().settings.audit_dir))
    return executor.submit(proposals, apply=apply, label=label).markdown()


# ---------------------------------------------------------------------------
# handlers
# ---------------------------------------------------------------------------


def tool_list_accounts(args: dict[str, Any]) -> str:
    gads = client()
    configured = load_accounts()
    try:
        children = gads.child_accounts(args.get("manager_id"))
    except GadsError as exc:
        return f"Could not list accounts: {exc}"
    lines = ["| customer id | name | currency | timezone | configured |", "|---|---|---|---|---|"]
    for row in children:
        cid = str(row.get("customer_client.id"))
        lines.append(
            f"| {cid} | {row.get('customer_client.descriptive_name')} | "
            f"{row.get('customer_client.currency_code')} | "
            f"{row.get('customer_client.time_zone')} | "
            f"{'yes' if cid in configured else 'no'} |")
    return "\n".join(lines) if children else "_No client accounts under this manager._"


def tool_account_overview(args: dict[str, Any]) -> str:
    cid = _cid(args)
    date_range = args.get("date_range", "LAST_30_DAYS")
    parts = [describe(_account(args)), ""]
    parts.append(reports.account_summary(client(), cid, date_range=date_range).markdown())
    parts.append(reports.budget_pacing(client(), cid).markdown())
    parts.append(optimize.conversion_health(client(), cid, _account(args))
                 .markdown(include_tables=False))
    return "\n\n".join(parts)


def tool_run_report(args: dict[str, Any]) -> str:
    name = args["report"]
    kwargs = {k: v for k, v in args.items()
              if k in {"date_range", "campaign_ids", "min_clicks", "min_impressions",
                       "only_unmapped", "dimension", "days", "limit",
                       "min_duration_seconds"} and v is not None}
    report = reports.run_report(client(), name, customer_id=_cid(args), **kwargs)
    return report.markdown(limit=int(args.get("rows", 40)))


def tool_list_reports(args: dict[str, Any]) -> str:
    def summary(fn: Callable[..., Any]) -> str:
        lines = (fn.__doc__ or "").strip().splitlines()
        return lines[0] if lines else "(no description)"

    return "\n".join(f"- `{name}`: {summary(fn)}"
                     for name, fn in sorted(reports.REPORTS.items()))


def tool_run_gaql(args: dict[str, Any]) -> str:
    rows = client().search(_cid(args), args["query"])
    if not rows:
        return "_No rows._"
    limit = int(args.get("rows", 50))
    columns = list(rows[0].keys())
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(str(row.get(c, "")).replace("|", "\\|")
                                       for c in columns) + " |")
    if len(rows) > limit:
        lines.append(f"\n_{len(rows) - limit} more rows._")
    return "\n".join(lines)


def tool_run_routine(args: dict[str, Any]) -> str:
    cid = _cid(args)
    routine = args.get("routine", "daily")
    account = _account(args)
    result = optimize.run_routine(
        client(), routine, cid, account,
        **({"shared_set_id": args["shared_set_id"]} if args.get("shared_set_id")
           and routine in {"daily", "weekly"} else {}))
    out = [result.markdown(include_tables=bool(args.get("include_tables", False)))]
    if result.proposals:
        out.append(_execute(result.proposals, cid, bool(args.get("apply", True)),
                            f"{routine}-routine"))
    return "\n\n".join(out)


def tool_add_negative_keywords(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.add_negative_keywords(
        client(), cid, args["keywords"],
        campaign_id=args.get("campaign_id"), ad_group_id=args.get("ad_group_id"),
        shared_set_id=args.get("shared_set_id"),
        default_match=args.get("match_type", "PHRASE"), reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "add-negatives")


def tool_add_keywords(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.add_keywords(
        client(), cid, args["ad_group_id"], args["keywords"],
        default_match=args.get("match_type", "PHRASE"), cpc_bid=args.get("cpc_bid"),
        final_url=args.get("final_url"), reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "add-keywords")


def tool_pause_keywords(args: dict[str, Any]) -> str:
    cid = _cid(args)
    targets = [tuple(t) for t in args["targets"]]
    proposal = mutations.pause_keywords(client(), cid, targets,
                                        labels=args.get("labels", []),
                                        reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "pause-keywords")


def tool_pause_ads(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.pause_ads(client(), cid, [tuple(t) for t in args["targets"]],
                                   reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "pause-ads")


def tool_set_target_cpa(args: dict[str, Any]) -> str:
    cid = _cid(args)
    settings = optimize.campaign_settings(client(), cid)
    meta = settings.get(args["campaign_id"], {})
    proposal = mutations.set_target_cpa(
        client(), cid, args["campaign_id"], float(args["target_cpa"]),
        args.get("current_target_cpa", meta.get("target_cpa")),
        strategy_type=str(meta.get("strategy") or "MAXIMIZE_CONVERSIONS"),
        campaign_age_days=meta.get("age_days"), reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "set-target-cpa")


def tool_update_budget(args: dict[str, Any]) -> str:
    cid = _cid(args)
    settings = optimize.campaign_settings(client(), cid)
    meta = next((m for m in settings.values()
                 if m.get("budget_id") == args.get("budget_id")
                 or m.get("id") == args.get("campaign_id")), {})
    proposal = mutations.update_budget(
        client(), cid, args.get("budget_id") or meta.get("budget_id"),
        float(args["daily_budget"]),
        args.get("current_daily_budget", meta.get("daily_budget")),
        campaign_id=meta.get("id"), campaign_age_days=meta.get("age_days"),
        reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "update-budget")


def tool_set_bid_modifier(args: dict[str, Any]) -> str:
    cid = _cid(args)
    kind = args.get("kind", "location")
    campaign_id = args["campaign_id"]
    modifier = float(args["modifier"])
    current = args.get("current_modifier")
    if kind == "location":
        proposal = mutations.set_location_bid_modifier(
            client(), cid, campaign_id, args["criterion_id"], modifier, current,
            label=args.get("label", ""), reason=args.get("reason", ""))
    elif kind == "device":
        proposal = mutations.set_device_bid_modifier(
            client(), cid, campaign_id, args["device"], modifier, current,
            reason=args.get("reason", ""))
    elif kind == "income":
        proposal = mutations.set_income_bid_modifier(
            client(), cid, campaign_id, args["income_bucket"], modifier,
            exclude=bool(args.get("exclude", False)), current_modifier=current,
            create=bool(args.get("create", False)), reason=args.get("reason", ""))
    else:
        return f"Unknown bid modifier kind {kind!r} - use location, device or income."
    return _execute([proposal], cid, bool(args.get("apply", True)), f"bid-modifier-{kind}")


def tool_set_ad_schedule(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.set_ad_schedule(
        client(), cid, args["campaign_id"], args["schedule"],
        replace_criterion_ids=args.get("replace_criterion_ids", []),
        reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "set-ad-schedule")


def tool_add_location_targets(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.add_location_targets(
        client(), cid, args["campaign_id"], args["geo_target_ids"],
        bid_modifier=args.get("bid_modifier"), negative=bool(args.get("negative", False)),
        reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", True)), "location-targets")


def tool_create_search_campaign(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.create_search_campaign(client(), cid, args["spec"])
    return _execute([proposal], cid, bool(args.get("apply", False)), "create-campaign")


def tool_create_ad_group(args: dict[str, Any]) -> str:
    cid = _cid(args)
    proposal = mutations.create_ad_group(
        client(), cid, args["campaign_id"], args["name"],
        cpc_bid=args.get("cpc_bid"), keywords=args.get("keywords", []),
        default_match=args.get("match_type", "PHRASE"), reason=args.get("reason", ""))
    return _execute([proposal], cid, bool(args.get("apply", False)), "create-ad-group")


def tool_create_rsa(args: dict[str, Any]) -> str:
    cid = _cid(args)
    try:
        proposal = mutations.create_rsa(
            client(), cid, args["ad_group_id"], args["headlines"], args["descriptions"],
            args["final_url"], path1=args.get("path1", ""), path2=args.get("path2", ""),
            reason=args.get("reason", ""))
    except ValueError as exc:
        return f"That ad would be rejected before it left the machine: {exc}"
    return _execute([proposal], cid, bool(args.get("apply", False)), "create-rsa")


def tool_zip_targeting_plan(args: dict[str, Any]) -> str:
    account = _account(args)
    geo = account.get("geo") or {}
    latitude = float(args.get("latitude") or account.get("latitude") or 0)
    longitude = float(args.get("longitude") or account.get("longitude") or 0)
    if not latitude or not longitude:
        return ("Need the practice's latitude and longitude - either pass them or put "
                "them in config/accounts.yaml.")
    plan = zips.build_targeting_plan(
        latitude, longitude,
        float(args.get("radius_miles") or geo.get("radius_miles") or 10),
        service_line=args.get("service_line", "general"),
        min_income=args.get("min_income") or geo.get("high_ticket_min_median_income")
        if args.get("service_line") in {"implants", "cosmetic"} else args.get("min_income"),
        always_include=args.get("always_include") or geo.get("always_include_zips") or [],
        exclude=args.get("exclude") or geo.get("exclude_zips") or [],
        local_path=args.get("local_path"))
    out = [plan.markdown(limit=int(args.get("rows", 40)))]
    if args.get("campaign_id"):
        proposals = zips.plan_to_proposals(client(), _cid(args), args["campaign_id"], plan)
        out.append(_execute(proposals, _cid(args), bool(args.get("apply", False)), "zip-plan"))
    return "\n\n".join(out)


def tool_find_geo_target_ids(args: dict[str, Any]) -> str:
    found = zips.find_geo_target_ids(client(), args["zips"],
                                     country_code=args.get("country_code", "US"))
    if not found:
        return "_No postal-code geo targets matched._"
    return "\n".join(f"- {zip_code}: geoTargetConstants/{gid}"
                     for zip_code, gid in sorted(found.items()))


def tool_upload_offline_conversions(args: dict[str, Any]) -> str:
    cid = _cid(args)
    account = _account(args)
    offset = args.get("utc_offset", "-05:00")
    kind = args.get("kind", "booked")
    if kind == "call":
        rows = offline.from_call_records(
            args["rows"], qualified_seconds=int(
                args.get("qualified_seconds", account.get("qualified_call_seconds", 60))),
            utc_offset=offset)
    else:
        rows = offline.from_appointments(args["rows"], utc_offset=offset,
                                         value_field=args.get("value_field", ""))
    try:
        proposal, summary = offline.upload_conversions(
            client(), cid, args["conversion_action_id"], rows,
            validate_only=not bool(args.get("apply", False)))
    except GadsError as exc:
        return f"Upload refused: {exc}"
    lines = [f"- rows in: {len(args['rows'])}, uploadable: {len(rows)}",
             f"- {'validated only' if summary['validate_only'] else 'uploaded'}: "
             f"{summary['uploaded']}"]
    if summary["errors"]:
        lines.append(f"- errors: {'; '.join(summary['errors'][:5])}")
    if len(rows) < len(args["rows"]):
        lines.append("- rows without a click id or under the qualified threshold were "
                     "skipped; they cannot be attributed.")
    return "\n".join(lines)


def tool_adjust_conversions(args: dict[str, Any]) -> str:
    cid = _cid(args)
    kind = args.get("adjustment", "retract")
    validate_only = not bool(args.get("apply", False))
    if kind == "retract":
        summary = offline.retract_no_shows(
            client(), cid, args["conversion_action_id"], args["appointment_ids"],
            args["adjustment_date_time"], validate_only=validate_only)
    else:
        summary = offline.restate_treatment_value(
            client(), cid, args["conversion_action_id"],
            [(row["appointment_id"], float(row["value"])) for row in args["values"]],
            args["adjustment_date_time"], validate_only=validate_only)
    return (f"- {'validated' if validate_only else 'applied'}: {summary['adjusted']} "
            f"{kind} adjustments"
            + (f"\n- errors: {'; '.join(summary['errors'][:5])}" if summary["errors"] else ""))


def tool_list_change_runs(args: dict[str, Any]) -> str:
    runs = AuditLog(client().settings.audit_dir).list_runs(int(args.get("limit", 20)))
    if not runs:
        return "_No change runs recorded yet._"
    lines = ["| run id | when | applied | total |", "|---|---|---|---|"]
    lines += [f"| `{r['run_id']}` | {r['created']} | {r['applied']} | {r['total']} |"
              for r in runs]
    return "\n".join(lines)


def tool_rollback_run(args: dict[str, Any]) -> str:
    result = mutations.rollback_run(client(), args["run_id"],
                                    apply=bool(args.get("apply", True)))
    return result.markdown()


def tool_guardrail_status(args: dict[str, Any]) -> str:
    cid = _cid(args)
    policy = GuardrailPolicy.load(account=cid, read_only=client().read_only)
    frozen, why = policy.frozen()
    ops = AuditLog(client().settings.audit_dir).ops_today(cid)
    lines = [f"**Guardrails for {cid}**", "",
             f"- state: {'FROZEN - ' + why if frozen else 'active'}",
             f"- read-only mode: {client().read_only}",
             f"- operations applied today: {ops} of {policy.limits['max_ops_per_day']}",
             "", "| action | mode |", "|---|---|"]
    lines += [f"| {name} | {mode} |" for name, mode in sorted(policy.config["actions"].items())]
    lines += ["", "**Limits**"]
    lines += [f"- {k}: {v}" for k, v in policy.limits.items()]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# tool definitions
# ---------------------------------------------------------------------------

_CUSTOMER = {"customer_id": {"type": "string",
                             "description": "10-digit account id; defaults to "
                                            "GOOGLE_ADS_DEFAULT_CUSTOMER_ID."}}
_APPLY = {"apply": {"type": "boolean", "default": True,
                    "description": "Apply what the guardrails allow. Anything "
                                   "structural still comes back as a proposal."}}
_REASON = {"reason": {"type": "string", "description": "Why - goes into the audit log."}}
_DATE_RANGE = {"date_range": {"type": "string", "default": "LAST_30_DAYS",
                              "description": "LAST_7_DAYS, LAST_30_DAYS, THIS_MONTH, "
                                             "LAST_MONTH, or 'YYYY-MM-DD,YYYY-MM-DD'."}}


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required or []}


TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_accounts",
        "description": "List the client accounts under the manager account, and whether "
                       "each one has a practice config.",
        "schema": _schema({"manager_id": {"type": "string"}}),
        "handler": tool_list_accounts,
    },
    {
        "name": "account_overview",
        "description": "Start here. Practice config, campaign performance, budget pacing "
                       "and whether conversion tracking is measuring real patients.",
        "schema": _schema({**_CUSTOMER, **_DATE_RANGE}),
        "handler": tool_account_overview,
    },
    {
        "name": "list_reports",
        "description": "Names and one-line descriptions of every available report.",
        "schema": _schema({}),
        "handler": tool_list_reports,
    },
    {
        "name": "run_report",
        "description": "Run one of the canonical reports (search_terms, keyword_performance, "
                       "zip_performance, auction_insights, rsa_asset_performance, calls, "
                       "change_history, ...). Use list_reports to see them all.",
        "schema": _schema({
            "report": {"type": "string"},
            **_CUSTOMER, **_DATE_RANGE,
            "campaign_ids": {"type": "array", "items": {"type": "integer"}},
            "min_clicks": {"type": "integer"},
            "min_impressions": {"type": "integer"},
            "only_unmapped": {"type": "boolean",
                              "description": "search_terms only: terms not yet added as a "
                                             "keyword or negative."},
            "dimension": {"type": "string", "enum": ["age", "gender", "parental"]},
            "days": {"type": "integer", "description": "change_history only (max 29)."},
            "rows": {"type": "integer", "default": 40},
        }, ["report"]),
        "handler": tool_run_report,
    },
    {
        "name": "run_gaql",
        "description": "Run a raw GAQL query when no canonical report fits.",
        "schema": _schema({**_CUSTOMER,
                           "query": {"type": "string"},
                           "rows": {"type": "integer", "default": 50}}, ["query"]),
        "handler": tool_run_gaql,
    },
    {
        "name": "run_routine",
        "description": "The day-to-day work: 'daily' (spend anomalies, disapprovals, new "
                       "search terms, call quality - proposes negatives only), 'weekly' "
                       "(the full optimisation pass), 'monthly' (structure, competition, "
                       "measurement - proposes nothing). Applies what the guardrails allow.",
        "schema": _schema({
            "routine": {"type": "string", "enum": ["daily", "weekly", "monthly"],
                        "default": "daily"},
            **_CUSTOMER, **_APPLY,
            "shared_set_id": {"type": "integer",
                              "description": "Shared negative list to add master-list "
                                             "negatives to."},
            "include_tables": {"type": "boolean", "default": False},
        }),
        "handler": tool_run_routine,
    },
    {
        "name": "add_negative_keywords",
        "description": "Block search terms at campaign, ad group or shared-list level.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "keywords": {"type": "array", "items": {"type": "string"}},
            "campaign_id": {"type": "integer"},
            "ad_group_id": {"type": "integer"},
            "shared_set_id": {"type": "integer"},
            "match_type": {"type": "string", "enum": ["EXACT", "PHRASE", "BROAD"],
                           "default": "PHRASE"},
        }, ["keywords"]),
        "handler": tool_add_negative_keywords,
    },
    {
        "name": "add_keywords",
        "description": "Add keywords to an ad group - usually promoting a search term "
                       "that is already converting.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "ad_group_id": {"type": "integer"},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "match_type": {"type": "string", "enum": ["EXACT", "PHRASE", "BROAD"],
                           "default": "PHRASE"},
            "cpc_bid": {"type": "number"},
            "final_url": {"type": "string"},
        }, ["ad_group_id", "keywords"]),
        "handler": tool_add_keywords,
    },
    {
        "name": "pause_keywords",
        "description": "Pause keywords by (ad_group_id, criterion_id) - the ids come from "
                       "the keyword_performance report.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "targets": {"type": "array",
                        "items": {"type": "array", "items": {"type": "integer"}}},
            "labels": {"type": "array", "items": {"type": "string"}},
        }, ["targets"]),
        "handler": tool_pause_keywords,
    },
    {
        "name": "pause_ads",
        "description": "Pause ads by (ad_group_id, ad_id).",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "targets": {"type": "array",
                        "items": {"type": "array", "items": {"type": "integer"}}},
        }, ["targets"]),
        "handler": tool_pause_ads,
    },
    {
        "name": "set_target_cpa",
        "description": "Move a campaign's target CPA. The guardrails cap the step size.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "campaign_id": {"type": "integer"},
            "target_cpa": {"type": "number"},
            "current_target_cpa": {"type": "number"},
        }, ["campaign_id", "target_cpa"]),
        "handler": tool_set_target_cpa,
    },
    {
        "name": "update_budget",
        "description": "Change a campaign's daily budget.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "campaign_id": {"type": "integer"},
            "budget_id": {"type": "integer"},
            "daily_budget": {"type": "number"},
            "current_daily_budget": {"type": "number"},
        }, ["daily_budget"]),
        "handler": tool_update_budget,
    },
    {
        "name": "set_bid_modifier",
        "description": "Bid up or down by location, device or household income decile.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "kind": {"type": "string", "enum": ["location", "device", "income"],
                     "default": "location"},
            "campaign_id": {"type": "integer"},
            "modifier": {"type": "number", "description": "1.2 = +20%, 0.8 = -20%."},
            "current_modifier": {"type": "number"},
            "criterion_id": {"type": "integer", "description": "location only"},
            "label": {"type": "string"},
            "device": {"type": "string", "enum": ["MOBILE", "DESKTOP", "TABLET"]},
            "income_bucket": {"type": "string",
                              "description": "INCOME_RANGE_0_50 ... INCOME_RANGE_90_UP"},
            "exclude": {"type": "boolean", "description": "income only: exclude the decile"},
            "create": {"type": "boolean"},
        }, ["campaign_id", "modifier"]),
        "handler": tool_set_bid_modifier,
    },
    {
        "name": "set_ad_schedule",
        "description": "Set the hours a campaign runs, with optional per-slot bid modifiers.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "campaign_id": {"type": "integer"},
            "schedule": {"type": "array", "items": {
                "type": "object",
                "properties": {"day": {"type": "string"}, "start_hour": {"type": "integer"},
                               "end_hour": {"type": "integer"},
                               "bid_modifier": {"type": "number"}},
                "required": ["day"]}},
            "replace_criterion_ids": {"type": "array", "items": {"type": "integer"}},
        }, ["campaign_id", "schedule"]),
        "handler": tool_set_ad_schedule,
    },
    {
        "name": "add_location_targets",
        "description": "Target or exclude locations by geo target constant id.",
        "schema": _schema({
            **_CUSTOMER, **_APPLY, **_REASON,
            "campaign_id": {"type": "integer"},
            "geo_target_ids": {"type": "array", "items": {"type": "string"}},
            "bid_modifier": {"type": "number"},
            "negative": {"type": "boolean", "default": False},
        }, ["campaign_id", "geo_target_ids"]),
        "handler": tool_add_location_targets,
    },
    {
        "name": "create_search_campaign",
        "description": "Build a Search campaign (budget, settings, geo, schedule) in one "
                       "atomic request. Created paused; needs approval by default.",
        "schema": _schema({
            **_CUSTOMER, "apply": {"type": "boolean", "default": False},
            "spec": {"type": "object", "description":
                     "name, daily_budget, target_cpa, status, geo_target_ids, "
                     "proximity {latitude, longitude, radius_miles}, languages, "
                     "ad_schedule, search_partners, display_expansion, presence_only"},
        }, ["spec"]),
        "handler": tool_create_search_campaign,
    },
    {
        "name": "create_ad_group",
        "description": "Create an ad group, optionally with its keywords, in one request.",
        "schema": _schema({
            **_CUSTOMER, "apply": {"type": "boolean", "default": False}, **_REASON,
            "campaign_id": {"type": "integer"},
            "name": {"type": "string"},
            "cpc_bid": {"type": "number"},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "match_type": {"type": "string", "default": "PHRASE"},
        }, ["campaign_id", "name"]),
        "handler": tool_create_ad_group,
    },
    {
        "name": "create_rsa",
        "description": "Create a responsive search ad. Headline and description limits are "
                       "checked locally before anything is sent. Created paused.",
        "schema": _schema({
            **_CUSTOMER, "apply": {"type": "boolean", "default": False}, **_REASON,
            "ad_group_id": {"type": "integer"},
            "headlines": {"type": "array", "items": {"type": "string"},
                          "description": "3-15, each 30 characters or fewer."},
            "descriptions": {"type": "array", "items": {"type": "string"},
                             "description": "2-4, each 90 characters or fewer."},
            "final_url": {"type": "string"},
            "path1": {"type": "string"}, "path2": {"type": "string"},
        }, ["ad_group_id", "headlines", "descriptions", "final_url"]),
        "handler": tool_create_rsa,
    },
    {
        "name": "zip_targeting_plan",
        "description": "Rank the postal codes around the practice for one service line "
                       "using income, age, tenure, household and language data, and say "
                       "which to target, bid up, bid down or exclude.",
        "schema": _schema({
            **_CUSTOMER, "apply": {"type": "boolean", "default": False},
            "latitude": {"type": "number"}, "longitude": {"type": "number"},
            "radius_miles": {"type": "number", "default": 10},
            "service_line": {"type": "string",
                             "enum": ["emergency", "general", "implants", "cosmetic",
                                      "ortho", "spanish"], "default": "general"},
            "min_income": {"type": "number"},
            "always_include": {"type": "array", "items": {"type": "string"}},
            "exclude": {"type": "array", "items": {"type": "string"}},
            "campaign_id": {"type": "integer",
                            "description": "If given, turn the plan into proposals."},
            "local_path": {"type": "string",
                           "description": "CSV of ZIP demographics instead of the Census API."},
            "rows": {"type": "integer", "default": 40},
        }),
        "handler": tool_zip_targeting_plan,
    },
    {
        "name": "find_geo_target_ids",
        "description": "Resolve postal codes to Google geo target constant ids.",
        "schema": _schema({"zips": {"type": "array", "items": {"type": "string"}},
                           "country_code": {"type": "string", "default": "US"}}, ["zips"]),
        "handler": tool_find_geo_target_ids,
    },
    {
        "name": "upload_offline_conversions",
        "description": "Send booked appointments or qualified calls back to Google by "
                       "click id. Patient data is stripped and refused, not uploaded.",
        "schema": _schema({
            **_CUSTOMER, "apply": {"type": "boolean", "default": False},
            "conversion_action_id": {"type": "integer"},
            "kind": {"type": "string", "enum": ["booked", "call"], "default": "booked"},
            "rows": {"type": "array", "items": {"type": "object"},
                     "description": "booked: gclid, booked_at, appointment_id[, value]. "
                                    "call: gclid, start_time, duration, status, call_id."},
            "value_field": {"type": "string"},
            "qualified_seconds": {"type": "integer"},
            "utc_offset": {"type": "string", "default": "-05:00"},
        }, ["conversion_action_id", "rows"]),
        "handler": tool_upload_offline_conversions,
    },
    {
        "name": "adjust_conversions",
        "description": "Retract no-shows, or restate a booking's value once treatment is "
                       "known, using the practice's own appointment reference.",
        "schema": _schema({
            **_CUSTOMER, "apply": {"type": "boolean", "default": False},
            "conversion_action_id": {"type": "integer"},
            "adjustment": {"type": "string", "enum": ["retract", "restate"],
                           "default": "retract"},
            "appointment_ids": {"type": "array", "items": {"type": "string"}},
            "values": {"type": "array", "items": {"type": "object"},
                       "description": "restate: [{appointment_id, value}]"},
            "adjustment_date_time": {"type": "string",
                                     "description": "'YYYY-MM-DD HH:MM:SS+HH:MM'"},
        }, ["conversion_action_id", "adjustment_date_time"]),
        "handler": tool_adjust_conversions,
    },
    {
        "name": "list_change_runs",
        "description": "Recent change runs, with their run ids for rollback.",
        "schema": _schema({"limit": {"type": "integer", "default": 20}}),
        "handler": tool_list_change_runs,
    },
    {
        "name": "rollback_run",
        "description": "Undo everything a change run applied.",
        "schema": _schema({"run_id": {"type": "string"}, **_APPLY}, ["run_id"]),
        "handler": tool_rollback_run,
    },
    {
        "name": "guardrail_status",
        "description": "What the agent may do on its own for this account right now, and "
                       "how much of today's operation budget is left.",
        "schema": _schema({**_CUSTOMER}),
        "handler": tool_guardrail_status,
    },
]

HANDLERS: dict[str, Callable[[dict[str, Any]], str]] = {t["name"]: t["handler"] for t in TOOLS}


def call_tool(name: str, arguments: dict[str, Any] | None) -> str:
    handler = HANDLERS.get(name)
    if handler is None:
        return f"Unknown tool {name!r}."
    try:
        return handler(arguments or {})
    except GadsError as exc:
        return f"**{type(exc).__name__}**: {exc}"
    except (KeyError, ValueError, TypeError) as exc:
        return f"**Bad request**: {exc}"


# ---------------------------------------------------------------------------
# MCP wiring
# ---------------------------------------------------------------------------


async def serve() -> None:
    from mcp import types
    from mcp.server.lowlevel import Server
    from mcp.server.stdio import stdio_server

    async def on_list_tools(ctx, params) -> "types.ListToolsResult":
        return types.ListToolsResult(tools=[
            types.Tool(name=t["name"], description=t["description"], inputSchema=t["schema"])
            for t in TOOLS
        ])

    async def on_call_tool(ctx, params) -> "types.CallToolResult":
        text = call_tool(params.name, params.arguments)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])

    server = Server(
        "google-ads-dental",
        version="1.0.0",
        instructions=(
            "Google Ads for local dental practices. Read before you write: "
            "account_overview, then run_routine. Writes are gated by "
            "config/guardrails.yaml - routine optimisation applies itself, structural "
            "changes come back for approval. Every change is logged and reversible with "
            "rollback_run."
        ),
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] == "--list-tools":
        for tool in TOOLS:
            print(f"{tool['name']}\n    {tool['description']}")
        return 0
    if argv and argv[0] == "--call":
        name = argv[1]
        arguments = json.loads(argv[2]) if len(argv) > 2 else {}
        print(call_tool(name, arguments))
        return 0
    asyncio.run(serve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
