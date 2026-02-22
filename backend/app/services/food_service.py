from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.food import BreakTimeSlot, FoodMenuItem, FoodOrder, FoodVendor, OrderItem
from app.utils.helpers import generate_unique_code

ALLOWED_STATUS_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"ready", "cancelled"},
    "ready": {"completed"},
    "completed": set(),
    "cancelled": set(),
}


def _get_active_vendor_by_user(db: Session, user_id: UUID) -> Optional[FoodVendor]:
    return (
        db.query(FoodVendor)
        .filter(FoodVendor.user_id == user_id, FoodVendor.is_active.is_(True))
        .first()
    )


def _get_active_vendor_by_id(db: Session, vendor_id: UUID) -> Optional[FoodVendor]:
    return (
        db.query(FoodVendor)
        .filter(FoodVendor.vendor_id == vendor_id, FoodVendor.is_active.is_(True))
        .first()
    )


def get_vendor_for_user(db: Session, user_id: UUID) -> Optional[FoodVendor]:
    return _get_active_vendor_by_user(db, user_id)


def serialize_menu_item(menu_item: FoodMenuItem) -> dict:
    return {
        "item_id": str(menu_item.item_id),
        "vendor_id": str(menu_item.vendor_id),
        "item_name": menu_item.item_name,
        "description": menu_item.description,
        "price": menu_item.price,
        "category": menu_item.category,
        "is_available": menu_item.is_available,
        "preparation_time": menu_item.preparation_time,
        "image_url": menu_item.image_url,
        "created_at": menu_item.created_at,
    }


def serialize_order(order: FoodOrder) -> dict:
    return {
        "order_id": str(order.order_id),
        "order_date": order.order_date,
        "total_amount": order.total_amount,
        "status": order.status,
        "pickup_code": order.pickup_code,
        "vendor_id": str(order.vendor_id),
        "slot_id": str(order.slot_id),
        "created_at": order.created_at,
    }


def serialize_slot(slot: BreakTimeSlot) -> dict:
    return {
        "slot_id": str(slot.slot_id),
        "slot_name": slot.slot_name,
        "start_time": slot.start_time.isoformat() if slot.start_time else None,
        "end_time": slot.end_time.isoformat() if slot.end_time else None,
        "max_orders_per_slot": slot.max_orders_per_slot,
        "is_active": slot.is_active,
    }


def list_active_slots(db: Session) -> List[BreakTimeSlot]:
    return (
        db.query(BreakTimeSlot)
        .filter(BreakTimeSlot.is_active.is_(True))
        .order_by(BreakTimeSlot.start_time.asc())
        .all()
    )


