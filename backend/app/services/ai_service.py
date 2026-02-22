import hashlib
import io
import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ai import StudentFaceProfile
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.course import CourseSection, SectionEnrollment
from app.models.food import FoodOrder
from app.models.student import Student

try:
    import numpy as np
except Exception:  # pragma: no cover - guarded runtime dependency
    np = None

try:
    import face_recognition
except Exception:  # pragma: no cover - optional dependency
    face_recognition = None


ACTIVE_ORDER_STATUSES = {"pending", "confirmed", "ready"}


def _ensure_numpy():
    if np is None:
        raise RuntimeError("numpy is required for AI operations")


def _normalize_embedding(vector: List[float]):
    _ensure_numpy()
    arr = np.asarray(vector, dtype=np.float32)
    if arr.ndim != 1:
        raise ValueError("Embedding vector must be one-dimensional")
    norm = float(np.linalg.norm(arr))
    if norm <= 1e-8:
        raise ValueError("Embedding norm is zero")
    return arr / norm


def _cosine_similarity(vec_a, vec_b) -> float:
    return float(np.dot(vec_a, vec_b))


def _hash_fallback_embedding(image_bytes: bytes):
    _ensure_numpy()
    digest = hashlib.sha256(image_bytes).digest()
    raw = np.frombuffer(digest * 8, dtype=np.uint8)[:128].astype(np.float32)
    normalized = (raw - 127.5) / 127.5
    return _normalize_embedding(normalized.tolist()), "hash-fallback"


def _extract_single_face_embedding(image_bytes: bytes):
    if not face_recognition:
        return _hash_fallback_embedding(image_bytes)

    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_locations = face_recognition.face_locations(image, model="hog")

    if len(face_locations) == 0:
        raise ValueError("No face detected in one of the uploaded images")
    if len(face_locations) > 1:
        raise ValueError("Multiple faces detected in one of the uploaded images")

    encodings = face_recognition.face_encodings(image, face_locations)
    if not encodings:
        raise ValueError("Could not extract face embedding from uploaded image")

    return _normalize_embedding(encodings[0].tolist()), "face-recognition"


def _extract_multi_face_embeddings(image_bytes: bytes):
    if not face_recognition:
        raise RuntimeError(
            "Photo-based multi-face capture requires face_recognition dependency in backend environment"
        )

    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_locations = face_recognition.face_locations(image, model="hog")
    encodings = face_recognition.face_encodings(image, face_locations)
    return [_normalize_embedding(encoding.tolist()) for encoding in encodings]


def enroll_face_profile(
    db: Session,
    student_id: UUID,
    image_samples: List[bytes],
    consent_given: bool,
) -> Dict:
    if not consent_given:
        raise ValueError("Consent is required for biometric enrollment")
    if len(image_samples) < 5 or len(image_samples) > 10:
        raise ValueError("Please upload between 5 and 10 face images")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise LookupError("Student not found")

    embeddings = []
    model_name = "hash-fallback"
    for image_bytes in image_samples:
        embedding, used_model = _extract_single_face_embedding(image_bytes)
        embeddings.append(embedding)
        model_name = used_model

    stacked = np.vstack(embeddings)
    averaged = np.mean(stacked, axis=0)
    normalized = _normalize_embedding(averaged.tolist())
    embedding_json = json.dumps(normalized.tolist())

    profile = db.query(StudentFaceProfile).filter(StudentFaceProfile.student_id == student_id).first()
    if profile is None:
        profile = StudentFaceProfile(student_id=student_id)

    profile.embedding_vector = embedding_json
    profile.model_name = model_name
    profile.sample_count = len(image_samples)
    profile.consent_given = True
    profile.approval_status = "pending"
    profile.reviewed_by = None
    profile.reviewed_at = None
    db.add(profile)

    # Keep backward compatibility with existing student face-encoding field.
    student.face_encoding = embedding_json
    db.add(student)

    db.commit()
    db.refresh(profile)

    return {
        "student_id": student_id,
        "sample_count": profile.sample_count,
        "approval_status": profile.approval_status,
        "consent_given": profile.consent_given,
        "model_name": profile.model_name,
        "updated_at": profile.updated_at,
    }


