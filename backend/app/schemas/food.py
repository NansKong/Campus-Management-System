from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

MenuCategory = Literal["breakfast", "lunch", "snacks", "beverages", "other"]
OrderStatus = Literal["pending", "confirmed", "ready", "completed", "cancelled"]


class MenuItemBase(BaseModel):
    item_name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Decimal = Field(gt=0)
    category: Optional[MenuCategory] = None
    is_available: bool = True
    preparation_time: Optional[int] = Field(default=None, ge=1, le=180)
    image_url: Optional[str] = Field(default=None, max_length=500)


class MenuItemCreate(MenuItemBase):
    vendor_id: Optional[str] = None


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[Decimal] = Field(default=None, gt=0)
    category: Optional[MenuCategory] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(default=None, ge=1, le=180)
    image_url: Optional[str] = Field(default=None, max_length=500)


class MenuItemResponse(BaseModel):
    item_id: str
    vendor_id: str
    item_name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    is_available: bool
    preparation_time: Optional[int]
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    item_id: str
    quantity: int = Field(ge=1, le=20)


class FoodOrderCreate(BaseModel):
    vendor_id: str
    slot_id: str
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, items: List[OrderItemCreate]) -> List[OrderItemCreate]:
        if not items:
            raise ValueError("At least one order item is required")
        return items


class FoodOrderResponse(BaseModel):
    order_id: str
    order_date: date
    total_amount: Decimal
    status: OrderStatus
    pickup_code: Optional[str]
    vendor_id: str
    slot_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class BreakTimeSlotResponse(BaseModel):
    slot_id: str
    slot_name: Optional[str]
    start_time: str
    end_time: str
    max_orders_per_slot: int
    is_active: bool
