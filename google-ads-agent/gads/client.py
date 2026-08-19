"""Authentication, account discovery and request execution.

Every other module in this package talks to Google through :class:`GadsClient`.
Two things make it worth having rather than using ``GoogleAdsClient`` directly:

1. **One write path.**  All mutations go through ``GoogleAdsService.mutate``
   using ``MutateOperation``, which lets a whole campaign build (budget ->
   campaign -> ad group -> keywords -> ads) be applied atomically with temporary
   resource names, and gives every write the same validate/log/apply treatment.

2. **Mock mode.**  With ``GADS_MOCK=1`` the real proto types are still used, but
   no RPC leaves the machine: reads come from ``gads/mock/*.json`` and writes
   return synthetic resource names.  The whole agent is exercisable before the
   developer token is approved.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from .errors import ApiError, ConfigError

MOCK_DIR = Path(__file__).parent / "mock"
_ENV_LOADED: set[str] = set()


# ---------------------------------------------------------------------------
# configuration
# ---------------------------------------------------------------------------


def load_dotenv(path: str | os.PathLike | None = None) -> None:
    """Load ``KEY=value`` pairs from a .env file without adding a dependency.

    Existing environment variables always win, so an explicit export or a value
    passed by the MCP host overrides the file.
    """
    path = Path(path) if path else Path(__file__).resolve().parents[1] / ".env"
    key = str(path)
    if key in _ENV_LOADED or not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        name, value = name.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(name, value)
    _ENV_LOADED.add(key)


def normalize_customer_id(customer_id: str | int | None) -> str:
    """``123-456-7890`` / ``customers/1234567890`` -> ``1234567890``."""
    if customer_id is None:
        raise ConfigError("No customer id given and no default configured.")
    digits = "".join(ch for ch in str(customer_id) if ch.isdigit())
    if len(digits) != 10:
        raise ConfigError(
            f"{customer_id!r} is not a Google Ads customer id "
            "(expected 10 digits, e.g. 123-456-7890)."
        )
    return digits


@dataclass
class Settings:
    developer_token: str = ""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    login_customer_id: str = ""
    default_customer_id: str = ""
    mock: bool = False
    read_only: bool = False
    audit_dir: Path = field(default_factory=lambda: Path(".audit"))

    @classmethod
    def from_env(cls, dotenv_path: str | os.PathLike | None = None) -> "Settings":
        load_dotenv(dotenv_path)

        def flag(name: str) -> bool:
            return os.environ.get(name, "0").strip().lower() in {"1", "true", "yes", "on"}

        def cid(name: str) -> str:
            raw = os.environ.get(name, "").strip()
            return normalize_customer_id(raw) if raw else ""

        return cls(
            developer_token=os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip(),
            client_id=os.environ.get("GOOGLE_ADS_CLIENT_ID", "").strip(),
            client_secret=os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "").strip(),
            refresh_token=os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", "").strip(),
            login_customer_id=cid("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            default_customer_id=cid("GOOGLE_ADS_DEFAULT_CUSTOMER_ID"),
            mock=flag("GADS_MOCK"),
            read_only=flag("GADS_READ_ONLY"),
            audit_dir=Path(os.environ.get("GADS_AUDIT_DIR", ".audit")),
        )

    def missing_credentials(self) -> list[str]:
        required = {
            "GOOGLE_ADS_DEVELOPER_TOKEN": self.developer_token,
            "GOOGLE_ADS_CLIENT_ID": self.client_id,
            "GOOGLE_ADS_CLIENT_SECRET": self.client_secret,
            "GOOGLE_ADS_REFRESH_TOKEN": self.refresh_token,
            "GOOGLE_ADS_LOGIN_CUSTOMER_ID": self.login_customer_id,
        }
        return [name for name, value in required.items() if not value]


# ---------------------------------------------------------------------------
# row flattening
# ---------------------------------------------------------------------------


def _value(node: Any) -> Any:
    """Convert a proto value into something JSON-serialisable."""
    if node is None or isinstance(node, (str, int, float, bool)):
        return node
    name = getattr(node, "name", None)  # proto-plus enums are IntEnum members
    if name is not None and isinstance(node, int):
        return name
    if isinstance(node, (list, tuple)) or (
        hasattr(node, "__iter__") and not isinstance(node, (bytes, dict))
    ):
        return [_value(item) for item in node]
    return str(node)


def field_value(row: Any, path: str) -> Any:
    """Read a GAQL field path (``metrics.cost_micros``) off a result row.

    GAQL spells some fields ``type``/``status`` where the generated Python class
    uses ``type_`` to dodge the keyword clash, so each segment falls back to the
    trailing-underscore name.
    """
    node = row
    for part in path.split("."):
        if node is None:
            return None
        node = getattr(node, part, None) if hasattr(node, part) else getattr(node, part + "_", None)
    return _value(node)


def flatten_row(row: Any, fields: Sequence[str]) -> dict[str, Any]:
    return {path: field_value(row, path) for path in fields}


def select_fields(query: str) -> list[str]:
    """Pull the selected field paths out of a GAQL query, in order."""
    lowered = query.lower()
    start = lowered.index("select") + len("select")
    end = lowered.index(" from ", start)
    return [f.strip() for f in query[start:end].split(",") if f.strip()]


def query_resource(query: str) -> str:
    """The resource named in the FROM clause."""
    lowered = query.lower()
    start = lowered.index(" from ") + len(" from ")
    rest = query[start:].strip()
    return rest.split()[0].strip()


# ---------------------------------------------------------------------------
# client
# ---------------------------------------------------------------------------


class GadsClient:
    """Thin, testable wrapper around the official Google Ads client."""

    def __init__(self, google_ads_client: Any, settings: Settings):
        self._client = google_ads_client
        self.settings = settings

    # -- construction ------------------------------------------------------

    @classmethod
    def from_env(cls, dotenv_path: str | os.PathLike | None = None) -> "GadsClient":
        settings = Settings.from_env(dotenv_path)
        return cls(build_google_ads_client(settings), settings)

    @property
    def mock(self) -> bool:
        return self.settings.mock

    @property
    def read_only(self) -> bool:
        return self.settings.read_only

    @property
    def raw(self) -> Any:
        """The underlying ``GoogleAdsClient`` (for types and enums)."""
        return self._client

    @property
    def enums(self) -> Any:
        return self._client.enums

    def get_type(self, name: str) -> Any:
        return self._client.get_type(name)

    def service(self, name: str) -> Any:
        return self._client.get_service(name)

    def customer_id(self, customer_id: str | int | None = None) -> str:
        return normalize_customer_id(customer_id or self.settings.default_customer_id)

    # -- reads -------------------------------------------------------------

    def search(self, customer_id: str | int | None, query: str) -> list[dict[str, Any]]:
        """Run a GAQL query and return flat dicts keyed by field path."""
        cid = self.customer_id(customer_id)
        fields = select_fields(query)
        if self.mock:
            return _mock_search(query, fields)

        service = self.service("GoogleAdsService")
        rows: list[dict[str, Any]] = []
        try:
            for batch in service.search_stream(customer_id=cid, query=query):
                for row in batch.results:
                    rows.append(flatten_row(row, fields))
        except Exception as exc:  # google.ads.googleads.errors.GoogleAdsException
            raise _as_api_error(exc, context=f"query on {cid}") from exc
        return rows

    # -- writes ------------------------------------------------------------

    def mutate(
        self,
        customer_id: str | int | None,
        operations: Iterable[Any],
        *,
        validate_only: bool = True,
        partial_failure: bool = False,
    ) -> list[str]:
        """Apply ``MutateOperation``s atomically; return the resource names touched.

        ``validate_only=True`` asks Google to check the request and change
        nothing - every write in this agent is validated that way first.
        """
        cid = self.customer_id(customer_id)
        operations = list(operations)
        if not operations:
            return []
        if self.read_only and not validate_only:
            raise ConfigError(
                "GADS_READ_ONLY=1 - refusing to apply changes. "
                "Unset it in .env when you are ready to let the agent write."
            )
        if self.mock:
            return [_mock_resource_name(cid, op, i) for i, op in enumerate(operations)]

        service = self.service("GoogleAdsService")
        request = self.get_type("MutateGoogleAdsRequest")
        request.customer_id = cid
        request.mutate_operations = operations
        request.validate_only = validate_only
        request.partial_failure = partial_failure
        try:
            response = service.mutate(request=request)
        except Exception as exc:
            raise _as_api_error(exc, context=f"mutate on {cid}") from exc
        return [
            getattr(getattr(result, result._pb.WhichOneof("response") or "", None), "resource_name", "")
            for result in response.mutate_operation_responses
        ]

    def operation(self, kind: str) -> tuple[Any, Any]:
        """Return ``(mutate_operation, sub_operation)`` for e.g. ``"campaign"``.

        Mutating the returned sub-operation mutates the wrapper, so callers can
        build one operation and append the wrapper to their batch.
        """
        wrapper = self.get_type("MutateOperation")
        sub = getattr(wrapper, f"{kind}_operation")
        return wrapper, sub

    # -- account discovery -------------------------------------------------

    def accessible_customers(self) -> list[str]:
        if self.mock:
            return [self.settings.default_customer_id or "1234567890"]
        service = self.service("CustomerService")
        try:
            response = service.list_accessible_customers()
        except Exception as exc:
            raise _as_api_error(exc, context="list_accessible_customers") from exc
        return [name.split("/")[-1] for name in response.resource_names]

    def child_accounts(self, manager_id: str | int | None = None) -> list[dict[str, Any]]:
        """Every non-manager account under an MCC, flattened."""
        manager = manager_id or self.settings.login_customer_id or self.settings.default_customer_id
        if not manager:
            raise ConfigError(
                "No manager account to list from. Set GOOGLE_ADS_LOGIN_CUSTOMER_ID to "
                "your MCC id in .env, or pass manager_id."
            )
        manager = normalize_customer_id(manager)
        query = """
            SELECT
              customer_client.client_customer,
              customer_client.id,
              customer_client.descriptive_name,
              customer_client.currency_code,
              customer_client.time_zone,
              customer_client.manager,
              customer_client.status,
              customer_client.level
            FROM customer_client
            WHERE customer_client.status = 'ENABLED'
        """
        rows = self.search(manager, query)
        return [r for r in rows if not r.get("customer_client.manager")]


def build_google_ads_client(settings: Settings) -> Any:
    """Construct the official client, or an offline-safe one in mock mode."""
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError as exc:  # pragma: no cover - dependency missing
        raise ConfigError(
            "The google-ads package is not installed. "
            "Run: pip install -r google-ads-agent/requirements.txt"
        ) from exc

    if settings.mock:
        from google.auth.credentials import AnonymousCredentials

        # Real proto types, no network: enough to build and inspect every
        # operation this agent can produce.
        return GoogleAdsClient(
            credentials=AnonymousCredentials(),
            developer_token="MOCK",
            login_customer_id=settings.login_customer_id or None,
            use_proto_plus=True,
        )

    missing = settings.missing_credentials()
    if missing:
        raise ConfigError(
            "Missing credentials: "
            + ", ".join(missing)
            + ".\nFill them in google-ads-agent/.env (see .env.example), or set "
            "GADS_MOCK=1 to run against fixtures while your developer token is "
            "pending."
        )

    return GoogleAdsClient.load_from_dict(
        {
            "developer_token": settings.developer_token,
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "refresh_token": settings.refresh_token,
            "login_customer_id": settings.login_customer_id,
            "use_proto_plus": True,
        }
    )


def _as_api_error(exc: Exception, *, context: str) -> ApiError:
    """Turn a GoogleAdsException into something a human can act on."""
    failure = getattr(exc, "failure", None)
    if failure is None:
        return ApiError(f"{context}: {exc}")
    details = []
    for error in failure.errors:
        location = ""
        if error.location and error.location.field_path_elements:
            location = " at " + ".".join(
                el.field_name for el in error.location.field_path_elements
            )
        details.append(f"{error.message.rstrip('.')}{location}")
    return ApiError(
        f"{context} failed: " + "; ".join(details),
        failures=details,
        request_id=getattr(exc, "request_id", None),
    )


# ---------------------------------------------------------------------------
# mock mode
# ---------------------------------------------------------------------------


def _mock_search(query: str, fields: Sequence[str]) -> list[dict[str, Any]]:
    """Serve a query from ``gads/mock/<resource>.json``.

    Fixtures are lists of flat dicts keyed by field path - the same shape a real
    query returns - so reports, guardrails and the whole daily routine behave
    identically with and without credentials.
    """
    resource = query_resource(query)
    # A resource can be segmented several ways (campaign by hour, by device, by
    # competitor domain...), so a fixture may be named for its segmentation.
    segments = [f.split(".")[-1] for f in fields if f.startswith("segments.") and f != "segments.date"]
    candidates = []
    if segments:
        candidates.append(MOCK_DIR / f"{resource}+{'-'.join(sorted(segments))}.json")
    candidates.append(MOCK_DIR / f"{resource}.json")
    path = next((c for c in candidates if c.exists()), None)
    if path is None:
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in rows if _mock_matches(row, query)]
    limit = _query_limit(query)
    if limit:
        rows = rows[:limit]
    return [{f: row.get(f) for f in fields} for row in rows]


_CONDITION = re.compile(
    r"(?P<field>[a-z_]+(?:\.[a-z_0-9]+)+)\s*(?P<op>!=|>=|<=|=|>|<|\bIN\b|\bNOT IN\b)\s*"
    r"(?P<value>\([^)]*\)|'[^']*'|[A-Za-z0-9_.]+)",
    re.IGNORECASE,
)


def _mock_matches(row: dict[str, Any], query: str) -> bool:
    """Apply the WHERE clause to a fixture row, as far as it can be evaluated.

    Fixtures are small, so honouring simple comparisons here is what makes mock
    runs behave like the real thing: a report that asks for disapproved ads gets
    disapproved ads, not the whole table.  Conditions on fields the fixture does
    not carry are ignored rather than guessed at.
    """
    lowered = query.lower()
    if " where " not in lowered:
        return True
    clause = query[lowered.index(" where ") + len(" where "):]
    for keyword in (" order by ", " limit "):
        if keyword in clause.lower():
            clause = clause[: clause.lower().index(keyword)]

    for match in _CONDITION.finditer(clause):
        field_path, op, raw = match.group("field"), match.group("op").upper(), match.group("value")
        if field_path.startswith("segments.date") or field_path not in row:
            continue
        actual = row.get(field_path)
        if op in {"IN", "NOT IN"}:
            wanted = {v.strip().strip("'") for v in raw.strip("()").split(",")}
            inside = str(actual) in wanted
            if (op == "IN") != inside:
                return False
            continue
        expected: Any = raw.strip("'")
        if isinstance(actual, bool):
            expected_bool = str(expected).upper() in {"TRUE", "1"}
            if (actual == expected_bool) != (op == "="):
                return False
            continue
        if isinstance(actual, (int, float)) and not isinstance(actual, bool):
            try:
                number = float(expected)
            except ValueError:
                continue
            checks = {"=": actual == number, "!=": actual != number, ">=": actual >= number,
                      "<=": actual <= number, ">": actual > number, "<": actual < number}
            if not checks.get(op, True):
                return False
            continue
        if op == "=" and str(actual) != expected:
            return False
        if op == "!=" and str(actual) == expected:
            return False
    return True


# MutateOperation field name -> the collection segment in a resource name.
_MOCK_COLLECTIONS = {
    "campaign": "campaigns",
    "campaign_budget": "campaignBudgets",
    "campaign_criterion": "campaignCriteria",
    "campaign_shared_set": "campaignSharedSets",
    "ad_group": "adGroups",
    "ad_group_criterion": "adGroupCriteria",
    "ad_group_ad": "adGroupAds",
    "ad_group_bid_modifier": "adGroupBidModifiers",
    "shared_set": "sharedSets",
    "shared_criterion": "sharedCriteria",
    "asset": "assets",
    "label": "labels",
}


def _mock_resource_name(customer_id: str, operation: Any, index: int) -> str:
    """Invent a resource name of the right shape so rollback is rehearsable.

    Updates and removals already carry the real name; only creates need one
    made up, and it has to look real enough for the undo planner to route it.
    """
    which = operation._pb.WhichOneof("operation") or ""
    sub = getattr(operation, which, None) if which else None
    kind = which[: -len("_operation")] if which.endswith("_operation") else which
    if sub is not None:
        existing = getattr(sub, "remove", "") or getattr(getattr(sub, "update", None),
                                                          "resource_name", "")
        if existing:
            return existing
    collection = _MOCK_COLLECTIONS.get(kind, "mock")
    return f"customers/{customer_id}/{collection}/{9_000_000 + index}"


def _query_limit(query: str) -> int | None:
    lowered = query.lower()
    if " limit " not in lowered:
        return None
    tail = query[lowered.rindex(" limit ") + len(" limit "):].strip()
    digits = "".join(ch for ch in tail.split()[0] if ch.isdigit())
    return int(digits) if digits else None