def list_pending_face_enrollments(db: Session) -> List[Dict]:
    pending_profiles = (
        db.query(StudentFaceProfile)
        .filter(StudentFaceProfile.approval_status == "pending")
        .order_by(StudentFaceProfile.created_at.asc())
        .all()
    )

    student_ids = [profile.student_id for profile in pending_profiles]
    if not student_ids:
        return []

    students = (
        db.query(Student)
        .filter(Student.student_id.in_(student_ids))
        .all()
    )
    by_id = {student.student_id: student for student in students}

    response = []
    for profile in pending_profiles:
        student = by_id.get(profile.student_id)
        if not student:
            continue
        response.append(
            {
                "student_id": profile.student_id,
                "registration_number": student.registration_number,
                "student_name": f"{student.first_name} {student.last_name}",
                "sample_count": profile.sample_count,
                "model_name": profile.model_name,
                "created_at": profile.created_at,
            }
        )
    return response


def review_face_enrollment(
    db: Session,
    student_id: UUID,
    action: str,
    reviewer_user_id: UUID,
) -> Dict:
    profile = db.query(StudentFaceProfile).filter(StudentFaceProfile.student_id == student_id).first()
    if not profile:
        raise LookupError("Face enrollment profile not found")

    if action not in {"approve", "reject"}:
        raise ValueError("Action must be 'approve' or 'reject'")

    profile.approval_status = "approved" if action == "approve" else "rejected"
    profile.reviewed_by = reviewer_user_id
    profile.reviewed_at = datetime.utcnow()
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "student_id": profile.student_id,
        "approval_status": profile.approval_status,
        "reviewed_at": profile.reviewed_at,
    }


def _resolve_profile_embeddings_for_section(
    db: Session, section_id: UUID
) -> Tuple[Dict[UUID, object], Dict[UUID, Student]]:
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
        return {}, {}

    profiles = (
        db.query(StudentFaceProfile)
        .filter(
            StudentFaceProfile.student_id.in_(student_ids),
            StudentFaceProfile.approval_status == "approved",
        )
        .all()
    )
    students = db.query(Student).filter(Student.student_id.in_(student_ids)).all()
    student_map = {student.student_id: student for student in students}

    embeddings = {}
    for profile in profiles:
        try:
            embeddings[profile.student_id] = _normalize_embedding(json.loads(profile.embedding_vector))
        except Exception:
            continue

    return embeddings, student_map


def capture_attendance_from_photo(
    db: Session,
    session_id: UUID,
    faculty_id: UUID,
    image_bytes: bytes,
    confidence_threshold: float = 0.75,
    late_threshold_minutes: int = 10,
    captured_at: Optional[datetime] = None,
) -> Dict:
    session = db.query(AttendanceSession).filter(AttendanceSession.session_id == session_id).first()
    if not session:
        raise LookupError("Attendance session not found")
    if session.marked_by != faculty_id:
        raise PermissionError("Faculty can run AI capture only for own sessions")
    if session.is_closed:
        raise ValueError("Attendance session is already closed")

    detected_embeddings = _extract_multi_face_embeddings(image_bytes)
    profile_embeddings, student_map = _resolve_profile_embeddings_for_section(db, session.section_id)

    if not student_map:
        raise ValueError("No active students enrolled in this section")
    if not profile_embeddings:
        raise ValueError("No approved face profiles found for enrolled students")

    best_match_for_student: Dict[UUID, Dict] = {}
    proxy_alerts = 0

    for detected in detected_embeddings:
        best_student_id = None
        best_similarity = -1.0

        for student_id, profile_embedding in profile_embeddings.items():
            similarity = _cosine_similarity(detected, profile_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_student_id = student_id

        if best_student_id is None or best_similarity < confidence_threshold:
            continue

        existing = best_match_for_student.get(best_student_id)
        if existing and best_similarity <= existing["similarity"]:
            proxy_alerts += 1
            continue
        if existing and best_similarity > existing["similarity"]:
            proxy_alerts += 1

        best_match_for_student[best_student_id] = {"similarity": best_similarity}

    now = captured_at or datetime.utcnow()
    late_cutoff = session.start_time + timedelta(minutes=late_threshold_minutes)
    late_detections = len(best_match_for_student) if now > late_cutoff else 0

    enrolled_ids = list(student_map.keys())
    existing_records = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.session_id == session_id)
        .all()
    )
    records_by_student = {record.student_id: record for record in existing_records}

    present_count = 0
    absent_count = 0
    confidence_values = []
    matched_registration_numbers = []

    for student_id in enrolled_ids:
        matched = best_match_for_student.get(student_id)
        status = "present" if matched else "absent"
        confidence = matched["similarity"] if matched else None

        if status == "present":
            present_count += 1
            confidence_values.append(confidence)
            student = student_map.get(student_id)
            if student:
                matched_registration_numbers.append(student.registration_number)
        else:
            absent_count += 1

        existing = records_by_student.get(student_id)
        if existing:
            existing.status = status
            existing.marked_at = now
            existing.marked_by = f"{faculty_id}:ai_face"
            existing.confidence_score = confidence
            db.add(existing)
        else:
            db.add(
                AttendanceRecord(
                    session_id=session_id,
                    student_id=student_id,
                    status=status,
                    marked_at=now,
                    marked_by=f"{faculty_id}:ai_face",
                    confidence_score=confidence,
                )
            )

    session.session_type = "ai_face"
    session.present_count = present_count
    session.absent_count = absent_count
    session.total_students = len(enrolled_ids)
    session.is_closed = True
    session.end_time = now
    db.add(session)
    db.commit()

    ai_accuracy = 0.0
    if confidence_values:
        ai_accuracy = round(float(sum(confidence_values) / len(confidence_values) * 100), 2)

    return {
        "message": "AI attendance capture completed",
        "total_faces_detected": len(detected_embeddings),
        "matched_students": len(best_match_for_student),
        "late_detections": late_detections,
        "proxy_detection_alerts": proxy_alerts,
        "ai_attendance_accuracy_percent": ai_accuracy,
        "present_count": present_count,
        "absent_count": absent_count,
        "matched_registration_numbers": matched_registration_numbers,
    }


