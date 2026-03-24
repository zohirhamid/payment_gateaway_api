from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, String, Integer

from app.db.base import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    