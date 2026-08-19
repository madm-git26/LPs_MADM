"""Per-practice configuration: what they sell, what a patient is worth, what they refuse.

Optimisation rules are only as good as this file.  A CPA target of $90 means
nothing without knowing that a general-dentistry patient is worth $900 and an
implant case $4,200.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .client import normalize_customer_id
from .errors import ConfigError

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
DEFAULT_PATHS = [CONFIG_DIR / "accounts.yaml", CONFIG_DIR / "accounts.example.yaml"]


def load_accounts(path: str | os.PathLike | None = None) -> dict[str, dict[str, Any]]:
    """Load accounts.yaml, keyed by normalised customer id."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("PyYAML is required to read account config.") from exc

    candidates = [Path(path)] if path else DEFAULT_PATHS
    source = next((p for p in candidates if p.exists()), None)
    if source is None:
        return {}
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    out: dict[str, dict[str, Any]] = {}
    for raw_id, config in (data.get("accounts") or {}).items():
        try:
            key = normalize_customer_id(raw_id)
        except ConfigError:
            continue
        config = dict(config or {})
        config["customer_id"] = key
        config["_source"] = str(source)
        out[key] = config
    return out


def account_config(customer_id: str | int, path: str | os.PathLike | None = None) -> dict[str, Any]:
    """One practice's config, or an empty dict with a warning-friendly marker."""
    accounts = load_accounts(path)
    key = normalize_customer_id(customer_id)
    return accounts.get(key, {"customer_id": key, "_missing": True})


def target_cpa_table(account: dict[str, Any]) -> dict[str, float]:
    return {k: float(v) for k, v in
            (((account.get("goals") or {}).get("target_cpa")) or {}).items()}


def describe(account: dict[str, Any]) -> str:
    if account.get("_missing"):
        return (f"No config found for {account['customer_id']}. Copy "
                "config/accounts.example.yaml to config/accounts.yaml and fill it in - "
                "targets, services, insurance and hours all feed the optimisation rules.")
    goals = account.get("goals") or {}
    lines = [
        f"**{account.get('name', account['customer_id'])}** ({account.get('city', '')})",
        f"- Monthly budget: {goals.get('monthly_budget', 'not set')}",
        f"- Target CPA: " + ", ".join(f"{k} ${v}" for k, v in target_cpa_table(account).items()),
        f"- Services not offered (auto negatives): "
        + ", ".join(account.get("services_not_offered", []) or ["none listed"]),
        f"- Insurance not accepted: "
        + ", ".join(((account.get("insurance") or {}).get("not_accepted")) or ["none listed"]),
        f"- Qualified call: {account.get('qualified_call_seconds', 60)}s",
    ]
    return "\n".join(lines)
