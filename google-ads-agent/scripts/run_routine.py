#!/usr/bin/env python3
"""Run a routine headlessly - cron, a scheduled task, or by hand.

    python scripts/run_routine.py --routine daily  --account 123-456-7890
    python scripts/run_routine.py --routine weekly --account 123-456-7890 --dry-run
    python scripts/run_routine.py --routine monthly --all-accounts --out reports/

Dry runs still validate every change against Google and write the audit log;
they simply never apply.  That is the safest way to watch the agent think for
a week before letting it act.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gads import mutations, optimize  # noqa: E402
from gads.accounts import account_config, load_accounts  # noqa: E402
from gads.audit import AuditLog  # noqa: E402
from gads.client import GadsClient  # noqa: E402
from gads.errors import GadsError  # noqa: E402
from gads.guardrails import GuardrailPolicy  # noqa: E402


def run_for_account(client: GadsClient, customer_id: str, routine: str,
                    apply: bool, include_tables: bool) -> str:
    account = account_config(customer_id)
    kwargs = {}
    if routine in {"daily", "weekly"} and account.get("shared_negative_list_id"):
        kwargs["shared_set_id"] = account["shared_negative_list_id"]
    result = optimize.run_routine(client, routine, customer_id, account, **kwargs)

    header = (f"# {account.get('name', customer_id)} - {routine} run\n"
              f"_{dt.datetime.now():%Y-%m-%d %H:%M}, account {customer_id}, "
              f"{'applying within guardrails' if apply else 'dry run'}_\n")
    parts = [header, result.markdown(include_tables=include_tables)]

    if result.proposals:
        policy = GuardrailPolicy.load(account=customer_id, read_only=client.read_only)
        executor = mutations.Executor(client, policy, AuditLog(client.settings.audit_dir))
        parts.append(executor.submit(result.proposals, apply=apply,
                                     label=f"{routine}-{customer_id}").markdown())
    return "\n\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--routine", default="daily", choices=sorted(optimize.ROUTINES))
    parser.add_argument("--account", help="Customer id. Defaults to the one in .env.")
    parser.add_argument("--all-accounts", action="store_true",
                        help="Every account in config/accounts.yaml.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and log, change nothing.")
    parser.add_argument("--tables", action="store_true", help="Include the data tables.")
    parser.add_argument("--out", help="Directory to write markdown reports into.")
    args = parser.parse_args()

    try:
        client = GadsClient.from_env()
    except GadsError as exc:
        print(f"Cannot start: {exc}")
        return 1

    if args.all_accounts:
        customer_ids = sorted(load_accounts())
        if not customer_ids:
            print("No accounts in config/accounts.yaml.")
            return 1
    else:
        customer_ids = [client.customer_id(args.account)]

    failures = 0
    for customer_id in customer_ids:
        try:
            report = run_for_account(client, customer_id, args.routine,
                                     apply=not args.dry_run, include_tables=args.tables)
        except GadsError as exc:
            failures += 1
            print(f"[{customer_id}] failed: {exc}", file=sys.stderr)
            continue
        if args.out:
            directory = Path(args.out)
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f"{dt.date.today():%Y-%m-%d}-{args.routine}-{customer_id}.md"
            path.write_text(report, encoding="utf-8")
            print(f"[{customer_id}] wrote {path}")
        else:
            print(report)
            print("\n" + "=" * 72 + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
