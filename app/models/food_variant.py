from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class FoodVariant(Base):
    __tablename__ = "food_variants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)

    # Relationship back to FoodItem
    food_item = relationship("FoodItem", back_populates="variants")