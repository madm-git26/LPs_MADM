# Dental Google Ads Agent

A live connection between Claude and Google Ads, built for local dental
practices. It reads the account, decides what to change using rules with explicit
evidence thresholds, applies the routine work itself, holds structural changes for
approval, and logs every change with a one-command undo.

It is the execution layer for the advisory dental skills already in this
workspace: they tell you what to do, this does it.

## What it actually does

**Reads** - 25 canonical reports: campaigns, ad groups, keywords with Quality
Score, search terms, postal codes, cities, distance from the practice, household
income deciles, age/gender, hour and day, devices, RSA asset-level performance,
auction insights (yes, via the API), landing pages, calls with duration,
conversion actions, disapprovals, change history, Google's recommendations - plus
raw GAQL.

**Decides** - dead-keyword sweeps, negative mining against a dental master list,
target CPA and budget steps, schedule and geography analysis, ad and asset
review, conversion-tracking audit, call quality. Each rule states the minimum
evidence it needs and refuses to fire below it.

**Writes** - negatives (campaign, ad group, shared list), keywords, pausing
keywords and ads, target CPA and ROAS, budgets, location/device/income bid
modifiers, ad schedules, geo targets and radius, whole Search campaigns, ad
groups and responsive search ads, plus offline conversion import and adjustments.

**Protects** - guardrail policy per account, `validate_only` on every write, an
append-only audit log, per-run undo plans, a read-only kill switch, and a freeze
switch.

## Five-minute start (no credentials needed)

```bash
cd google-ads-agent
pip install -r requirements.txt

export GADS_MOCK=1 GOOGLE_ADS_DEFAULT_CUSTOMER_ID=1234567890

python -m gads.selfcheck
python scripts/run_routine.py --routine weekly --dry-run
python mcp_server/server.py --call account_overview '{}'
```

Mock mode serves realistic fixtures for a single-location Miami practice - a
leaky broad-match ad group, wasted spend on job-seeker searches, a budget-limited
emergency campaign, a disapproved implant ad. Enough for every rule to fire, so
you can see exactly what the agent would do before it can do anything.

## Going live

1. `docs/developer-token-application.md` - get a developer token (the part with a
   waiting period).
2. `docs/oauth-setup.md` - OAuth client and refresh token, then fill in `.env`.
3. `cp config/accounts.example.yaml config/accounts.yaml` and describe the
   practice: target CPA per service line, services **not** offered, insurance
   **not** accepted, hours, coordinates. This file is what makes the rules
   dental-specific rather than generic.
4. `python -m gads.selfcheck`
5. Run `--dry-run` for two weeks before letting it apply anything.
6. `docs/connecting-claude.md` - wire it into Claude Code or Claude Desktop.

## Layout

```
gads/
  client.py       auth, MCC traversal, GAQL execution, mock mode
  gaql.py         query building, micros, derived metrics
  reports.py      the 25 canonical reports
  optimize.py     the rules: what to change and the evidence for it
  guardrails.py   auto / approval / blocked, and the numeric limits
  mutations.py    every write, as validated proposals + the executor + rollback
  audit.py        append-only log and undo plans
  offline.py      booked appointments, qualified calls, no-show adjustments
  zips.py         postal-code research: income, demographics, geo target ids
  accounts.py     per-practice config
  selfcheck.py    "is this thing connected?"
mcp_server/       the MCP tool surface Claude talks to
scripts/          OAuth setup, routine runner, rollback, Editor CSV export
skills/           the operating playbook (copy into ~/.claude/skills/)
config/           guardrails, accounts, master negative list
docs/             token application, OAuth, connecting Claude, planning numbers
tests/            offline tests - no credentials required
```

## Safety, briefly

| Mechanism | Effect |
|---|---|
| `config/guardrails.yaml` | Which actions are automatic, which need a yes, which never happen |
| `validate_only` first | Google checks every write before it is applied |
| `.audit/` | Every decision - applied, held, blocked, rejected - with before/after |
| `scripts/rollback.py --run-id` | Undoes a whole run |
| `GADS_READ_ONLY=1` | Propose everything, apply nothing |
| `freeze.enabled` | Same, per account, with a reason in every report |

Nothing about a patient is ever sent to Google. The offline upload path strips
non-essential fields and refuses outright if a row carries names, phone numbers,
insurance ids, procedures or notes - Google receives a click id, a timestamp, an
opaque appointment reference and optionally an amount.

## Tests

```bash
pip install pytest
GADS_MOCK=1 python -m pytest tests/ -q
```
