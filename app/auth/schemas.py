from pydantic import EmailStr, BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum
from app.core.api_response import custome_validation_error
import re


class Role(str, Enum):
    STUDENT="Student"
    ADMIN="Admin"
    STAFF="Staff"
    TEACHER="Teacher"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., examples=["1234567890"])
    role: Role

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise custome_validation_error(
                "phone",
                "Phone number must be a valid 10-digit Indian mobile number"
            )
        return value 

class UserCreate(UserBase):
    password: str = Field(..., max_length=20)
    cpassword: str = Field(..., max_length=20, description="Confirm password, must match password")

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
            if len(value) < 8:
                raise custome_validation_error("password", "Password must contain at least 8 characters")
    
            if not any(char.isupper() for char in value):
                raise custome_validation_error("password", "Password must contain at least one uppercase letter")
    
            if not any(char.islower() for char in value):
                raise custome_validation_error("password", "Password must contain at least one lowercase letter")
    
            if not any(char.isdigit() for char in value):
                raise custome_validation_error("password", "Password must contain at least one digit")
    
            return value

    @model_validator(mode="after")
    def validate_confirm_password(self) -> "UserCreate":
        if self.password != self.cpassword:
            raise custome_validation_error(
                "cpassword",
                "Passwords do not match"
            )
        return self

class UserOut(UserBase):
    email_verfied: bool = False
    model_config = ConfigDict(from_attributes=True)

class LoginUser(BaseModel):
    name: str
    email: EmailStr

class RegSuccess(BaseModel):
    message: str = "User created successfully"
    user: UserOut