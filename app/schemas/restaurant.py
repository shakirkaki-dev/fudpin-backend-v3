from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# -------------------------
# Create Restaurant
# -------------------------
class RestaurantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    landmark: Optional[str] = None
    phone: Optional[str] = None
    latitude: float
    longitude: float


# -------------------------
# Update Restaurant (Partial)
# -------------------------
class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None


# -------------------------
# Restaurant Response
# -------------------------
class RestaurantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    address: str
    landmark: Optional[str]
    phone: Optional[str]
    latitude: float
    longitude: float
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }