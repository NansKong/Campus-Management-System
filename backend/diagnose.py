def _check_environment(settings) -> None:
    required_vars = ["DATABASE_URL", "SECRET_KEY"]
    firebase_recommended = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_PRIVATE_KEY",
    ]

    print("\n" + "-" * 60)
    print("ENVIRONMENT CHECK")
    print("-" * 60)

    for key in required_vars:
        value = getattr(settings, key, None)
        if value:
            print(f"OK   {key}")
        else:
            print(f"FAIL {key} is missing")

    missing_firebase = [k for k in firebase_recommended if not getattr(settings, k, None)]
    if missing_firebase:
        print(
            "WARN Firebase variables missing (expected before Phase 2 auth migration): "
            + ", ".join(missing_firebase)
        )
    else:
        print("OK   Firebase env scaffold detected")


def diagnose() -> None:
    try:
        from app.config import settings
        from app.database import SessionLocal, engine
        from app.models.faculty import Faculty
        from app.models.food import BreakTimeSlot, FoodMenuItem, FoodVendor
        from app.models.student import Student
        from app.models.user import User
    except ImportError as exc:
        print("\n" + "=" * 60)
        print("SMART CAMPUS SYSTEM - DIAGNOSTIC CHECK")
        print("=" * 60 + "\n")
        print(f"FAIL Missing dependency/module: {exc}")
        print("Install dependencies first:")
        print("  python -m pip install -r requirements.txt")
        return

    db = SessionLocal()

    print("\n" + "=" * 60)
    print("SMART CAMPUS SYSTEM - DIAGNOSTIC CHECK")
    print("=" * 60 + "\n")

    _check_environment(settings)

    try:
        engine.connect()
        print("\nOK   Database connection")
    except Exception as exc:
        print(f"\nFAIL Database connection: {exc}")
        db.close()
        return

    user_count = db.query(User).count()
    student_count = db.query(Student).count()
    faculty_count = db.query(Faculty).count()
    food_count = db.query(FoodMenuItem).count()
    vendor_count = db.query(FoodVendor).count()
    slot_count = db.query(BreakTimeSlot).count()

    print("\n" + "-" * 60)
    print("DATA SUMMARY")
    print("-" * 60)
    print(f"Users: {user_count}")
    print(f"Students: {student_count}")
    print(f"Faculty: {faculty_count}")
    print(f"Food menu items: {food_count}")
    print(f"Food vendors: {vendor_count}")
    print(f"Break time slots: {slot_count}")

    if faculty_count == 0:
        print("WARN No faculty records found. Attendance creation will fail.")
    if food_count == 0:
        print("WARN No food menu items found. Food ordering will fail.")
    if slot_count == 0:
        print("WARN No break time slots found. Food ordering will fail.")

    print("\n" + "-" * 60)
    print("TEST ACCOUNTS")
    print("-" * 60)
    for email in [
        "admin@lpu.in",
        "faculty@lpu.in",
        "student1@lpu.in",
        "student2@lpu.in",
        "vendor@lpu.in",
    ]:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"OK   {email} ({user.role})")
        else:
            print(f"MISS {email}")

    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60 + "\n")
    db.close()


if __name__ == "__main__":
    diagnose()
