import datetime as dt

import pytest

from gads import offline
from gads.errors import ConfigError
from tests.conftest import CUSTOMER_ID


def test_patient_data_is_refused_not_stripped():
    with pytest.raises(ConfigError, match="patient data"):
        offline.sanitize({"gclid": "abc", "patient_name": "Jane Doe"})
    with pytest.raises(ConfigError):
        offline.sanitize({"gclid": "abc", "procedure": "root canal"})
    with pytest.raises(ConfigError):
        offline.sanitize({"gclid": "abc", "phone": "3054046659"})


def test_unknown_but_harmless_fields_are_dropped():
    cleaned = offline.sanitize({"gclid": "abc", "conversion_date_time": "x",
                                "internal_row_number": 12})
    assert cleaned == {"gclid": "abc", "conversion_date_time": "x"}


def test_timestamps_always_carry_an_offset():
    stamped = offline.format_datetime(dt.datetime(2026, 8, 18, 14, 30), "-04:00")
    assert stamped == "2026-08-18 14:30:00-04:00"
    assert offline.format_datetime("2026-08-18 14:30:00-04:00") == "2026-08-18 14:30:00-04:00"


def test_short_and_missed_calls_are_not_uploaded():
    rows = offline.from_call_records([
        {"gclid": "a", "start_time": "2026-08-18 10:00:00", "duration": 95},
        {"gclid": "b", "start_time": "2026-08-18 10:05:00", "duration": 20},
        {"gclid": "", "start_time": "2026-08-18 10:06:00", "duration": 300},
        {"gclid": "d", "start_time": "2026-08-18 10:07:00", "duration": 300,
         "status": "missed"},
    ], qualified_seconds=60, utc_offset="-04:00")
    assert [row.gclid for row in rows] == ["a"]


def test_appointments_keep_the_practice_reference_only():
    rows = offline.from_appointments([
        {"gclid": "a", "booked_at": "2026-08-18 09:00:00", "appointment_id": "APT-1",
         "value": 450},
        {"click_id": "b", "booked_at": "2026-08-18 09:30:00", "appointment_id": "APT-2"},
        {"booked_at": "2026-08-18 10:00:00", "appointment_id": "APT-3"},
    ], utc_offset="-04:00", value_field="value")
    assert len(rows) == 2
    assert rows[0].order_id == "APT-1"
    assert rows[0].conversion_value == 450
    assert "patient" not in str(rows[0].as_dict())


def test_upload_skips_rows_without_a_click_id(client):
    rows = [offline.ConversionRow(gclid="a", conversion_date_time="2026-08-18 09:00:00-04:00"),
            offline.ConversionRow(conversion_date_time="2026-08-18 09:00:00-04:00")]
    proposal, summary = offline.upload_conversions(client, CUSTOMER_ID, 905, rows)
    assert summary["uploaded"] == 1
    assert proposal.change.action == "upload_offline_conversions"


def test_no_show_retraction_and_value_restatement(client):
    retracted = offline.retract_no_shows(client, CUSTOMER_ID, 905, ["APT-1", "APT-2"],
                                         "2026-08-20 09:00:00-04:00")
    assert retracted["adjusted"] == 2
    restated = offline.restate_treatment_value(client, CUSTOMER_ID, 905,
                                               [("APT-3", 4200.0)],
                                               "2026-08-20 09:00:00-04:00")
    assert restated["adjusted"] == 1
