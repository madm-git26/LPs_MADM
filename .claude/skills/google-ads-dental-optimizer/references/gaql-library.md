# GAQL QUERY LIBRARY

Every query the agent needs, keyed to the audit step it serves. Written against the Google Ads
Query Language as of API v18+. Field names are stable across recent versions, but **if a query
returns a field error, read the error and correct the field name — do not fabricate the value it
would have returned.**

## Conventions

- **Money is in micros.** `metrics.cost_micros`, `metrics.average_cpc`, `metrics.cost_per_conversion`,
  and `campaign_budget.amount_micros` are all millionths of a currency unit. Divide by 1,000,000.
- **Impression-share metrics are fractions** (0.0–1.0), not percentages. They are also capped: a
  value of `0.9` may mean ">90%". Values above 0.9 are reported by Google as 0.9 exactly.
- **Dates use the account time zone**, not yours. Confirm it in §1.1 before comparing periods.
- Impression share is **not available** for some campaign types and is **never** available when
  segmented too finely — the row is simply absent, which is not the same as zero.
- **Auction Insights has no API surface.** If asked for competitor auction data, answer
  `DATA NOT AVAILABLE — CANNOT CONFIRM` and point to the Google Ads UI.
- Prefer `segments.date DURING LAST_30_DAYS` for standard windows and
  `segments.date BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'` for custom comparisons.
- If the connected tool is a wrapper (Supermetrics, AdvisorPPC) that does not accept raw GAQL, map
  each query below onto the wrapper's own report/field names and keep the same field list.

---

## 1. Account discovery

### 1.1 Customer

```sql
SELECT
  customer.id,
  customer.descriptive_name,
  customer.currency_code,
  customer.time_zone,
  customer.auto_tagging_enabled,
  customer.manager,
  customer.test_account,
  customer.tracking_url_template
FROM customer
```

`auto_tagging_enabled = false` is an immediate 🟠 finding — GCLID-based conversion import and
offline conversion upload both depend on it.

### 1.2 Accounts under a manager (MCC)

```sql
SELECT
  customer_client.id,
  customer_client.descriptive_name,
  customer_client.currency_code,
  customer_client.time_zone,
  customer_client.manager,
  customer_client.status,
  customer_client.level
FROM customer_client
WHERE customer_client.status = 'ENABLED'
```

### 1.3 Campaign inventory + settings

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.serving_status,
  campaign.advertising_channel_type,
  campaign.advertising_channel_sub_type,
  campaign.bidding_strategy_type,
  campaign.start_date,
  campaign.end_date,
  campaign.target_cpa.target_cpa_micros,
  campaign.target_roas.target_roas,
  campaign.maximize_conversions.target_cpa_micros,
  campaign.maximize_conversion_value.target_roas,
  campaign.geo_target_type_setting.positive_geo_target_type,
  campaign.geo_target_type_setting.negative_geo_target_type,
  campaign.network_settings.target_search_network,
  campaign.network_settings.target_content_network,
  campaign.network_settings.target_partner_search_network,
  campaign_budget.amount_micros,
  campaign_budget.explicitly_shared,
  campaign_budget.delivery_method
FROM campaign
WHERE campaign.status != 'REMOVED'
```

`positive_geo_target_type = PRESENCE_OR_INTEREST` on a local dental account is a standing 🟠
finding — it serves to people merely *interested in* the area. Local practices almost always want
`PRESENCE`. Flag it every audit until fixed.

`target_content_network = true` on a Search campaign (Display Expansion) is a common source of
cheap junk clicks. Check it.

### 1.4 Conversion actions

```sql
SELECT
  conversion_action.id,
  conversion_action.name,
  conversion_action.category,
  conversion_action.type,
  conversion_action.status,
  conversion_action.primary_for_goal,
  conversion_action.counting_type,
  conversion_action.click_through_lookback_window_days,
  conversion_action.view_through_lookback_window_days,
  conversion_action.value_settings.default_value,
  conversion_action.value_settings.always_use_default_value,
  conversion_action.phone_call_duration_seconds,
  conversion_action.attribution_model_settings.attribution_model
