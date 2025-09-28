from pydantic import BaseModel, Field, validator
from typing import List, Optional

class Medicine(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=50)       # e.g., "500mg"
    frequency: str = Field(..., min_length=1, max_length=50)    # e.g., "Twice a day"
    duration: str = Field(..., min_length=1, max_length=50)     # e.g., "5 days"

    @validator('name')
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Medicine name cannot be empty.")
        return value

class CreatePrescription(BaseModel):
    patient_id: str = Field(..., min_length=5, max_length=50)
    # doctor_id: str = Field(..., min_length=5, max_length=50)
    symptoms: str = Field(..., min_length=5, max_length=500)
    medicines: List[Medicine] = Field(..., min_items=1)
    notes: Optional[str] = Field(None, max_length=1000)
    follow_up_days: Optional[int] = Field(None, ge=1, le=365)

    @validator('symptoms')
    def validate_symptoms(cls, value):
        if not value.strip():
            raise ValueError("Symptoms field cannot be empty.")
        return value


class UpdatePrescription(BaseModel):
    symptoms: Optional[str]
    medicines: Optional[list[Medicine]]
    notes: Optional[str]
    follow_up_days: Optional[int]

class PrescriptionResponse(CreatePrescription):
    symptoms: str
    medicines: list[Medicine]
    notes: Optional[str]
    follow_up_days: Optional[int]
    created_at: int
    updated_at: int