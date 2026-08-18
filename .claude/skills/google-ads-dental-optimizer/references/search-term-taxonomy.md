# DENTAL SEARCH-TERM TAXONOMY

Classify every search term from `gaql-library.md` §4 into exactly one category, then act on the
category — not on the term in isolation.

## The evidence rule

Before adding any negative, weigh: **spend · clicks · frequency · intent · conversion behavior.**

- Never negate on a single isolated search **unless** the term is unambiguously irrelevant
  (jobs, schools, DIY, veterinary, another industry entirely).
- A term with ≥1 conversion is not a negative candidate, whatever it looks like.
- A term with ≥5 clicks, 0 conversions, and weak intent is a candidate — check the landing page
  match first; the term may be fine and the page wrong.
- Always run §5.1 first. Never propose a negative that already exists.
- Choose the level deliberately: **account/shared list** for universal junk, **campaign** for
  service mismatches, **ad group** for cross-contamination between your own services.
- Prefer **phrase** negatives for concepts and **exact** negatives for single bad terms. Broad
  negatives over-block: `-free` also blocks "free consultation" and "free implant consult."

---

## The nine categories

### 1. HIGH INTENT — a potential patient, ready now
`emergency dentist near me` · `dentist open now` · `dental implants cost near me` ·
`invisalign consultation [city]` · `same day crown [city]` · `pediatric dentist accepting new patients`

Signals: near me · [city] · open now · same day · today · cost/price with a service · book ·
appointment · accepting new patients · a specific procedure name.

**Action:** protect these. Ensure exact/phrase coverage, check impression share, check the ad and
landing page match the service named. This is where budget should concentrate.

### 2. LOW INTENT — dental, but not ready
`teeth whitening tips` · `how much does a filling usually cost` · `best toothpaste for sensitivity`

**Action:** do not treat as a negative reflexively; some become patients. Keep out of exact-match
scaling, allow only if CPA supports it, and route to informational content rather than a booking
page if the practice has any.

### 3. IRRELEVANT — not the service at all
`dental assistant salary` · `dentist office supplies` · `tooth fairy ideas` · `dog teeth cleaning`

**Action:** negative immediately, account level. This category needs no volume threshold.

### 4. WRONG SERVICE — dentistry, but not what this campaign sells
An implant campaign catching `denture repair`; a general campaign catching `braces for adults`
when the practice does not do ortho.

**Action:** two different fixes, and choosing wrong costs money:
- Practice **does** offer it → this is a **structure** problem. Route the term to the right
  campaign/ad group. Negative it here, add it there.
- Practice does **not** offer it → campaign or account negative.

Never negate a service the practice sells without checking whether another campaign should have it.

### 5. WRONG LOCATION — outside the service area
`dentist in [city 40 miles away]` · `[other state] dentist`

**Action:** location negatives, plus check §1.3 for `PRESENCE_OR_INTEREST` and §6.1 for
`AREA_OF_INTEREST` spend. The setting is usually the real cause; negatives alone treat the symptom.

Care required: patients do travel for implants, full-arch, sedation, and specialist work. Check
which campaign the term hit before excluding a city.

### 6. INSURANCE / MEDICAID — value depends entirely on client strategy
`medicaid dentist near me` · `dentist that takes [plan]` · `free dental clinic` ·
`low income dentist` · `dental school clinic`

**Action:** **ask the practice once, then apply consistently.** This is a business-model question,
not a performance question:
- Practice is fee-for-service / PPO-only → these are negatives, and usually the single largest
  recoverable waste category in a US dental account.
- Practice accepts the plan → these are high-value and should be their own ad group with matching
  ad copy naming the plan.

`free dental clinic`, `dental school`, and `charity dental` are negatives for essentially every
private practice regardless of payer mix.

### 7. INFORMATIONAL — researching, not treating
`what causes tooth sensitivity` · `is root canal painful` · `how long do implants last`

**Action:** generally negative for a direct-response Search campaign. Exception: high-consideration
services (implants, full-arch, ortho) where research terms feed a longer cycle — keep only if the
practice runs remarketing and the CPA supports it.

