from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

class PatientBase(BaseModel):
    mrn: str = Field(..., description="Medical Record Number", min_length=3)
    first_name: str
    last_name: str
    dob: date


class PatientCreate(PatientBase):
    pass

class LabCreate(BaseModel):
    patient_id: UUID
    lab_code: str
    lab_name: str
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    collected_at: datetime = Field(default_factory=datetime.now)


class PatientResponse(PatientBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class LabResponse(BaseModel):
    lab_name: str
    result_value: Optional[float]
    result_unit: Optional[str]
    is_abnormal: bool
    collected_at: datetime

    class Config:
        from_attributes = True

class PillarPatientResponse(BaseModel):
    id: UUID
    mrn: str
    name: str 