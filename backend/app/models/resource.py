from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Block(Base):
    __tablename__ = "blocks"
    
    block_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_name = Column(String(100), nullable=False)
    block_code = Column(String(10), unique=True, nullable=False)
    total_floors = Column(Integer)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    classrooms = relationship("Classroom", back_populates="block")
    
    def __repr__(self):
        return f"<Block {self.block_code}>"

class Classroom(Base):
    __tablename__ = "classrooms"
    
    classroom_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(UUID(as_uuid=True), ForeignKey('blocks.block_id'))
    room_number = Column(String(20), nullable=False)
    floor_number = Column(Integer)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(50))  # 'lecture_hall', 'lab', 'seminar'
    has_projector = Column(Boolean, default=False)
    has_ac = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    block = relationship("Block", back_populates="classrooms")
    
    __table_args__ = (
        UniqueConstraint('block_id', 'room_number', name='unique_classroom'),
    )
    
    def __repr__(self):
        return f"<Classroom {self.room_number}>"

class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    
    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.section_id'))
    classroom_id = Column(UUID(as_uuid=True), ForeignKey('classrooms.classroom_id'))
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Schedule {self.day_of_week} {self.start_time}>"