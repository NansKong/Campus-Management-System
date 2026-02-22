from datetime import date, datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

AttendanceStatus = Literal["present", "absent"]


class AttendanceSessionCreate(BaseModel):
    section_id: UUID
    classroom_id: Optional[UUID] = None
    session_date: date


class AttendanceRecordCreate(BaseModel):
    student_id: UUID
    status: AttendanceStatus


class BulkAttendanceMark(BaseModel):
    attendance_records: List[AttendanceRecordCreate] = Field(min_length=1)

    @field_validator("attendance_records")
    @classmethod
    def validate_unique_students(cls, records: List[AttendanceRecordCreate]) -> List[AttendanceRecordCreate]:
        student_ids = [record.student_id for record in records]
        if len(student_ids) != len(set(student_ids)):
            raise ValueError("Duplicate student_id values are not allowed")
        return records


class AttendanceRecordResponse(BaseModel):
    record_id: UUID
    session_id: UUID
    student_id: Optional[UUID] = None
    status: AttendanceStatus
    marked_at: datetime

    class Config:
        from_attributes = True


class AttendanceSessionResponse(BaseModel):
    session_id: UUID
    section_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    session_date: date
    total_students: Optional[int] = 0
    present_count: int
    absent_count: int
    is_closed: bool

    class Config:
        from_attributes = True


class AttendanceSectionResponse(BaseModel):
    section_id: UUID
    section_name: str
    course_id: Optional[UUID] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[int] = None


class SectionStudentResponse(BaseModel):
    student_id: UUID
    registration_number: str
    first_name: str
    last_name: str
    section: Optional[str] = None
    semester: Optional[int] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None


class ClassroomResponse(BaseModel):
    classroom_id: UUID
    room_number: str
    block_code: Optional[str] = None
    block_name: Optional[str] = None
    capacity: int
