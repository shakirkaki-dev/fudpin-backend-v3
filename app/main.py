from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db

# Models (only what search needs)
from app.models.restaurant import Restaurant
from app.models.menu_item import FoodItem

# Routers
from app.routers import restaurant
from app.routers import menu_item


app = FastAPI()

# Include Routers
app.include_router(restaurant.router)
app.include_router(menu_item.router)


# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health_check():
    return {"status": "Fudpin Backend Running"}


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