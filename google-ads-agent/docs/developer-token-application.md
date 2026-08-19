# Getting a Google Ads API developer token

You need three things to connect: a **developer token** (from a manager account),
an **OAuth client** (from Google Cloud), and a **refresh token** (from the OAuth
flow). This page covers the first, which is the one with a waiting period.

Until it is approved, run everything with `GADS_MOCK=1` - every tool, report and
routine works against fixtures.

## 1. You need a manager account (MCC)

Developer tokens are issued to manager accounts, not to individual advertisers.
If you run several dental practices, you almost certainly want one anyway.

- Create one at <https://ads.google.com/home/tools/manager-accounts/>
- Link each practice account to it (they approve the link from their side)

## 2. Apply

In the manager account: **Tools & Settings → Setup → API Center**.

You will be asked how you intend to use the API. Applications get rejected for
being vague, so be concrete. What works:

> We manage Google Ads accounts for dental practices as a marketing agency. We
> will use the API to pull performance reports (campaign, keyword, search term,
> geographic and conversion data) into our internal reporting and to apply
> routine optimisations we already perform manually: adding negative keywords,
> pausing non-converting keywords, adjusting target CPA and budgets within
> pre-set limits, and importing offline conversions (booked appointments) from
> our clients' scheduling systems. Tool is internal to our agency; we are not
> reselling API access or building a third-party product.

Also expect to confirm: your company website, that you comply with the Required
Minimum Functionality policy, and how many accounts you manage.

Be honest about internal use. "Internal tool for accounts we manage" is the
easiest category to get approved.

## 3. Access levels

| Level | What it can do | Limit |
|---|---|---|
| **Test** | Only test accounts. Cannot touch a real account. | - |
| **Basic** | Production accounts. | 15,000 operations/day |
| **Standard** | Production accounts. | Effectively unlimited |

Basic is plenty for an agency: this agent uses a few hundred operations a day
across a handful of accounts. Apply for Standard only when you actually hit the
ceiling - the review is stricter.

Approval usually takes a few business days. A Test token arrives immediately, and
it is worth confirming your credentials work with it, but note that a Test token
against a production account returns an error, not data - that is expected.

## 4. When it arrives

Put it in `google-ads-agent/.env`:

```
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890   # your MCC, digits only
```

Then follow `oauth-setup.md`, and check the whole chain with:

```
python -m gads.selfcheck
```

## While you wait

```
GADS_MOCK=1 python -m gads.selfcheck
GADS_MOCK=1 python scripts/run_routine.py --routine weekly --dry-run
GADS_MOCK=1 python mcp_server/server.py --call account_overview '{}'
```

The fixtures model a real single-location practice with a leaky broad-match ad
group, wasted spend on job-seeker searches, and a budget-limited emergency
campaign - enough for the rules to fire and for you to see what the agent would
do on day one.
