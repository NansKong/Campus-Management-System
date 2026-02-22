from sqlalchemy import Column, String, Boolean, Integer, Numeric, ForeignKey, DateTime, Date, Time, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class FoodVendor(Base):
    __tablename__ = "food_vendors"
    
    vendor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    vendor_name = Column(String(200), nullable=False)
    stall_location = Column(String(200))
    contact_phone = Column(String(15))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    menu_items = relationship("FoodMenuItem", back_populates="vendor")
    orders = relationship("FoodOrder", back_populates="vendor")
    
    def __repr__(self):
        return f"<Vendor {self.vendor_name}>"

class FoodMenuItem(Base):
    __tablename__ = "food_menu_items"
    
    item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('food_vendors.vendor_id'))
    item_name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50))  # 'breakfast', 'lunch', 'snacks', 'beverages'
    is_available = Column(Boolean, default=True)
    preparation_time = Column(Integer)  # in minutes
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor = relationship("FoodVendor", back_populates="menu_items")
    
    def __repr__(self):
        return f"<MenuItem {self.item_name}>"

class BreakTimeSlot(Base):
    __tablename__ = "break_time_slots"
    
    slot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slot_name = Column(String(50))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_orders_per_slot = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    orders = relationship("FoodOrder", back_populates="slot")
    
    def __repr__(self):
        return f"<Slot {self.slot_name}>"

class FoodOrder(Base):
    __tablename__ = "food_orders"
    
    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.student_id'))
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('food_vendors.vendor_id'))
    slot_id = Column(UUID(as_uuid=True), ForeignKey('break_time_slots.slot_id'))
    order_date = Column(Date, nullable=False)
    order_time = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default='pending')  # 'pending', 'confirmed', 'ready', 'completed', 'cancelled'
    pickup_code = Column(String(10), unique=True)
    picked_up_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")
    vendor = relationship("FoodVendor", back_populates="orders")
    slot = relationship("BreakTimeSlot", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    
    def __repr__(self):
        return f"<Order {self.pickup_code}>"

class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('food_orders.order_id', ondelete='CASCADE'))
    item_id = Column(UUID(as_uuid=True), ForeignKey('food_menu_items.item_id'))
    quantity = Column(Integer, nullable=False)
    item_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order = relationship("FoodOrder", back_populates="items")
    menu_item = relationship("FoodMenuItem")
    
    def __repr__(self):
        return f"<OrderItem {self.quantity}x>"