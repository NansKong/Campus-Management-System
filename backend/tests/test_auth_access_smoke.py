from datetime import datetime
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api import attendance, auth, food, remedial, student
from app.database import get_db
from app.services import food_service, remedial_service, student_service
from app.utils import auth as auth_utils


class DummyDB:
    def query(self, *_args, **_kwargs):
        return self

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return None


def _override_db():
    yield DummyDB()


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    test_app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
    test_app.include_router(food.router, prefix="/api/food", tags=["Food Ordering"])
    test_app.include_router(remedial.router, prefix="/api/remedial", tags=["Remedial Classes"])
    test_app.include_router(student.router, prefix="/api/students", tags=["Student Management"])
    test_app.dependency_overrides[get_db] = _override_db
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


def _set_current_user(app, role, email="user@example.com"):
    fake_user = SimpleNamespace(role=role, email=email, user_id="u1")

    def _override_user():
        return fake_user

    app.dependency_overrides[auth_utils.get_current_user] = _override_user
    return fake_user


def test_requires_auth_by_default(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_student_cannot_create_attendance_session(client, app):
    _set_current_user(app, role="student")

    response = client.post(
        "/api/attendance/sessions",
        json={
            "section_id": "00000000-0000-0000-0000-000000000000",
            "session_date": "2026-02-18",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )
    assert response.status_code == 403
    assert "Only faculty" in response.json()["detail"]


def test_faculty_cannot_place_food_order(client, app):
    _set_current_user(app, role="faculty")

    response = client.post(
        "/api/food/orders",
        json={
            "vendor_id": "00000000-0000-0000-0000-000000000001",
            "slot_id": "00000000-0000-0000-0000-000000000002",
            "items": [
                {
                    "item_id": "00000000-0000-0000-0000-000000000003",
                    "quantity": 1,
                }
            ],
        },
    )
    assert response.status_code == 403
    assert "Only students" in response.json()["detail"]


def test_student_cannot_manage_food_catalog(client, app):
    _set_current_user(app, role="student")

    response = client.post(
        "/api/food/catalog/items",
        json={
            "item_name": "Masala Dosa",
            "price": 60,
            "category": "breakfast",
            "is_available": True,
        },
    )
    assert response.status_code == 403
    assert "Only admin or vendor" in response.json()["detail"]


def test_vendor_can_create_food_catalog_item(client, app, monkeypatch):
    _set_current_user(app, role="vendor")

    sentinel = object()
    monkeypatch.setattr(food_service, "create_menu_item", lambda *args, **kwargs: sentinel)
    monkeypatch.setattr(
        food_service,
        "serialize_menu_item",
        lambda *_args, **_kwargs: {
            "item_id": "33333333-3333-3333-3333-333333333333",
            "vendor_id": "44444444-4444-4444-4444-444444444444",
            "item_name": "Masala Dosa",
            "description": "Crispy dosa",
            "price": "60.00",
            "category": "breakfast",
            "is_available": True,
            "preparation_time": 10,
            "image_url": None,
            "created_at": "2026-02-20T00:00:00",
        },
    )

    response = client.post(
        "/api/food/catalog/items",
        json={
            "item_name": "Masala Dosa",
            "price": 60,
            "category": "breakfast",
            "is_available": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["item_name"] == "Masala Dosa"


def test_vendor_status_update_requires_valid_status(client, app):
    _set_current_user(app, role="vendor")

    response = client.put(
        "/api/food/orders/00000000-0000-0000-0000-000000000999/status?new_status=unknown",
    )
    assert response.status_code == 400
    assert "Invalid status value" in response.json()["detail"]


def test_student_cannot_view_vendor_orders(client, app):
    _set_current_user(app, role="student")

    response = client.get("/api/food/orders/vendor")
    assert response.status_code == 403
    assert "Only vendors" in response.json()["detail"]


def test_vendor_can_view_vendor_orders(client, app, monkeypatch):
    _set_current_user(app, role="vendor")
    monkeypatch.setattr(food_service, "get_vendor_orders", lambda *_args, **_kwargs: [])

    response = client.get("/api/food/orders/vendor")
    assert response.status_code == 200
    assert response.json() == []


def test_vendor_cannot_mark_remedial_attendance(client, app):
    _set_current_user(app, role="vendor")

    response = client.post(
        "/api/remedial/attendance/mark",
        json={"remedial_code": "ABC123"},
    )
    assert response.status_code == 403
    assert "Only students" in response.json()["detail"]


def test_student_cannot_list_students(client, app):
    _set_current_user(app, role="student")

    response = client.get("/api/students")
    assert response.status_code == 403
    assert "Only admin or faculty" in response.json()["detail"]


def test_faculty_can_list_students(client, app, monkeypatch):
    _set_current_user(app, role="faculty")

    student_obj = SimpleNamespace(
        student_id=UUID("11111111-1111-1111-1111-111111111111"),
        user_id=UUID("22222222-2222-2222-2222-222222222222"),
        registration_number="REG001",
        first_name="Ari",
        last_name="Patel",
        phone="+1-555-0001",
        parent_email="parent@example.com",
        parent_phone="+1-555-0002",
        program="BTech",
        semester=5,
        section="A",
        enrollment_year=2023,
        created_at=datetime(2026, 2, 20, 0, 0, 0),
        user=SimpleNamespace(email="ari@example.com"),
    )

    monkeypatch.setattr(student_service, "list_students", lambda *args, **kwargs: [student_obj])

    response = client.get("/api/students")
    assert response.status_code == 200
    assert response.json()[0]["registration_number"] == "REG001"
    assert response.json()[0]["email"] == "ari@example.com"


def test_create_student_validation_error_returns_400(client, app, monkeypatch):
    _set_current_user(app, role="admin")

    def _raise_validation(*_args, **_kwargs):
        raise ValueError("Email already registered")

    monkeypatch.setattr(student_service, "create_student", _raise_validation)

    response = client.post(
        "/api/students",
        json={
            "registration_number": "REG002",
            "first_name": "Riya",
            "last_name": "Shah",
            "email": "riya@example.com",
            "firebase_uid": "firebase-uid-riya",
            "enrollment_year": 2024,
            "semester": 2,
            "section": "B",
        },
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_get_student_not_found_returns_404(client, app, monkeypatch):
    _set_current_user(app, role="admin")

    def _raise_not_found(*_args, **_kwargs):
        raise LookupError("Student not found")

    monkeypatch.setattr(student_service, "get_student", _raise_not_found)

    response = client.get("/api/students/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    assert response.status_code == 404
    assert "Student not found" in response.json()["detail"]


def test_student_cannot_list_remedial_classes(client, app):
    _set_current_user(app, role="student")

    response = client.get("/api/remedial/classes")
    assert response.status_code == 403
    assert "Only admin or faculty" in response.json()["detail"]


def test_admin_can_list_remedial_classes(client, app, monkeypatch):
    _set_current_user(app, role="admin")
    monkeypatch.setattr(remedial_service, "list_remedial_classes", lambda *args, **kwargs: [])

    response = client.get("/api/remedial/classes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_current_user_prefers_firebase_subject(monkeypatch):
    fake_user = SimpleNamespace(email="firebase@example.com", role="student")

    class FakeQuery:
        def __init__(self, user):
            self.user = user

        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return self.user

    class FakeDB:
        def __init__(self, user):
            self.user = user

        def query(self, *_args, **_kwargs):
            return FakeQuery(self.user)

    monkeypatch.setattr(auth_utils, "_get_subject_from_firebase", lambda _token: ("firebase@example.com", "firebase-uid-1"))

    current_user = auth_utils.get_current_user(token="firebase-token", db=FakeDB(fake_user))
    assert current_user.email == "firebase@example.com"


def test_get_current_user_links_by_email_when_uid_not_present(monkeypatch):
    fake_user = SimpleNamespace(email="firebase@example.com", role="faculty", firebase_uid=None)

    class FakeQuery:
        def __init__(self, user):
            self.user = user

        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return self.user

    class FakeDB:
        def __init__(self, user):
            self.user = user

        def query(self, *_args, **_kwargs):
            return FakeQuery(self.user)

    monkeypatch.setattr(auth_utils, "_get_subject_from_firebase", lambda _token: ("firebase@example.com", "firebase-uid-1"))

    current_user = auth_utils.get_current_user(token="firebase-token", db=FakeDB(fake_user))
    assert current_user.email == "firebase@example.com"


def test_get_current_user_raises_if_no_valid_subject(monkeypatch):
    class FakeDB:
        def query(self, *_args, **_kwargs):
            return self

        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return None

    monkeypatch.setattr(auth_utils, "_get_subject_from_firebase", lambda _token: (None, None))

    with pytest.raises(HTTPException) as exc:
        auth_utils.get_current_user(token="bad-token", db=FakeDB())

    assert exc.value.status_code == 401
