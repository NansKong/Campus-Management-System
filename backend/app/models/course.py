from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_code = Column(String(20), unique=True, nullable=False, index=True)
    course_name = Column(String(200), nullable=False)
    credits = Column(Integer, nullable=False)
    department = Column(String(100))
    semester = Column(Integer)
    course_type = Column(String(50))  # 'theory', 'lab', 'project'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sections = relationship("CourseSection", back_populates="course")
    
    def __repr__(self):
        return f"<Course {self.course_code}>"

class CourseSection(Base):
    __tablename__ = "course_sections"
    
    section_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'))
    faculty_id = Column(UUID(as_uuid=True), ForeignKey('faculty.faculty_id'))
    section_name = Column(String(10), nullable=False)
    academic_year = Column(String(10))  # '2024-25'
    semester = Column(Integer)
    max_students = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="sections")
    faculty = relationship("Faculty")
    enrollments = relationship("SectionEnrollment", back_populates="section")
    
    def __repr__(self):
        return f"<Section {self.section_name}>"

class SectionEnrollment(Base):
    __tablename__ = "section_enrollments"
    
    enrollment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.section_id'))
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.student_id'))
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')  # 'active', 'dropped', 'completed'
    
    # Relationships
    section = relationship("CourseSection", back_populates="enrollments")
    student = relationship("Student")
    
    __table_args__ = (
        UniqueConstraint('section_id', 'student_id', name='unique_enrollment'),
    )
    
    def __repr__(self):
        return f"<Enrollment {self.enrollment_id}>"