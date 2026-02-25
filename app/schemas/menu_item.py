from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# -------------------------
# Create Attribute
# -------------------------
class ItemAttributeCreate(BaseModel):
    key: str
    value: str


# -------------------------
# Create Menu Item
# -------------------------
class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    restaurant_id: int
    attributes: List[ItemAttributeCreate]


# -------------------------
# Update Menu Item (Partial Update)
# -------------------------
class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


# -------------------------
# Attribute Response
# -------------------------
class ItemAttributeResponse(BaseModel):
    id: int
    key: str
    value: str

    model_config = {
        "from_attributes" : True
    }


# -------------------------
# Menu Item Response
# -------------------------
class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    is_available: bool
    restaurant_id: int
    created_at: datetime
    attributes: List[ItemAttributeResponse]

    class Config:
        from_attributes = True