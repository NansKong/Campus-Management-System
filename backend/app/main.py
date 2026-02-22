from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, attendance, food, remedial, debug, student, ai, realtime
from app.database import engine, Base
from app.config import settings

# Import ALL models to ensure they're registered
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course, CourseSection, SectionEnrollment
from app.models.resource import Block, Classroom, ClassSchedule
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.remedial import RemedialClass, RemedialAttendance
from app.models.food import FoodVendor, FoodMenuItem, BreakTimeSlot, FoodOrder, OrderItem
from app.models.notification import Notification
from app.models.ai import StudentFaceProfile


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Campus Management System API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(food.router, prefix="/api/food", tags=["Food Ordering"])
app.include_router(remedial.router, prefix="/api/remedial", tags=["Remedial Classes"])
app.include_router(student.router, prefix="/api/students", tags=["Student Management"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Realtime"])

@app.get("/")
def root():
    return {
        "message": "Smart Campus Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
