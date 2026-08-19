# Where to advertise, and how hard

Dental is a drive-time business with a huge spread in what a patient is worth.
The same postal code can be a good buy for emergency extractions and a bad buy
for implants. So targeting is decided per service line, not per account.

## The three layers

1. **Radius or postal codes.** A radius is fine to launch with; postal codes are
   how the account gets efficient, because they can be bid on individually.
2. **Household income deciles** (US only). Google's own estimate of the searcher's
   area income, in ten bands, usable as bid modifiers or exclusions.
3. **Actual postal-code performance.** After ~30 days this beats both of the above.

## Building the plan

`zip_targeting_plan` scores every postal code inside the radius using Census data:

| Signal | Emergency | General | Implants / Cosmetic | Ortho |
|---|---|---|---|---|
| Distance | heavily negative | negative | mildly negative | negative |
| Population | high | high | low | medium |
| Median income | barely matters | some | dominant | medium |
| Median age | - | - | positive | negative (families) |
| Owner occupancy | - | some | positive | some |
| Households with children | some | positive | slightly negative | dominant |
| Spanish-speaking share | - | - | - | - (drives the ES campaign instead) |

Output per postal code: target, boost (+20%), trim (-20%) or exclude, plus the
reason. For high-ticket lines set `min_income` - below the floor the ZIP is
excluded from *that campaign*, not bid down, because a $4,000 case is not a
bid-modifier problem.

Then: `find_geo_target_ids` → `add_location_targets` (needs approval) →
`set_bid_modifier` once the criteria exist. Targets have to exist before they can
carry a modifier, which is why the first run targets and the second tunes.

## Google's income deciles

`set_bid_modifier kind=income` with `INCOME_RANGE_0_50` … `INCOME_RANGE_90_UP`.

- Implants, veneers, full-mouth: bid up the top three deciles, consider excluding
  the bottom two.
- Emergency and general: leave alone. Toothache does not means-test, and excluding
  income bands in an emergency campaign removes patients who pay cash today.
- US only. In Canada, use postal-code targeting from census data instead.

Report income performance with `run_report income_performance` before changing
anything - Google's decile estimate is an estimate.

## Presence, not interest

Campaigns are created with `positive_geo_target_type = PRESENCE`. "Presence or
interest" is the default in the UI and it buys clicks from people who are merely
reading about the city. Check this on any account you inherit; it is the most
common expensive misconfiguration in local dental accounts.

## Drive time beats distance

Three miles across a bridge, a river or a downtown at 5pm can be worse than eight
miles up a highway. Before excluding a nearby underperforming ZIP, check how
people actually get there - and use `run_report distance_performance` (needs
location assets) to see where patients really come from.

## Reconciling with reality

Monthly: pull `zip_performance`, resolve the codes, and let bookings override the
model. A postal code that has spent 2× target CPA with no bookings gets excluded
whatever its demographics say; one booking at 0.7× target gets bid up whatever its
median income says.
