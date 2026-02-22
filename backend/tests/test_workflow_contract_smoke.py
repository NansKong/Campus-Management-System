from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import attendance, food, remedial
from app.database import get_db
from app.services import attendance_service
from app.utils import auth as auth_utils


class DummyDB:
    def query(self, *_args, **_kwargs):
        return self

    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def count(self):
        return 0


def _override_db():
    yield DummyDB()


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
    test_app.include_router(food.router, prefix="/api/food", tags=["Food"])
    test_app.include_router(remedial.router, prefix="/api/remedial", tags=["Remedial"])
    test_app.dependency_overrides[get_db] = _override_db
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


def _set_current_user(app, role, user_id="00000000-0000-0000-0000-000000000001"):
    fake_user = SimpleNamespace(role=role, email="user@example.com", user_id=UUID(user_id))

    def _override_user():
        return fake_user

    app.dependency_overrides[auth_utils.get_current_user] = _override_user
    return fake_user


def test_student_cannot_access_faculty_sections(client, app):
    _set_current_user(app, role="student")

    response = client.get("/api/attendance/sections/my")
    assert response.status_code == 403
    assert "Only faculty" in response.json()["detail"]


def test_student_cannot_mark_attendance(client, app):
    _set_current_user(app, role="student")

    response = client.post(
        "/api/attendance/sessions/00000000-0000-0000-0000-000000000010/mark",
        json={
            "attendance_records": [
                {
                    "student_id": "00000000-0000-0000-0000-000000000011",
                    "status": "present",
                }
            ]
        },
    )
    assert response.status_code == 403
    assert "Only faculty" in response.json()["detail"]


def test_faculty_can_get_section_students_when_service_returns_data(client, app, monkeypatch):
    _set_current_user(app, role="faculty")

    monkeypatch.setattr(
        attendance_service,
        "list_section_students",
        lambda *_args, **_kwargs: [
            SimpleNamespace(
                student_id=UUID("00000000-0000-0000-0000-000000000021"),
                registration_number="REG1001",
                first_name="Asha",
                last_name="Rao",
                section="A",
                semester=5,
                phone="+1-555-1111",
                parent_phone="+1-555-2222",
            )
        ],
    )
    monkeypatch.setattr(
        attendance_service,
        "serialize_student",
        lambda student: {
            "student_id": student.student_id,
            "registration_number": student.registration_number,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "section": student.section,
            "semester": student.semester,
            "phone": student.phone,
            "parent_phone": student.parent_phone,
        },
    )
    monkeypatch.setattr(
        attendance,
        "_get_faculty_profile",
        lambda *_args, **_kwargs: SimpleNamespace(
            faculty_id=UUID("00000000-0000-0000-0000-000000000020")
        ),
    )

    response = client.get("/api/attendance/sections/00000000-0000-0000-0000-000000000022/students")
    assert response.status_code == 200
    assert response.json()[0]["registration_number"] == "REG1001"


def test_student_remedial_history_requires_student_profile(client, app):
    _set_current_user(app, role="student")

    response = client.get("/api/remedial/attendance/my-history")
    assert response.status_code == 404


def test_invalid_status_payload_for_vendor_order_update_returns_400(client, app):
    _set_current_user(app, role="vendor")

    response = client.put(
        "/api/food/orders/00000000-0000-0000-0000-000000000040/status",
        json={"status": "invalid"},
    )
    assert response.status_code == 422
