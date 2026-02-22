# Smart Campus System

Phase 1 setup baseline for backend, frontend, PostgreSQL, and Firebase scaffolding.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

## Backend Setup

1. Open `backend/`.
2. Create `.env` from the template:
   - `Copy-Item .env.example .env` (PowerShell)
3. Update required variables in `backend/.env`:
   - `DATABASE_URL`
   - `AUTH_AUTO_LINK_FIREBASE_UID` (optional; defaults to `True`)
4. (Phase 1 scaffold) Add Firebase Admin vars if available:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_WEB_API_KEY` (recommended for local token verification fallback)
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_PRIVATE_KEY` or `FIREBASE_CREDENTIALS_PATH`
   - `FIREBASE_CHECK_REVOKED=True`
   - `FIREBASE_REQUIRE_EMAIL_VERIFIED=False` (set `True` only after email verification flow is enabled)
5. Install dependencies:
   - `pip install -r requirements.txt`
6. Run migrations (if needed) and diagnostics:
   - `alembic upgrade head`
   - `python test_db_connection.py`
   - `python diagnose.py`
   - `pytest tests/test_auth_access_smoke.py -q`

### If your backend venv is broken

Run:
- `powershell -ExecutionPolicy Bypass -File backend/repair_env.ps1`

This recreates `backend/venv`, installs requirements, and runs DB diagnostics.

## Frontend Setup

1. Open `frontend/`.
2. Create `.env` from the template:
   - `Copy-Item .env.example .env` (PowerShell)
3. Set `REACT_APP_API_BASE_URL` if backend is not running on `http://localhost:8000/api`.
4. Set Firebase client config:
   - `REACT_APP_FIREBASE_*` keys in `frontend/.env`
5. Install and run:
   - `npm install`
   - `npm start`

6. For Firebase auth migration (Phase 2), ensure `firebase` dependency is installed:
   - `npm install firebase`

## Notes

- Authentication uses Firebase ID tokens only.
- Backend does not issue JWT login tokens and does not store passwords.

## AI Module Endpoints (Phase 1 Scaffold)

- `POST /api/ai/attendance/enroll`:
  Upload `5-10` face images (multipart) for enrollment. Student self-enrollment supported.
- `GET /api/ai/attendance/enrollments/pending`:
  Admin list for pending biometric approvals.
- `POST /api/ai/attendance/enrollments/{student_id}/review`:
  Admin approve/reject enrollment.
- `POST /api/ai/attendance/sessions/{session_id}/capture-photo`:
  Faculty photo-based AI attendance capture for an open session.
- `GET /api/ai/attendance/faculty-insights`:
  Faculty AI accuracy/proxy alerts/trend/risk list.
- `GET /api/ai/food/rush`:
  Rush-level and demand forecast for student/vendor/admin views.

Important:
- Face enrollment stores embeddings, not raw images.
- If `face_recognition` is unavailable in backend runtime, enrollment uses deterministic fallback embeddings and photo-based multi-face capture endpoint will return a dependency error.

## AI Phase 2 Realtime

- `POST /api/ai/attendance/stream/start`:
  Start RTSP/source stream capture for a faculty attendance session.
- `GET /api/ai/attendance/stream/{stream_id}`:
  Read live stream runtime status.
- `POST /api/ai/attendance/stream/{stream_id}/stop`:
  Stop active stream capture.
- `WS /api/realtime/ws/food-rush?token=<firebase_id_token>`:
  Realtime food rush feed for student/vendor/admin dashboards.

## Live Firebase Sign-In Validation (Production Path)

1. Apply DB migration:
   - `alembic upgrade head`
2. Ensure backend `.env` has:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_WEB_API_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_PRIVATE_KEY` (or `FIREBASE_CREDENTIALS_PATH`)
   - `FIREBASE_CHECK_REVOKED=True`
   - `FIREBASE_REQUIRE_EMAIL_VERIFIED=True`
3. Ensure frontend `.env` has:
   - all `REACT_APP_FIREBASE_*` values
4. Install frontend firebase package:
   - `npm install firebase`
5. Start backend + frontend and sign in with a real Firebase user.
6. Verify protected endpoint with bearer token path:
   - `GET /api/auth/me` returns user profile from app DB.

Important: user email in Firebase must exist in app `users` table (or be provisioned through your user onboarding flow).

## Firebase Troubleshooting

If you see `Firebase: Error (auth/configuration-not-found)` during login/register:

1. Open Firebase Console for your exact `REACT_APP_FIREBASE_PROJECT_ID`.
2. Go to `Authentication -> Sign-in method` and enable `Email/Password`.
3. Go to `Authentication -> Settings -> Authorized domains` and add `localhost`.
4. Verify frontend `.env` keys match the same Firebase project.
5. Restart the frontend after any `.env` change.
