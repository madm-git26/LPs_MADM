# Building a new dental account

Before anything is created, you need five answers from the practice. Without
them you are guessing, and the account will show it:

1. What do they actually want more of? (Emergency volume, implant cases, hygiene
   recalls, a second location's launch - these build differently.)
2. What is a new patient worth, by service line?
3. Which services do they *not* offer, and which insurance do they *not* take?
4. Who answers the phone, when, and what happens after hours?
5. What is the new patient offer, and where does it lead?

## Campaign structure

One campaign per intent and per budget decision. Split when the answer to "would
I ever want to fund these differently?" is yes.

```
Brand   | Search | Brand                          (cheap, defensive, always on)
Emerg   | Search | Emergency Dentist | 24-7       (own budget, own tCPA, 24/7)
General | Search | General Dentist                (the main volume campaign)
Implants| Search | Dental Implants                (high tCPA, income-targeted)
Ortho   | Search | Invisalign + Braces            (only if they offer it)
Cosmetic| Search | Veneers + Whitening
ES      | Search | Espanol                        (if the practice is bilingual)
```

Naming convention: `PRACTICE | CHANNEL | SERVICE | CITY | MODIFIER`. Reports,
automation and the exports all key off names - make them scannable and stable.

Do not start a single-location practice with more than four campaigns. Budget
spread thin learns nothing.

## Ad groups

Tight themes, 5-20 keywords each, one intent per group so the ad can match the
search:

- `Emergency Dentist - Exact`, `Tooth Pain - Phrase`, `Broken Tooth - Phrase`
- `Dentist Near Me - Exact`, `New Patient Special - Phrase`
- `Dental Implants - Exact`, `Implant Cost - Phrase`

Single-keyword ad groups are worth it only for the two or three head terms that
carry the account. Everything else does better in a themed group.

## Settings

| Setting | Value | Why |
|---|---|---|
| Networks | Search only | Search partners and display expansion spend a local budget on nothing. Test later, deliberately. |
| Location | **Presence** ("people in") | Not "presence or interest" - a Brazilian searching "dentist in Miami" is not a patient. This is the single most common setting error in local accounts. |
| Bidding | Maximize Conversions, no target for 2 weeks, then a target | Needs conversion data first. |
| Budget | Enough for ~10 clicks/day per campaign | Less than that and nothing learns. |
| Ad rotation | Optimise | |
| Schedule | Match front-desk hours, except emergency | See the schedule rules. |
| Language | English (+ Spanish where relevant) | |
| Status at creation | **PAUSED** | Read the whole build before it spends. |

## Keywords

Start narrow: exact and phrase on the terms a patient actually types. Broad match
only once the negative list is in place and smart bidding has conversion data.

The keyword set comes from `dental-keyword-research-skill` - do not invent it here.
Map every keyword to the ad group whose ad can answer it.

## Ads

Each ad group gets one RSA: 10-15 headlines, 4 descriptions, and:

- The offer (`$159 New Patient Special`, `Free Implant Consult`)
- Urgency or availability (`Same-Day Appointments`, `Open Saturdays`, `Walk-Ins Welcome`)
- Money (`Financing Available`, `Most Insurance Accepted`)
- Location (`Dentist in Brickell`, `2 Blocks from Downtown`)
- Proof (`500+ 5-Star Reviews`, `Dentist Since 2009`)

Never: guarantees, "best", "painless", "#1", clinical outcome claims, or
before/after promises. That is what trips the healthcare policy.

Assets on every campaign: call, location, sitelinks (Book Online, New Patient
Offer, Insurance, Emergency), callouts, structured snippets (services), and a
lead form only if the front desk works leads within minutes.

## The first 14 days

Change nothing but negatives. Watch:

- day 1-2: are ads approved and serving? is the call asset showing?
- day 3-7: search terms every day; the first week of a new account is where the
  waste is
- day 8-14: conversion tracking sanity - are calls recording, is the booking page
  firing?
- day 15: first target CPA, first real optimisation pass

Tell the practice this schedule in advance. The most common reason a good build
fails is someone panicking on day 4.
