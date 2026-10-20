
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError, PydanticCustomError


FIELD_NAMES = {
    "f_name": "First Name",
    "l_name": "Last Name",
    "name": "Name",
    "email": "Email",
    "password": "Password",
    "role": "Role",
    "cpassword": "Confirm Password",
}


def custome_validation_error(field: str, message: str):
    return ValidationError.from_exception_data(
        title="Validation Error",
        line_errors=[
            {
                "type": PydanticCustomError(
                    "custom_validation_error",
                    message,
                ),
                "loc": (field,),
                "input": "",
            }
        ],
    )


def SuccessResp(
    message: str | None = None,
    data: Any = None,
):
    return JSONResponse(
        status_code=200,
        content={
            "status": True,
            "message": message,
            "data": jsonable_encoder(data),
        },
    )


def ErrorResp(
    message: str | None = None,
    data: Any = None,
    status_code: int = 400,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": False,
            "message": message,
            "data": jsonable_encoder(data),
        },
    )


def FieldErrorResp(
    errors: dict[str, str] | None = None,
    field: str | None = None,
    message: str | None = None,
    jsnorsp: bool = True,
):
    errs = dict(errors) if errors else {}

    if field is not None and message is not None:
        errs[field] = message

    response_data = {
        "status": False,
        "errors": errs,
    }

    if not jsnorsp:
        return response_data

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(response_data),
    )


async def validation_exception_handler(exc):
    formatted_errors = {}

    for error in exc.errors():
        location = error.get("loc", ())
        field = location[-1] if location else "body"

        field_name = FIELD_NAMES.get(field, str(field))
        error_type = error.get("type")
        message = error.get("msg", "Invalid value")

        if error_type == "string_too_short":
            min_length = error.get("ctx", {}).get("min_length")
            message = (
                f"{field_name} should have at least "
                f"{min_length} characters"
            )

        elif error_type == "string_too_long":
            max_length = error.get("ctx", {}).get("max_length")
            message = (
                f"{field_name} should not exceed "
                f"{max_length} characters"
            )

        elif error_type == "missing":
            message = f"{field_name} is required"

        elif error_type == "enum":
            expected_values = error.get("ctx", {}).get("expected")

            if expected_values:
                cleaned_values = expected_values.replace("'", "")
                message = f"{field_name} must be {cleaned_values}"
            else:
                message = f"Invalid value for {field_name}"

        elif error_type == "json_invalid":
            field = "body"
            message = "Invalid JSON format in request body"

        elif error_type == "value_error":
            message = f"Invalid value for {field_name}"

        elif error_type == "string_pattern_mismatch":
            message = message.replace("String", field_name)

        # Keep the first error for each field.
        formatted_errors.setdefault(field, message)

    return FieldErrorResp(errors=formatted_errors)
