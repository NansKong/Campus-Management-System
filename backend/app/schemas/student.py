from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

class StudentBase(BaseModel):
    registration_number: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None
    program: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None

class StudentCreate(StudentBase):
    email: EmailStr
    firebase_uid: Optional[str] = None
    enrollment_year: int

    @field_validator("semester")
    @classmethod
    def validate_semester(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 1 or value > 12:
            raise ValueError("Semester must be between 1 and 12")
        return value

    @field_validator("enrollment_year")
    @classmethod
    def validate_enrollment_year(cls, value: int) -> int:
        if value < 2000 or value > 2100:
            raise ValueError("Enrollment year must be between 2000 and 2100")
        return value


class StudentUpdate(BaseModel):
    registration_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None
    program: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    enrollment_year: Optional[int] = None
    email: Optional[EmailStr] = None
    firebase_uid: Optional[str] = None

    @field_validator("semester")
    @classmethod
    def validate_semester(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 1 or value > 12:
            raise ValueError("Semester must be between 1 and 12")
        return value

    @field_validator("enrollment_year")
    @classmethod
    def validate_enrollment_year(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 2000 or value > 2100:
            raise ValueError("Enrollment year must be between 2000 and 2100")
        return value

class StudentResponse(StudentBase):
    student_id: UUID
    user_id: UUID
    enrollment_year: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True
