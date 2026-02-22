from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True))  # Allow NULL for mock data
    classroom_id = Column(UUID(as_uuid=True))  # Allow NULL for mock data
    session_date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    session_type = Column(String(50), default='regular')
    is_closed = Column(Boolean, default=False)
    marked_by = Column(UUID(as_uuid=True), ForeignKey('faculty.faculty_id'))
    total_students = Column(Integer)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    faculty = relationship("Faculty")
    records = relationship("AttendanceRecord", back_populates="session")
    
    def __repr__(self):
        return f"<Session {self.session_date}>"

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('attendance_sessions.session_id'))
    student_id = Column(UUID(as_uuid=True))  # Allow NULL for mock data
    status = Column(String(20), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow)
    marked_by = Column(String(50))
    confidence_score = Column(Float)
    image_url = Column(String(500))
    
    # Relationships
    session = relationship("AttendanceSession", back_populates="records")
    
    def __repr__(self):
        return f"<Record {self.status}>"