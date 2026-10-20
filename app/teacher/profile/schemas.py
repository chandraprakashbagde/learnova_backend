from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum

class VerificationStatus(str, Enum):
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    PROFILE_COMPLETED = "PROFILE_COMPLETED"
    DOCUMENTS_PENDING = "DOCUMENTS_PENDING"
    UNDER_VERIFICATION = "UNDER_VERIFICATION"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    VERIFIED = "VERIFIED"

class TeacherBase(BaseModel):
    first_name:str 
    last_name: str 
    email: EmailStr 

class TeacherCreate(TeacherBase):
    password: str = Field(..., min_length=8, max_length=20, description="Password should have minimum 8 characters")

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

class TeacherOut(TeacherBase):
    verification_status:VerificationStatus
