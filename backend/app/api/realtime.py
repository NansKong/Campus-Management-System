import asyncio
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import func

from app.config import settings
from app.database import SessionLocal
from app.models.user import User
from app.services import ai_service, food_service
from app.utils import auth as auth_utils

router = APIRouter()


def _role_to_str(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _resolve_user_from_token(token: str, db) -> Optional[User]:
    firebase_email, firebase_uid = auth_utils._get_subject_from_firebase(token)
    if not firebase_uid:
        return None

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user is None and firebase_email:
        user = db.query(User).filter(func.lower(User.email) == firebase_email).first()
    return user


@router.websocket("/ws/food-rush")
async def ws_food_rush(websocket: WebSocket):
    await websocket.accept()

    token = websocket.query_params.get("token")
    if not token:
        await websocket.send_json({"error": "Missing authentication token"})
        await websocket.close(code=4401)
        return

    with SessionLocal() as db:
        user = _resolve_user_from_token(token, db)
        if not user:
            await websocket.send_json({"error": "Invalid authentication token"})
            await websocket.close(code=4401)
            return

        role = _role_to_str(user.role)
        if role not in {"student", "vendor", "admin"}:
            await websocket.send_json({"error": "Role not authorized for realtime rush feed"})
            await websocket.close(code=4403)
            return

        vendor_id = None
        if role == "vendor":
            vendor = food_service.get_vendor_for_user(db, user.user_id)
            if not vendor:
                await websocket.send_json({"error": "Vendor profile not found"})
                await websocket.close(code=4404)
                return
            vendor_id = vendor.vendor_id
        else:
            raw_vendor_id = websocket.query_params.get("vendor_id")
            if raw_vendor_id:
                try:
                    vendor_id = UUID(raw_vendor_id)
                except ValueError:
                    await websocket.send_json({"error": "Invalid vendor_id format"})
                    await websocket.close(code=4400)
                    return

    interval = max(3, int(getattr(settings, "FOOD_RUSH_WS_INTERVAL_SECONDS", 8)))

    try:
        while True:
            with SessionLocal() as db:
                payload = ai_service.predict_food_rush(db=db, vendor_id=vendor_id)

            payload["timestamp"] = datetime.utcnow().isoformat()
            await websocket.send_json(payload)
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        return
    except Exception as exc:
        try:
            await websocket.send_json({"error": str(exc)})
            await websocket.close(code=1011)
        except Exception:
            return
