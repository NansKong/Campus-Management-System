# Smart Campus Release Checklist (v1)

## 1) Environment and Config
- Backend `.env` exists with valid `DATABASE_URL` and Firebase admin values.
- Frontend `.env` exists with `REACT_APP_API_BASE_URL` and Firebase client values.
- Database migrations are applied (`alembic upgrade head`).

## 2) Backend Verification
- Run smoke tests:
  - `python -m pytest tests/test_auth_access_smoke.py tests/test_workflow_contract_smoke.py -q -p no:cacheprovider`
- Confirm health endpoints:
  - `GET /health`
  - `GET /api/debug/debug/food-data` (optional data sanity)

## 3) Frontend Verification
- Run frontend tests:
  - `npm test -- --watchAll=false --runInBand`
- Build frontend:
  - `npm run build`
- Confirm role flows in browser:
  - student: attendance history, food ordering, remedial mark
  - faculty: attendance session + mark, remedial create/update, students page
  - vendor/admin: food catalog and order lifecycle pages

## 4) Critical Functional Paths
- Auth:
  - login/logout works, `/api/auth/me` resolves user role
- Attendance:
  - faculty can create session and mark attendance
  - student can view own attendance
- Food:
  - student can place order
  - vendor can transition order status (`pending -> confirmed -> ready -> completed`)
- Remedial:
  - faculty can create remedial class for owned section
  - student can mark remedial attendance using valid code

## 5) Data and Error Handling
- Invalid UUID payloads return clear `400`/`422`.
- Unauthorized role actions return `403`.
- Missing user profile records return clear `404`.
- Frontend shows API error detail messages on core pages.

## 6) Final Release Gate
- Working tree reviewed.
- No unresolved blocking defects.
- Release tag/changelog prepared.
- Deployment and rollback plan validated.
