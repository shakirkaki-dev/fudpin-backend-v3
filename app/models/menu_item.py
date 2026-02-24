from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)

    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

    # Relationship to Restaurant
    restaurant = relationship("Restaurant", back_populates="menu_items")

    # Relationship to ItemAttribute
    attributes = relationship(
        "ItemAttribute",
        back_populates="menu_item",
        cascade="all, delete-orphan"
    )