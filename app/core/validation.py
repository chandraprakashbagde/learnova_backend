"""Safe request-validation handling on top of fastapi_response_handler.

The package's handler already returns sanitised field paths and fixed
messages for every pydantic error type, so no rejected input value or
pydantic/library internals are ever exposed. On top of that, this handler
substitutes the real message for the application-owned ``PydanticCustomError``
types raised in ``app.auth.schemas`` — those messages are static strings from
our own code, so they are safe to disclose. The malformed email message from
pydantic is replaced with a friendlier, library-free phrase. Everything else
keeps the package's fixed message.
"""
import json

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi_response_handler import http_response
from fastapi_response_handler.handlers import request_validation_handler
from starlette.responses import JSONResponse

# Stable PydanticCustomError types whose message comes from app.auth.schemas;
# their ``msg`` is a static string owned by our code, so it is safe to expose.
APP_MESSAGE_TYPES = frozenset({"phone", "password", "cpassword"})

# Replacements keyed by the last location segment for library-raised errors.
SAFE_FIELD_MESSAGES = {
    "email": "Enter a valid email address",
}


def _replacement(error: dict) -> str | None:
    field = ".".join(str(part) for part in error.get("loc", ()))
    leaf = field.rsplit(".", 1)[-1] if field else ""
    if error.get("type") in APP_MESSAGE_TYPES:
        message = error.get("msg")
        return message if message else None
    return SAFE_FIELD_MESSAGES.get(leaf)


async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Use the package's safe response and expose only allow-listed messages."""
    response = await request_validation_handler(request, exc)
    body = json.loads(response.body)
    print(body)
    for detail, error in zip(body.get("details") or [], exc.errors()):
        message = _replacement(error)
        if message:
            detail["message"] = message

    resp = http_response(body, status_code=response.status_code)
    print(body)
    return resp
