from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String)
    rating = Column(Float, default=0.0)

    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

    # Relationship to Restaurant
    restaurant = relationship("Restaurant", back_populates="menu_items")

    # Relationship to FoodVariant
    variants = relationship(
        "FoodVariant",
        back_populates="food_item",
        cascade="all, delete-orphan"
    )

    # Relationship to FoodSpecification
    specifications = relationship(
        "FoodSpecification",
        back_populates="food_item",
        cascade="all, delete-orphan"
    )