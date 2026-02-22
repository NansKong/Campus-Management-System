from app.database import SessionLocal
from app.models.food import BreakTimeSlot, FoodMenuItem, FoodVendor
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.user import User, UserRole


def verify_and_fix_food_data():
    db = SessionLocal()

    print("\n" + "=" * 60)
    print("VERIFYING SMART CAMPUS DATA")
    print("=" * 60 + "\n")

    user_count = db.query(User).count()
    print(f"Users in database: {user_count}")

    student_count = db.query(Student).count()
    print(f"Students in database: {student_count}")

    faculty_count = db.query(Faculty).count()
    print(f"Faculty in database: {faculty_count}")

    vendor_count = db.query(FoodVendor).count()
    print(f"Food vendors: {vendor_count}")

    if vendor_count == 0:
        print("\nNo vendors found. Creating default vendor...")

        vendor_user = db.query(User).filter(User.email == "vendor@lpu.in").first()
        if not vendor_user:
            vendor_user = User(
                email="vendor@lpu.in",
                role=UserRole.VENDOR,
            )
            db.add(vendor_user)
            db.flush()
            print("Created vendor user")

        vendor = FoodVendor(
            user_id=vendor_user.user_id,
            vendor_name="Campus Canteen",
            stall_location="Near Library",
            contact_phone="9876543211",
        )
        db.add(vendor)
        db.flush()
        print(f"Created vendor: {vendor.vendor_name}")

        items = [
            FoodMenuItem(
                vendor_id=vendor.vendor_id,
                item_name="Sandwich",
                description="Veg grilled sandwich",
                price=50.00,
                category="breakfast",
                is_available=True,
                preparation_time=10,
            ),
            FoodMenuItem(
                vendor_id=vendor.vendor_id,
                item_name="Coffee",
                description="Hot coffee",
                price=20.00,
                category="beverages",
                is_available=True,
                preparation_time=5,
            ),
            FoodMenuItem(
                vendor_id=vendor.vendor_id,
                item_name="Pasta",
                description="White sauce pasta",
                price=80.00,
                category="lunch",
                is_available=True,
                preparation_time=15,
            ),
        ]

        for item in items:
            db.add(item)

        print(f"Created {len(items)} menu items")
        db.commit()

    menu_count = db.query(FoodMenuItem).count()
    print(f"Menu items: {menu_count}")

    if menu_count > 0:
        print("\nMenu Items:")
        items = db.query(FoodMenuItem).all()
        for item in items:
            print(f"  - {item.item_name}: INR {item.price} ({item.category})")

    slot_count = db.query(BreakTimeSlot).count()
    print(f"\nTime slots: {slot_count}")

    if slot_count == 0:
        print("Creating time slots...")
        from datetime import time

        slots = [
            BreakTimeSlot(
                slot_name="Morning Break",
                start_time=time(10, 0),
                end_time=time(10, 30),
                max_orders_per_slot=100,
            ),
            BreakTimeSlot(
                slot_name="Lunch Break",
                start_time=time(13, 0),
                end_time=time(14, 0),
                max_orders_per_slot=150,
            ),
            BreakTimeSlot(
                slot_name="Evening Break",
                start_time=time(16, 0),
                end_time=time(16, 30),
                max_orders_per_slot=80,
            ),
        ]

        for slot in slots:
            db.add(slot)

        db.commit()
        print(f"Created {len(slots)} time slots")

    if slot_count > 0:
        print("\nTime Slots:")
        slots = db.query(BreakTimeSlot).all()
        for slot in slots:
            print(f"  - {slot.slot_name}: {slot.start_time} - {slot.end_time}")

    if menu_count > 0:
        first_item = db.query(FoodMenuItem).first()
        print(f"\nUse vendor_id: {first_item.vendor_id} for food orders")

    if slot_count > 0:
        first_slot = db.query(BreakTimeSlot).first()
        print(f"Use slot_id: {first_slot.slot_id} for time slot selection")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60 + "\n")

    db.close()


if __name__ == "__main__":
    verify_and_fix_food_data()
