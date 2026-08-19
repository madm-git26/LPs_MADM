import pytest

from gads import zips

SAMPLE = "config/zip_demographics.sample.csv"
MIAMI = (25.7651, -80.2131)


def test_haversine_is_sane():
    # Miami to Fort Lauderdale is about 25 miles.
    assert 20 < zips.haversine_miles(25.7651, -80.2131, 26.1224, -80.1373) < 30
    assert zips.haversine_miles(25.0, -80.0, 25.0, -80.0) == 0.0


def test_local_profiles_derive_shares():
    profiles = zips.local_profiles(SAMPLE)
    assert profiles["33135"]["median_household_income"] == 42000
    assert profiles["33156"]["owner_occupied_pct"] == 71.0


def test_normalise_scales_to_unit_range():
    scaled = zips._normalise({"a": 10, "b": 20, "c": 30})
    assert scaled["a"] == 0.0 and scaled["c"] == 1.0
    assert zips._normalise({"a": 5, "b": 5}) == {"a": 0.5, "b": 0.5}


def test_income_floor_excludes_rather_than_bids_down():
    plan = zips.build_targeting_plan(*MIAMI, 5, service_line="implants",
                                     min_income=70000, local_path=SAMPLE)
    poor = next(r for r in plan.rows if r.zip_code == "33135")
    assert poor.action == "exclude"
    assert "income" in poor.note


def test_always_include_beats_the_model():
    plan = zips.build_targeting_plan(*MIAMI, 5, service_line="implants",
                                     min_income=70000, always_include=["33135"],
                                     local_path=SAMPLE)
    forced = next(r for r in plan.rows if r.zip_code == "33135")
    assert forced.action == "target"


def test_service_lines_rank_differently():
    implants = zips.build_targeting_plan(*MIAMI, 5, service_line="implants",
                                         local_path=SAMPLE)
    emergency = zips.build_targeting_plan(*MIAMI, 5, service_line="emergency",
                                          local_path=SAMPLE)
    assert implants.rows[0].zip_code != emergency.rows[0].zip_code
    # implants should favour the wealthier postal code of the two
    assert implants.rows[0].median_household_income > 100000


def test_zips_without_data_are_skipped_not_excluded():
    plan = zips.build_targeting_plan(*MIAMI, 5, service_line="general",
                                     local_path=SAMPLE)
    assert plan.skipped()
    # Skipping means "we know nothing"; excluding would be asserting something.
    assert all(r.action == "skip" for r in plan.skipped())
    assert not ({r.zip_code for r in plan.skipped()}
                & {r.zip_code for r in plan.excluded()})
    assert any("no demographic data" in note for note in plan.notes)


def test_real_performance_overrides_the_model():
    plan = zips.build_targeting_plan(*MIAMI, 5, service_line="general",
                                     local_path=SAMPLE)
    performance = [
        {"postal_code": "33130", "metrics.clicks": 120, "metrics.conversions": 0,
         "cost": 400.0},
        {"postal_code": "33129", "metrics.clicks": 90, "metrics.conversions": 6,
         "cost": 300.0},
    ]
    zips.reconcile_with_performance(plan, performance, target_cpa=100)
    waster = next(r for r in plan.rows if r.zip_code == "33130")
    winner = next(r for r in plan.rows if r.zip_code == "33129")
    assert waster.action == "exclude"
    assert winner.action == "boost" and winner.bid_modifier > 1


def test_thin_data_does_not_override_the_model():
    plan = zips.build_targeting_plan(*MIAMI, 5, service_line="general",
                                     local_path=SAMPLE)
    before = {r.zip_code: r.action for r in plan.rows}
    zips.reconcile_with_performance(
        plan, [{"postal_code": "33130", "metrics.clicks": 5, "metrics.conversions": 0,
                "cost": 400.0}], target_cpa=100)
    assert {r.zip_code: r.action for r in plan.rows} == before


def test_bid_modifier_formatting():
    assert zips.format_bid_modifier(1.0) == "-"
    assert zips.format_bid_modifier(1.2) == "+20%"
    assert zips.format_bid_modifier(0.8) == "-20%"


def test_plan_becomes_proposals(client):
    plan = zips.build_targeting_plan(*MIAMI, 3, service_line="general",
                                     local_path=SAMPLE)
    proposals = zips.plan_to_proposals(client, "1234567890", 2002, plan)
    actions = {p.change.action for p in proposals}
    assert "add_location_targets" in actions
    assert "exclude_locations" in actions or not plan.excluded()
    # ZIPs skipped for lack of data must not turn into negative criteria
    skipped = {r.zip_code for r in plan.skipped()}
    targeted_zips = {r.zip_code for r in plan.targeted() + plan.excluded()}
    assert not skipped & targeted_zips
