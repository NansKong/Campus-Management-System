from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.auth import get_current_user, get_firebase_subject

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    firebase_subject=Depends(get_firebase_subject),
    db: Session = Depends(get_db),
):
    """Create a user profile for an already authenticated Firebase user."""
    if str(user_data.role) == "admin":
        raise HTTPException(status_code=403, detail="Admin self-registration is not allowed")

    firebase_email, firebase_uid = firebase_subject
    if not firebase_email:
        raise HTTPException(status_code=400, detail="Firebase token does not include an email")

    normalized_email = str(firebase_email).strip().lower()
    requested_email = str(user_data.email).strip().lower()
    if normalized_email != requested_email:
        raise HTTPException(status_code=400, detail="Email must match authenticated Firebase user")

    existing_by_uid = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if existing_by_uid:
        return existing_by_uid

    existing_by_email = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if existing_by_email:
        if existing_by_email.firebase_uid and existing_by_email.firebase_uid != firebase_uid:
            raise HTTPException(status_code=409, detail="Email is already linked to another Firebase account")

        existing_by_email.firebase_uid = firebase_uid
        db.add(existing_by_email)
        db.commit()
        db.refresh(existing_by_email)
        return existing_by_email

    new_user = User(
        email=normalized_email,
        role=user_data.role,
        firebase_uid=firebase_uid,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user profile resolved from Firebase ID token."""
    return current_user