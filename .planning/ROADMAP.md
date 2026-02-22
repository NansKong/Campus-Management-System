# Roadmap: Smart Campus Management System

## Overview

This roadmap hardens the existing smart campus platform into a reliable baseline release with Firebase-based authentication and database-backed management for students, food data, and remedial workflows.

## Phases

- [x] **Phase 1: Foundation and Firebase Setup** - Make local setup reproducible and establish Firebase/DB environment configuration.
- [x] **Phase 2: Firebase Authentication and Access Integrity** - Migrate login/session handling to Firebase and enforce role-safe protected access.
- [x] **Phase 3: Student and Remedial Data Management** - Add database-backed create/update/list management for students and remedial classes.
- [x] **Phase 4: Food Data and Ordering Management** - Add database-backed food catalog management and stabilize student/vendor ordering lifecycle.
- [x] **Phase 5: Attendance and Workflow Reliability** - Stabilize attendance/remedial execution paths with validation and consistent contracts.
- [x] **Phase 6: Quality Gates and Release Readiness** - Add automated checks and release validation for all core flows.

## Phase Details

### Phase 1: Foundation and Firebase Setup
**Goal**: Developers can run backend/frontend with Firebase and DB configuration predictably.
**Depends on**: Nothing (first phase)
**Requirements**: [OPS-01]
**Success Criteria** (what must be TRUE):
  1. A new developer can run backend and frontend using documented commands and env setup.
  2. Firebase project credentials and server config are documented and load correctly.
  3. Health and database connectivity checks run without manual code edits.
  4. Environment assumptions and known local pitfalls are documented.
**Plans**: 3 plans

Plans:
- [x] 01-01: Document and normalize backend/frontend env vars including Firebase and DB settings.
- [x] 01-02: Validate bootstrap scripts (`diagnose.py`, DB checks, seed scripts) and add Firebase config checks.
- [x] 01-03: Add/update contributor setup notes for local execution with Firebase emulator/credentials guidance.

### Phase 2: Firebase Authentication and Access Integrity
**Goal**: Login/session handling uses Firebase end-to-end with role-safe protected access.
**Depends on**: Phase 1
**Requirements**: [AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, UI-01]
**Success Criteria** (what must be TRUE):
  1. Firebase sign-in/sign-up and session restore work for supported users.
  2. Backend verifies Firebase ID tokens and maps them to app roles consistently.
  3. Unauthorized role actions are blocked with clear HTTP responses.
  4. Frontend protected routes redirect correctly for unauthenticated users and logout clears access.
**Plans**: 3 plans

Plans:
- [x] 02-01: Integrate Firebase SDK/admin verification flow and token plumbing in backend auth middleware.
- [x] 02-02: Migrate frontend auth context/services from custom JWT flow to Firebase session handling.
- [x] 02-03: Add auth/access smoke checks covering positive and negative role scenarios with Firebase tokens.

### Phase 3: Student and Remedial Data Management
**Goal**: Authorized users can manage student and remedial records directly in the database.
**Depends on**: Phase 2
**Requirements**: [DATA-01, DATA-03]
**Success Criteria** (what must be TRUE):
  1. Authorized users can create/update/list student data via validated API flows.
  2. Authorized users can create/update/list remedial class records reliably.
  3. Permission boundaries are enforced across student/remedial data actions.
**Plans**: 3 plans

Plans:
- [x] 03-01: Add/standardize student management endpoints and service validations.
- [x] 03-02: Add/standardize remedial management endpoints and service validations.
- [x] 03-03: Add frontend management flows/forms for student and remedial data handling.

### Phase 4: Food Data and Ordering Management
**Goal**: Food catalog is DB-manageable and order workflow is reliable end-to-end.
**Depends on**: Phase 3
**Requirements**: [DATA-02, FOOD-01, FOOD-02, FOOD-03]
**Success Criteria** (what must be TRUE):
  1. Authorized users can add/update/list menu/catalog entries in the database.
  2. Students can browse menu, place valid orders, and view own order history.
  3. Vendors can update order status with role-safe authorization.
  4. Invalid payloads and ID formats return stable, understandable errors.
**Plans**: 3 plans

Plans:
- [x] 04-01: Add/standardize food catalog management endpoints and service validation.
- [x] 04-02: Stabilize ordering backend flow including ID conversion and status transitions.
- [x] 04-03: Align frontend food management/order pages and add lifecycle integration checks.

### Phase 5: Attendance and Workflow Reliability
**Goal**: Attendance and remedial attendance execution paths are stable with consistent validation/error handling.
**Depends on**: Phase 4
**Requirements**: [ATT-01, ATT-02, ATT-03, REMD-01, REMD-02, DATA-04]
**Success Criteria** (what must be TRUE):
  1. Faculty can create sessions/classes and submit attendance with validated payloads.
  2. Student attendance history and remedial marking are consistent and permission-safe.
  3. Edge cases (missing profile, invalid IDs/codes, invalid payloads) return clear errors.
**Plans**: 3 plans

Plans:
- [x] 05-01: Stabilize attendance API contracts and edge-case validation.
- [x] 05-02: Stabilize remedial attendance execution contracts and model relations.
- [x] 05-03: Verify frontend attendance/remedial pages align with backend behavior.

### Phase 6: Quality Gates and Release Readiness
**Goal**: Project has repeatable checks and clear release criteria for the full scope including Firebase and data management.
**Depends on**: Phase 5
**Requirements**: [UI-02, OPS-02]
**Success Criteria** (what must be TRUE):
  1. Automated smoke tests cover auth (Firebase), attendance, food, remedial, and management CRUD paths.
  2. Frontend surfaces API failures with actionable messages on core pages.
  3. Release checklist defines what must pass before shipping.
**Plans**: 3 plans

Plans:
- [x] 06-01: Implement backend and frontend smoke test suite for critical paths.
- [x] 06-02: Standardize error-state UX on core pages and shared service calls.
- [x] 06-03: Create release checklist and verification runbook.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Firebase Setup | 3/3 | Complete | 2026-02-18 |
| 2. Firebase Authentication and Access Integrity | 3/3 | Complete | 2026-02-18 |
| 3. Student and Remedial Data Management | 3/3 | Complete | 2026-02-20 |
| 4. Food Data and Ordering Management | 3/3 | Complete | 2026-02-20 |
| 5. Attendance and Workflow Reliability | 3/3 | Complete | 2026-02-20 |
| 6. Quality Gates and Release Readiness | 3/3 | Complete | 2026-02-20 |