FROM conversion_action
WHERE conversion_action.status != 'REMOVED'
```

Read this carefully — most dental tracking failures are visible right here. See
`root-cause-playbook.md` §Level 1.

---

## 2. Performance by period

### 2.1 Campaign performance (swap the date range for each window)

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.advertising_channel_type,
  campaign.bidding_strategy_type,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.average_cpc,
  metrics.conversions,
  metrics.all_conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion,
  metrics.conversions_from_interactions_rate,
  metrics.search_impression_share,
  metrics.search_budget_lost_impression_share,
  metrics.search_rank_lost_impression_share,
  metrics.search_absolute_top_impression_share,
  metrics.search_click_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
```

Run for `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, and explicit 60/90-day `BETWEEN` ranges.
For MoM and YoY, use two explicit `BETWEEN` queries and compare — never estimate a prior period.

### 2.2 Daily trend (find the inflection date)

```sql
SELECT
  segments.date,
  campaign.name,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.average_cpc,
  metrics.conversions,
  metrics.conversions_from_interactions_rate
FROM campaign
WHERE segments.date DURING LAST_90_DAYS
  AND campaign.status != 'REMOVED'
ORDER BY segments.date
```

This is the query that answers "WHEN did it change?" Plot each metric by day and find the first
one that broke trend. Do not skip it — period totals hide inflection points.

### 2.3 Account totals by day

```sql
SELECT
  segments.date,
  metrics.cost_micros,
  metrics.clicks,
  metrics.conversions,
  metrics.all_conversions
FROM customer
WHERE segments.date DURING LAST_90_DAYS
ORDER BY segments.date
```

---

## 3. Conversion tracking audit

### 3.1 Conversions by action (the inflation check)

```sql
SELECT
  segments.conversion_action_name,
  segments.conversion_action_category,
  segments.date,
  metrics.all_conversions,
  metrics.all_conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

Use `all_conversions` here — `conversions` counts only actions marked primary, so a secondary
action's volume is invisible in the standard column. Compare the two.

### 3.2 Conversions by campaign and action

```sql
SELECT
  campaign.name,
  segments.conversion_action_name,
  metrics.all_conversions,
  metrics.all_conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status != 'REMOVED'
```

### 3.3 Calls (when call reporting is enabled)

```sql
SELECT
  call_view.caller_area_code,
  call_view.caller_country_code,
  call_view.call_duration_seconds,
  call_view.call_status,
  call_view.call_tracking_display_location,
  call_view.start_call_date_time,
  call_view.type,
  campaign.name,
  ad_group.name
FROM call_view
WHERE segments.date DURING LAST_30_DAYS
```

Gold for dental. Area codes outside the service area, and a mass of sub-30-second calls, are both
direct evidence — the first of geo leakage, the second of spam or misrouted calls.

---

## 4. Search terms

```sql
SELECT
  search_term_view.search_term,
  search_term_view.status,
  segments.keyword.info.text,
  segments.keyword.info.match_type,
  campaign.name,
  ad_group.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.ctr
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
```

`search_term_view.status` tells you whether the term is already added as a keyword or excluded —
check it before recommending an add or a negative.

Note: Google withholds low-volume search terms for privacy. The report will not sum to campaign
totals, and the gap is often 20–40% of spend on small accounts. Say so when quoting coverage.

### 4.1 PMax search categories

PMax exposes categories, not raw terms:

```sql
SELECT
  campaign_search_term_insight.category_label,
  campaign_search_term_insight.id,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM campaign_search_term_insight
WHERE segments.date DURING LAST_30_DAYS
  AND campaign_search_term_insight.campaign_id = <CAMPAIGN_ID>
ORDER BY metrics.impressions DESC
```

This resource requires the campaign id filter. If it errors or is unsupported by the connected
tool, report `DATA NOT AVAILABLE — CANNOT CONFIRM` for PMax search themes rather than inferring
them from Search-campaign terms.

---

## 5. Keywords

```sql
SELECT
  campaign.name,
  ad_group.name,
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  ad_group_criterion.status,
  ad_group_criterion.system_serving_status,
  ad_group_criterion.quality_info.quality_score,
  ad_group_criterion.quality_info.creative_quality_score,
  ad_group_criterion.quality_info.post_click_quality_score,
  ad_group_criterion.quality_info.search_predicted_ctr,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.ctr,
  metrics.average_cpc,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion,
  metrics.search_impression_share,
  metrics.search_rank_lost_impression_share
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_criterion.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
```

