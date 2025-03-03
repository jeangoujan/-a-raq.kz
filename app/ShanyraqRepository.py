from pydantic import BaseModel, field_validator, EmailStr
import re
from .database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import Session, relationship
from typing import Optional

class AdsDB(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    price = Column(Integer)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="ads")

class AdRequest(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str

    @field_validator("price", mode="before")
    def price_validator(cls, value):
        if value < 0:
            raise ValueError("Price must be positive")
        return value
    
    @field_validator("area", mode="before")
    def area_validator(cls, value):
        if value < 0:
            raise ValueError("Area must be positive")
        return value

    @field_validator("rooms_count", mode="before")
    def rooms_count_validator(cls, value):
        if value < 0:
            raise ValueError("Rooms count must be positive")
        return value

class AdResponse(BaseModel):
    id: int

class GetAd(BaseModel):
    id: int
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    user_id: Optional[int] = None

class AdRepository():
    def __init__(self):
        pass

    def get_ad_by_id(self, db: Session, ad_id: int):
        return db.query(AdsDB).filter(AdsDB.id == ad_id).first()
    
    def create_ad(self, db: Session, ad: AdRequest, user_id: int):
        db_ad = AdsDB(type=ad.type, price=ad.price, address=ad.address, area=ad.area, rooms_count=ad.rooms_count, description=ad.description, user_id=user_id)
        db.add(db_ad)
        db.commit()
        db.refresh(db_ad)
        return db_ad  