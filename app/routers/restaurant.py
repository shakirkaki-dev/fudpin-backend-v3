from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.restaurant import Restaurant
from app.models.menu_item import FoodItem
from app.models.food_variant import FoodVariant
from app.models.food_specification import FoodSpecification
from app.models.user import User

from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate
)
from app.schemas.restaurant_menu import RestaurantMenuResponse


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"]
)


# -------------------------
# Create Restaurant (Owner Protected)
# -------------------------
@router.post("", response_model=RestaurantResponse)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_restaurant = Restaurant(
        name=restaurant.name,
        description=restaurant.description,
        address=restaurant.address,
        landmark=restaurant.landmark,
        phone=restaurant.phone,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
        owner_id=current_user.id
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant


# -------------------------
# Get My Restaurants (Owner or Admin)
# -------------------------
@router.get("/me", response_model=list[RestaurantResponse])
def get_my_restaurants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        return db.query(Restaurant).all()

    return (
        db.query(Restaurant)
        .filter(Restaurant.owner_id == current_user.id)
        .all()
    )


# -------------------------
# Update Restaurant (Owner or Admin)
# -------------------------
@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if current_user.role != "admin" and restaurant.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this restaurant"
        )

    update_data = restaurant_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)

    return restaurant


# -------------------------
# Delete Restaurant (Owner or Admin)
# -------------------------
@router.delete("/{restaurant_id}")
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if current_user.role != "admin" and restaurant.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this restaurant"
        )

    db.delete(restaurant)
    db.commit()

    return {"message": "Restaurant deleted successfully"}


# -------------------------
# Get Restaurant Menu (Public)
# -------------------------
@router.get("/{restaurant_id}/menu", response_model=RestaurantMenuResponse)
def get_restaurant_menu(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    restaurant = (
        db.query(Restaurant)
        .options(
            joinedload(Restaurant.menu_items)
            .joinedload(FoodItem.variants),
            joinedload(Restaurant.menu_items)
            .joinedload(FoodItem.specifications)
        )
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    available_items = [
        item for item in restaurant.menu_items if item.is_available
    ]

    return {
        "restaurant_id": restaurant.id,
        "restaurant_name": restaurant.name,
        "menu": available_items
    }