Quality Score components matter more than the composite: `post_click_quality_score` = landing page,
`search_predicted_ctr` = relevance/offer, `creative_quality_score` = ad copy. They point at
different fixes.

### 5.1 Negative keywords already in place

```sql
SELECT
  campaign.name,
  campaign_criterion.keyword.text,
  campaign_criterion.keyword.match_type,
  campaign_criterion.negative,
  campaign_criterion.type
FROM campaign_criterion
WHERE campaign_criterion.negative = TRUE
```

Always run this before proposing negatives. Proposing a negative that already exists destroys
trust in the whole recommendation set. Also check for over-blocking — a broad negative like
`-free` blocks "free consultation", which is a core dental offer term.

### 5.2 Shared negative lists

```sql
SELECT
  shared_set.id,
  shared_set.name,
  shared_set.type,
  shared_set.status,
  shared_set.member_count
FROM shared_set
```

```sql
SELECT
  shared_criterion.keyword.text,
  shared_criterion.keyword.match_type,
  shared_set.name
FROM shared_criterion
```

---

## 6. Locations

### 6.1 Geographic performance (where users actually were)

```sql
SELECT
  geographic_view.location_type,
  geographic_view.country_criterion_id,
  segments.geo_target_city,
  segments.geo_target_metro,
  segments.geo_target_region,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```

`geographic_view.location_type` distinguishes `LOCATION_OF_PRESENCE` from `AREA_OF_INTEREST`.
Splitting spend by that field is the single fastest way to quantify presence-vs-interest waste.
The `segments.geo_target_*` fields return geo target constant resource names — resolve them via
`geo_target_constant` when you need readable names.

### 6.2 Resolve geo target names

```sql
SELECT
  geo_target_constant.id,
  geo_target_constant.name,
  geo_target_constant.canonical_name,
  geo_target_constant.target_type,
  geo_target_constant.country_code
FROM geo_target_constant
WHERE geo_target_constant.resource_name IN (<RESOURCE_NAMES>)
```

### 6.3 Distance from the practice — the dental-specific one

```sql
SELECT
  distance_view.distance_bucket,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM distance_view
WHERE segments.date DURING LAST_30_DAYS
```

Requires a location extension / location asset on the account. This is how you learn whether
patients 15+ miles out ever actually book — for most general dentistry they do not, while implant
and full-arch patients routinely travel 30+ miles. Segment by campaign before concluding anything.

### 6.4 What is currently targeted

```sql
SELECT
  campaign.name,
  campaign_criterion.type,
  campaign_criterion.negative,
  campaign_criterion.location.geo_target_constant,
  campaign_criterion.proximity.radius,
  campaign_criterion.proximity.radius_units,
  campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
  campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
  campaign_criterion.proximity.address.postal_code,
  campaign_criterion.proximity.address.city_name
FROM campaign_criterion
WHERE campaign_criterion.type IN ('LOCATION', 'PROXIMITY')
```

---

## 7. Ads, assets, landing pages

### 7.1 Ads

```sql
SELECT
  campaign.name,
  ad_group.name,
  ad_group_ad.ad.id,
  ad_group_ad.ad.type,
  ad_group_ad.status,
  ad_group_ad.policy_summary.approval_status,
  ad_group_ad.ad_strength,
  ad_group_ad.ad.final_urls,
  ad_group_ad.ad.responsive_search_ad.headlines,
  ad_group_ad.ad.responsive_search_ad.descriptions,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.conversions,
  metrics.cost_micros
FROM ad_group_ad
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_ad.status != 'REMOVED'
```

Check `policy_summary.approval_status` on every audit — a disapproved ad in a single-ad ad group
silently zeroes that ad group.

### 7.2 RSA asset performance

```sql
SELECT
  campaign.name,
  ad_group.name,
  ad_group_ad_asset_view.field_type,
  ad_group_ad_asset_view.performance_label,
  asset.text_asset.text,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions
FROM ad_group_ad_asset_view
WHERE segments.date DURING LAST_30_DAYS
```

