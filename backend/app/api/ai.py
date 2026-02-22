from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.faculty import Faculty
from app.models.user import User
from app.schemas.ai import (
    AIAttendanceCaptureResponse,
    AIAttendanceStreamResponse,
    AIAttendanceStreamStartRequest,
    FaceEnrollmentResponse,
    FaceEnrollmentReviewRequest,
    FacultyAIAttendanceInsightsResponse,
    FoodRushPredictionResponse,
    PendingFaceEnrollmentItem,
)
from app.services import ai_service, attendance_service, food_service
from app.services.ai_stream_service import ai_stream_manager
from app.utils.auth import get_current_user

router = APIRouter()


def _role_to_str(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _require_roles(current_user: User, allowed: set[str]) -> str:
    role = _role_to_str(current_user.role)
    if role not in allowed:
        raise HTTPException(status_code=403, detail="Not authorized for this AI workflow")
    return role


def _resolve_faculty_id(db: Session, current_user: User) -> UUID:
    faculty = db.query(Faculty).filter(Faculty.user_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    return faculty.faculty_id


@router.post("/attendance/enroll", response_model=FaceEnrollmentResponse)
async def enroll_face_profile(
    files: List[UploadFile] = File(...),
    consent_given: bool = Form(...),
    student_id: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_roles(current_user, {"student", "faculty", "admin"})

    if role == "student":
        try:
            target_student_id = attendance_service.resolve_student_id_for_user(db, current_user.user_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    else:
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id is required for faculty/admin enrollment")
        try:
            target_student_id = UUID(student_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid student_id format") from exc

    image_samples = []
    for upload in files:
        content = await upload.read()
        if content:
            image_samples.append(content)

    try:
        return ai_service.enroll_face_profile(
            db=db,
            student_id=target_student_id,
            image_samples=image_samples,
            consent_given=consent_given,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/attendance/enrollments/pending", response_model=List[PendingFaceEnrollmentItem])
def get_pending_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, {"admin"})
    return ai_service.list_pending_face_enrollments(db)


@router.post("/attendance/enrollments/{student_id}/review")
def review_enrollment(
    student_id: UUID,
    review_payload: FaceEnrollmentReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, {"admin"})
    try:
        return ai_service.review_face_enrollment(
            db=db,
            student_id=student_id,
            action=review_payload.action,
            reviewer_user_id=current_user.user_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/attendance/sessions/{session_id}/capture-photo", response_model=AIAttendanceCaptureResponse)
async def capture_attendance_photo(
    session_id: UUID,
    image_file: UploadFile = File(...),
    confidence_threshold: float = Form(default=0.75),
    late_threshold_minutes: int = Form(default=10),
    captured_at: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, {"faculty"})
    faculty_id = _resolve_faculty_id(db, current_user)

    image_bytes = await image_file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image file is empty")

    parsed_capture_time = None
    if captured_at:
        try:
            parsed_capture_time = datetime.fromisoformat(captured_at)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid captured_at datetime format") from exc

    try:
        return ai_service.capture_attendance_from_photo(
            db=db,
            session_id=session_id,
            faculty_id=faculty_id,
            image_bytes=image_bytes,
            confidence_threshold=confidence_threshold,
            late_threshold_minutes=late_threshold_minutes,
            captured_at=parsed_capture_time,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/attendance/stream/start", response_model=AIAttendanceStreamResponse)
async def start_attendance_stream(
    payload: AIAttendanceStreamStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, {"faculty"})
    faculty_id = _resolve_faculty_id(db, current_user)

    try:
        return await ai_stream_manager.start_stream(
            session_id=payload.session_id,
            faculty_id=faculty_id,
            source_url=payload.source_url,
            confidence_threshold=payload.confidence_threshold,
            late_threshold_minutes=payload.late_threshold_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/attendance/stream/{stream_id}/stop", response_model=AIAttendanceStreamResponse)
async def stop_attendance_stream(
    stream_id: UUID,
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, {"faculty", "admin"})
    try:
        return await ai_stream_manager.stop_stream(stream_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/attendance/stream/{stream_id}", response_model=AIAttendanceStreamResponse)
async def get_attendance_stream_status(
    stream_id: UUID,
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, {"faculty", "admin"})
    try:
        return await ai_stream_manager.get_stream_status(stream_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/attendance/faculty-insights", response_model=FacultyAIAttendanceInsightsResponse)
def get_faculty_insights(
    faculty_id: Optional[str] = Query(default=None),
    threshold: float = Query(default=75.0, ge=40.0, le=95.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_roles(current_user, {"faculty", "admin"})

    if role == "faculty":
        target_faculty_id = _resolve_faculty_id(db, current_user)
    else:
        if not faculty_id:
            raise HTTPException(status_code=400, detail="faculty_id is required for admin insights view")
        try:
            target_faculty_id = UUID(faculty_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid faculty_id format") from exc

    return ai_service.get_faculty_attendance_ai_insights(
        db=db,
        faculty_id=target_faculty_id,
        low_attendance_threshold=threshold,
    )


@router.get("/food/rush", response_model=FoodRushPredictionResponse)
def get_food_rush_prediction(
    vendor_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_roles(current_user, {"student", "vendor", "admin"})

    parsed_vendor_id = None
    if role == "vendor":
        vendor = food_service.get_vendor_for_user(db, current_user.user_id)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")
        parsed_vendor_id = vendor.vendor_id
    elif vendor_id:
        try:
            parsed_vendor_id = UUID(vendor_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid vendor_id format") from exc

    return ai_service.predict_food_rush(db=db, vendor_id=parsed_vendor_id)
