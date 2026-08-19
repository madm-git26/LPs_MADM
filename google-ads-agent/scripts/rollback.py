#!/usr/bin/env python3
"""Undo a change run.

    python scripts/rollback.py --list
    python scripts/rollback.py --run-id 20260818-140700-weekly-8015
    python scripts/rollback.py --run-id ... --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gads import mutations  # noqa: E402
from gads.audit import AuditLog  # noqa: E402
from gads.client import GadsClient  # noqa: E402
from gads.errors import GadsError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id")
    parser.add_argument("--list", action="store_true", help="Show recent runs.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        client = GadsClient.from_env()
    except GadsError as exc:
        print(f"Cannot start: {exc}")
        return 1
    audit = AuditLog(client.settings.audit_dir)

    if args.list or not args.run_id:
        runs = audit.list_runs(30)
        if not runs:
            print(f"No runs recorded under {audit.runs_dir}.")
            return 0
        print(f"{'run id':<52} {'when':<20} applied/total")
        for run in runs:
            print(f"{run['run_id']:<52} {run['created']:<20} "
                  f"{run['applied']}/{run['total']}")
        return 0

    try:
        result = mutations.rollback_run(client, args.run_id, audit=audit,
                                        apply=not args.dry_run)
    except (GadsError, FileNotFoundError) as exc:
        print(f"Rollback failed: {exc}")
        return 1
    print(result.markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
