from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class ItemAttribute(Base):
    __tablename__ = "item_attributes"

    id = Column(Integer, primary_key=True, index=True)

    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)

    menu_item = relationship("MenuItem", back_populates="attributes")