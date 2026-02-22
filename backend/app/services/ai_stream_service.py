import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID, uuid4

from app.config import settings
from app.database import SessionLocal
from app.services import ai_service

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency
    cv2 = None


@dataclass
class AIAttendanceStreamRuntime:
    stream_id: UUID
    session_id: UUID
    faculty_id: UUID
    source_url: str
    confidence_threshold: float
    late_threshold_minutes: int
    status: str = "starting"
    frames_processed: int = 0
    captures_succeeded: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_capture_at: Optional[datetime] = None
    last_error: Optional[str] = None
    stop_reason: Optional[str] = None
    last_result: Optional[Dict] = None
    stop_requested: bool = False
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)
    task: Optional[asyncio.Task] = None


class AIAttendanceStreamManager:
    def __init__(self):
        self._streams: Dict[UUID, AIAttendanceStreamRuntime] = {}
        self._lock = asyncio.Lock()

    async def start_stream(
        self,
        session_id: UUID,
        faculty_id: UUID,
        source_url: str,
        confidence_threshold: float,
        late_threshold_minutes: int,
    ) -> Dict:
        async with self._lock:
            for runtime in self._streams.values():
                if runtime.session_id == session_id and runtime.status in {"starting", "running"}:
                    raise ValueError("An active stream already exists for this session")

            stream_id = uuid4()
            runtime = AIAttendanceStreamRuntime(
                stream_id=stream_id,
                session_id=session_id,
                faculty_id=faculty_id,
                source_url=source_url,
                confidence_threshold=confidence_threshold,
                late_threshold_minutes=late_threshold_minutes,
            )
            runtime.task = asyncio.create_task(self._run_stream(runtime))
            self._streams[stream_id] = runtime
            return self._serialize(runtime)

    async def stop_stream(self, stream_id: UUID, reason: str = "stopped_by_user") -> Dict:
        runtime = await self._get_runtime(stream_id)
        runtime.stop_requested = True
        runtime.stop_reason = reason
        runtime.status = "stopping"
        runtime.updated_at = datetime.utcnow()
        runtime.stop_event.set()

        if runtime.task and not runtime.task.done():
            try:
                await asyncio.wait_for(runtime.task, timeout=5)
            except asyncio.TimeoutError:
                runtime.task.cancel()
                runtime.status = "stopped"
                runtime.updated_at = datetime.utcnow()

        if runtime.status == "stopping":
            runtime.status = "stopped"
            runtime.updated_at = datetime.utcnow()

        return self._serialize(runtime)

    async def get_stream_status(self, stream_id: UUID) -> Dict:
        runtime = await self._get_runtime(stream_id)
        return self._serialize(runtime)

    async def _get_runtime(self, stream_id: UUID) -> AIAttendanceStreamRuntime:
        async with self._lock:
            runtime = self._streams.get(stream_id)
        if not runtime:
            raise LookupError("Stream not found")
        return runtime

    async def _run_stream(self, runtime: AIAttendanceStreamRuntime):
        runtime.status = "running"
        runtime.updated_at = datetime.utcnow()

        if cv2 is None:
            runtime.status = "failed"
            runtime.last_error = "opencv-python dependency is unavailable for RTSP capture"
            runtime.updated_at = datetime.utcnow()
            return

        timeout_seconds = max(30, int(getattr(settings, "AI_STREAM_FRAME_TIMEOUT_SECONDS", 120)))
        retry_seconds = float(getattr(settings, "AI_STREAM_RETRY_SECONDS", 1.5))
        deadline = datetime.utcnow() + timedelta(seconds=timeout_seconds)

        capture = cv2.VideoCapture(runtime.source_url)
        try:
            while not runtime.stop_event.is_set():
                if datetime.utcnow() > deadline:
                    runtime.status = "failed"
                    runtime.last_error = "No usable frame received before stream timeout"
                    runtime.updated_at = datetime.utcnow()
                    return

                if not capture.isOpened():
                    await asyncio.sleep(retry_seconds)
                    capture.release()
                    capture = cv2.VideoCapture(runtime.source_url)
                    continue

                ok, frame = capture.read()
                if not ok:
                    await asyncio.sleep(retry_seconds)
                    continue

                runtime.frames_processed += 1
                runtime.updated_at = datetime.utcnow()

                encoded_ok, encoded = cv2.imencode(".jpg", frame)
                if not encoded_ok:
                    await asyncio.sleep(retry_seconds)
                    continue

                image_bytes = encoded.tobytes()
                with SessionLocal() as db:
                    try:
                        result = ai_service.capture_attendance_from_photo(
                            db=db,
                            session_id=runtime.session_id,
                            faculty_id=runtime.faculty_id,
                            image_bytes=image_bytes,
                            confidence_threshold=runtime.confidence_threshold,
                            late_threshold_minutes=runtime.late_threshold_minutes,
                        )
                    except Exception as exc:
                        runtime.last_error = str(exc)
                        runtime.updated_at = datetime.utcnow()
                        await asyncio.sleep(retry_seconds)
                        continue

                runtime.last_result = result
                runtime.captures_succeeded += 1
                runtime.last_capture_at = datetime.utcnow()
                runtime.status = "completed"
                runtime.stop_reason = "capture_completed"
                runtime.updated_at = datetime.utcnow()
                return

            runtime.status = "stopped"
            runtime.updated_at = datetime.utcnow()
        finally:
            capture.release()

    @staticmethod
    def _serialize(runtime: AIAttendanceStreamRuntime) -> Dict:
        return {
            "stream_id": runtime.stream_id,
            "session_id": runtime.session_id,
            "status": runtime.status,
            "source_url": runtime.source_url,
            "frames_processed": runtime.frames_processed,
            "captures_succeeded": runtime.captures_succeeded,
            "started_at": runtime.started_at,
            "updated_at": runtime.updated_at,
            "last_capture_at": runtime.last_capture_at,
            "last_error": runtime.last_error,
            "stop_reason": runtime.stop_reason,
            "last_result": runtime.last_result,
        }


ai_stream_manager = AIAttendanceStreamManager()
