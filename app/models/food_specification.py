from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class FoodSpecification(Base):
    __tablename__ = "food_specifications"

    id = Column(Integer, primary_key=True, index=True)

    label = Column(String, nullable=False)
    value = Column(String, nullable=False)

    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)

    # Relationship back to FoodItem
    food_item = relationship("FoodItem", back_populates="specifications")