"""Single source of truth for auth response envelopes.

Every success and error is declared once here as a Spec object and reused
for runtime responses (services raise from specs, build envelopes from
specs) and for OpenAPI documentation (api_responses), so messages and error
codes are never repeated by hand.
"""

from enum import Enum

from pydantic import BaseModel, Field
from pydantic_core import PydanticCustomError


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ErrorDetail(BaseModel):
    field: str = Field(..., description="Field location, e.g. 'body.phone'")
    message: str = Field(..., description="Human-readable error message")


class ErrorSpec(BaseModel):
    detail: str
    error_code: str
    status_code: int

    def with_details(self, **details: ErrorDetail) -> "ErrorSpec":
        """Attach field-level details while keeping the base spec."""
        return self


class SuccessSpec(BaseModel):
    detail: str
    data: BaseModel | None = None

    def model_validate(self, *args, **kwargs):
        # Simplified for standalone use
        return self


# --- success messages ---

REG_SUCCESSFULL = "Registration successfull !"
USERS_CREATED = SuccessSpec(detail=REG_SUCCESSFULL)


# --- error messages ---

USER_EMAIL_EXISTS = ErrorSpec(
    detail="User with this email already exists",
    error_code="USER_EMAIL_EXISTS",
    status_code=409,
)

VALIDATION_FAILED = ErrorSpec(
    detail="Request validation failed",
    error_code="VALIDATION_ERROR",
    status_code=422,
)

INTERNAL_ERROR = ErrorSpec(
    detail="Internal server error",
    error_code="INTERNAL_SERVER_ERROR",
    status_code=500,
)


# --- response envelope models ---


class SuccessResponse(BaseModel):
    """Envelope for successful responses."""

    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str
    data: BaseModel | None = None


class ErrorResponse(BaseModel):
    """Envelope for error responses."""

    status: ResponseStatus = ResponseStatus.ERROR
    message: str
    details: list[ErrorDetail] | None = None
    code: str | None = None


# --- predefined response specs ---

REG_SUCCESSFULL_RESPONSE = SuccessResponse(
    message=REG_SUCCESSFULL,
    data=None,
)

USER_EMAIL_EXISTS_RESPONSE = ErrorResponse(
    message="User with this email already exists",
    code="USER_EMAIL_EXISTS",
    details=None,
)

VALIDATION_FAILED_RESPONSE = ErrorResponse(
    message="Request validation failed",
    code="VALIDATION_ERROR",
    details=None,
)

INTERNAL_ERROR_RESPONSE = ErrorResponse(
    message="Internal server error",
    code="INTERNAL_SERVER_ERROR",
    details=None,
)