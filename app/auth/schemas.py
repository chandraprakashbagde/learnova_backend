from enum import Enum
import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError


class Role(str, Enum):
    STUDENT = "Student"
    ADMIN = "Admin"
    STAFF = "Staff"
    TEACHER = "Teacher"


# Application-owned validation messages. They are raised as
# PydanticCustomError values, exposed verbatim only for these stable error
# types (allow-listed in app/core/validation.py), and reused by
# app.auth.response for OpenAPI documentation — never duplicated.
MSG_PHONE = "Phone number must be a valid 10-digit Indian mobile number"
MSG_PASSWORD_SHORT = "Password must contain at least 8 characters"
MSG_PASSWORD_UPPERCASE = "Password must contain at least one uppercase letter"
MSG_PASSWORD_LOWERCASE = "Password must contain at least one lowercase letter"
MSG_PASSWORD_DIGIT = "Password must contain at least one digit"
MSG_PASSWORD_MISMATCH = "password and confirm password should match"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., examples=["1234567890"], description="10-digit Indian mobile number")
    role: Role

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise PydanticCustomError("phone", MSG_PHONE)
        return value


class UserCreate(UserBase):
    password: str = Field(..., max_length=20)
    cpassword: str = Field(..., max_length=20, description="Confirm password, must match password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise PydanticCustomError("password", MSG_PASSWORD_SHORT)

        if not any(char.isupper() for char in value):
            raise PydanticCustomError("password", MSG_PASSWORD_UPPERCASE)

        if not any(char.islower() for char in value):
            raise PydanticCustomError("password", MSG_PASSWORD_LOWERCASE)

        if not any(char.isdigit() for char in value):
            raise PydanticCustomError("password", MSG_PASSWORD_DIGIT)

        return value

    @model_validator(mode="after")
    def validate_confirm_password(self) -> "UserCreate":
        if self.password != self.cpassword:
            raise PydanticCustomError("cpassword", MSG_PASSWORD_MISMATCH)
        return self


class UserOut(UserBase):
    email_verified: bool = False
    model_config = ConfigDict(from_attributes=True)


class LoginUser(BaseModel):
    name: str
    email: EmailStr


class RegSuccess(BaseModel):
    message: str = "User created successfully"
    user: UserOut

class EmailVerification(BaseModel):
    user_name: str
    user_role: Role
    user_id: int
    user_email: EmailStr = "chandraprakashbcca@gmail.com"