def list_menu_items(
    db: Session,
    vendor_id: Optional[UUID] = None,
    include_unavailable: bool = False,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[FoodMenuItem]:
    query = db.query(FoodMenuItem)

    if vendor_id:
        query = query.filter(FoodMenuItem.vendor_id == vendor_id)

    if not include_unavailable:
        query = query.filter(FoodMenuItem.is_available.is_(True))

    if category:
        query = query.filter(FoodMenuItem.category == category)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(FoodMenuItem.item_name.ilike(pattern))

    return (
        query.order_by(FoodMenuItem.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def create_menu_item(
    db: Session,
    item_payload: Dict,
    actor_role: str,
    actor_user_id: UUID,
) -> FoodMenuItem:
    payload = dict(item_payload)

    if actor_role == "vendor":
        vendor = _get_active_vendor_by_user(db, actor_user_id)
        if not vendor:
            raise LookupError("Vendor profile not found")
        vendor_id = vendor.vendor_id
    elif actor_role == "admin":
        raw_vendor_id = payload.pop("vendor_id", None)
        if not raw_vendor_id:
            raise ValueError("vendor_id is required for admin menu item creation")
        try:
            vendor_id = UUID(str(raw_vendor_id))
        except ValueError as exc:
            raise ValueError("Invalid vendor_id format") from exc
        vendor = _get_active_vendor_by_id(db, vendor_id)
        if not vendor:
            raise LookupError("Vendor not found")
    else:
        raise PermissionError("Only admin or vendor can manage food catalog")

    duplicate = (
        db.query(FoodMenuItem)
        .filter(
            FoodMenuItem.vendor_id == vendor_id,
            func.lower(FoodMenuItem.item_name) == payload["item_name"].strip().lower(),
        )
        .first()
    )
    if duplicate:
        raise ValueError("Menu item already exists for this vendor")

    try:
        item = FoodMenuItem(
            vendor_id=vendor_id,
            item_name=payload["item_name"].strip(),
            description=payload.get("description"),
            price=payload["price"],
            category=payload.get("category"),
            is_available=payload.get("is_available", True),
            preparation_time=payload.get("preparation_time"),
            image_url=payload.get("image_url"),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except Exception:
        db.rollback()
        raise


def update_menu_item(
    db: Session,
    item_id: UUID,
    item_payload: Dict,
    actor_role: str,
    actor_user_id: UUID,
) -> FoodMenuItem:
    item = db.query(FoodMenuItem).filter(FoodMenuItem.item_id == item_id).first()
    if not item:
        raise LookupError("Menu item not found")

    vendor = None
    if actor_role == "vendor":
        vendor = _get_active_vendor_by_user(db, actor_user_id)
        if not vendor:
            raise LookupError("Vendor profile not found")
        if item.vendor_id != vendor.vendor_id:
            raise PermissionError("Vendors can update only their own menu items")
    elif actor_role != "admin":
        raise PermissionError("Only admin or vendor can manage food catalog")

    payload = dict(item_payload)
    if actor_role == "admin" and "vendor_id" in payload:
        try:
            next_vendor_id = UUID(str(payload["vendor_id"]))
        except ValueError as exc:
            raise ValueError("Invalid vendor_id format") from exc
        next_vendor = _get_active_vendor_by_id(db, next_vendor_id)
        if not next_vendor:
            raise LookupError("Vendor not found")
        item.vendor_id = next_vendor_id
        payload.pop("vendor_id")

    for key, value in payload.items():
        if key == "item_name" and isinstance(value, str):
            setattr(item, key, value.strip())
        else:
            setattr(item, key, value)

    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except Exception:
        db.rollback()
        raise


def create_food_order(
    db: Session,
    vendor_id: UUID,
    slot_id: UUID,
    items: List[Dict],
    student_id: UUID,
) -> FoodOrder:
    vendor = _get_active_vendor_by_id(db, vendor_id)
    if not vendor:
        raise LookupError("Vendor not found")

    slot = (
        db.query(BreakTimeSlot)
        .filter(BreakTimeSlot.slot_id == slot_id, BreakTimeSlot.is_active.is_(True))
        .first()
    )
    if not slot:
        raise LookupError("Break slot not found")

    total_amount = Decimal("0")
    normalized_items: List[Dict] = []
    seen_items = set()

    for item_data in items:
        item_id = item_data["item_id"]
        quantity = int(item_data["quantity"])
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if item_id in seen_items:
            raise ValueError("Duplicate item in order payload")
        seen_items.add(item_id)

        menu_item = (
            db.query(FoodMenuItem)
            .filter(
                FoodMenuItem.item_id == item_id,
                FoodMenuItem.vendor_id == vendor_id,
                FoodMenuItem.is_available.is_(True),
            )
            .first()
        )
        if not menu_item:
            raise LookupError(f"Menu item {item_id} not found for selected vendor")

        subtotal = menu_item.price * quantity
        total_amount += subtotal
        normalized_items.append(
            {
                "item_id": item_id,
                "quantity": quantity,
                "item_price": menu_item.price,
                "subtotal": subtotal,
            }
        )

    pickup_code = generate_unique_code(6)
    while db.query(FoodOrder).filter(FoodOrder.pickup_code == pickup_code).first():
        pickup_code = generate_unique_code(6)

    try:
        new_order = FoodOrder(
            student_id=student_id,
            vendor_id=vendor_id,
            slot_id=slot_id,
            order_date=date.today(),
            total_amount=total_amount,
            pickup_code=pickup_code,
        )
        db.add(new_order)
        db.flush()

        for item in normalized_items:
            db.add(
                OrderItem(
                    order_id=new_order.order_id,
                    item_id=item["item_id"],
                    quantity=item["quantity"],
                    item_price=item["item_price"],
                    subtotal=item["subtotal"],
                )
            )

        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception:
        db.rollback()
        raise


def get_student_orders(db: Session, student_id: UUID) -> List[FoodOrder]:
    return (
        db.query(FoodOrder)
        .filter(FoodOrder.student_id == student_id)
        .order_by(FoodOrder.order_time.desc())
        .all()
    )


def get_vendor_orders(db: Session, actor_user_id: UUID) -> List[FoodOrder]:
    vendor = _get_active_vendor_by_user(db, actor_user_id)
    if not vendor:
        raise LookupError("Vendor profile not found")
    return (
        db.query(FoodOrder)
        .filter(FoodOrder.vendor_id == vendor.vendor_id)
        .order_by(FoodOrder.order_time.desc())
        .all()
    )


def update_order_status(
    db: Session,
    order_id: UUID,
    new_status: str,
    actor_user_id: UUID,
) -> FoodOrder:
    order = db.query(FoodOrder).filter(FoodOrder.order_id == order_id).first()
    if not order:
        raise LookupError("Order not found")

    vendor = _get_active_vendor_by_user(db, actor_user_id)
    if not vendor:
        raise LookupError("Vendor profile not found")
    if order.vendor_id != vendor.vendor_id:
        raise PermissionError("Vendor can update only their own orders")

    current_status = str(order.status)
    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next:
        raise ValueError(
            f"Invalid status transition from '{current_status}' to '{new_status}'"
        )

    try:
        order.status = new_status
        if new_status == "completed":
            order.picked_up_at = datetime.utcnow()
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise
