"""Exception types used across the agent."""


class GadsError(Exception):
    """Base class for every error this package raises."""


class ConfigError(GadsError):
    """Missing or contradictory configuration (credentials, account config)."""


class GuardrailError(GadsError):
    """A requested change is not permitted by the guardrail policy."""

    def __init__(self, message: str, *, decision=None):
        super().__init__(message)
        self.decision = decision


class ApiError(GadsError):
    """The Google Ads API rejected a request.

    Carries the per-error detail Google returns, which is far more useful than
    the stringified exception: it names the offending field and the index of the
    operation that failed.
    """

    def __init__(self, message: str, *, failures=None, request_id=None):
        super().__init__(message)
        self.failures = failures or []
        self.request_id = request_id
