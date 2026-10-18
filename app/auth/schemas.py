from pydantic import EmailStr, BaseModel, Field, field_validator
from enum import Enum
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
            raise ValueError(
                "Phone number must be a valid 10-digit Indian mobile number"
            )
        return value 

class UserCreate(UserBase):
    password: str = Field(..., max_length=20)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
            if len(value) < 8:
                raise ValueError("Password must contain at least 8 characters")
    
            if not any(char.isupper() for char in value):
                raise ValueError("Password must contain at least one uppercase letter")
    
            if not any(char.islower() for char in value):
                raise ValueError("Password must contain at least one lowercase letter")
    
            if not any(char.isdigit() for char in value):
                raise ValueError("Password must contain at least one digit")
    
            return value

class UserOut(UserBase):
    email_verfied: bool 
    pass

class LoginUser(BaseModel):
    name: str
    email: EmailStr

class RegSuccess(BaseModel):
    message: str = "User created successfully"
    user: UserOut