`performance_label` values are `LOW` / `GOOD` / `BEST` / `PENDING` / `LEARNING`. Replace `LOW`
assets; never delete `BEST` ones.

### 7.3 Landing pages

```sql
SELECT
  landing_page_view.unexpanded_final_url,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_from_interactions_rate,
  metrics.bounce_rate,
  metrics.average_cpc
FROM landing_page_view
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```

`metrics.bounce_rate` requires a linked Analytics property. If it comes back empty, that is a
missing link, not a zero bounce rate.

---

## 8. Devices, schedule, demographics, audiences

```sql
SELECT
  campaign.name,
  segments.device,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_from_interactions_rate
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

Mobile is where dental calls happen. A mobile conversion rate far below desktop usually means the
phone CTA or the page is broken on mobile — check it before touching bids.

```sql
SELECT
  campaign.name,
  segments.day_of_week,
  segments.hour,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

Cross this against practice opening hours. Spend at 9pm Sunday on a call-driven campaign with no
answering service is measurable, recoverable waste.

```sql
SELECT ad_group.name, age_range_view.resource_name,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM age_range_view
WHERE segments.date DURING LAST_30_DAYS
```

```sql
SELECT ad_group.name, gender_view.resource_name,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM gender_view
WHERE segments.date DURING LAST_30_DAYS
```

```sql
SELECT
  campaign.name,
  campaign_audience_view.resource_name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM campaign_audience_view
WHERE segments.date DURING LAST_30_DAYS
```

---

## 9. Performance Max

```sql
SELECT
  campaign.name,
  asset_group.id,
  asset_group.name,
  asset_group.status,
  asset_group.ad_strength,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM asset_group
WHERE segments.date DURING LAST_30_DAYS
```

```sql
SELECT
  asset_group.name,
  asset_group_asset.field_type,
  asset_group_asset.performance_label,
  asset.type,
  asset.text_asset.text,
  asset.image_asset.full_size.url
FROM asset_group_asset
```

```sql
SELECT
  campaign.name,
  asset_group_listing_group_filter.id,
  asset_group_signal.audience.audience
FROM asset_group_signal
```

PMax channel-level breakdown is not exposed in the API. If asked how much PMax spent on Search vs
Display vs YouTube: `DATA NOT AVAILABLE — CANNOT CONFIRM`.

---

## 10. Change history

```sql
SELECT
  change_event.change_date_time,
  change_event.change_resource_type,
  change_event.change_resource_name,
  change_event.client_type,
  change_event.user_email,
  change_event.resource_change_operation,
  change_event.changed_fields,
  change_event.old_resource,
  change_event.new_resource,
  campaign.name,
  ad_group.name
FROM change_event
WHERE change_event.change_date_time DURING LAST_14_DAYS
ORDER BY change_event.change_date_time DESC
LIMIT 1000
```

Constraints that will bite you:

- `change_event` requires **both** a date filter and a `LIMIT` (max 10,000).
- History is retained for **30 days only**. A decline that started 6 weeks ago cannot be explained
  from change history — say `DATA NOT AVAILABLE` for the window rather than reaching.
- `client_type` distinguishes human edits from `GOOGLE_ADS_AUTOMATED_RULE`, recommendations
  auto-apply, and Google's own optimizations. Auto-applied recommendations are a frequent and
  under-suspected cause of sudden account-wide change — check this field first.

Also check auto-apply settings directly when the tool exposes them; a silently enabled
"automatically apply recommendations" setting explains a great many overnight shifts.

---

## 11. Budgets and pacing

```sql
SELECT
  campaign_budget.id,
  campaign_budget.name,
  campaign_budget.amount_micros,
  campaign_budget.total_amount_micros,
  campaign_budget.explicitly_shared,
  campaign_budget.has_recommended_budget,
  campaign_budget.recommended_budget_amount_micros,
  campaign.name,
  metrics.cost_micros
FROM campaign_budget
WHERE segments.date DURING LAST_30_DAYS
```

Compare `metrics.cost_micros / days` against `amount_micros`. A campaign at >95% of budget with
`search_budget_lost_impression_share > 0.10` is budget-constrained; that is a scale opportunity
**only if** its cost per qualified lead is acceptable.
