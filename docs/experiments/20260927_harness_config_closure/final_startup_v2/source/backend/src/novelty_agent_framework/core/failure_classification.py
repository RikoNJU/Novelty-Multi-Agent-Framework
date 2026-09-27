"""Classify observed boundary failures without parsing narrative explanations."""
from __future__ import annotations

import urllib.error
import httpx

from ..schemas.failures import FailureCode as C, FailureScope, make_failure


def provider_failure(exc: Exception, *, scope: FailureScope, occurrence_id: str):
    status = getattr(exc, "status_code", None)
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
    elif isinstance(exc, urllib.error.HTTPError):
        status = exc.code
    if status is not None:
        code = ({401: C.PROVIDER_AUTHENTICATION, 403: C.PROVIDER_AUTHORIZATION,
                 404: C.PROVIDER_RESOURCE_MISSING, 429: C.PROVIDER_RATE_LIMIT}.get(status)
                or (C.PROVIDER_SERVICE if 500 <= status <= 599 else C.PROVIDER_PROTOCOL))
        message = f"Provider returned HTTP {status}; underlying cause is not established by status alone."
    elif isinstance(exc, (httpx.RequestError, TimeoutError, ConnectionError, urllib.error.URLError)) or getattr(exc, "transport_error_type", None):
        code, message = C.PROVIDER_NETWORK, "Provider transport failed; no search result was established."
    elif type(exc).__name__ == "MissingProviderCredentialError":
        code, message = C.PROVIDER_AUTHENTICATION, "Provider credential is missing."
    elif isinstance(exc, (ValueError, TypeError)):
        code, message = C.PROVIDER_PROTOCOL, "Provider result did not satisfy the expected data contract."
    else:
        code, message = C.PROVIDER_UNKNOWN, "Provider failed for an unclassified reason; no search result was established."
    return make_failure(code, scope=scope, message=message, occurrence_id=occurrence_id)
