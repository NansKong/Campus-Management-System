from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.user import User
from app.schemas.remedial import (
    MarkRemedialAttendance,
    RemedialAttendanceHistoryResponse,
    RemedialClassCreate,
    RemedialClassResponse,
    RemedialClassUpdate,
)
from app.services import remedial_service
from app.utils.auth import get_current_user

router = APIRouter()


def _role_to_str(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _require_management_role(current_user: User) -> str:
    role = _role_to_str(current_user.role)
    if role not in {"admin", "faculty"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or faculty can manage remedial classes",
        )
    return role


def _get_faculty_profile(db: Session, user_id: UUID) -> Faculty:
    faculty = db.query(Faculty).filter(Faculty.user_id == user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    return faculty


@router.post("/classes", response_model=RemedialClassResponse, status_code=201)
def create_remedial_class(
    remedial_data: RemedialClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a remedial class (Faculty only)."""

    role = _role_to_str(current_user.role)
    if role != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty can schedule remedial classes")

    faculty = _get_faculty_profile(db, current_user.user_id)

    try:
        remedial = remedial_service.create_remedial_class(db, remedial_data, faculty.faculty_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return remedial


@router.get("/classes", response_model=List[RemedialClassResponse])
def list_remedial_classes(
    faculty_id: Optional[UUID] = Query(default=None),
    section_id: Optional[UUID] = Query(default=None),
    scheduled_date: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_management_role(current_user)

    if role == "faculty":
        faculty = _get_faculty_profile(db, current_user.user_id)
        faculty_id = faculty.faculty_id

    return remedial_service.list_remedial_classes(
        db=db,
        faculty_id=faculty_id,
        section_id=section_id,
        scheduled_date=scheduled_date,
        limit=limit,
        offset=offset,
    )


@router.get("/classes/{remedial_id}", response_model=RemedialClassResponse)
def get_remedial_class(
    remedial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_management_role(current_user)

    try:
        remedial = remedial_service.get_remedial_class(db, remedial_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if role == "faculty":
        faculty = _get_faculty_profile(db, current_user.user_id)
        if remedial.faculty_id != faculty.faculty_id:
            raise HTTPException(status_code=403, detail="Faculty can only access their own remedial classes")

    return remedial


@router.put("/classes/{remedial_id}", response_model=RemedialClassResponse)
def update_remedial_class(
    remedial_id: UUID,
    remedial_data: RemedialClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_management_role(current_user)

    actor_faculty_id = None
    if role == "faculty":
        faculty = _get_faculty_profile(db, current_user.user_id)
        actor_faculty_id = faculty.faculty_id

    try:
        return remedial_service.update_remedial_class(
            db=db,
            remedial_id=remedial_id,
            remedial_data=remedial_data,
            actor_role=role,
            actor_faculty_id=actor_faculty_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/attendance/mark")
def mark_remedial_attendance(
    attendance_data: MarkRemedialAttendance,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark attendance for remedial class using code."""

    role = _role_to_str(current_user.role)
    if role != "student":
        raise HTTPException(status_code=403, detail="Only students can mark attendance")

    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    result = remedial_service.mark_remedial_attendance(
        db,
        student.student_id,
        attendance_data.remedial_code,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/attendance/my-history", response_model=List[RemedialAttendanceHistoryResponse])
def get_my_remedial_attendance_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _role_to_str(current_user.role)
    if role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their remedial attendance history")

    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return remedial_service.get_student_remedial_attendance(db, student.student_id)
