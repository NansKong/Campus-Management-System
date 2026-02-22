from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class FacultyBase(BaseModel):
    email: EmailStr
    full_name: str
    department: Optional[str] = None

class FacultyCreate(FacultyBase):
    firebase_uid: Optional[str] = None

class FacultyResponse(FacultyBase):
    id: UUID

    class Config:
        from_attributes = True