### 8. JOB / CAREER — not a patient
`dental hygienist jobs near me` · `dental office hiring` · `dentist salary` · `dental assistant resume`

**Action:** negative immediately, account level, no threshold.

### 9. EDUCATIONAL — courses, schools, training
`dental hygiene programs` · `dental school requirements` · `dental ce courses` · `dat exam`

**Action:** negative immediately, account level, no threshold.

---

## Starter negative list

Apply as an account-level shared list. **Review before applying** — items marked ⚠ depend on the
practice's payer mix or service list and must be confirmed with the client first.

**Employment / education**
```
jobs, job, hiring, career, careers, salary, salaries, wage, resume, employment, apprenticeship,
internship, school, schools, college, university, course, courses, class, classes, training,
certification, degree, program, programs, ce credits, continuing education, dat, board exam,
how to become
```

**Not-a-patient / trade**
```
supplies, equipment, chair for sale, wholesale, distributor, manufacturer, software, practice
management, marketing, seo, for sale, buy a practice, dso, insurance company, lawsuit, malpractice,
complaint, board complaint
```

**Animals**
```
dog, cat, pet, puppy, kitten, veterinary, vet, animal, horse
```

**DIY / self-treatment**
```
diy, at home, home remedy, remedies, yourself, kit, how to remove, superglue, temporary fix
```

**Free / charity ⚠** — confirm; some practices run genuine free-consult offers
```
free clinic, free dental clinic, charity, charitable, donated, volunteer, mission trip, no cost,
government, grant, grants
```

**Insurance / public program ⚠** — confirm against payer mix
```
medicaid, medicare, chip, denti-cal, state insurance, public aid, sliding scale, low income,
payment plan only, no insurance discount plan
```

**Wrong service ⚠** — remove any the practice actually offers
```
denture repair, veterinary, orthodontist, oral surgeon, periodontist, endodontist, braces,
wisdom teeth removal, tmj specialist, sleep apnea, botox, facial
```

**Informational**
```
what is, what causes, why does, how long does, symptoms, meaning, definition, wikipedia, reddit,
pictures, images, video, before and after photos
```

**Competitor-adjacent** — never blanket-negate competitor names; they can be a deliberate,
high-intent conquesting strategy. Decide per client and document the decision.

---

## Positive intent modifiers to protect

Never negate these, and check they have exact/phrase coverage: `near me` · `open now` ·
`open today` · `open saturday` · `open sunday` · `walk in` · `same day` · `emergency` · `24 hour` ·
`accepting new patients` · `best` · `top rated` · `reviews` · `consultation` · `appointment` ·
`book` · `cost` · `price` · `financing` · `affordable` (⚠ read alongside the payer-mix decision).

---

## Service-specific intent

Never apply one optimization logic to every dental service — the economics differ by an order of
magnitude.

| Service | Intent window | Distance patients travel | Notes |
|---|---|---|---|
| **Emergency** | Minutes to hours | Closest available | `open now`, `walk in`, `today`, `tonight`, `24 hour` are decisive. Ad schedule and answered calls matter more than bids. Never send emergency traffic to a general homepage. |
| **Implants / full arch** | Weeks to months | 30+ miles routinely | Highest value per patient; tolerate far higher CPA. Research terms have real value here. Consultation is the conversion, not the implant. |
| **Invisalign / clear aligners** | Weeks | 15–25 miles | Price and monthly-payment terms convert. Heavy competition from DTC brands — negate `at home aligners`, `mail order`, brand names the practice does not offer. |
| **Pediatric** | Days to weeks | Close to home or school | Parent is the searcher. `kids`, `children's`, `toddler`, `first visit`. School-calendar seasonality is strong. |
| **General / new patient** | Days to weeks | 5–10 miles | Volume driver. New-patient offer and insurance acceptance are the levers. Distance decay is steep — check §6.3. |
| **Cosmetic (veneers, whitening)** | Weeks | 20+ miles | Elective, income-sensitive, image-driven. Photos and financing matter. Weakest emergency-style urgency. |

Segment campaigns along these lines before optimizing. A shared budget across emergency and
implants will let emergency's volume starve implants' value, or the reverse — and no bid
adjustment fixes a structural conflict.
