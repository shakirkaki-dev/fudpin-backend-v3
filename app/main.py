from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db

# Models
from app.models.restaurant import Restaurant
from app.models.menu_item import MenuItem
from app.models.item_attribute import ItemAttribute

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
    return {"status": "Fudpin Backend V3 Running"}


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
        phone=restaurant.phone,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant


# -------------------------
# Update Restaurant (Partial)
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
# Create Menu Item + Attributes
# -------------------------
@app.post("/menu-items", response_model=MenuItemResponse)
def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    new_menu_item = MenuItem(
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
        restaurant_id=menu_item.restaurant_id
    )

    db.add(new_menu_item)
    db.flush()

    for attr in menu_item.attributes:
        new_attr = ItemAttribute(
            key=attr.key,
            value=attr.value,
            menu_item_id=new_menu_item.id
        )
        db.add(new_attr)

    db.commit()
    db.refresh(new_menu_item)

    return new_menu_item


# -------------------------
# Get Restaurant Menu (Only Available Items)
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
            .joinedload(MenuItem.attributes)
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
# Get Single Menu Item
# -------------------------
@app.get("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
):

    menu_item = (
        db.query(MenuItem)
        .options(joinedload(MenuItem.attributes))
        .filter(MenuItem.id == menu_item_id)
        .first()
    )

    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return menu_item


# -------------------------
# Update Menu Item (Partial Update)
# -------------------------
@app.put("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(
    menu_item_id: int,
    menu_item_data: MenuItemUpdate,
    db: Session = Depends(get_db)
):

    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    update_data = menu_item_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(menu_item, key, value)

    db.commit()
    db.refresh(menu_item)

    return menu_item


# -------------------------
# Delete Menu Item
# -------------------------
@app.delete("/menu-items/{menu_item_id}")
def delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
):

    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(menu_item)
    db.commit()

    return {"message": "Menu item deleted successfully"}