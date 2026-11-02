"""Single source of truth for auth response envelopes.

Every success and error is declared once here as a Spec object and reused
for runtime responses (services raise from specs, build envelopes from
specs) and for OpenAPI documentation (api_responses), so messages and error
codes are never repeated by hand.
"""
from fastapi_response_handler import (
    ErrorDetail,
    ErrorSpec,
    SuccessResponse,
    SuccessSpec,
    api_responses,
)

from app.auth.schemas import (
    MSG_PASSWORD_DIGIT,
    MSG_PHONE,
    MSG_PASSWORD_MISMATCH,
    UserOut,
)

# --- success ------------------------------------------------------------
REG_SUCCESSFULL = "Registration successfull !"

USERS_CREATED = SuccessSpec(REG_SUCCESSFULL)


class RegistrationSuccess(SuccessResponse[UserOut]):
    """Envelope for the created user; FastAPI validates against this model."""

    message: str = REG_SUCCESSFULL


# --- errors --------------------------------------------------------------
USER_EMAIL_EXISTS = ErrorSpec(
    "User with this email already exists",
    error_code="USER_EMAIL_EXISTS",
    status_code=409,
)

VALIDATION_FAILED = ErrorSpec(
    "Request validation failed",
    error_code="VALIDATION_ERROR",
    status_code=422,
)

INTERNAL_ERROR = ErrorSpec(
    "Internal server error",
    error_code="INTERNAL_SERVER_ERROR",
    status_code=500,
)

# Field-level details mirror what the runtime handler reports: the request
# location ("body.<field>") and the message raised by the schema validators.
DETAIL_PHONE = ErrorDetail(field="body.phone", message=MSG_PHONE)
DETAIL_PASSWORD_STRENGTH = ErrorDetail(field="body.password", message=MSG_PASSWORD_DIGIT)
DETAIL_PASSWORD_MISMATCH = ErrorDetail(field="body.cpassword", message=MSG_PASSWORD_MISMATCH)

VALIDATION_PHONE = VALIDATION_FAILED.with_details(DETAIL_PHONE)
VALIDATION_PASSWORD_STRENGTH = VALIDATION_FAILED.with_details(DETAIL_PASSWORD_STRENGTH)
VALIDATION_PASSWORD_MISMATCH = VALIDATION_FAILED.with_details(DETAIL_PASSWORD_MISMATCH)

INTERNAL_EXAMPLE = {"internal_error": INTERNAL_ERROR}
VALIDATION_EXAMPLES = {
    "phone": VALIDATION_PHONE,
    "password_strength": VALIDATION_PASSWORD_STRENGTH,
    "password_mismatch": VALIDATION_PASSWORD_MISMATCH,
}
ERROR_EXAMPLES = {
    "email_exists": USER_EMAIL_EXISTS,
}

# 422 and 500 are documented by api_responses itself; 409 must be passed in.
register_responses = api_responses(
    409,
    examples={
        409: ERROR_EXAMPLES,
        422: VALIDATION_EXAMPLES,
        500: INTERNAL_EXAMPLE,
    },
)
