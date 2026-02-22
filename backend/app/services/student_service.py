from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.student import StudentCreate, StudentUpdate


def serialize_student(student: Student) -> dict:
    return {
        "student_id": student.student_id,
        "user_id": student.user_id,
        "registration_number": student.registration_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "phone": student.phone,
        "parent_email": student.parent_email,
        "parent_phone": student.parent_phone,
        "program": student.program,
        "semester": student.semester,
        "section": student.section,
        "enrollment_year": student.enrollment_year,
        "email": student.user.email if student.user else None,
        "created_at": student.created_at,
    }


def list_students(
    db: Session,
    search: Optional[str] = None,
    section: Optional[str] = None,
    semester: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Student]:
    query = db.query(Student).join(User, Student.user_id == User.user_id)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.registration_number.ilike(pattern),
                Student.first_name.ilike(pattern),
                Student.last_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )

    if section:
        query = query.filter(Student.section == section.strip())

    if semester is not None:
        query = query.filter(Student.semester == semester)

    return (
        query.order_by(Student.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_student(db: Session, student_id: UUID) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise LookupError("Student not found")
    return student


def create_student(db: Session, student_data: StudentCreate) -> Student:
    payload = student_data.model_dump()
    email = str(payload["email"]).lower().strip()
    registration_number = payload["registration_number"].strip()
    firebase_uid = payload.get("firebase_uid")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("Email already registered")

    existing_student = (
        db.query(Student)
        .filter(Student.registration_number == registration_number)
        .first()
    )
    if existing_student:
        raise ValueError("Registration number already exists")

    if firebase_uid:
        existing_firebase_uid = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if existing_firebase_uid:
            raise ValueError("Firebase UID already linked to another account")

    try:
        new_user = User(
            email=email,
            role=UserRole.STUDENT,
            firebase_uid=firebase_uid,
        )
        db.add(new_user)
        db.flush()

        new_student = Student(
            user_id=new_user.user_id,
            registration_number=registration_number,
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            phone=payload.get("phone"),
            parent_email=payload.get("parent_email"),
            parent_phone=payload.get("parent_phone"),
            program=payload.get("program"),
            semester=payload.get("semester"),
            section=payload.get("section"),
            enrollment_year=payload["enrollment_year"],
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except Exception:
        db.rollback()
        raise


def update_student(db: Session, student_id: UUID, student_data: StudentUpdate) -> Student:
    student = get_student(db, student_id)
    update_payload = student_data.model_dump(exclude_unset=True)

    if not update_payload:
        raise ValueError("No fields provided for update")

    if "registration_number" in update_payload:
        registration_number = update_payload["registration_number"].strip()
        existing_student = (
            db.query(Student)
            .filter(
                Student.registration_number == registration_number,
                Student.student_id != student_id,
            )
            .first()
        )
        if existing_student:
            raise ValueError("Registration number already exists")
        update_payload["registration_number"] = registration_number

    if "email" in update_payload:
        email = str(update_payload["email"]).lower().strip()
        existing_user = (
            db.query(User)
            .filter(User.email == email, User.user_id != student.user_id)
            .first()
        )
        if existing_user:
            raise ValueError("Email already registered")
        if student.user:
            student.user.email = email
        update_payload.pop("email")

    if "firebase_uid" in update_payload:
        firebase_uid = update_payload["firebase_uid"]
        if student.user:
            if firebase_uid:
                existing_firebase_uid = (
                    db.query(User)
                    .filter(User.firebase_uid == firebase_uid, User.user_id != student.user_id)
                    .first()
                )
                if existing_firebase_uid:
                    raise ValueError("Firebase UID already linked to another account")
            student.user.firebase_uid = firebase_uid
        update_payload.pop("firebase_uid")

    for key, value in update_payload.items():
        setattr(student, key, value)

    try:
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    except Exception:
        db.rollback()
        raise
