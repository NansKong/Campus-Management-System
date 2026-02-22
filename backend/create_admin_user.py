from app.database import Base, SessionLocal, engine
from app.models.user import User, UserRole


ADMIN_USERNAME = "Nans"
ADMIN_EMAIL = "nans@admin.local"


def upsert_admin_user():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_user = (
            db.query(User)
            .filter((User.email.ilike(ADMIN_EMAIL)) | (User.email.ilike(f"{ADMIN_USERNAME}@%")))
            .first()
        )

        if admin_user:
            admin_user.email = ADMIN_EMAIL
            admin_user.role = UserRole.ADMIN
            admin_user.is_active = True
            db.add(admin_user)
            action = "updated"
        else:
            admin_user = User(
                email=ADMIN_EMAIL,
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            action = "created"

        db.commit()
        db.refresh(admin_user)
        print(f"Admin user {action}: username={ADMIN_USERNAME} email={admin_user.email}")
        print("Authenticate this user through Firebase Auth; backend passwords are disabled.")
    except Exception as error:
        db.rollback()
        raise error
    finally:
        db.close()


if __name__ == "__main__":
    upsert_admin_user()
