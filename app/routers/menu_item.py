from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.restaurant import Restaurant
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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):

    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == menu_item.restaurant_id,
            Restaurant.owner_id == current_user.id
        )
        .first()
    )

    if not restaurant:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add menu to this restaurant"
        )

    new_item = FoodItem(
        name=menu_item.name,
        description=menu_item.description,
        rating=menu_item.rating,
        restaurant_id=menu_item.restaurant_id,
        is_available=menu_item.is_available
    )

    db.add(new_item)
    db.flush()

    # add variants
    for variant in menu_item.variants:
        db.add(
            FoodVariant(
                name=variant.name,
                price=variant.price,
                food_item_id=new_item.id
            )
        )

    # add specifications
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
# Get Food Item
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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):

    food_item = (
        db.query(FoodItem)
        .join(Restaurant)
        .filter(
            FoodItem.id == menu_item_id,
            Restaurant.owner_id == current_user.id
        )
        .first()
    )

    if not food_item:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this food item"
        )

    # update basic fields
    if menu_item_data.name is not None:
        food_item.name = menu_item_data.name

    if menu_item_data.description is not None:
        food_item.description = menu_item_data.description

    if menu_item_data.rating is not None:
        food_item.rating = menu_item_data.rating

    if menu_item_data.is_available is not None:
        food_item.is_available = menu_item_data.is_available

    # -------------------------
    # Update variants
    # -------------------------
    if menu_item_data.variants is not None:

        db.query(FoodVariant).filter(
            FoodVariant.food_item_id == menu_item_id
        ).delete()

        for variant in menu_item_data.variants:
            db.add(
                FoodVariant(
                    name=variant.name,
                    price=variant.price,
                    food_item_id=menu_item_id
                )
            )

    # -------------------------
    # Update specifications
    # -------------------------
    if menu_item_data.specifications is not None:

        db.query(FoodSpecification).filter(
            FoodSpecification.food_item_id == menu_item_id
        ).delete()

        for spec in menu_item_data.specifications:
            db.add(
                FoodSpecification(
                    label=spec.label,
                    value=spec.value,
                    food_item_id=menu_item_id
                )
            )

    db.commit()

    updated_item = (
        db.query(FoodItem)
        .options(
            joinedload(FoodItem.variants),
            joinedload(FoodItem.specifications)
        )
        .filter(FoodItem.id == menu_item_id)
        .first()
    )

    return updated_item


# -------------------------
# Delete Food Item
# -------------------------
@router.delete("/{menu_item_id}")
def delete_food_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):

    food_item = (
        db.query(FoodItem)
        .join(Restaurant)
        .filter(
            FoodItem.id == menu_item_id,
            Restaurant.owner_id == current_user.id
        )
        .first()
    )

    if not food_item:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this food item"
        )

    db.delete(food_item)
    db.commit()

    return {"message": "Food item deleted successfully"}