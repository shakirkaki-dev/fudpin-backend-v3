from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db

from app.models.menu_item import FoodItem
from app.models.food_variant import FoodVariant
from app.models.food_specification import FoodSpecification

from app.schemas.menu_item import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate
)

router = APIRouter(
    prefix="/menu-items",
    tags=["Menu Items"]
)


# -------------------------
# Create Food Item
# -------------------------
@router.post("", response_model=MenuItemResponse)
def create_food_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    new_item = FoodItem(
        name=menu_item.name,
        description=menu_item.description,
        rating=menu_item.rating,
        restaurant_id=menu_item.restaurant_id,
        is_available=menu_item.is_available
    )

    db.add(new_item)
    db.flush()

    # Add variants
    for variant in menu_item.variants:
        db.add(
            FoodVariant(
                name=variant.name,
                price=variant.price,
                food_item_id=new_item.id
            )
        )

    # Add specifications
    for spec in menu_item.specifications:
        db.add(
            FoodSpecification(
                label=spec.label,
                value=spec.value,
                food_item_id=new_item.id
            )
        )

    db.commit()
    db.refresh(new_item)

    return new_item


# -------------------------
# Get Single Food Item
# -------------------------
@router.get("/{menu_item_id}", response_model=MenuItemResponse)
def get_food_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
):
    food_item = (
        db.query(FoodItem)
        .options(
            joinedload(FoodItem.variants),
            joinedload(FoodItem.specifications)
        )
        .filter(FoodItem.id == menu_item_id)
        .first()
    )

    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")

    return food_item


# -------------------------
# Update Food Item
# -------------------------
@router.put("/{menu_item_id}", response_model=MenuItemResponse)
def update_food_item(
    menu_item_id: int,
    menu_item_data: MenuItemUpdate,
    db: Session = Depends(get_db)
):
    food_item = db.query(FoodItem).filter(FoodItem.id == menu_item_id).first()

    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")

    update_data = menu_item_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(food_item, key, value)

    db.commit()
    db.refresh(food_item)

    return food_item


# -------------------------
# Delete Food Item
# -------------------------
@router.delete("/{menu_item_id}")
def delete_food_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
):
    food_item = db.query(FoodItem).filter(FoodItem.id == menu_item_id).first()

    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")

    db.delete(food_item)
    db.commit()

    return {"message": "Food item deleted successfully"}