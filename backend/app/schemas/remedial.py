from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date, time

class RemedialClassCreate(BaseModel):
    section_id: UUID
    classroom_id: UUID
    scheduled_date: date
    start_time: time
    end_time: time
    reason: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def validate_time_window(cls, end_time: time, info):
        start_time = info.data.get("start_time")
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be later than start_time")
        return end_time


class RemedialClassUpdate(BaseModel):
    section_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("end_time")
    @classmethod
    def validate_time_window(cls, end_time: Optional[time], info):
        if end_time is None:
            return end_time
        start_time = info.data.get("start_time")
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be later than start_time")
        return end_time

class RemedialClassResponse(BaseModel):
    remedial_id: UUID
    section_id: UUID
    faculty_id: UUID
    classroom_id: UUID
    remedial_code: str
    scheduled_date: date
    start_time: time
    end_time: time
    reason: Optional[str] = None
    code_expires_at: datetime
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarkRemedialAttendance(BaseModel):
    remedial_code: str


class RemedialAttendanceHistoryResponse(BaseModel):
    remedial_attendance_id: UUID
    remedial_id: UUID
    student_id: UUID
    marked_at: datetime
    code_used: Optional[str] = None

    class Config:
        from_attributes = True
