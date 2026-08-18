"""Telling Google what actually happened after the click.

A dental account that only counts form submits and call clicks is optimising
for people who dialled, not for people who sat in the chair.  This module
closes the loop:

    click  ->  call over 60s      ->  booked appointment  ->  showed up
               (qualified call)      (offline conversion)   (adjustment)

Each step is a separate conversion action so bidding can be pointed at the one
that matters, and so the gap between them stays visible.

**Nothing here sends patient information.**  Google receives a click id, a
timestamp, an opaque appointment reference and, at most, a currency amount.
Names, phone numbers, procedures, diagnoses and notes are stripped before the
request is built - see :func:`sanitize`.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from .client import GadsClient
from .errors import ApiError, ConfigError
from .guardrails import Change
from .mutations import Proposal

# Keys that must never reach Google. Presence of any of these is a bug in the
# caller's export, not something to quietly drop in production.
PHI_KEYS = {
    "name", "first_name", "last_name", "patient_name", "dob", "date_of_birth",
    "ssn", "insurance_id", "member_id", "chart_number", "diagnosis", "procedure",
    "treatment", "notes", "note", "condition", "address", "email", "phone",
    "phone_number", "caller_id", "medical_history",
}

ALLOWED_KEYS = {
    "gclid", "wbraid", "gbraid", "conversion_date_time", "conversion_value",
    "currency_code", "order_id", "consent_ad_user_data", "consent_ad_personalization",
}


def conversion_action_path(customer_id: str, conversion_action_id: int | str) -> str:
    return f"customers/{customer_id}/conversionActions/{conversion_action_id}"


def format_datetime(when: _dt.datetime | str, utc_offset: str = "+00:00") -> str:
    """Google wants ``yyyy-mm-dd hh:mm:ss+|-hh:mm`` - offset included, always.

    Pass the practice's offset (``-04:00`` for Miami in summer); a timestamp
    without one is rejected, and a wrong one silently misattributes the day.
    """
    if isinstance(when, str):
        return when
    if when.tzinfo is not None:
        return when.strftime("%Y-%m-%d %H:%M:%S%z")[:-2] + ":" + when.strftime("%z")[-2:]
    return f"{when.strftime('%Y-%m-%d %H:%M:%S')}{utc_offset}"


def sanitize(row: dict[str, Any]) -> dict[str, Any]:
    """Drop anything that is not one of the allowed upload fields.

    Raises if the row carries obvious patient data, so an export that was never
    meant to leave the practice fails loudly instead of being uploaded.
    """
    offenders = sorted(PHI_KEYS.intersection({k.lower() for k in row}))
    if offenders:
        raise ConfigError(
            "Refusing to upload: the row contains patient data "
            f"({', '.join(offenders)}). Export only the click id, the timestamp, "
            "an opaque appointment reference and (optionally) a value."
        )
    return {k: v for k, v in row.items() if k in ALLOWED_KEYS}


# ---------------------------------------------------------------------------
# building conversions from practice-side data
# ---------------------------------------------------------------------------


@dataclass
class ConversionRow:
    """One thing that happened, ready to upload."""

    gclid: str = ""
    wbraid: str = ""
    gbraid: str = ""
    conversion_date_time: str = ""
    conversion_value: float | None = None
    currency_code: str = "USD"
    order_id: str = ""
    consent_ad_user_data: str = "GRANTED"
    consent_ad_personalization: str = "UNSPECIFIED"

    def as_dict(self) -> dict[str, Any]:
        return sanitize({k: v for k, v in self.__dict__.items() if v not in (None, "")})


def from_call_records(records: Iterable[dict[str, Any]], *,
                      qualified_seconds: int = 60,
                      utc_offset: str = "+00:00",
                      value_per_call: float | None = None) -> list[ConversionRow]:
    """CallRail-style call logs -> qualified-call conversions.

    Expects each record to carry ``gclid`` (from the visitor's session),
    ``start_time`` and ``duration`` in seconds.  Short calls, missed calls and
    calls with no click id are dropped - they cannot be attributed anyway.
    """
    out: list[ConversionRow] = []
    for record in records:
        gclid = record.get("gclid") or record.get("click_id") or ""
        duration = int(record.get("duration") or record.get("duration_seconds") or 0)
        answered = str(record.get("status", "answered")).lower() in {"answered", "completed", "received"}
        if not gclid or duration < qualified_seconds or not answered:
            continue
        out.append(ConversionRow(
            gclid=gclid,
            conversion_date_time=format_datetime(
                record.get("start_time") or record.get("started_at") or "", utc_offset),
            conversion_value=value_per_call,
            order_id=str(record.get("call_id") or record.get("id") or ""),
        ))
    return out


def from_appointments(rows: Iterable[dict[str, Any]], *,
                      utc_offset: str = "+00:00",
                      value_field: str = "",
                      booked_field: str = "booked_at") -> list[ConversionRow]:
    """Scheduler / PMS export -> booked-appointment conversions.

    ``order_id`` is the practice's own appointment reference, which is what
    makes the later showed-up adjustment possible without storing anything
    identifying on either side.
    """
    out: list[ConversionRow] = []
    for row in rows:
        gclid = row.get("gclid") or row.get("click_id") or ""
        if not gclid:
            continue
        out.append(ConversionRow(
            gclid=gclid,
            conversion_date_time=format_datetime(row.get(booked_field) or "", utc_offset),
            conversion_value=float(row[value_field]) if value_field and row.get(value_field) else None,
            order_id=str(row.get("appointment_id") or row.get("order_id") or ""),
        ))
    return out


# ---------------------------------------------------------------------------
# uploads
# ---------------------------------------------------------------------------


def upload_conversions(client: GadsClient, customer_id: str, conversion_action_id: int,
                       rows: Sequence[ConversionRow | dict[str, Any]],
                       *, validate_only: bool = True,
                       reason: str = "") -> tuple[Proposal, dict[str, Any]]:
    """Upload click conversions. Returns the proposal and the API summary.

    Uploads are always ``partial_failure=True``: one stale click id must not
    throw away the rest of the day's bookings.
    """
    cid = client.customer_id(customer_id)
    payload = [r.as_dict() if isinstance(r, ConversionRow) else sanitize(r) for r in rows]
    payload = [p for p in payload if p.get("gclid") or p.get("wbraid") or p.get("gbraid")]

    change = Change(
        action="upload_offline_conversions",
        entity=f"{len(payload)} conversions to action {conversion_action_id}",
        customer_id=cid,
        entity_count=len(payload),
        reason=reason or "Closing the loop between clicks and booked patients.",
    )
    proposal = Proposal(change, [])

    if not payload:
        return proposal, {"uploaded": 0, "errors": [], "validate_only": validate_only}
    if client.mock:
        return proposal, {"uploaded": len(payload), "errors": [], "validate_only": validate_only,
                          "mock": True}

    service = client.service("ConversionUploadService")
    conversions = []
    for row in payload:
        conversion = client.get_type("ClickConversion")
        conversion.conversion_action = conversion_action_path(cid, conversion_action_id)
        for key in ("gclid", "wbraid", "gbraid", "order_id"):
            if row.get(key):
                setattr(conversion, key, row[key])
        conversion.conversion_date_time = row["conversion_date_time"]
        if row.get("conversion_value") is not None:
            conversion.conversion_value = float(row["conversion_value"])
            conversion.currency_code = row.get("currency_code", "USD")
        conversion.consent.ad_user_data = client.enums.ConsentStatusEnum[
            row.get("consent_ad_user_data", "UNSPECIFIED")]
        conversion.consent.ad_personalization = client.enums.ConsentStatusEnum[
            row.get("consent_ad_personalization", "UNSPECIFIED")]
        conversions.append(conversion)

    try:
        response = service.upload_click_conversions(
            customer_id=cid, conversions=conversions,
            partial_failure=True, validate_only=validate_only)
    except Exception as exc:
        raise ApiError(f"conversion upload failed: {exc}") from exc

    errors = _partial_failure_messages(response)
    return proposal, {
        "uploaded": len(conversions) - len(errors),
        "errors": errors,
        "validate_only": validate_only,
    }


def upload_adjustments(client: GadsClient, customer_id: str, conversion_action_id: int,
                       adjustments: Sequence[dict[str, Any]],
                       *, adjustment_type: str = "RESTATEMENT",
                       validate_only: bool = True) -> dict[str, Any]:
    """Correct a conversion after the fact.

    ``RETRACTION`` for a no-show or a cancellation - it removes the conversion,
    so bidding stops chasing whatever produced it.  ``RESTATEMENT`` for the real
    value once treatment is known.

    Each adjustment needs either ``order_id`` or ``gclid`` + the original
    ``conversion_date_time``, plus ``adjustment_date_time``.
    """
    cid = client.customer_id(customer_id)
    adjustment_type = adjustment_type.upper()
    if client.mock:
        return {"adjusted": len(adjustments), "errors": [], "mock": True,
                "validate_only": validate_only}

    service = client.service("ConversionAdjustmentUploadService")
    payload = []
    for row in adjustments:
        adjustment = client.get_type("ConversionAdjustment")
        adjustment.conversion_action = conversion_action_path(cid, conversion_action_id)
        adjustment.adjustment_type = client.enums.ConversionAdjustmentTypeEnum[adjustment_type]
        adjustment.adjustment_date_time = row["adjustment_date_time"]
        if row.get("order_id"):
            adjustment.order_id = str(row["order_id"])
        else:
            adjustment.gclid_date_time_pair.gclid = row["gclid"]
            adjustment.gclid_date_time_pair.conversion_date_time = row["conversion_date_time"]
        if adjustment_type == "RESTATEMENT":
            adjustment.restatement_value.adjusted_value = float(row["adjusted_value"])
            adjustment.restatement_value.currency_code = row.get("currency_code", "USD")
        payload.append(adjustment)

    try:
        response = service.upload_conversion_adjustments(
            customer_id=cid, conversion_adjustments=payload,
            partial_failure=True, validate_only=validate_only)
    except Exception as exc:
        raise ApiError(f"conversion adjustment upload failed: {exc}") from exc

    errors = _partial_failure_messages(response)
    return {"adjusted": len(payload) - len(errors), "errors": errors,
            "validate_only": validate_only}


def retract_no_shows(client: GadsClient, customer_id: str, conversion_action_id: int,
                     appointment_ids: Sequence[str], when: str,
                     *, validate_only: bool = True) -> dict[str, Any]:
    """Take back the bookings that never walked in."""
    return upload_adjustments(
        client, customer_id, conversion_action_id,
        [{"order_id": str(a), "adjustment_date_time": when} for a in appointment_ids],
        adjustment_type="RETRACTION", validate_only=validate_only)


def restate_treatment_value(client: GadsClient, customer_id: str, conversion_action_id: int,
                            values: Sequence[tuple[str, float]], when: str,
                            *, currency: str = "USD",
                            validate_only: bool = True) -> dict[str, Any]:
    """Replace the placeholder value with what the patient was actually worth."""
    return upload_adjustments(
        client, customer_id, conversion_action_id,
        [{"order_id": str(a), "adjusted_value": v, "currency_code": currency,
          "adjustment_date_time": when} for a, v in values],
        adjustment_type="RESTATEMENT", validate_only=validate_only)


def _partial_failure_messages(response: Any) -> list[str]:
    failure = getattr(response, "partial_failure_error", None)
    if not failure or not getattr(failure, "message", ""):
        return []
    messages = []
    for detail in getattr(failure, "details", []) or []:
        messages.append(str(getattr(detail, "type_url", "")) or failure.message)
    return messages or [failure.message]
