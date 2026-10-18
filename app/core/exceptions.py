from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.api_response import ApiResponse, ApiError


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        location = error.get("loc", ())
        field = str(location[-1]) if location else None

        errors.append(
            ApiError(
                field=field,
                code=error.get("type", "VALIDATION_ERROR").upper(),
                message=error.get("msg", "Invalid value"),
                scope="field",
            )
        )

    response = ApiResponse(
        success=False,
        message="Please correct the highlighted fields.",
        code="VALIDATION_ERROR",
        scope="field",
        errors=errors,
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode="json"),
    )