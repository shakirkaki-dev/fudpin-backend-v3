from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RestaurantCreate(BaseModel):
    name: str
    description: str
    address: str
    phone: str
    latitude: float
    longitude: float


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None


class RestaurantResponse(BaseModel):
    id: int
    name: str
    description: str
    address: str
    phone: str
    latitude: float
    longitude: float
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes" : True
    }