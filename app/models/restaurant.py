from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String)
    address = Column(String)
    phone = Column(String)

    latitude = Column(Float)
    longitude = Column(Float)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to MenuItem
    menu_items = relationship(
        "MenuItem",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )