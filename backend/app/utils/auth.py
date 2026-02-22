import json
import os
from typing import Optional, Tuple
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    from firebase_admin import credentials
except Exception:
    firebase_admin = None
    firebase_auth = None
    credentials = None

try:
    from google.auth.transport import requests as google_auth_requests
    from google.oauth2 import id_token as google_id_token
except Exception:
    google_auth_requests = None
    google_id_token = None

# Firebase ID tokens are provided by the frontend in Authorization: Bearer <id_token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/register")

_firebase_init_attempted = False
_google_request = None


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _initialize_firebase():
    """Initialize Firebase Admin SDK once, if configured."""
    global _firebase_init_attempted

    if _firebase_init_attempted:
        if firebase_admin and firebase_admin._apps:
            return firebase_admin.get_app()
        return None

    _firebase_init_attempted = True

    if not firebase_admin or not credentials:
        return None

    if firebase_admin._apps:
        return firebase_admin.get_app()

    try:
        if settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        elif (
            settings.FIREBASE_PROJECT_ID
            and settings.FIREBASE_CLIENT_EMAIL
            and settings.FIREBASE_PRIVATE_KEY
        ):
            cred = credentials.Certificate(
                {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            )
        else:
            return None

        return firebase_admin.initialize_app(cred)
    except Exception:
        return None


def _normalize_subject(decoded_token: dict) -> Tuple[Optional[str], Optional[str]]:
    email = decoded_token.get("email")
    uid = decoded_token.get("uid") or decoded_token.get("sub")

    normalized_email = str(email).strip().lower() if email else None
    normalized_uid = str(uid).strip() if uid else None
    return normalized_email, normalized_uid


def _verify_with_google_fallback(token: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Verify Firebase token without Admin SDK service-account credentials.
    This validates signature/issuer using Google's public certs but cannot check revocation.
    """
    global _google_request

    if not google_auth_requests or not google_id_token:
        return None, None

    try:
        if _google_request is None:
            _google_request = google_auth_requests.Request()

        decoded = google_id_token.verify_firebase_token(token, _google_request)
        if not decoded:
            return None, None

        expected_project = settings.FIREBASE_PROJECT_ID
        token_audience = decoded.get("aud")
        if expected_project and token_audience and token_audience != expected_project:
            return None, None

        if settings.FIREBASE_REQUIRE_EMAIL_VERIFIED and not decoded.get("email_verified", False):
            return None, None

        return _normalize_subject(decoded)
    except Exception:
        return None, None


def _get_firebase_web_api_key() -> Optional[str]:
    """Resolve Firebase Web API key from backend envs."""
    if settings.FIREBASE_WEB_API_KEY:
        return settings.FIREBASE_WEB_API_KEY.strip()

    env_key = os.getenv("REACT_APP_FIREBASE_API_KEY")
    if env_key:
        return env_key.strip()

    # Backward compatibility for older local setups where API key was incorrectly
    # placed in FIREBASE_PRIVATE_KEY.
    if settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_PRIVATE_KEY.startswith("AIza"):
        return settings.FIREBASE_PRIVATE_KEY.strip().strip('"')

    return None


def _verify_with_identity_toolkit(token: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Verify Firebase ID token via Google Identity Toolkit.
    This path works without firebase-admin/google-auth packages.
    """
    api_key = _get_firebase_web_api_key()
    if not api_key:
        return None, None

    payload = json.dumps({"idToken": token}).encode("utf-8")
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
    request = urllib_request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib_request.urlopen(request, timeout=10) as response:
            response_payload = response.read().decode("utf-8")
        decoded = json.loads(response_payload)
    except (urllib_error.URLError, urllib_error.HTTPError, TimeoutError, OSError, ValueError):
        return None, None

    users = decoded.get("users") or []
    if not users:
        return None, None

    subject = users[0]
    if settings.FIREBASE_REQUIRE_EMAIL_VERIFIED and not subject.get("emailVerified", False):
        return None, None

    normalized_email = str(subject.get("email")).strip().lower() if subject.get("email") else None
    normalized_uid = str(subject.get("localId")).strip() if subject.get("localId") else None
    return normalized_email, normalized_uid


def _get_subject_from_firebase(token: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (email, uid) from a Firebase ID token."""
    app = _initialize_firebase()
    if app and firebase_auth:
        try:
            decoded = firebase_auth.verify_id_token(
                token,
                app=app,
                check_revoked=settings.FIREBASE_CHECK_REVOKED,
            )

            if settings.FIREBASE_REQUIRE_EMAIL_VERIFIED and not decoded.get("email_verified", False):
                return None, None

            return _normalize_subject(decoded)
        except Exception:
            return None, None

    fallback_email, fallback_uid = _verify_with_google_fallback(token)
    if fallback_uid:
        return fallback_email, fallback_uid

    return _verify_with_identity_toolkit(token)


def get_firebase_subject(token: str = Depends(oauth2_scheme)) -> Tuple[str, str]:
    """Validate bearer token and return Firebase subject (email, uid)."""
    firebase_email, firebase_uid = _get_subject_from_firebase(token)
    if not firebase_uid:
        raise _credentials_exception()
    return firebase_email, firebase_uid


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Resolve the current user using only a verified Firebase ID token."""
    firebase_email, firebase_uid = _get_subject_from_firebase(token)
    if not firebase_uid:
        raise _credentials_exception()

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if user is None and firebase_email:
        user = db.query(User).filter(func.lower(User.email) == firebase_email).first()
        if user is not None and settings.AUTH_AUTO_LINK_FIREBASE_UID and not user.firebase_uid:
            user.firebase_uid = firebase_uid
            db.add(user)
            db.commit()
            db.refresh(user)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please register first.",
        )

    return user
