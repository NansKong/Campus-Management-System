# Requirements: Smart Campus Management System

**Defined:** 2026-02-18
**Core Value:** Daily campus workflows (attendance, food ordering, and remedial tracking) must be reliable and role-correct from login to task completion.

## v1 Requirements

### Authentication and Access

- [ ] **AUTH-01**: User can sign up/sign in through Firebase Authentication.
- [ ] **AUTH-02**: Frontend stores and refreshes Firebase session state across browser refresh.
- [ ] **AUTH-03**: Frontend sends Firebase ID token on protected API requests.
- [ ] **AUTH-04**: Backend verifies Firebase ID tokens and resolves application user identity/role.
- [ ] **AUTH-05**: Protected endpoints enforce role-based access for student, faculty, vendor, and admin actions.
- [ ] **AUTH-06**: User can log out and lose access to protected routes immediately.

### Data Management (DB-backed)

- [ ] **DATA-01**: Authorized users can create, edit, and list student records in the database.
- [ ] **DATA-02**: Authorized users can create, edit, and list food menu/catalog records in the database.
- [ ] **DATA-03**: Authorized users can create, edit, and list remedial class records in the database.
- [ ] **DATA-04**: Data-management endpoints return consistent validation errors for bad input.

### Attendance

- [ ] **ATT-01**: Faculty user can create an attendance session for a class section.
- [ ] **ATT-02**: Faculty user can submit bulk attendance marks for an existing session.
- [ ] **ATT-03**: Student attendance history can be retrieved reliably by student ID.

### Food Ordering

- [ ] **FOOD-01**: Student can browse available menu items (with optional vendor filtering).
- [ ] **FOOD-02**: Student can place an order and receive order ID, status, and pickup code.
- [ ] **FOOD-03**: Vendor can update order status; student can retrieve own order history.

### Remedial Classes

- [ ] **REMD-01**: Faculty can schedule a remedial class with required metadata.
- [ ] **REMD-02**: Student can mark remedial attendance using a valid remedial code.

### Frontend Experience

- [ ] **UI-01**: All core pages remain protected behind authentication routing.
- [ ] **UI-02**: API failures on dashboard/workflow pages show clear user-facing error states.

### Reliability and Delivery

- [ ] **OPS-01**: Developers can run backend and frontend locally with clear, reproducible setup instructions.
- [ ] **OPS-02**: Automated smoke tests validate auth, attendance, food, and remedial critical paths.

## v2 Requirements

### AI and Automation

- **AI-01**: Attendance can be marked from uploaded class images using face recognition.
- **AI-02**: Face enrollment workflows include quality checks and admin review.

### Notifications and Async Work

- **NOTF-01**: Attendance and order events trigger asynchronous notifications via Redis/Celery.
- **NOTF-02**: Users can see in-app notification history and unread counts.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Native mobile apps | Web-first stabilization has priority. |
| Payment gateway integration | Current food order scope does not include payments. |
| Multi-campus tenancy | Existing schema and workflows are single-campus oriented. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| AUTH-04 | Phase 2 | Pending |
| AUTH-05 | Phase 2 | Pending |
| AUTH-06 | Phase 2 | Pending |
| DATA-01 | Phase 3 | Pending |
| DATA-02 | Phase 4 | Pending |
| DATA-03 | Phase 3 | Pending |
| DATA-04 | Phase 5 | Pending |
| ATT-01 | Phase 5 | Pending |
| ATT-02 | Phase 5 | Pending |
| ATT-03 | Phase 5 | Pending |
| FOOD-01 | Phase 4 | Pending |
| FOOD-02 | Phase 4 | Pending |
| FOOD-03 | Phase 4 | Pending |
| REMD-01 | Phase 5 | Pending |
| REMD-02 | Phase 5 | Pending |
| UI-01 | Phase 2 | Pending |
| UI-02 | Phase 6 | Pending |
| OPS-01 | Phase 1 | Pending |
| OPS-02 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0

---
*Requirements defined: 2026-02-18*
*Last updated: 2026-02-18 after Phase 1 review and Firebase/data-management scope update*
