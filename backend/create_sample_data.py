from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.resource import Block, Classroom
from app.models.course import Course, CourseSection, SectionEnrollment
from app.models.food import FoodVendor, FoodMenuItem, BreakTimeSlot
from datetime import time
import uuid

def create_sample_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Creating sample data...")
        
        # 1. Create Users
        print("Creating users...")
        
        # Admin User
        admin_user = User(
            email="admin@lpu.in",
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        
        # Faculty User
        faculty_user = User(
            email="faculty@lpu.in",
            role=UserRole.FACULTY
        )
        db.add(faculty_user)
        
        # Student User 1
        student_user1 = User(
            email="student1@lpu.in",
            role=UserRole.STUDENT
        )
        db.add(student_user1)
        
        # Student User 2
        student_user2 = User(
            email="student2@lpu.in",
            role=UserRole.STUDENT
        )
        db.add(student_user2)
        
        # Vendor User
        vendor_user = User(
            email="vendor@lpu.in",
            role=UserRole.VENDOR
        )
        db.add(vendor_user)
        
        db.flush()  # Get user IDs
        
        # 2. Create Faculty Profile
        print("Creating faculty profile...")
        faculty = Faculty(
            user_id=faculty_user.user_id,
            employee_id="FAC001",
            first_name="Dr. John",
            last_name="Doe",
            phone="9876543210",
            department="Computer Science",
            designation="Associate Professor",
            specialization="Artificial Intelligence"
        )
        db.add(faculty)
        db.flush()
        
        # 3. Create Student Profiles
        print("Creating student profiles...")
        student1 = Student(
            user_id=student_user1.user_id,
            registration_number="12012345",
            first_name="Rahul",
            last_name="Sharma",
            phone="9123456780",
            parent_email="parent1@example.com",
            parent_phone="9123456789",
            program="B.Tech CSE",
            semester=5,
            section="A",
            enrollment_year=2022
        )
        db.add(student1)
        
        student2 = Student(
            user_id=student_user2.user_id,
            registration_number="12012346",
            first_name="Priya",
            last_name="Singh",
            phone="9123456781",
            parent_email="parent2@example.com",
            parent_phone="9123456790",
            program="B.Tech CSE",
            semester=5,
            section="A",
            enrollment_year=2022
        )
        db.add(student2)
        db.flush()
        
        # 4. Create Blocks
        print("Creating blocks...")
        block = Block(
            block_name="Academic Block 1",
            block_code="AB1",
            total_floors=5,
            description="Main academic building"
        )
        db.add(block)
        db.flush()
        
        # 5. Create Classrooms
        print("Creating classrooms...")
        classroom1 = Classroom(
            block_id=block.block_id,
            room_number="101",
            floor_number=1,
            capacity=60,
            room_type="lecture_hall",
            has_projector=True,
            has_ac=True
        )
        db.add(classroom1)
        
        classroom2 = Classroom(
            block_id=block.block_id,
            room_number="201",
            floor_number=2,
            capacity=40,
            room_type="lab",
            has_projector=True,
            has_ac=True
        )
        db.add(classroom2)
        db.flush()
        
        # 6. Create Courses
        print("Creating courses...")
        course = Course(
            course_code="CSE301",
            course_name="Database Management Systems",
            credits=4,
            department="Computer Science",
            semester=5,
            course_type="theory"
        )
        db.add(course)
        db.flush()
        
        # 7. Create Course Section
        print("Creating course section...")
        section = CourseSection(
            course_id=course.course_id,
            faculty_id=faculty.faculty_id,
            section_name="A",
            academic_year="2024-25",
            semester=5,
            max_students=60
        )
        db.add(section)
        db.flush()
        
        # 8. Enroll Students
        print("Enrolling students...")
        enrollment1 = SectionEnrollment(
            section_id=section.section_id,
            student_id=student1.student_id,
            status='active'
        )
        db.add(enrollment1)
        
        enrollment2 = SectionEnrollment(
            section_id=section.section_id,
            student_id=student2.student_id,
            status='active'
        )
        db.add(enrollment2)
        
        # 9. Create Food Vendor
        print("Creating food vendor...")
        vendor = FoodVendor(
            user_id=vendor_user.user_id,
            vendor_name="Campus Canteen",
            stall_location="Near Library",
            contact_phone="9876543211"
        )
        db.add(vendor)
        db.flush()
        
        # 10. Create Menu Items
        print("Creating menu items...")
        items = [
            FoodMenuItem(
                vendor_id=vendor.vendor_id,
                item_name="Sandwich",
                description="Veg grilled sandwich",
                price=50.00,
                category="breakfast",
                is_available=True,
                preparation_time=10
            ),
            FoodMenuItem(
                vendor_id=vendor.vendor_id,
                item_name="Coffee",
                description="Hot coffee",
                price=20.00,
                category="beverages",
                is_available=True,
                preparation_time=5
            ),
            FoodMenuItem(
                vendor_id=vendor.vendor_id,
                item_name="Pasta",
                description="White sauce pasta",
                price=80.00,
                category="lunch",
                is_available=True,
                preparation_time=15
            ),
        ]
        
        for item in items:
            db.add(item)
        
        # 11. Create Break Time Slots
        print("Creating break time slots...")
        slots = [
            BreakTimeSlot(
                slot_name="Morning Break",
                start_time=time(10, 0),
                end_time=time(10, 30),
                max_orders_per_slot=100
            ),
            BreakTimeSlot(
                slot_name="Lunch Break",
                start_time=time(13, 0),
                end_time=time(14, 0),
                max_orders_per_slot=150
            ),
            BreakTimeSlot(
                slot_name="Evening Break",
                start_time=time(16, 0),
                end_time=time(16, 30),
                max_orders_per_slot=80
            ),
        ]
        
        for slot in slots:
            db.add(slot)
        
        db.commit()
        
        print("\n" + "="*50)
        print("Sample data created successfully!")
        print("="*50)
        print("\nSeeded Accounts (Firebase Authentication Required):")
        print("-" * 50)
        print("ADMIN:")
        print("  Email: admin@lpu.in")
        print("\nFACULTY:")
        print("  Email: faculty@lpu.in")
        print("\nSTUDENT 1:")
        print("  Email: student1@lpu.in")
        print("  Reg No: 12012345")
        print("\nSTUDENT 2:")
        print("  Email: student2@lpu.in")
        print("  Reg No: 12012346")
        print("\nVENDOR:")
        print("  Email: vendor@lpu.in")
        print("  Note: Set/Manage passwords in Firebase Auth.")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()