"""Safe request-validation handling without fastapi_response_handler.

Handles Pydantic validation errors and substitutes application-owned
messages for stable error types (phone, password, cpassword). All other
field messages are sanitized to safe fallbacks.
"""

import json
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


# Application-owned PydanticCustomError types whose message comes from
# app.auth.schemas; their `msg` is a static string owned by our code,
# so it is safe to expose.
APP_MESSAGE_TYPES = frozenset({"phone", "password", "cpassword"})

# Replacements keyed by the last location segment for common pydantic errors.
SAFE_FIELD_MESSAGES = {
    "email": "Enter a valid email address",
}


def _replacement(error: dict) -> str | None:
    """Map a pydantic validation error to a safe message."""
    field = ".".join(str(part) for part in error.get("loc", ()))
    leaf = field.rsplit(".", 1)[-1] if field else ""
    if error.get("type") in APP_MESSAGE_TYPES:
        message = error.get("msg")
        return message if message else None
    return SAFE_FIELD_MESSAGES.get(leaf)


async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors and return a sanitized JSON response."""
    body = json.loads(exc.body) if exc.body else {}

    # Normalize pydantic error details into a flat list of {loc, msg}
    errors = exc.errors() if hasattr(exc, "errors") else []

    for detail, error in zip(errors, body.get("details", []) if isinstance(body, dict) else []):
        message = _replacement(error)
        if message and isinstance(detail, dict):
            detail["message"] = message

    # Build a clean response body
    resp_body = {}
    if body.get("details"):
        resp_body["details"] = body["details"]

    # Add non-field errors if any
    if body.get("body"):
        resp_body["body"] = body["body"]

    status_code = getattr(exc, "status_code", 422) or 422
    resp = JSONResponse(content=resp_body, status_code=status_code)
    return resp