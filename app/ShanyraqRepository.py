from pydantic import BaseModel, field_validator, EmailStr
from fastapi import HTTPException
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
    comments = relationship("CommentDB", back_populates="shanyrak", cascade="all, delete")

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

class AdUpdateRequest(BaseModel):
    type: Optional[str] = None
    price: Optional[int] = None
    address: Optional[str] = None
    area: Optional[float] = None
    rooms_count: Optional[int] = None
    description: Optional[str] = None

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
    total_comments: int


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
    
    def update_ad(self, db: Session, ad_id: int, us_id: int, **kwargs):
        db_ad = db.query(AdsDB).filter(AdsDB.id == ad_id).first()
        if not db_ad:
            return None
        if db_ad.user_id != us_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        for key, value in kwargs.items():
            setattr(db_ad, key, value) 
        db.commit()
        db.refresh(db_ad)
        return db_ad
    
    def delete_ad(self, db: Session, ad_id: int, us_id: int):
        db_ad = db.query(AdsDB).filter(AdsDB.id == ad_id).first()
        if db_ad is None:
            return None
        if db_ad.user_id != us_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        db.delete(db_ad)
        db.commit()
        return db_ad
    

    