def get_faculty_attendance_ai_insights(
    db: Session,
    faculty_id: UUID,
    low_attendance_threshold: float = 75.0,
) -> Dict:
    sections = (
        db.query(CourseSection)
        .filter(CourseSection.faculty_id == faculty_id)
        .all()
    )
    section_ids = [section.section_id for section in sections]
    if not section_ids:
        return {
            "ai_attendance_accuracy_percent": 0.0,
            "proxy_detection_alerts": 0,
            "ai_sessions_count": 0,
            "trend_graph": [],
            "risk_students": [],
        }

    ai_sessions = (
        db.query(AttendanceSession)
        .filter(
            AttendanceSession.section_id.in_(section_ids),
            AttendanceSession.session_type == "ai_face",
        )
        .order_by(AttendanceSession.session_date.desc())
        .all()
    )
    ai_session_ids = [session.session_id for session in ai_sessions]

    ai_records = []
    if ai_session_ids:
        ai_records = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id.in_(ai_session_ids),
                AttendanceRecord.confidence_score.isnot(None),
            )
            .all()
        )

    confidence_values = [record.confidence_score for record in ai_records if record.confidence_score is not None]
    ai_accuracy = round(float(sum(confidence_values) / len(confidence_values) * 100), 2) if confidence_values else 0.0
    proxy_alerts = len([value for value in confidence_values if value < 0.65])

    recent_sessions = (
        db.query(AttendanceSession)
        .filter(AttendanceSession.section_id.in_(section_ids))
        .order_by(AttendanceSession.session_date.desc())
        .limit(14)
        .all()
    )
    trend_graph = []
    for session in recent_sessions[:7]:
        total_students = session.total_students or 0
        present_rate = round((session.present_count / total_students) * 100, 2) if total_students else 0.0
        trend_graph.append(
            {
                "date": session.session_date.isoformat(),
                "present_rate": present_rate,
                "total_students": total_students,
            }
        )
    trend_graph.reverse()

    enrollments = (
        db.query(SectionEnrollment)
        .filter(
            SectionEnrollment.section_id.in_(section_ids),
            SectionEnrollment.status == "active",
        )
        .all()
    )
    student_ids = sorted({enrollment.student_id for enrollment in enrollments})

    risk_students = []
    if student_ids:
        recent_window = datetime.utcnow() - timedelta(days=60)
        records = (
            db.query(AttendanceRecord)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.session_id)
            .filter(
                AttendanceSession.section_id.in_(section_ids),
                AttendanceRecord.student_id.in_(student_ids),
                AttendanceRecord.marked_at >= recent_window,
            )
            .all()
        )

        totals = defaultdict(int)
        presents = defaultdict(int)
        for record in records:
            totals[record.student_id] += 1
            if record.status == "present":
                presents[record.student_id] += 1

        students = db.query(Student).filter(Student.student_id.in_(student_ids)).all()
        by_student = {student.student_id: student for student in students}

        for student_id in student_ids:
            total = totals.get(student_id, 0)
            if total == 0:
                continue

            attendance_percent = round((presents.get(student_id, 0) / total) * 100, 2)
            if attendance_percent >= low_attendance_threshold:
                continue

            gap = max(0.0, low_attendance_threshold - attendance_percent)
            dropout_risk = round(min(99.0, gap * 1.8 + 10), 2)
            student = by_student.get(student_id)
            if not student:
                continue
            risk_students.append(
                {
                    "student_id": student_id,
                    "registration_number": student.registration_number,
                    "name": f"{student.first_name} {student.last_name}",
                    "attendance_percent": attendance_percent,
                    "dropout_risk_percent": dropout_risk,
                }
            )

    risk_students.sort(key=lambda item: item["attendance_percent"])

    return {
        "ai_attendance_accuracy_percent": ai_accuracy,
        "proxy_detection_alerts": proxy_alerts,
        "ai_sessions_count": len(ai_sessions),
        "trend_graph": trend_graph,
        "risk_students": risk_students[:8],
    }


