from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services import student_service
from app.utils.auth import get_current_user

router = APIRouter()

ALLOWED_MANAGEMENT_ROLES = {"admin", "faculty"}


def _role_to_str(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _ensure_management_access(current_user: User) -> None:
    if _role_to_str(current_user.role) not in ALLOWED_MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or faculty can manage student records",
        )


@router.get("", response_model=List[StudentResponse])
def list_students(
    search: Optional[str] = Query(default=None, max_length=100),
    section: Optional[str] = Query(default=None, max_length=20),
    semester: Optional[int] = Query(default=None, ge=1, le=12),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_management_access(current_user)

    students = student_service.list_students(
        db=db,
        search=search,
        section=section,
        semester=semester,
        limit=limit,
        offset=offset,
    )
    return [student_service.serialize_student(student) for student in students]


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_management_access(current_user)

    try:
        student = student_service.get_student(db, student_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return student_service.serialize_student(student)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_management_access(current_user)

    try:
        student = student_service.create_student(db, student_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return student_service.serialize_student(student)


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: UUID,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_management_access(current_user)

    try:
        student = student_service.update_student(db, student_id, student_data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return student_service.serialize_student(student)
