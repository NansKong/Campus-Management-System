# Import all models here
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
