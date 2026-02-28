from pydantic import BaseModel
from typing import List
from app.schemas.menu_item import MenuItemResponse


class RestaurantMenuResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    menu: List[MenuItemResponse]

    class Config:
        from_attributes = True