"""Google Ads execution layer for local dental practices.

Layers, bottom up:

    client.py      authentication, account discovery, GAQL execution, mock mode
    gaql.py        query building + row flattening
    reports.py     the canonical reports the agent reads every day
    guardrails.py  what the agent may do on its own vs. what needs a human
    mutations.py   every write operation, validated before it is applied
    audit.py       append-only log of every change, with inverse ops for rollback
    offline.py     offline conversion import (booked / showed / revenue)
    zips.py        postal-code research: income, demographics, geo target constants

The MCP server in ../mcp_server exposes these to Claude as tools.
"""

__version__ = "1.0.0"
