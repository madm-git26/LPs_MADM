"""Which postal codes to buy, and how hard.

Dental is a drive-time business with a wide spread in what a patient is worth.
The ZIP two miles away with a median income of $42k is a good buy for emergency
extractions and a bad buy for $4,000 implants.  This module builds that
judgement from public data instead of guesswork:

    practice address
        -> ZIPs inside the radius            (Census Gazetteer centroids)
        -> income / age / tenure / language  (Census ACS 5-year)
        -> score per service line            (weights below)
        -> target / bid up / bid down / exclude
        -> Google geo target constant ids    (GeoTargetConstantService)

The output plugs straight into ``gads.mutations.add_location_targets`` and
``set_location_bid_modifier``, and is reconciled against real ZIP performance
from ``reports.zip_performance`` once the account has data.
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from .client import GadsClient
from .errors import ConfigError

CACHE_DIR = Path(os.environ.get("GADS_CACHE_DIR", Path(__file__).resolve().parents[1] / ".cache"))
GAZETTEER_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_zcta_national.zip"
ACS_URL = "https://api.census.gov/data/{year}/acs/acs5"
LOCAL_PROFILE_PATH = Path(__file__).resolve().parents[1] / "config" / "zip_demographics.csv"

# ACS 5-year variables. Kept small on purpose: every one of these earns its
# place in a scoring weight below.
ACS_VARIABLES = {
    "B19013_001E": "median_household_income",
    "B01003_001E": "population",
    "B01002_001E": "median_age",
    "B25003_001E": "occupied_units",
    "B25003_002E": "owner_occupied_units",
    "B11005_002E": "households_with_children",
    "C16001_003E": "spanish_speakers",
}

# How much each signal matters, by service line. Distance is always negative:
# people do not drive past three other dentists for a cleaning.
SERVICE_WEIGHTS: dict[str, dict[str, float]] = {
    "emergency": {"distance": -3.0, "population": 1.5, "income": 0.2, "age": 0.0,
                  "owner": 0.0, "children": 0.3, "spanish": 0.0},
    "general":   {"distance": -2.5, "population": 1.2, "income": 0.6, "age": 0.0,
                  "owner": 0.5, "children": 0.8, "spanish": 0.0},
    "implants":  {"distance": -1.2, "population": 0.5, "income": 2.5, "age": 1.2,
                  "owner": 0.8, "children": -0.2, "spanish": 0.0},
    "cosmetic":  {"distance": -1.5, "population": 0.6, "income": 2.2, "age": 0.4,
                  "owner": 0.6, "children": 0.0, "spanish": 0.0},
    "ortho":     {"distance": -2.0, "population": 1.0, "income": 1.2, "age": -0.5,
                  "owner": 0.5, "children": 1.8, "spanish": 0.0},
    "spanish":   {"distance": -2.5, "population": 1.0, "income": 0.2, "age": 0.0,
                  "owner": 0.0, "children": 0.4, "spanish": 3.0},
}


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 3958.7613
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return round(2 * radius * math.asin(math.sqrt(a)), 2)


# ---------------------------------------------------------------------------
# data sources
# ---------------------------------------------------------------------------


def _get(url: str, params: dict[str, Any] | None = None, *, binary: bool = False) -> Any:
    try:
        import requests
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("The requests package is required for ZIP research.") from exc
    response = requests.get(url, params=params, timeout=90)
    response.raise_for_status()
    return response.content if binary else response.text


def zip_centroids(*, refresh: bool = False) -> dict[str, tuple[float, float]]:
    """ZIP -> (latitude, longitude), from the Census Gazetteer, cached on disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / "zcta_centroids.json"
    if cache.exists() and not refresh:
        return {k: tuple(v) for k, v in json.loads(cache.read_text()).items()}

    archive = _get(GAZETTEER_URL, binary=True)
    centroids: dict[str, tuple[float, float]] = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        name = next(n for n in bundle.namelist() if n.lower().endswith(".txt"))
        text = bundle.read(name).decode("utf-8", errors="replace")
    for row in csv.DictReader(io.StringIO(text), delimiter="\t"):
        clean = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        zip_code = clean.get("GEOID") or clean.get("ZCTA5")
        try:
            centroids[zip_code] = (float(clean["INTPTLAT"]), float(clean["INTPTLONG"]))
        except (KeyError, TypeError, ValueError):
            continue
    cache.write_text(json.dumps(centroids), encoding="utf-8")
    return centroids


