from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# -------------------------
# Variant Schemas
# -------------------------
class FoodVariantCreate(BaseModel):
    name: str
    price: float


class FoodVariantResponse(BaseModel):
    id: int
    name: str
    price: float

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Specification Schemas
# -------------------------
class FoodSpecificationCreate(BaseModel):
    label: str
    value: str


class FoodSpecificationResponse(BaseModel):
    id: int
    label: str
    value: str

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Create Food Item
# -------------------------
class MenuItemCreate(BaseModel):
    name: str
    description: str
    rating: float = 0.0
    is_available: bool = True
    restaurant_id: int
    variants: List[FoodVariantCreate]
    specifications: List[FoodSpecificationCreate]


# -------------------------
# Update Food Item (Partial)
# -------------------------
class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    is_available: Optional[bool] = None


# -------------------------
# Food Item Response
# -------------------------
class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str
    rating: float
    is_available: bool
    restaurant_id: int
    created_at: datetime
    variants: List[FoodVariantResponse]
    specifications: List[FoodSpecificationResponse]

    model_config = {
        "from_attributes": True
    }