def _classify_rush_level(rush_score: float, active_orders: int) -> str:
    if rush_score >= 18 or active_orders >= 20:
        return "high"
    if rush_score >= 8 or active_orders >= 8:
        return "moderate"
    return "low"


def _build_suggestions(level: str) -> List[str]:
    if level == "high":
        return [
            "Order 15-20 minutes earlier to avoid queues.",
            "Try alternate vendors with lower active order load.",
            "Vendors should pre-start high-demand menu items.",
        ]
    if level == "moderate":
        return [
            "Order a little early for shorter wait.",
            "Prefer fast-prep items during peak half-hours.",
            "Vendors should keep moderate buffer stock ready.",
        ]
    return [
        "Low rush window detected, ideal time to place orders.",
        "Vendors can use this time for prep/reset activities.",
        "Students can expect near-immediate pickup flow.",
    ]


def predict_food_rush(db: Session, vendor_id: Optional[UUID] = None) -> Dict:
    now = datetime.utcnow()
    today = now.date()
    today_query = db.query(FoodOrder).filter(FoodOrder.order_date == today)
    if vendor_id:
        today_query = today_query.filter(FoodOrder.vendor_id == vendor_id)
    today_orders = today_query.all()

    active_orders = len([order for order in today_orders if order.status in ACTIVE_ORDER_STATUSES])
    last_30_min = now - timedelta(minutes=30)
    order_velocity = len([order for order in today_orders if order.order_time and order.order_time >= last_30_min])

    history_from = today - timedelta(days=14)
    history_query = (
        db.query(FoodOrder)
        .filter(FoodOrder.order_date >= history_from, FoodOrder.order_date < today)
    )
    if vendor_id:
        history_query = history_query.filter(FoodOrder.vendor_id == vendor_id)
    historical_orders = history_query.all()

    same_hour_counts = defaultdict(int)
    for order in historical_orders:
        if order.order_time and order.order_time.hour == now.hour:
            same_hour_counts[order.order_date] += 1
    historical_peak_similarity = (
        sum(same_hour_counts.values()) / len(same_hour_counts) if same_hour_counts else 0.0
    )

    rush_score = round(
        (order_velocity * 0.55) + (historical_peak_similarity * 0.25) + (active_orders * 0.35),
        2,
    )
    level = _classify_rush_level(rush_score, active_orders)

    if level == "high":
        predicted_wait = max(15, 12 + active_orders // 2)
    elif level == "moderate":
        predicted_wait = max(6, 5 + active_orders // 3)
    else:
        predicted_wait = max(2, 2 + active_orders // 6)

    next_hour_demand = int(max(5, (order_velocity * 2.0), (historical_peak_similarity * 1.2)))
    suggested_prep_qty = int(max(5, next_hour_demand * (1.25 if level == "high" else 1.1)))

    hourly_counts = defaultdict(int)
    for order in today_orders:
        if order.order_time:
            hourly_counts[order.order_time.hour] += 1

    peak_hour = now.hour
    if hourly_counts:
        peak_hour = max(hourly_counts.keys(), key=lambda hour: hourly_counts[hour])

    order_load_graph = []
    for hour_delta in range(7, -1, -1):
        hour_value = (now - timedelta(hours=hour_delta)).hour
        order_load_graph.append({"hour": f"{hour_value:02d}:00", "orders": hourly_counts.get(hour_value, 0)})

    recommended_time = (now + timedelta(minutes=max(0, predicted_wait - 5))).strftime("%H:%M")

    return {
        "level": level,
        "predicted_wait_minutes": int(predicted_wait),
        "recommended_order_time": recommended_time,
        "peak_expected_at": f"{peak_hour:02d}:15",
        "expected_peak_window": f"{peak_hour:02d}:00-{peak_hour:02d}:30",
        "next_hour_demand": int(next_hour_demand),
        "suggested_prep_quantity": int(suggested_prep_qty),
        "rush_score": rush_score,
        "active_orders": active_orders,
        "order_velocity_30m": order_velocity,
        "order_load_graph": order_load_graph,
        "suggestions": _build_suggestions(level),
    }
