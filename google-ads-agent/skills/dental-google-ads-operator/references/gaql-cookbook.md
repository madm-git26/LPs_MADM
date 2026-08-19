# GAQL cookbook

For the questions the canonical reports do not answer. Run with `run_gaql`.

Rules worth remembering: metrics need a `segments.date` filter to mean anything;
`change_event` needs both a date filter and a `LIMIT`; you cannot mix segments
that Google does not allow together (it tells you which); and everything comes
back in micros.

## Which keywords have no ads to serve

```sql
SELECT campaign.name, ad_group.name, ad_group.id
FROM ad_group
WHERE ad_group.status = 'ENABLED'
```
then compare against ad_group_ad - an ad group with no enabled ad is spending
nothing and is easy to miss.

## Search terms that converted but are not keywords yet

```sql
SELECT search_term_view.search_term, campaign.name, ad_group.name,
       metrics.conversions, metrics.cost_micros
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND search_term_view.status = 'NONE'
  AND metrics.conversions > 0
ORDER BY metrics.conversions DESC
```

## Where impression share is being lost, by campaign

```sql
SELECT campaign.name,
       metrics.search_impression_share,
       metrics.search_rank_lost_impression_share,
       metrics.search_budget_lost_impression_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS AND campaign.status = 'ENABLED'
```
Rank loss and budget loss have opposite fixes - never treat them as one number.

## Auction insights (yes, this is available via the API)

```sql
SELECT campaign.name, segments.auction_insight_domain,
       metrics.auction_insight_search_impression_share,
       metrics.auction_insight_search_overlap_rate,
       metrics.auction_insight_search_outranking_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS AND campaign.status = 'ENABLED'
```

## Performance by postal code

```sql
SELECT campaign.name, segments.geo_target_postal_code,
       metrics.clicks, metrics.conversions, metrics.cost_micros
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
  AND geographic_view.location_type = 'LOCATION_OF_PRESENCE'
ORDER BY metrics.cost_micros DESC
```
Postal codes come back as `geoTargetConstants/<id>`; resolve them with a second
query against `geo_target_constant`.

## Conversion actions and how they count

```sql
SELECT conversion_action.name, conversion_action.category,
       conversion_action.primary_for_goal, conversion_action.counting_type,
       conversion_action.click_through_lookback_window_days
FROM conversion_action
WHERE conversion_action.status = 'ENABLED'
```

## Calls longer than 60 seconds

```sql
SELECT campaign.name, call_view.start_call_date_time,
       call_view.call_duration_seconds, call_view.call_status
FROM call_view
WHERE segments.date DURING LAST_30_DAYS
  AND call_view.call_duration_seconds >= 60
ORDER BY call_view.start_call_date_time DESC
```

## Who changed what (last 14 days, 30-day retention)

```sql
SELECT change_event.change_date_time, change_event.user_email,
       change_event.change_resource_type, change_event.resource_change_operation,
       change_event.changed_fields, change_event.campaign
FROM change_event
WHERE change_event.change_date_time >= '2026-08-04'
ORDER BY change_event.change_date_time DESC
LIMIT 500
```

## Asset-level ad copy performance

```sql
SELECT ad_group.name, asset.text_asset.text,
       ad_group_ad_asset_view.field_type,
       ad_group_ad_asset_view.performance_label,
       metrics.impressions, metrics.clicks, metrics.conversions
FROM ad_group_ad_asset_view
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_ad_asset_view.enabled = TRUE
```

## Landing pages

```sql
SELECT landing_page_view.unexpanded_final_url, metrics.clicks,
       metrics.conversions, metrics.cost_micros
FROM landing_page_view
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```
