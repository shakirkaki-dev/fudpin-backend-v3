from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.restaurant import Restaurant
from app.models.menu_item import FoodItem


router = APIRouter(
    prefix="",
    tags=["Search"]
)


# -------------------------
# SEARCH API (Geo + Pagination)
# -------------------------
@router.get("/search")
def search_food(
    food: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Haversine distance formula
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

    # Base query (without pagination)
    base_query = (
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
    )

    # Total matching results
    total_results = base_query.count()

    # Calculate total pages
    total_pages = (total_results + limit - 1) // limit if total_results > 0 else 0

    # Apply sorting + pagination
    paginated_query = (
        base_query
        .order_by(distance_formula.asc())
        .limit(limit)
        .offset(offset)
    )

    results = paginated_query.all()

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

    return {
        "page": page,
        "limit": limit,
        "total_results": total_results,
        "total_pages": total_pages,
        "results": response
    }