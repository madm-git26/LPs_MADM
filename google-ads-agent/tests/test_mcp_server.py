import json

import pytest

from mcp_server import server


def test_every_tool_is_well_formed():
    names = set()
    for tool in server.TOOLS:
        assert tool["name"] not in names, f"duplicate tool {tool['name']}"
        names.add(tool["name"])
        assert tool["description"].strip()
        schema = tool["schema"]
        assert schema["type"] == "object"
        for required in schema.get("required", []):
            assert required in schema["properties"], (tool["name"], required)
        assert callable(tool["handler"])
    # the tools the skill tells Claude to reach for first
    assert {"account_overview", "run_routine", "run_report", "guardrail_status",
            "rollback_run"} <= names


def test_schemas_are_json_serialisable():
    json.dumps([{k: v for k, v in tool.items() if k != "handler"}
                for tool in server.TOOLS])


def test_read_tools_return_tables():
    assert "| campaign |" in server.call_tool("run_report", {"report": "account_summary"})
    assert "Guardrails for" in server.call_tool("guardrail_status", {})
    assert "account_summary" in server.call_tool("list_reports", {})


def test_write_tool_respects_guardrails(tmp_path, monkeypatch):
    monkeypatch.setenv("GADS_AUDIT_DIR", str(tmp_path))
    monkeypatch.setattr(server, "_CLIENT", None)
    out = server.call_tool("create_search_campaign",
                           {"spec": {"name": "Test", "daily_budget": 50}})
    assert "Waiting for your approval" in out


def test_bad_arguments_do_not_crash_the_server():
    assert "Bad request" in server.call_tool("run_report", {})
    assert "Unknown tool" in server.call_tool("does_not_exist", {})


def test_rsa_limits_are_reported_not_raised():
    out = server.call_tool("create_rsa", {"ad_group_id": 1, "headlines": ["a"],
                                          "descriptions": ["b", "c"],
                                          "final_url": "https://x"})
    assert "would be rejected" in out
