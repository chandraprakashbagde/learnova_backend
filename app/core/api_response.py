from typing import Any, Literal
from pydantic import BaseModel


class ApiError(BaseModel):
    field: str | None = None
    code: str
    message: str
    scope: Literal["field", "global"] = "global"


class ApiResponse(BaseModel):
    success: bool
    message: str
    code: str | None = None
    scope: Literal["field", "global"] = "global"
    data: Any = None
    errors: list[ApiError] = []