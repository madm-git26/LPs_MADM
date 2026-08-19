# Negatives: the highest-return work in a dental account

In a typical local dental account, 20-40% of spend before cleanup goes to people
who were never going to book: job seekers, students, DIY researchers, people
looking for free clinics, and searches for services the practice does not perform.

## How it is organised

1. **One shared negative list** applied to every campaign - the master list in
   `config/dental_negatives_master.txt`. Blocked once, blocked everywhere.
2. **Campaign-level negatives** for cross-campaign separation (keep "emergency"
   out of the general campaign so each keeps its own intent) and for expensive
   terms that wasted money in that campaign specifically.
3. **Ad group negatives** only for steering traffic between ad groups in the same
   campaign.

## The master list

Categories in `mode=auto` are added by the agent when it sees them: employment,
education, DIY/informational, free/charity, veterinary, retail products,
insurance shopping, legal, industry/research.

Categories in `mode=review` need a decision per practice, and the decision is
usually obvious once you ask:

| Category | Add it when |
|---|---|
| medicaid / medicare | The practice does not accept them |
| cheap / free / discount | The practice sells implants and cosmetic, not a $59 special |
| kids / pediatric | They do not treat children |
| braces / invisalign / ortho | They do not offer ortho |
| wisdom teeth / oral surgeon | They refer those out |
| competitor brand names | Almost always - expensive, low conversion for one location |

Everything in the practice's `services_not_offered` and `insurance.not_accepted`
config becomes an automatic negative. Keeping that config accurate is worth more
than any bid change.

## The weekly loop

1. `run_report search_terms` over 30 days (`only_unmapped: true` for the queue).
2. Sort by cost. Work top-down - the tail does not matter yet.
3. For each term, ask: could this person become a patient here?
   - Never → negative. Pick the *smallest* phrase that blocks the family of terms:
     `jobs`, not `dental assistant jobs in miami fl`.
   - Yes, but wrong ad group → move it, do not block it.
   - Yes and converting → promote it to a keyword.
4. Any term with zero conversions and spend ≥ 2× target CPA becomes an exact
   negative in the campaign that served it, even if it looks relevant. The account
   has already voted.

## Match types for negatives

- **Phrase** for categories and families ("jobs", "how to", "free").
- **Exact** for specific wasteful searches you still want the near-variants of.
- **Broad negatives** rarely - they block more than people expect.

Negatives do not match close variants: `dentist jobs` does not block `dentist job`.
Add both forms for anything that matters.

## What not to block

- Symptom searches ("tooth hurts", "swollen gum") - those are emergency patients.
- "Near me" variants - highest intent in the account.
- Insurance names the practice *does* accept.
- Price questions in a practice that leads with an offer - answer them instead.

## Sanity check, quarterly

Run through the negative list looking for terms that block real patients. A
"cheap" negative added during an implant push will quietly kill the $99 cleaning
campaign a year later.
