from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.food import FoodMenuItem, FoodVendor, BreakTimeSlot

router = APIRouter()

@router.get("/debug/food-data")
def get_food_data(db: Session = Depends(get_db)):
    """Debug endpoint to check food data"""
    
    vendors = db.query(FoodVendor).all()
    items = db.query(FoodMenuItem).all()
    slots = db.query(BreakTimeSlot).all()
    
    return {
        "vendors": [
            {
                "vendor_id": str(v.vendor_id),
                "vendor_name": v.vendor_name
            }
            for v in vendors
        ],
        "menu_items": [
            {
                "item_id": str(i.item_id),
                "item_name": i.item_name,
                "vendor_id": str(i.vendor_id),
                "price": float(i.price)
            }
            for i in items
        ],
        "time_slots": [
            {
                "slot_id": str(s.slot_id),
                "slot_name": s.slot_name
            }
            for s in slots
        ]
    }