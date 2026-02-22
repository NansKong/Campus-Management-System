from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.food import (
    BreakTimeSlotResponse,
    FoodOrderCreate,
    FoodOrderResponse,
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
    OrderStatusUpdate,
)
from app.services import food_service
from app.utils.auth import get_current_user

router = APIRouter()


def _role_to_str(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _require_catalog_role(current_user: User) -> str:
    role = _role_to_str(current_user.role)
    if role not in {"admin", "vendor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or vendor can manage food catalog",
        )
    return role


@router.get("/menu", response_model=List[MenuItemResponse])
def get_menu(
    vendor_id: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Public menu listing for available items only."""

    parsed_vendor_id = None
    if vendor_id:
        try:
            parsed_vendor_id = UUID(vendor_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid vendor_id format") from exc

    menu_items = food_service.list_menu_items(
        db=db,
        vendor_id=parsed_vendor_id,
        include_unavailable=False,
        category=category,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [food_service.serialize_menu_item(item) for item in menu_items]


@router.get("/slots", response_model=List[BreakTimeSlotResponse])
def get_active_slots(db: Session = Depends(get_db)):
    slots = food_service.list_active_slots(db)
    return [food_service.serialize_slot(slot) for slot in slots]


@router.get("/catalog/items", response_model=List[MenuItemResponse])
def list_catalog_items(
    vendor_id: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    include_unavailable: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_catalog_role(current_user)

    parsed_vendor_id = None
    if role == "vendor":
        include_unavailable = True
    if vendor_id:
        try:
            parsed_vendor_id = UUID(vendor_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid vendor_id format") from exc

    if role == "vendor":
        vendor = food_service.get_vendor_for_user(db, current_user.user_id)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")
        parsed_vendor_id = vendor.vendor_id

    items = food_service.list_menu_items(
        db=db,
        vendor_id=parsed_vendor_id,
        include_unavailable=include_unavailable,
        category=category,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [food_service.serialize_menu_item(item) for item in items]


@router.post("/catalog/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_catalog_item(
    item_data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_catalog_role(current_user)

    try:
        item = food_service.create_menu_item(
            db=db,
            item_payload=item_data.model_dump(),
            actor_role=role,
            actor_user_id=current_user.user_id,
        )
        return food_service.serialize_menu_item(item)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/catalog/items/{item_id}", response_model=MenuItemResponse)
def update_catalog_item(
    item_id: str,
    item_data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = _require_catalog_role(current_user)

    try:
        item_uuid = UUID(item_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid item_id format") from exc

    payload = item_data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    try:
        item = food_service.update_menu_item(
            db=db,
            item_id=item_uuid,
            item_payload=payload,
            actor_role=role,
            actor_user_id=current_user.user_id,
        )
        return food_service.serialize_menu_item(item)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/orders", response_model=FoodOrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: FoodOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new food order (Student only)."""

    if _role_to_str(current_user.role) != "student":
        raise HTTPException(status_code=403, detail="Only students can place orders")

    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    try:
        vendor_uuid = UUID(order_data.vendor_id)
        slot_uuid = UUID(order_data.slot_id)
        items_with_uuid = [
            {"item_id": UUID(item.item_id), "quantity": item.quantity}
            for item in order_data.items
        ]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid UUID format in order payload") from exc

    try:
        order = food_service.create_food_order(
            db=db,
            vendor_id=vendor_uuid,
            slot_id=slot_uuid,
            items=items_with_uuid,
            student_id=student.student_id,
        )
        return food_service.serialize_order(order)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/orders/my-orders", response_model=List[FoodOrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current student's orders."""

    if _role_to_str(current_user.role) != "student":
        raise HTTPException(status_code=403, detail="Only students can view orders")

    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    orders = food_service.get_student_orders(db, student.student_id)
    return [food_service.serialize_order(order) for order in orders]


@router.get("/orders/vendor", response_model=List[FoodOrderResponse])
def get_vendor_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if _role_to_str(current_user.role) != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can view vendor orders")

    try:
        orders = food_service.get_vendor_orders(db, current_user.user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [food_service.serialize_order(order) for order in orders]


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    status_payload: Optional[OrderStatusUpdate] = Body(default=None),
    new_status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update order status (Vendor only)."""

    if _role_to_str(current_user.role) != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can update status")

    try:
        order_uuid = UUID(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid order_id format") from exc

    status_value = status_payload.status if status_payload else new_status
    if not status_value:
        raise HTTPException(status_code=400, detail="Status value is required")

    if status_value not in {"pending", "confirmed", "ready", "completed", "cancelled"}:
        raise HTTPException(status_code=400, detail="Invalid status value")

    try:
        order = food_service.update_order_status(
            db=db,
            order_id=order_uuid,
            new_status=status_value,
            actor_user_id=current_user.user_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Status updated",
        "order": {
            "order_id": str(order.order_id),
            "status": order.status,
        },
    }
