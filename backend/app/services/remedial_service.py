from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime, timedelta
from app.models.course import CourseSection, SectionEnrollment
from app.models.remedial import RemedialClass, RemedialAttendance
from app.models.resource import Classroom
from app.schemas.remedial import RemedialClassCreate, RemedialClassUpdate
from app.utils.helpers import generate_unique_code, is_code_expired

def _ensure_valid_time_window(start_time, end_time):
    if end_time <= start_time:
        raise ValueError("End time must be later than start time")


def _compute_code_expiry(scheduled_date, end_time):
    end_datetime = datetime.combine(scheduled_date, end_time)
    return end_datetime + timedelta(minutes=30)


def create_remedial_class(db: Session, remedial_data: RemedialClassCreate, faculty_id: UUID):
    """Create a new remedial class"""
    _ensure_valid_time_window(remedial_data.start_time, remedial_data.end_time)

    section = db.query(CourseSection).filter(CourseSection.section_id == remedial_data.section_id).first()
    if not section:
        raise LookupError("Section not found")
    if section.faculty_id != faculty_id:
        raise PermissionError("Faculty can create remedial classes only for assigned sections")

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.classroom_id == remedial_data.classroom_id,
            Classroom.is_available == True,
        )
        .first()
    )
    if not classroom:
        raise LookupError("Classroom not found")

    # Generate unique code
    remedial_code = generate_unique_code(6)
    
    # While loop to ensure code is unique
    while db.query(RemedialClass).filter(RemedialClass.remedial_code == remedial_code).first():
        remedial_code = generate_unique_code(6)
    
    # Calculate expiry time (30 minutes after end time)
    expiry_time = _compute_code_expiry(remedial_data.scheduled_date, remedial_data.end_time)
    
    # Create remedial class
    new_remedial = RemedialClass(
        section_id=remedial_data.section_id,
        faculty_id=faculty_id,
        classroom_id=remedial_data.classroom_id,
        scheduled_date=remedial_data.scheduled_date,
        start_time=remedial_data.start_time,
        end_time=remedial_data.end_time,
        remedial_code=remedial_code,
        reason=remedial_data.reason,
        code_expires_at=expiry_time
    )
    
    try:
        db.add(new_remedial)
        db.commit()
        db.refresh(new_remedial)
        return new_remedial
    except Exception:
        db.rollback()
        raise


def list_remedial_classes(
    db: Session,
    faculty_id: Optional[UUID] = None,
    section_id: Optional[UUID] = None,
    scheduled_date: Optional[date] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[RemedialClass]:
    query = db.query(RemedialClass)

    if faculty_id:
        query = query.filter(RemedialClass.faculty_id == faculty_id)

    if section_id:
        query = query.filter(RemedialClass.section_id == section_id)

    if scheduled_date:
        query = query.filter(RemedialClass.scheduled_date == scheduled_date)

    return (
        query.order_by(RemedialClass.scheduled_date.desc(), RemedialClass.start_time.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_remedial_class(db: Session, remedial_id: UUID) -> RemedialClass:
    remedial = db.query(RemedialClass).filter(RemedialClass.remedial_id == remedial_id).first()
    if not remedial:
        raise LookupError("Remedial class not found")
    return remedial


def update_remedial_class(
    db: Session,
    remedial_id: UUID,
    remedial_data: RemedialClassUpdate,
    actor_role: str,
    actor_faculty_id: Optional[UUID],
) -> RemedialClass:
    remedial = get_remedial_class(db, remedial_id)
    payload = remedial_data.model_dump(exclude_unset=True)

    if not payload:
        raise ValueError("No fields provided for update")

    if actor_role == "faculty" and actor_faculty_id != remedial.faculty_id:
        raise PermissionError("Faculty can only update their own remedial classes")

    next_start = payload.get("start_time", remedial.start_time)
    next_end = payload.get("end_time", remedial.end_time)
    _ensure_valid_time_window(next_start, next_end)

    for key, value in payload.items():
        setattr(remedial, key, value)

    if "scheduled_date" in payload or "end_time" in payload:
        remedial.code_expires_at = _compute_code_expiry(remedial.scheduled_date, remedial.end_time)

    try:
        db.add(remedial)
        db.commit()
        db.refresh(remedial)
        return remedial
    except Exception:
        db.rollback()
        raise

def mark_remedial_attendance(db: Session, student_id: UUID, code: str):
    """Mark attendance using remedial code"""
    
    # Find remedial class by code
    remedial = db.query(RemedialClass).filter(
        RemedialClass.remedial_code == code,
        RemedialClass.is_active == True
    ).first()
    
    if not remedial:
        return {"error": "Invalid code"}
    
    # Check if expired
    if is_code_expired(remedial.code_expires_at):
        return {"error": "Code has expired"}
    
    # Check if already marked
    existing = db.query(RemedialAttendance).filter(
        RemedialAttendance.remedial_id == remedial.remedial_id,
        RemedialAttendance.student_id == student_id
    ).first()
    
    if existing:
        return {"error": "Attendance already marked"}

    # Student must be actively enrolled in the remedial section
    enrollment = (
        db.query(SectionEnrollment)
        .filter(
            SectionEnrollment.section_id == remedial.section_id,
            SectionEnrollment.student_id == student_id,
            SectionEnrollment.status == "active",
        )
        .first()
    )
    if not enrollment:
        return {"error": "Student is not enrolled in this section"}
    
    # Mark attendance
    attendance = RemedialAttendance(
        remedial_id=remedial.remedial_id,
        student_id=student_id,
        code_used=code
    )
    
    db.add(attendance)
    db.commit()
    
    return {"success": True, "message": "Attendance marked successfully"}


def get_student_remedial_attendance(db: Session, student_id: UUID) -> List[RemedialAttendance]:
    return (
        db.query(RemedialAttendance)
        .filter(RemedialAttendance.student_id == student_id)
        .order_by(RemedialAttendance.marked_at.desc())
        .all()
    )
