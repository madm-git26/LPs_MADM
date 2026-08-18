#!/usr/bin/env python3
"""Export a routine's proposed changes as CSVs instead of applying them.

For accounts where the API is not connected yet, or where the practice wants to
review everything in Google Ads Editor first:

    python scripts/export_editor_csv.py --routine weekly --account 123-456-7890 --out out/

Writes up to three files:

    negatives.csv      import into Google Ads Editor (Keywords -> Negative keywords)
    keywords.csv       import into Google Ads Editor (Keywords -> Keywords)
    other-changes.csv  everything Editor cannot import - budgets, targets, bid
                       modifiers, schedules - as a checklist with before/after

Editor imports by campaign and ad group NAME, so the names in these files must
match the account exactly - they are taken from the account, so they do.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gads import optimize, reports  # noqa: E402
from gads.accounts import account_config  # noqa: E402
from gads.client import GadsClient  # noqa: E402
from gads.errors import GadsError  # noqa: E402

EDITOR_MATCH = {"EXACT": "Exact", "PHRASE": "Phrase", "BROAD": "Broad"}


def _campaign_names(client: GadsClient, customer_id: str) -> dict[int, str]:
    rows = client.search(customer_id,
                         "SELECT campaign.id, campaign.name FROM campaign "
                         "WHERE campaign.status != 'REMOVED'")
    return {r["campaign.id"]: r["campaign.name"] for r in rows}


def _ad_group_names(client: GadsClient, customer_id: str) -> dict[int, tuple[str, str]]:
    rows = client.search(customer_id,
                         "SELECT ad_group.id, ad_group.name, campaign.name FROM ad_group "
                         "WHERE ad_group.status != 'REMOVED'")
    return {r["ad_group.id"]: (r["campaign.name"], r["ad_group.name"]) for r in rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--routine", default="weekly", choices=sorted(optimize.ROUTINES))
    parser.add_argument("--account")
    parser.add_argument("--out", default="out")
    args = parser.parse_args()

    try:
        client = GadsClient.from_env()
    except GadsError as exc:
        print(f"Cannot start: {exc}")
        return 1

    customer_id = client.customer_id(args.account)
    account = account_config(customer_id)
    result = optimize.run_routine(client, args.routine, customer_id, account)
    campaigns = _campaign_names(client, customer_id)
    ad_groups = _ad_group_names(client, customer_id)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    negatives: list[dict[str, str]] = []
    keywords: list[dict[str, str]] = []
    others: list[dict[str, str]] = []

    for proposal in result.proposals:
        change = proposal.change
        pairs = (change.evidence or {}).get("keywords") or []
        if change.action in {"add_negative_keywords", "create_shared_negative_list"}:
            for text, match in pairs:
                negatives.append({
                    "Campaign": campaigns.get(change.campaign_id, ""),
                    "Ad Group": "",
                    "Keyword": text,
                    "Criterion Type": "Campaign Negative "
                                      + EDITOR_MATCH.get(str(match).upper(), "Phrase"),
                    "Status": "Enabled",
                })
        elif change.action == "add_keywords":
            ad_group_id = (change.evidence or {}).get("ad_group_id")
            campaign_name, ad_group_name = ad_groups.get(ad_group_id, ("", ""))
            for text, match in pairs:
                keywords.append({
                    "Campaign": campaign_name, "Ad Group": ad_group_name,
                    "Keyword": text,
                    "Criterion Type": EDITOR_MATCH.get(str(match).upper(), "Phrase"),
                    "Status": "Enabled",
                })
        elif change.action == "pause_keywords":
            others.append({"action": "pause keywords", "entity": change.entity,
                           "before": "Enabled", "after": "Paused",
                           "reason": change.reason})
        else:
            others.append({"action": change.action, "entity": change.entity,
                           "before": str(change.before), "after": str(change.after),
                           "reason": change.reason})

    written = []
    for name, rows, columns in [
        ("negatives.csv", negatives, ["Campaign", "Ad Group", "Keyword",
                                      "Criterion Type", "Status"]),
        ("keywords.csv", keywords, ["Campaign", "Ad Group", "Keyword",
                                    "Criterion Type", "Status"]),
        ("other-changes.csv", others, ["action", "entity", "before", "after", "reason"]),
    ]:
        if not rows:
            continue
        path = out / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        written.append(f"{path} ({len(rows)} rows)")

    report_path = out / f"{args.routine}-findings.md"
    report_path.write_text(result.markdown(), encoding="utf-8")
    written.append(str(report_path))

    print("Wrote:")
    for line in written:
        print(f"  {line}")
    if not negatives and not keywords:
        print("\nNothing for Editor this time - the findings file has the reasoning.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
