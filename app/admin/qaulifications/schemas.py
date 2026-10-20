from pydantic import BaseModel,field_validator
import re
from app.core.api_response import custome_validation_error


class QualificationOut(BaseModel):
    id: int
    name: str

class CreateUpdateQualification(BaseModel):
    name: str

    @field_validator("name", mode="before")
    @classmethod
    def validate_subject_name(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z]+(?:[ -][A-Za-z]+)*", value):
            raise custome_validation_error("name", "Qualification name can contain only letters, spaces, and hyphens")
            

        return value
