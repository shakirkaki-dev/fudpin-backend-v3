from pydantic import BaseModel
from typing import List
from .menu_item import MenuItemResponse


class RestaurantMenuResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    menu: List[MenuItemResponse]

    class Config:
        orm_mode = True