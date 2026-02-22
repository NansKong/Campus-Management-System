from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole

class UserBase(BaseModel):
    role: UserRole

class UserCreate(UserBase):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Invalid email format")
        return email

class UserResponse(UserBase):
    user_id: UUID
    email: str
    firebase_uid: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
