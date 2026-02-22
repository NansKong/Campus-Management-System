from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(15))
    parent_email = Column(String(255))
    parent_phone = Column(String(15))
    program = Column(String(100))
    semester = Column(Integer)
    section = Column(String(10))
    enrollment_year = Column(Integer)
    face_encoding = Column(Text)  # Store face encoding as JSON string
    profile_image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="student_profile")
    
    def __repr__(self):
        return f"<Student {self.registration_number}>"