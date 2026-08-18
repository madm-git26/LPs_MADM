# WRITE SAFETY

Read-only by default. Write actions are permitted **only** when the connected tool explicitly
supports them, and even then only within the gate below.

## Preconditions for any write

1. The full audit has been completed at least once on this account.
2. Level 1 (tracking) is verified sound. **Never** write bidding, budget, or targeting changes into
   an account whose conversion data is unreliable — you would be automating a mistake.
3. The change is backed by ≥30 days of data, or is a pure irrelevance negative.
4. The rollback is known and stated before the change is made.

## The pre-write block

Before **every** write, safe or gated, output:

```
CURRENT STATE     <exact values, queried this session, with resource names>
PROPOSED CHANGE   <exact values after>
REASON            <the finding, with evidence and date range>
EXPECTED IMPACT   <in qualified leads / bookings / dollars>
RISK              <what could go wrong, and the early warning signal>
ROLLBACK PLAN     <the exact reverse operation, and how long recovery takes>
```

## Safe — may be auto-applied

| Action | Bound |
|---|---|
| Add negative keywords for unambiguously irrelevant intent | Categories 3, 8, 9 in `search-term-taxonomy.md` only — irrelevant, jobs, educational |
| Add negative keywords for wrong-service terms the practice does not offer | Only after confirming the service list; never a service another campaign should own |
| Pause a disapproved ad | Only when another approved ad serves the same ad group |
| Flag anomalies, produce reports, prepare recommendation sets | Always safe |

Bounds on the safe set, per run:
- Maximum 25 negatives added in a single run. More than that is a structural finding, not a
  batch job — surface it for approval.
- Never a broad-match negative that could block a positive intent modifier
  (`near me`, `emergency`, `cost`, `consultation`, `open now`, …).
- Always check §5.1 and §5.2 first; never re-add an existing negative.
- Log every auto-applied change in the run output with its rollback.

## Gated — requires explicit user approval

- Budget changes beyond ±10% of current daily budget
- Any budget change on a campaign spending >$100/day
- Pausing or enabling a campaign
- Pausing any keyword with conversion history in the last 90 days
- Bulk keyword removal (>10 keywords)
- Bidding strategy changes, and tCPA/tROAS target changes beyond ±15%
- Geo-targeting changes, including radius and presence/interest settings
- Ad group or campaign creation, renaming, or restructuring
- Conversion action changes — primary/secondary status, counting type, value settings
- Anything touching an asset group or PMax structure
- Anything the user has not previously approved in this account

Approval for one change is not approval for the next. Ask each time.

## Never

- Never write during the first audit of an account.
- Never pause on fewer than 30 days of data, or on a temporary CPA spike inside a strong history.
- Never make more than one bidding-strategy change per campaign per 21 days — the learning period
  invalidates the comparison, and stacked changes make the cause unknowable.
- Never change budget and bid strategy in the same action; you lose the ability to attribute the
  result to either.
- Never remove a conversion action. Set it to secondary if it should stop driving bidding.
- Never bulk-apply Google's recommendations. Evaluate each one against the account's actual goal.
- Never enable auto-apply recommendations. If it is already on, flag it 🟠 — it is a frequent cause
  of unexplained overnight change (§10).

## After a write

1. Record: what changed, when, the resource name, the prior value, and the reason.
2. Set a review date — 7 days for negatives and budget, 21 days for bidding changes.
3. Do not evaluate a bidding change before its learning period ends. Reading a learning period as
   a result is how good strategies get reverted.
4. On the review date, compare against the pre-change baseline you captured. If the change made
   things worse, roll back using the stated plan and say so plainly.
