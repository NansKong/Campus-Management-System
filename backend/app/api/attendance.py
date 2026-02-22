from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.faculty import Faculty
from app.models.user import User
from app.schemas.attendance import (
    AttendanceRecordResponse,
    AttendanceSectionResponse,
    AttendanceSessionCreate,
    AttendanceSessionResponse,
    BulkAttendanceMark,
    ClassroomResponse,
    SectionStudentResponse,
)
from app.services import attendance_service
from app.utils.auth import get_current_user

router = APIRouter()


def _role_to_str(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _require_faculty(current_user: User) -> None:
    if _role_to_str(current_user.role) != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty can perform this action")


def _get_faculty_profile(db: Session, user_id: UUID) -> Faculty:
    faculty = db.query(Faculty).filter(Faculty.user_id == user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    return faculty


@router.get("/sections/my", response_model=List[AttendanceSectionResponse])
def get_my_sections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_faculty(current_user)
    faculty = _get_faculty_profile(db, current_user.user_id)
    sections = attendance_service.get_faculty_sections(db, faculty.faculty_id)
    return [attendance_service.serialize_section(section) for section in sections]


@router.get("/sections/{section_id}/students", response_model=List[SectionStudentResponse])
def get_section_students(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_faculty(current_user)
    faculty = _get_faculty_profile(db, current_user.user_id)

    try:
        students = attendance_service.list_section_students(db, section_id, faculty.faculty_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return [attendance_service.serialize_student(student) for student in students]


@router.get("/classrooms", response_model=List[ClassroomResponse])
def get_available_classrooms(db: Session = Depends(get_db)):
    classrooms = attendance_service.list_available_classrooms(db)
    return [attendance_service.serialize_classroom(classroom) for classroom in classrooms]


@router.post("/sessions", response_model=AttendanceSessionResponse)
def create_attendance_session(
    session_data: AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new attendance session (Faculty only)."""

    _require_faculty(current_user)
    faculty = _get_faculty_profile(db, current_user.user_id)

    try:
        session = attendance_service.create_session(db, session_data, faculty.faculty_id)
        return session
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/mark")
def mark_attendance(
    session_id: UUID,
    attendance_data: BulkAttendanceMark,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark attendance for a session and close it (Faculty only)."""

    _require_faculty(current_user)
    faculty = _get_faculty_profile(db, current_user.user_id)

    try:
        return attendance_service.mark_bulk_attendance(
            db=db,
            session_id=session_id,
            attendance_data=attendance_data.attendance_records,
            faculty_id=faculty.faculty_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/student/{student_id}", response_model=List[AttendanceRecordResponse])
def get_student_attendance(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attendance records for a specific student."""

    role = _role_to_str(current_user.role)
    if role == "student":
        try:
            own_student_id = attendance_service.resolve_student_id_for_user(db, current_user.user_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        if own_student_id != student_id:
            raise HTTPException(status_code=403, detail="Students can view only their own attendance")
    elif role not in {"faculty", "admin"}:
        raise HTTPException(status_code=403, detail="Not authorized to view attendance data")

    records = attendance_service.get_student_attendance(db, student_id)
    return records


@router.get("/me/history", response_model=List[AttendanceRecordResponse])
def get_my_attendance_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if _role_to_str(current_user.role) != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can view their own history")

    try:
        student_id = attendance_service.resolve_student_id_for_user(db, current_user.user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return attendance_service.get_student_attendance(db, student_id)
