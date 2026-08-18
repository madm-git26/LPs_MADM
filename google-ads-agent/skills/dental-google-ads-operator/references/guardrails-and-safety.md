# Guardrails, audit and rollback

The agent is allowed to run an account day to day. It is not allowed to surprise
anyone. Three mechanisms enforce that.

## 1. The policy (`config/guardrails.yaml`)

Every write is classified before it is sent:

- **auto** - applied, logged, reported afterwards
- **approval** - validated, logged, and handed back with the numbers
- **blocked** - never, for anyone

Numeric limits can escalate an auto action to approval on their own: a target CPA
move over 15%, a budget over the daily ceiling, a batch over 50 entities, a change
projected to move daily spend more than $50, or any non-negative change to a
campaign still inside its 14-day learning period.

Per-account overrides go under `accounts:` keyed by customer id - a nervous client
can have `update_budget: approval` while everyone else keeps it automatic.

## 2. Validate before apply

Every operation is sent to Google once with `validate_only=true` before it is sent
for real. If Google would reject it, nothing is applied and the error names the
field. A rejected validation is a bug to fix, not a change to retry.

Two kill switches sit above all of this:

- `GADS_READ_ONLY=1` - propose everything, apply nothing, regardless of policy.
- `freeze.enabled: true` in guardrails.yaml - the same, per account, with a reason
  that shows up in every report. Use it during holidays, disputes, or a practice
  closure.

## 3. The audit log

`.audit/events-YYYY-MM-DD.jsonl` holds every decision - applied, held for
approval, blocked, or rejected by Google - with before/after values and the
reason. `.audit/runs/<run_id>.json` holds the undo plan for that run.

```
python scripts/rollback.py --list
python scripts/rollback.py --run-id 20260818-140700-weekly-8015 --dry-run
python scripts/rollback.py --run-id 20260818-140700-weekly-8015
```

Rollback re-enables what was paused, restores previous targets and budgets, and
removes what was created. It runs under relaxed limits - restoring a previous
value must never be blocked by the step limit that governed the change - but it is
still validated and logged like anything else.

Google's own `change_event` log is the independent record: `run_report
change_history` shows what the agent did alongside what humans did in the UI.

## Habits that keep this safe

- Never bypass a guardrail by splitting a change into smaller pieces. If a change
  needs approval, ask for it.
- Never apply Google's recommendations in bulk. Read them, pick the ones that fit,
  apply individually.
- Say what was held back and why - a report of only what changed is half the story.
- Before a large change, note the run id. The first thing anyone asks when spend
  moves is "what changed on Tuesday".
