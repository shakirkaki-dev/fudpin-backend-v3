from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.core.database import get_db

# Models
from app.models.restaurant import Restaurant
from app.models.menu_item import FoodItem
from app.models.food_variant import FoodVariant
from app.models.food_specification import FoodSpecification

# Schemas
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate
)
from app.schemas.menu_item import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate
)
from app.schemas.restaurant_menu import RestaurantMenuResponse

app = FastAPI()


# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health_check():
    return {"status": "Fudpin Backend Running"}


# -------------------------
# Create Restaurant
# -------------------------
@app.post("/restaurants", response_model=RestaurantResponse)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db)
):
    new_restaurant = Restaurant(
        name=restaurant.name,
        description=restaurant.description,
        address=restaurant.address,
        landmark=restaurant.landmark,
        phone=restaurant.phone,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant


# -------------------------
# Update Restaurant
# -------------------------
@app.put("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    update_data = restaurant_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)

    return restaurant


# -------------------------
# Create Food Item
# -------------------------
@app.post("/menu-items", response_model=MenuItemResponse)
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
# Get Restaurant Menu
# -------------------------
@app.get("/restaurants/{restaurant_id}/menu", response_model=RestaurantMenuResponse)
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


# -------------------------
# Get Single Food Item
# -------------------------
@app.get("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
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
@app.put("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
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
@app.delete("/menu-items/{menu_item_id}")
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


# -------------------------
# SEARCH API (Safe Distance)
# -------------------------
@app.get("/search")
def search_food(
    food: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(...),
    db: Session = Depends(get_db)
):
    distance_formula = (
        6371 * func.acos(
            func.least(
                1,
                func.greatest(
                    -1,
                    func.cos(func.radians(lat)) *
                    func.cos(func.radians(Restaurant.latitude)) *
                    func.cos(func.radians(Restaurant.longitude) - func.radians(lng)) +
                    func.sin(func.radians(lat)) *
                    func.sin(func.radians(Restaurant.latitude))
                )
            )
        )
    )

    query = (
        db.query(
            Restaurant.id,
            Restaurant.name,
            FoodItem.id,
            distance_formula.label("distance"),
            FoodItem
        )
        .join(FoodItem, FoodItem.restaurant_id == Restaurant.id)
        .filter(FoodItem.name.ilike(f"%{food}%"))
        .filter(distance_formula <= radius)
        .order_by(distance_formula.asc())
    )

    results = query.all()

    response = []

    for restaurant_id, restaurant_name, food_item_id, distance, item in results:
        starting_price = min([v.price for v in item.variants]) if item.variants else None

        response.append({
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant_name,
            "food_item_id": food_item_id,
            "food_name": item.name,
            "distance_km": round(distance, 2) if distance else 0,
            "starting_price": starting_price
        })

    return response