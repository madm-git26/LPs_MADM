import pytest

from gads.client import (Settings, normalize_customer_id, query_resource,
                         select_fields)
from gads.errors import ConfigError


@pytest.mark.parametrize("raw", ["123-456-7890", "1234567890", "customers/1234567890"])
def test_customer_ids_are_normalised(raw):
    assert normalize_customer_id(raw) == "1234567890"


@pytest.mark.parametrize("raw", ["12345", "", None, "not-an-id"])
def test_bad_customer_ids_are_rejected(raw):
    with pytest.raises(ConfigError):
        normalize_customer_id(raw)


def test_query_parsing():
    query = ("SELECT campaign.name, metrics.clicks FROM campaign "
             "WHERE campaign.status = 'ENABLED' LIMIT 5")
    assert select_fields(query) == ["campaign.name", "metrics.clicks"]
    assert query_resource(query) == "campaign"


def test_missing_credentials_are_named():
    settings = Settings()
    missing = settings.missing_credentials()
    assert "GOOGLE_ADS_DEVELOPER_TOKEN" in missing
    assert "GOOGLE_ADS_REFRESH_TOKEN" in missing


def test_mock_search_honours_equality_filters(client):
    enabled = client.search("1234567890",
                            "SELECT campaign.id, campaign.status FROM campaign "
                            "WHERE campaign.status = 'ENABLED'")
    missing = client.search("1234567890",
                            "SELECT campaign.id, campaign.status FROM campaign "
                            "WHERE campaign.status = 'PAUSED'")
    assert enabled and not missing


def test_mock_search_honours_in_and_numeric_filters(client):
    rows = client.search("1234567890",
                         "SELECT campaign.id FROM campaign "
                         "WHERE campaign.id IN (2001, 2002)")
    assert {r["campaign.id"] for r in rows} == {2001, 2002}
    big = client.search("1234567890",
                        "SELECT ad_group_criterion.keyword.text, metrics.clicks "
                        "FROM keyword_view WHERE metrics.clicks >= 400")
    assert big and all(r["metrics.clicks"] >= 400 for r in big)


def test_mock_search_applies_limit(client):
    rows = client.search("1234567890", "SELECT campaign.id FROM campaign LIMIT 2")
    assert len(rows) == 2


def test_mock_search_returns_nothing_for_unknown_resources(client):
    assert client.search("1234567890", "SELECT ad.id FROM unicorn_view") == []


def test_mock_mutate_returns_usable_resource_names(client):
    wrapper, operation = client.operation("ad_group_criterion")
    operation.create.keyword.text = "test"
    names = client.mutate("1234567890", [wrapper], validate_only=False)
    assert names[0].startswith("customers/1234567890/adGroupCriteria/")


def test_mock_mutate_echoes_existing_names_for_updates(client):
    wrapper, operation = client.operation("campaign")
    operation.update.resource_name = "customers/1234567890/campaigns/2001"
    names = client.mutate("1234567890", [wrapper], validate_only=False)
    assert names == ["customers/1234567890/campaigns/2001"]