def zips_within_radius(latitude: float, longitude: float, radius_miles: float,
                       *, centroids: dict[str, tuple[float, float]] | None = None
                       ) -> list[tuple[str, float]]:
    """Every ZIP whose centroid is inside the radius, nearest first."""
    centroids = centroids or zip_centroids()
    out = []
    for zip_code, (lat, lon) in centroids.items():
        distance = haversine_miles(latitude, longitude, lat, lon)
        if distance <= radius_miles:
            out.append((zip_code, distance))
    return sorted(out, key=lambda item: item[1])


def local_profiles(path: str | os.PathLike | None = None) -> dict[str, dict[str, float]]:
    """Read ZIP demographics from a CSV instead of calling the Census API.

    Columns: ``zip`` plus any of ``median_household_income``, ``population``,
    ``median_age``, ``owner_occupied_pct``, ``children_pct``, ``spanish_pct``.
    This is the escape hatch when there is no Census key, or when the practice
    would rather use a bought dataset.
    """
    path = Path(path or LOCAL_PROFILE_PATH)
    if not path.exists():
        return {}
    profiles: dict[str, dict[str, float]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            zip_code = str(row.get("zip") or row.get("zip_code") or "").strip().zfill(5)
            if not zip_code:
                continue
            profile: dict[str, float] = {}
            for key, value in row.items():
                if key in {"zip", "zip_code"}:
                    continue
                try:
                    profile[key.strip()] = float(str(value).replace(",", "").replace("$", ""))
                except (TypeError, ValueError):
                    continue
            profiles[zip_code] = profile
    return profiles


def census_profile(zips: Sequence[str], *, year: str = "2023",
                   local_path: str | os.PathLike | None = None) -> dict[str, dict[str, float]]:
    """Pull the ACS 5-year numbers for a list of ZIPs.

    A local CSV (see :func:`local_profiles`) wins where it has data; anything
    still missing is fetched from the Census API, which now requires a free key
    in ``CENSUS_API_KEY``.  Long lists are chunked.
    """
    profiles: dict[str, dict[str, float]] = {}
    local = local_profiles(local_path)
    for zip_code in zips:
        if zip_code in local:
            profiles[zip_code] = _derive_shares(local[zip_code])
    missing = [z for z in zips if z not in profiles]
    if not missing:
        return profiles

    variables = ",".join(ACS_VARIABLES)
    key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not key:
        if profiles:
            # Partial local coverage is workable: the ZIPs we know about get
            # scored, and the rest are flagged rather than silently dropped.
            return profiles
        raise ConfigError(
            "The Census API needs a free key. Get one in about a minute at "
            "https://api.census.gov/data/key_signup.html and put it in .env as "
            "CENSUS_API_KEY, or supply demographics yourself in "
            f"{LOCAL_PROFILE_PATH.name} (see gads.zips.local_profiles)."
        )

    zips = missing
    for start in range(0, len(zips), 40):
        chunk = zips[start:start + 40]
        params = {
            "get": f"NAME,{variables}",
            "for": f"zip code tabulation area:{','.join(chunk)}",
        }
        params["key"] = key
        body = _get(ACS_URL.format(year=year), params)
        if not body.lstrip().startswith("["):
            snippet = " ".join(body.split())[:160]
            raise ConfigError(f"Census API did not return data: {snippet}")
        header, *rows = json.loads(body)
        for row in rows:
            record = dict(zip(header, row))
            zip_code = record.get("zip code tabulation area") or record.get("NAME", "")[-5:]
            profile: dict[str, float] = {}
            for code, label in ACS_VARIABLES.items():
                value = record.get(code)
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    number = 0.0
                # ACS uses large negative sentinels for suppressed values.
                profile[label] = number if number > -1e6 else 0.0
            profiles[zip_code] = _derive_shares(profile)
    return profiles


def _derive_shares(profile: dict[str, float]) -> dict[str, float]:
    """Turn raw ACS counts into the percentages the scoring model uses."""
    profile = dict(profile)
    occupied = profile.get("occupied_units") or 0
    population = profile.get("population") or 0
    if "owner_occupied_pct" not in profile:
        profile["owner_occupied_pct"] = round(
            (profile.get("owner_occupied_units", 0) / occupied) * 100, 1) if occupied else 0.0
    if "spanish_pct" not in profile:
        profile["spanish_pct"] = round(
            (profile.get("spanish_speakers", 0) / population) * 100, 1) if population else 0.0
    if "children_pct" not in profile:
        profile["children_pct"] = round(
            (profile.get("households_with_children", 0) / occupied) * 100, 1) if occupied else 0.0
    return profile


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------


def _normalise(values: dict[str, float]) -> dict[str, float]:
    """Scale to 0-1 so weights mean the same thing across different units."""
    numbers = [v for v in values.values() if v is not None]
    if not numbers:
        return {k: 0.0 for k in values}
    low, high = min(numbers), max(numbers)
    if high == low:
        return {k: 0.5 for k in values}
    return {k: round((v - low) / (high - low), 4) for k, v in values.items()}


def format_bid_modifier(modifier: float) -> str:
    """1.2 -> "+20%", 0.8 -> "-20%", 1.0 -> "-" (no modifier set)."""
    if modifier is None or abs(modifier - 1.0) < 1e-9:
        return "-"
    return f"{(modifier - 1.0) * 100:+.0f}%"


@dataclass
class ZipRow:
    zip_code: str
    distance_miles: float
    median_household_income: float = 0.0
    population: float = 0.0
    median_age: float = 0.0
    owner_occupied_pct: float = 0.0
    children_pct: float = 0.0
    spanish_pct: float = 0.0
    score: float = 0.0
    action: str = "target"
    bid_modifier: float = 1.0
    geo_target_id: str = ""
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class TargetingPlan:
    service_line: str
    center: tuple[float, float]
    radius_miles: float
    rows: list[ZipRow] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def targeted(self) -> list[ZipRow]:
        return [r for r in self.rows if r.action in {"target", "boost", "trim"}]

    def excluded(self) -> list[ZipRow]:
        """Deliberate exclusions - these become negative location criteria."""
        return [r for r in self.rows if r.action == "exclude"]

    def skipped(self) -> list[ZipRow]:
        """Left out for lack of data. Not targeted, but not excluded either -
        excluding a ZIP because the census is quiet about it would be a decision
        the data does not support."""
        return [r for r in self.rows if r.action == "skip"]

    def markdown(self, limit: int = 40) -> str:
        lines = [
            f"### ZIP targeting plan - {self.service_line}",
            f"_{self.radius_miles} miles around {self.center[0]:.4f}, {self.center[1]:.4f}; "
            f"{len(self.targeted())} targeted, {len(self.excluded())} excluded"
            + (f", {len(self.skipped())} skipped for lack of data" if self.skipped() else "")
            + "._",
            "",
            "| zip | mi | median income | pop | med age | owner% | kids% | es% | score | action | bid |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for row in self.rows[:limit]:
            lines.append(
                f"| {row.zip_code} | {row.distance_miles} | "
                f"${row.median_household_income:,.0f} | {row.population:,.0f} | "
                f"{row.median_age:.0f} | {row.owner_occupied_pct} | {row.children_pct} | "
                f"{row.spanish_pct} | {row.score} | {row.action} | "
                f"{format_bid_modifier(row.bid_modifier)} |"
            )
        if len(self.rows) > limit:
            lines.append(f"\n_{len(self.rows) - limit} more ZIPs not shown._")
        for note in self.notes:
            lines.append(f"\n> {note}")
        return "\n".join(lines)


def build_targeting_plan(latitude: float, longitude: float, radius_miles: float,
                         *, service_line: str = "general",
                         min_income: float | None = None,
                         min_population: float = 500,
                         always_include: Sequence[str] = (),
                         exclude: Sequence[str] = (),
                         year: str = "2023",
                         local_path: str | os.PathLike | None = None,
                         boost_top_pct: float = 0.25,
                         trim_bottom_pct: float = 0.25) -> TargetingPlan:
    """Rank every ZIP in the radius for one service line.

    ``min_income`` is the hard floor for high-ticket lines: below it, the ZIP is
    excluded from *that* campaign rather than bid down, because a $4,000 case is
    not a bid-modifier problem.
    """
    service_line = service_line.lower()
    weights = SERVICE_WEIGHTS.get(service_line)
    if not weights:
        raise ValueError(f"service_line must be one of {sorted(SERVICE_WEIGHTS)}")

    nearby = zips_within_radius(latitude, longitude, radius_miles)
    zip_codes = [z for z, _ in nearby]
    profiles = census_profile(zip_codes, year=year, local_path=local_path) if zip_codes else {}

    rows: list[ZipRow] = []
    for zip_code, distance in nearby:
        profile = profiles.get(zip_code, {})
        rows.append(ZipRow(
            zip_code=zip_code,
            distance_miles=distance,
            median_household_income=profile.get("median_household_income", 0.0),
            population=profile.get("population", 0.0),
            median_age=profile.get("median_age", 0.0),
            owner_occupied_pct=profile.get("owner_occupied_pct", 0.0),
            children_pct=profile.get("children_pct", 0.0),
            spanish_pct=profile.get("spanish_pct", 0.0),
        ))

    scaled = {
        "distance": _normalise({r.zip_code: r.distance_miles for r in rows}),
        "population": _normalise({r.zip_code: r.population for r in rows}),
        "income": _normalise({r.zip_code: r.median_household_income for r in rows}),
        "age": _normalise({r.zip_code: r.median_age for r in rows}),
        "owner": _normalise({r.zip_code: r.owner_occupied_pct for r in rows}),
        "children": _normalise({r.zip_code: r.children_pct for r in rows}),
        "spanish": _normalise({r.zip_code: r.spanish_pct for r in rows}),
    }
    for row in rows:
        row.score = round(sum(weight * scaled[signal][row.zip_code]
                              for signal, weight in weights.items()), 4)

    rows.sort(key=lambda r: r.score, reverse=True)
    ranked = [r for r in rows if r.zip_code not in set(exclude)]
    boost_cut = max(1, int(len(ranked) * boost_top_pct)) if ranked else 0
    trim_cut = max(1, int(len(ranked) * trim_bottom_pct)) if ranked else 0

    unknown = [r.zip_code for r in rows if r.zip_code not in profiles]
    for index, row in enumerate(rows):
        if row.zip_code in unknown and row.zip_code not in set(always_include):
            row.action, row.bid_modifier = "skip", 1.0
            row.note = "no demographic data for this ZIP"
            continue
        if row.zip_code in set(always_include):
            row.action, row.bid_modifier, row.note = "target", 1.0, "forced in by config"
            continue
        if row.zip_code in set(exclude):
            row.action, row.bid_modifier, row.note = "exclude", 1.0, "excluded by config"
            continue
        if row.population < min_population:
            row.action, row.bid_modifier = "exclude", 1.0
            row.note = f"population {row.population:,.0f} is too small to buy"
            continue
        if min_income and row.median_household_income and row.median_household_income < min_income:
            row.action, row.bid_modifier = "exclude", 1.0
            row.note = (f"median income ${row.median_household_income:,.0f} is under the "
                        f"${min_income:,.0f} floor for {service_line}")
            continue
        if index < boost_cut:
            row.action, row.bid_modifier, row.note = "boost", 1.2, "top of the ranking"
        elif index >= len(rows) - trim_cut:
            row.action, row.bid_modifier, row.note = "trim", 0.8, "bottom of the ranking"
        else:
            row.action, row.bid_modifier = "target", 1.0

    plan = TargetingPlan(service_line=service_line, center=(latitude, longitude),
                         radius_miles=radius_miles, rows=rows)
    if unknown:
        plan.notes.append(
            f"{len(unknown)} ZIPs in the radius had no demographic data and were left "
            f"out ({', '.join(unknown[:8])}{'...' if len(unknown) > 8 else ''}). Set "
            "CENSUS_API_KEY or add them to config/zip_demographics.csv before trusting "
            "the coverage of this plan.")
    plan.notes.append(
        "Bid modifiers here are a starting position from demographics only. After "
        "~30 days, reconcile against reports.zip_performance and let real bookings "
        "override the model.")
    if service_line in {"implants", "cosmetic"} and not min_income:
        plan.notes.append(
            "No income floor was set for a high-ticket line - consider "
            "min_income to keep the budget off ZIPs that cannot fund the case.")
    return plan


def reconcile_with_performance(plan: TargetingPlan, zip_rows: Iterable[dict[str, Any]],
                               *, target_cpa: float, min_clicks: int = 25) -> TargetingPlan:
    """Let real results override the demographic model where there is enough data.

    ``zip_rows`` are rows from ``reports.zip_performance`` after
    :func:`resolve_postal_codes` has turned geo target ids into ZIP codes.
    """
    actuals = {str(r.get("postal_code") or r.get("zip") or ""): r for r in zip_rows}
    for row in plan.rows:
        actual = actuals.get(row.zip_code)
        if not actual:
            continue
        clicks = actual.get("metrics.clicks") or 0
        conversions = actual.get("metrics.conversions") or 0
        cost = actual.get("cost") or 0.0
        if clicks < min_clicks:
            continue
        if conversions == 0 and cost >= 2 * target_cpa:
            row.action, row.bid_modifier = "exclude", 1.0
            row.note = f"${cost:,.0f} spent, no bookings - the data beats the model"
            continue
        cpa = cost / conversions if conversions else None
        if cpa and cpa <= target_cpa * 0.7:
            row.action, row.bid_modifier = "boost", 1.3
            row.note = f"CPA ${cpa:,.0f} vs target ${target_cpa:,.0f}"
        elif cpa and cpa >= target_cpa * 1.5:
            row.action, row.bid_modifier = "trim", 0.7
            row.note = f"CPA ${cpa:,.0f} vs target ${target_cpa:,.0f}"
    return plan


# ---------------------------------------------------------------------------
# Google geo target constants
# ---------------------------------------------------------------------------


def resolve_postal_codes(client: GadsClient, resource_names: Sequence[str],
                         customer_id: str | None = None) -> dict[str, str]:
    """``geoTargetConstants/9060601`` -> ``"33131"`` for report rows."""
    ids = [name.split("/")[-1] for name in resource_names if name]
    if not ids:
        return {}
    quoted = ", ".join(f"'geoTargetConstants/{i}'" for i in sorted(set(ids)))
    rows = client.search(customer_id, (
        "SELECT geo_target_constant.resource_name, geo_target_constant.name, "
        "geo_target_constant.canonical_name, geo_target_constant.target_type "
        f"FROM geo_target_constant WHERE geo_target_constant.resource_name IN ({quoted})"
    ))
    return {r["geo_target_constant.resource_name"]: r["geo_target_constant.name"] for r in rows}


def find_geo_target_ids(client: GadsClient, zips: Sequence[str],
                        *, country_code: str = "US", locale: str = "en") -> dict[str, str]:
    """ZIP -> geo target constant id, via Google's own suggestion service."""
    if client.mock:
        return {z: str(9060600 + i) for i, z in enumerate(zips)}
    service = client.service("GeoTargetConstantService")
    request = client.get_type("SuggestGeoTargetConstantsRequest")
    request.locale = locale
    request.country_code = country_code
    request.location_names.names.extend(list(zips))
    response = service.suggest_geo_target_constants(request=request)
    out: dict[str, str] = {}
    for suggestion in response.geo_target_constant_suggestions:
        constant = suggestion.geo_target_constant
        if str(constant.target_type).upper().endswith("POSTAL_CODE"):
            out[constant.name] = str(constant.id)
    return out


def plan_to_proposals(client: GadsClient, customer_id: str, campaign_id: int,
                      plan: TargetingPlan, *, apply_bid_modifiers: bool = False,
                      existing_criteria: dict[str, int] | None = None) -> list[Any]:
    """Turn a plan into proposals: target the winners, exclude the losers.

    Bid modifiers are only emitted for ZIPs already targeted (Google needs the
    criterion to exist before it can carry a modifier), which is why the first
    run targets and the second run tunes.
    """
    from . import mutations

    # Both the ZIPs to buy and the ZIPs to exclude need Google ids; the ones
    # skipped for lack of data need nothing, because nothing is being asserted
    # about them.
    needed = [r for r in plan.targeted() + plan.excluded() if not r.geo_target_id]
    if needed:
        found = find_geo_target_ids(client, [r.zip_code for r in needed])
        for row in needed:
            row.geo_target_id = found.get(row.zip_code, "")

    proposals = []
    to_add = [r.geo_target_id for r in plan.targeted() if r.geo_target_id]
    if to_add:
        proposals.append(mutations.add_location_targets(
            client, customer_id, campaign_id, to_add,
            reason=f"ZIP plan for {plan.service_line}: {len(to_add)} postal codes in "
                   f"{plan.radius_miles} miles"))

    excluded = [r for r in plan.excluded() if r.geo_target_id]
    if excluded:
        proposals.append(mutations.add_location_targets(
            client, customer_id, campaign_id, [r.geo_target_id for r in excluded],
            negative=True,
            reason="ZIPs below the income floor or with no bookings after real spend"))

    if apply_bid_modifiers and existing_criteria:
        for row in plan.rows:
            criterion_id = existing_criteria.get(row.zip_code)
            if criterion_id and row.bid_modifier != 1.0:
                proposals.append(mutations.set_location_bid_modifier(
                    client, customer_id, campaign_id, criterion_id, row.bid_modifier,
                    label=row.zip_code, reason=row.note))
    return proposals
