from pydantic import BaseModel,field_validator
import re
from app.core.api_response import custome_validation_error


class CreateUpdateQualification(BaseModel):
    name: str

    @field_validator("name", mode="before")
    @classmethod
    def validate_subject_name(cls, value: str) -> str:
        # Qualification names routinely contain punctuation (the UI itself
        # suggests "B.Ed."), so allow letters, digits, spaces and a small set
        # of separators instead of letters/spaces/hyphens only.
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 &'(),./-]*", value):
            raise custome_validation_error(
                "name",
                "Qualification name can contain letters, numbers, spaces, and . , ' ( ) - & / characters",
            )

        return value
