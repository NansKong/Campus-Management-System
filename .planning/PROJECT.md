# Smart Campus Management System

## What This Is

Smart Campus Management System is a full-stack campus operations app with a FastAPI backend and React frontend. It currently supports attendance sessions, food ordering, and remedial class workflows for students, faculty, admins, and vendors. The updated plan adds Firebase-based authentication and stronger database-backed management for students, food data, and remedial classes.

## Core Value

Daily campus workflows (attendance, food ordering, and remedial tracking) must be reliable and role-correct from login to task completion.

## Requirements

### Validated

- [x] JWT-based auth (`/api/auth/register`, `/api/auth/login`, `/api/auth/me`) exists and is wired end-to-end.
- [x] Attendance APIs support session creation, bulk marking, and student history retrieval.
- [x] Food APIs support menu retrieval, order creation, order history, and vendor status updates.
- [x] Remedial APIs support class creation and attendance marking by code.
- [x] Frontend has protected routes and pages for dashboard, attendance, food, remedial, resources, and profile.

### Active

- [ ] Add Firebase authentication (frontend sign-in/session + backend token verification).
- [ ] Enforce role-based access uniformly using verified Firebase identity.
- [ ] Add database-backed admin/faculty/vendor management flows for students, food catalog, and remedial classes.
- [ ] Harden attendance, food, and remedial workflows with stronger validation and error handling.
- [ ] Add baseline automated test coverage for key backend and frontend workflows.
- [ ] Improve local developer setup and release-readiness documentation.

### Out of Scope

- Native mobile app clients - web app stabilization is higher priority.
- Payments and billing integration - current food flow does not require payment processing.
- Multi-campus tenancy - current data model assumes a single campus domain.

## Context

- Backend: FastAPI + SQLAlchemy + Alembic under `backend/app`.
- Frontend: React (CRA) + Tailwind + React Router under `frontend/src`.
- Current auth is custom JWT-based and localStorage-backed in frontend service layer.
- Database connection is environment-driven via `DATABASE_URL` in `backend/.env`.
- Required change: Firebase Auth will become the login/session provider; backend will validate Firebase ID tokens.
- Existing advanced/optional ML support exists (`face_recognition_service.py`) but is not a core shipped path today.
- Repository currently includes vendored dependency directories (`backend/venv`, `frontend/node_modules`), which can affect performance and repository hygiene.

## Constraints

- **Tech stack**: Keep FastAPI + React architecture - this is the deployed and implemented baseline.
- **Compatibility**: Preserve existing API route contracts used by frontend services - avoid breaking current UI behavior.
- **Security**: Secrets must remain environment-driven (`.env`) - no hardcoded credentials.
- **Auth provider**: Firebase Auth is the required login/session source for this milestone.
- **Quality baseline**: No broad backend test suite is present yet - stabilization work must add verification before major refactors.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat this as brownfield stabilization first | Core capabilities already exist and need reliability more than net-new scope | Pending |
| Migrate login/session handling to Firebase Auth | Centralized auth handling and easier client session management | Pending |
| Add explicit admin data-management capabilities as first-class scope | Team requested DB-backed create/update flows for students, food, and remedial data | Pending |
| Keep balanced GSD model profile defaults | Good tradeoff between execution speed and planning quality | Pending |
| Keep planning docs committed (`commit_docs=true`) | Preserve planning history and execution traceability in repo | Pending |

---
*Last updated: 2026-02-18 after Phase 1 review and scope update*
