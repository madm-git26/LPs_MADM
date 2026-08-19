# Measuring a patient, not a click

Everything downstream - bidding, budget, every rule in this skill - is only as
good as what counts as a conversion. Audit this before optimising anything.

## The four steps of a dental conversion

```
click -> call over 60s -> booked appointment -> showed up (and paid)
         qualified call    offline import       adjustment
```

Most accounts measure step one and optimise for it, which teaches Google to buy
people who dial and hang up.

## What should be primary

Primary (drives bidding):
- Calls from ads over 60 seconds
- Click-to-call on the landing page
- Online booking completed
- Form submitted (if the front desk works leads within minutes)
- Booked appointment (offline import) - once it exists, this is the best signal

Secondary (recorded, does not drive bidding): directions clicks, page views,
insurance-page visits, PDF downloads, scroll depth.

Common failures: everything set to primary; "MANY_PER_CLICK" counting on a
new-patient action; a 90-day click-through window inflating this month; two
conversion actions counting the same call.

## Wiring it up

1. **On the landing pages** (this repo already fires these): `click_to_call`,
   `click_book_online`, `click_directions` to `gtag`. Map each to a conversion
   action and mark the first two primary.
2. **Call tracking.** Google's call reporting covers calls from ads and from
   call assets. A dedicated tracker (CallRail and similar) also attributes calls
   from the website to the click - that is what makes qualified-call import
   possible.
3. **Offline import** (`upload_offline_conversions`): the scheduler or PMS export,
   one row per booking with the click id, the booking time, and the practice's own
   appointment reference as `order_id`.
4. **Adjustments** (`adjust_conversions`): retract no-shows, restate the value once
   treatment is known. This is what stops the account optimising for people who
   book and never arrive.

## What never leaves the practice

The upload path strips and, where it looks like patient data, **refuses**: names,
dates of birth, phone numbers, email addresses, addresses, insurance ids, chart
numbers, procedures, diagnoses, notes.

What Google receives: a click id, a timestamp, an opaque appointment reference,
and optionally a currency amount. Nothing else, ever.

Also: never build remarketing audiences or targeting around a dental condition.
Google's personalised advertising policy prohibits it, and it is the wrong thing
to do regardless.

## Practical checks

- `run_report conversion_actions` - what exists, what is primary, how it counts.
- `run_report conversion_breakdown` - which action is actually producing the
  numbers the practice is celebrating.
- Compare Google's conversion count with the practice's new-patient count for the
  same month. A 3× gap means the account is optimising towards something that is
  not a patient.
- If bookings are healthy but chairs are empty, that is the no-show problem -
  `no-show-diagnostic-skill`, then feed the answer back through adjustments.
