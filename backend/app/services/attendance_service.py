from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.course import CourseSection, SectionEnrollment
from app.models.resource import Classroom
from app.models.student import Student
from app.schemas.attendance import AttendanceRecordCreate, AttendanceSessionCreate


def _get_section(db: Session, section_id: UUID) -> CourseSection:
    section = db.query(CourseSection).filter(CourseSection.section_id == section_id).first()
    if not section:
        raise LookupError("Section not found")
    return section


def _get_classroom(db: Session, classroom_id: UUID) -> Classroom:
    classroom = (
        db.query(Classroom)
        .filter(Classroom.classroom_id == classroom_id, Classroom.is_available.is_(True))
        .first()
    )
    if not classroom:
        raise LookupError("Classroom not found")
    return classroom


def get_faculty_sections(db: Session, faculty_id: UUID) -> List[CourseSection]:
    return (
        db.query(CourseSection)
        .filter(CourseSection.faculty_id == faculty_id)
        .order_by(CourseSection.created_at.desc())
        .all()
    )


def serialize_section(section: CourseSection) -> dict:
    return {
        "section_id": section.section_id,
        "section_name": section.section_name,
        "course_id": section.course_id,
        "course_code": section.course.course_code if section.course else None,
        "course_name": section.course.course_name if section.course else None,
        "academic_year": section.academic_year,
        "semester": section.semester,
    }


def list_section_students(db: Session, section_id: UUID, faculty_id: UUID) -> List[Student]:
    section = _get_section(db, section_id)
    if section.faculty_id != faculty_id:
        raise PermissionError("Faculty can access only their assigned sections")

    enrollments = (
        db.query(SectionEnrollment)
        .filter(
            SectionEnrollment.section_id == section_id,
            SectionEnrollment.status == "active",
        )
        .all()
    )
    student_ids = [enrollment.student_id for enrollment in enrollments]
    if not student_ids:
        return []

    return (
        db.query(Student)
        .filter(Student.student_id.in_(student_ids))
        .order_by(Student.registration_number.asc())
        .all()
    )


def serialize_student(student: Student) -> dict:
    return {
        "student_id": student.student_id,
        "registration_number": student.registration_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "section": student.section,
        "semester": student.semester,
        "phone": student.phone,
        "parent_phone": student.parent_phone,
    }


def list_available_classrooms(db: Session) -> List[Classroom]:
    return (
        db.query(Classroom)
        .filter(Classroom.is_available.is_(True))
        .order_by(Classroom.room_number.asc())
        .all()
    )


def serialize_classroom(classroom: Classroom) -> dict:
    return {
        "classroom_id": classroom.classroom_id,
        "room_number": classroom.room_number,
        "block_code": classroom.block.block_code if classroom.block else None,
        "block_name": classroom.block.block_name if classroom.block else None,
        "capacity": classroom.capacity,
    }


def create_session(db: Session, session_data: AttendanceSessionCreate, faculty_id: UUID) -> AttendanceSession:
    section = _get_section(db, session_data.section_id)
    if section.faculty_id != faculty_id:
        raise PermissionError("Faculty can create sessions only for assigned sections")

    if session_data.classroom_id:
        _get_classroom(db, session_data.classroom_id)

    existing = (
        db.query(AttendanceSession)
        .filter(
            AttendanceSession.section_id == session_data.section_id,
            AttendanceSession.session_date == session_data.session_date,
            AttendanceSession.is_closed.is_(False),
        )
        .first()
    )
    if existing:
        raise ValueError("An open attendance session already exists for this section/date")

    total_students = (
        db.query(SectionEnrollment)
        .filter(
            SectionEnrollment.section_id == session_data.section_id,
            SectionEnrollment.status == "active",
        )
        .count()
    )

    try:
        new_session = AttendanceSession(
            section_id=session_data.section_id,
            classroom_id=session_data.classroom_id,
            session_date=session_data.session_date,
            start_time=datetime.utcnow(),
            marked_by=faculty_id,
            total_students=total_students,
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session
    except Exception:
        db.rollback()
        raise


def _validate_session_access(session: AttendanceSession, faculty_id: UUID):
    if session.marked_by != faculty_id:
        raise PermissionError("Faculty can mark only their own sessions")


def mark_bulk_attendance(
    db: Session,
    session_id: UUID,
    attendance_data: List[AttendanceRecordCreate],
    faculty_id: UUID,
) -> Dict:
    session = db.query(AttendanceSession).filter(AttendanceSession.session_id == session_id).first()
    if not session:
        raise LookupError("Session not found")

    _validate_session_access(session, faculty_id)
    if session.is_closed:
        raise ValueError("Attendance session is already closed")

    enrolled_student_ids = {
        enrollment.student_id
        for enrollment in db.query(SectionEnrollment)
        .filter(
            SectionEnrollment.section_id == session.section_id,
            SectionEnrollment.status == "active",
        )
        .all()
    }
    if not enrolled_student_ids:
        raise ValueError("No active students enrolled in this section")

    submitted_student_ids = {record.student_id for record in attendance_data}
    invalid_student_ids = [student_id for student_id in submitted_student_ids if student_id not in enrolled_student_ids]
    if invalid_student_ids:
        raise ValueError("Attendance payload includes students not enrolled in this section")

    existing_records = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.session_id == session_id)
        .all()
    )
    existing_by_student = {record.student_id: record for record in existing_records}

    present_count = 0
    absent_count = 0
    absent_student_ids = []

    try:
        for record_data in attendance_data:
            existing_record = existing_by_student.get(record_data.student_id)
            if existing_record:
                existing_record.status = record_data.status
                existing_record.marked_at = datetime.utcnow()
                existing_record.marked_by = str(faculty_id)
                target_record = existing_record
            else:
                target_record = AttendanceRecord(
                    session_id=session_id,
                    student_id=record_data.student_id,
                    status=record_data.status,
                    marked_at=datetime.utcnow(),
                    marked_by=str(faculty_id),
                )
                db.add(target_record)

            if target_record.status == "present":
                present_count += 1
            else:
                absent_count += 1
                absent_student_ids.append(record_data.student_id)

        session.present_count = present_count
        session.absent_count = absent_count
        session.total_students = len(enrolled_student_ids)
        session.is_closed = True
        session.end_time = datetime.utcnow()
        db.add(session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    absent_students = []
    if absent_student_ids:
        students = db.query(Student).filter(Student.student_id.in_(absent_student_ids)).all()
        absent_students = [
            {
                "name": f"{student.first_name} {student.last_name}",
                "reg_no": student.registration_number,
            }
            for student in students
        ]

    notification_result = {
        "student_sms": absent_count,
        "parent_sms": absent_count,
        "student_emails": absent_count,
        "parent_emails": absent_count,
        "absentees": absent_students,
    }

    return {
        "message": "Attendance marked successfully",
        "notifications": notification_result,
        "present_count": present_count,
        "absent_count": absent_count,
    }


def get_student_attendance(db: Session, student_id: UUID) -> List[AttendanceRecord]:
    return (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.student_id == student_id)
        .order_by(AttendanceRecord.marked_at.desc())
        .all()
    )


def resolve_student_id_for_user(db: Session, user_id: UUID) -> UUID:
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise LookupError("Student profile not found")
    return student.student_id
