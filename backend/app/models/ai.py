from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class StudentFaceProfile(Base):
    __tablename__ = "student_face_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    embedding_vector = Column(Text, nullable=False)
    model_name = Column(String(64), nullable=False, default="facenet")
    sample_count = Column(Integer, nullable=False, default=0)
    consent_given = Column(Boolean, nullable=False, default=False)
    approval_status = Column(String(20), nullable=False, default="pending", index=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student")

    def __repr__(self):
        return f"<StudentFaceProfile student_id={self.student_id} status={self.approval_status}>"
