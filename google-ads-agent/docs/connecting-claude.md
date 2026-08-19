# Connecting the agent to Claude

The agent is an MCP server. Claude Code picks it up from `.mcp.json` in the
repository root; Claude Desktop needs the same block in its own config.

## Claude Code (this repository)

`.mcp.json` at the repo root already contains:

```json
{
  "mcpServers": {
    "google-ads-dental": {
      "command": "python3",
      "args": ["google-ads-agent/mcp_server/server.py"],
      "env": { "GADS_MOCK": "1" }
    }
  }
}
```

Install the dependencies, then restart Claude Code:

```
pip install -r google-ads-agent/requirements.txt
```

Remove the `GADS_MOCK` line (or set it to `0`) once your developer token is live
and `.env` is filled in.

If you use a virtualenv, point `command` at its interpreter:

```json
"command": "/path/to/venv/bin/python"
```

## Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS,
`%APPDATA%\Claude\claude_desktop_config.json` on Windows:

```json
{
  "mcpServers": {
    "google-ads-dental": {
      "command": "/path/to/venv/bin/python",
      "args": ["/absolute/path/to/google-ads-agent/mcp_server/server.py"]
    }
  }
}
```

Absolute paths only - Claude Desktop does not run from your project directory.

## The skill

`skills/dental-google-ads-operator/` holds the operating playbook: when to pull
which lever, the evidence thresholds, and the dental specifics. Copy it to
`~/.claude/skills/` (or your organisation's skills directory) so Claude loads it
alongside the tools:

```
cp -r google-ads-agent/skills/dental-google-ads-operator ~/.claude/skills/
```

The tools without the skill will do what you ask. The skill is what makes it ask
the right questions first.

## Checking the connection

Without Claude, from a terminal:

```
GADS_MOCK=1 python google-ads-agent/mcp_server/server.py --list-tools
GADS_MOCK=1 python google-ads-agent/mcp_server/server.py --call run_routine '{"routine":"weekly"}'
```

Inside Claude, ask for an account overview. If the tools are connected you will
get tables of real numbers; if not, Claude will say the tools are unavailable
rather than inventing them.

## Running it on a schedule

The routines also run headlessly, which is how the daily check happens without
anyone opening a laptop:

```cron
0 8  * * 1-5  cd /path/to/google-ads-agent && python scripts/run_routine.py --routine daily  --all-accounts --out reports/
0 9  * * 1    cd /path/to/google-ads-agent && python scripts/run_routine.py --routine weekly --all-accounts --out reports/
0 10 1 * *    cd /path/to/google-ads-agent && python scripts/run_routine.py --routine monthly --all-accounts --out reports/
```

Start with `--dry-run` in those lines for the first two weeks. Watching the agent
be right for a fortnight costs nothing; watching it be wrong on a live account
costs a month of bookings.
