from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Date, Time, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class RemedialClass(Base):
    __tablename__ = "remedial_classes"
    
    remedial_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.section_id'))
    faculty_id = Column(UUID(as_uuid=True), ForeignKey('faculty.faculty_id'))
    classroom_id = Column(UUID(as_uuid=True), ForeignKey('classrooms.classroom_id'))
    scheduled_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    remedial_code = Column(String(10), unique=True, nullable=False)
    reason = Column(Text)
    code_expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    section = relationship("CourseSection")
    faculty = relationship("Faculty")
    classroom = relationship("Classroom")
    attendance_records = relationship("RemedialAttendance", back_populates="remedial_class")
    
    def __repr__(self):
        return f"<Remedial {self.remedial_code}>"

class RemedialAttendance(Base):
    __tablename__ = "remedial_attendance"
    
    remedial_attendance_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    remedial_id = Column(UUID(as_uuid=True), ForeignKey('remedial_classes.remedial_id'))
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.student_id'))
    marked_at = Column(DateTime, default=datetime.utcnow)
    code_used = Column(String(10))
    
    # Relationships
    remedial_class = relationship("RemedialClass", back_populates="attendance_records")
    student = relationship("Student")
    
    __table_args__ = (
        UniqueConstraint('remedial_id', 'student_id', name='unique_remedial_attendance'),
    )
    
    def __repr__(self):
        return f"<RemedialAttendance {self.remedial_attendance_id}>"