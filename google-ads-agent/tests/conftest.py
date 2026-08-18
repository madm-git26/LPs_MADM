"""Test setup: everything runs in mock mode, nothing touches a real account."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["GADS_MOCK"] = "1"
os.environ.setdefault("GOOGLE_ADS_DEFAULT_CUSTOMER_ID", "1234567890")
os.environ.setdefault("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "1234567890")

from gads.client import GadsClient  # noqa: E402
from gads.guardrails import GuardrailPolicy  # noqa: E402

CUSTOMER_ID = "1234567890"


@pytest.fixture(scope="session")
def client() -> GadsClient:
    return GadsClient.from_env()


@pytest.fixture()
def audit_dir(tmp_path, monkeypatch) -> Path:
    directory = tmp_path / "audit"
    monkeypatch.setenv("GADS_AUDIT_DIR", str(directory))
    return directory


@pytest.fixture()
def policy() -> GuardrailPolicy:
    return GuardrailPolicy.load()


@pytest.fixture()
def account() -> dict:
    import yaml

    data = yaml.safe_load((ROOT / "config" / "accounts.example.yaml").read_text())
    return data["accounts"]["123-456-7890"]
