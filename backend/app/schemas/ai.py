from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class FaceEnrollmentResponse(BaseModel):
    student_id: UUID
    sample_count: int
    approval_status: str
    consent_given: bool
    model_name: str
    updated_at: datetime


class PendingFaceEnrollmentItem(BaseModel):
    student_id: UUID
    registration_number: str
    student_name: str
    sample_count: int
    model_name: str
    created_at: datetime


class FaceEnrollmentReviewRequest(BaseModel):
    action: Literal["approve", "reject"]


class FoodDemandPoint(BaseModel):
    hour: str
    orders: int


class FoodRushPredictionResponse(BaseModel):
    level: Literal["low", "moderate", "high"]
    predicted_wait_minutes: int
    recommended_order_time: str
    peak_expected_at: str
    expected_peak_window: str
    next_hour_demand: int
    suggested_prep_quantity: int
    rush_score: float
    active_orders: int
    order_velocity_30m: int
    order_load_graph: List[FoodDemandPoint]
    suggestions: List[str]


class AttendanceTrendPoint(BaseModel):
    date: str
    present_rate: float
    total_students: int


class RiskStudentItem(BaseModel):
    student_id: UUID
    registration_number: str
    name: str
    attendance_percent: float
    dropout_risk_percent: float


class FacultyAIAttendanceInsightsResponse(BaseModel):
    ai_attendance_accuracy_percent: float
    proxy_detection_alerts: int
    ai_sessions_count: int
    trend_graph: List[AttendanceTrendPoint]
    risk_students: List[RiskStudentItem]


class AIAttendanceCaptureResponse(BaseModel):
    message: str
    total_faces_detected: int
    matched_students: int
    late_detections: int
    proxy_detection_alerts: int
    ai_attendance_accuracy_percent: float
    present_count: int
    absent_count: int
    matched_registration_numbers: List[str] = Field(default_factory=list)


class AIAttendanceStreamStartRequest(BaseModel):
    session_id: UUID
    source_url: str = Field(min_length=8, max_length=1024)
    confidence_threshold: float = Field(default=0.75, ge=0.4, le=0.99)
    late_threshold_minutes: int = Field(default=10, ge=1, le=120)


class AIAttendanceStreamResponse(BaseModel):
    stream_id: UUID
    session_id: UUID
    status: str
    source_url: str
    frames_processed: int
    captures_succeeded: int
    started_at: datetime
    updated_at: datetime
    last_capture_at: Optional[datetime] = None
    last_error: Optional[str] = None
    stop_reason: Optional[str] = None
    last_result: Optional[Dict] = None
