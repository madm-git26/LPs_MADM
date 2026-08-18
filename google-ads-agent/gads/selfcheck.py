"""``python -m gads.selfcheck`` - is this thing actually connected?

Prints, in order: which mode it is in, whether credentials load, which accounts
the token can see, whether the configured account answers a query, and what the
guardrails currently allow.
"""

from __future__ import annotations

import sys

from .accounts import account_config, describe
from .client import GadsClient, Settings
from .errors import GadsError
from .guardrails import GuardrailPolicy


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    customer_id = argv[0] if argv else None

    settings = Settings.from_env()
    print("Google Ads agent self-check")
    print("=" * 40)
    print(f"mode           : {'MOCK (fixtures)' if settings.mock else 'LIVE'}")
    print(f"read-only      : {settings.read_only}")
    print(f"login customer : {settings.login_customer_id or '(not set)'}")
    print(f"audit dir      : {settings.audit_dir}")

    missing = settings.missing_credentials()
    if missing and not settings.mock:
        print("\nMissing credentials:", ", ".join(missing))
        print("Fill them into google-ads-agent/.env, or set GADS_MOCK=1 to run on "
              "fixtures while the developer token is pending.")
        return 1

    try:
        client = GadsClient.from_env()
    except GadsError as exc:
        print(f"\nCould not build a client: {exc}")
        return 1

    try:
        accessible = client.accessible_customers()
        print(f"\naccessible accounts ({len(accessible)}): "
              + ", ".join(accessible[:10]) + ("..." if len(accessible) > 10 else ""))
    except GadsError as exc:
        print(f"\nlist_accessible_customers failed: {exc}")
        return 1

    target = customer_id or settings.default_customer_id
    if not target:
        print("\nNo account to test - pass one as an argument or set "
              "GOOGLE_ADS_DEFAULT_CUSTOMER_ID.")
        return 0

    try:
        rows = client.search(target, "SELECT customer.id, customer.descriptive_name, "
                                     "customer.currency_code, customer.time_zone FROM customer")
        if rows:
            row = rows[0]
            print(f"\naccount        : {row.get('customer.descriptive_name')} "
                  f"({row.get('customer.id')}, {row.get('customer.currency_code')}, "
                  f"{row.get('customer.time_zone')})")
        else:
            print(f"\naccount {target}: query returned no rows "
                  "(mock mode has no customer fixture - this is fine).")
    except GadsError as exc:
        print(f"\nQuery against {target} failed: {exc}")
        return 1

    print()
    print(describe(account_config(target)))

    policy = GuardrailPolicy.load(account=target, read_only=settings.read_only)
    frozen, why = policy.frozen()
    auto = sorted(k for k, v in policy.config["actions"].items() if v == "auto")
    print(f"\nguardrails     : {'FROZEN - ' + why if frozen else 'active'}")
    print(f"auto actions   : {', '.join(auto)}")
    print(f"limits         : tCPA +/-{policy.limits['target_cpa_change_pct']}%, "
          f"budget +/-{policy.limits['budget_change_pct']}% up to "
          f"{policy.limits['max_daily_budget']}/day, "
          f"{policy.limits['max_ops_per_day']} ops/day")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
