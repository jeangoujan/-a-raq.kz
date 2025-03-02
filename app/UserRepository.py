from pydantic import BaseModel, field_validator, EmailStr
import re
from .database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from typing import Optional

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    city = Column(String)


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None

    @field_validator("phone", mode="before")
    def phone_validator(cls, value):
        if value and not re.match(r"^\+7\d{10}$", value):
            raise ValueError("Phone number is not valid: must be +7XX-XXX-XX-XX")
        return value
    
    @field_validator("name", mode="before")
    def name_validator(cls, value):
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ .]+$", value):
            raise ValueError("Invalid name: must contain only letters")
        return value


class UserResponse(BaseModel):
    username: EmailStr
    phone: str
    name: str
    city: str


class UserRequest(BaseModel):
    username: EmailStr
    phone: str
    password: str
    name: str
    city: str


    @field_validator("phone", mode="before")
    def phone_validator(cls, value):
        if not re.match(r"^\+7\d{10}$", value):
            raise ValueError("Phone number is not valid: must be +7XX-XXX-XX-XX")
        return value
    
    @field_validator("password", mode="before")
    def password_validator(cls, value):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', value):
            raise ValueError("Invalid password: must 8 characters long and contain at least one letter and one number")
        return value
    
    @field_validator("name", mode="before")
    def name_validator(cls, value):
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ .]+$", value):
            raise ValueError("Invalid name: must contain only letters")
        return value
    
    @field_validator("city", mode="before")
    def city_validator(cls, value):
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ]+$", value):
            raise ValueError("Invalid city: must contain only letters")
        return value
    

class UsersRepository:
    def __init__(self):
        pass

    def create_user(self, db: Session, user: UserRequest):
        db_user = UserDB(username=user.username, phone=user.phone, password=user.password, name=user.name, city=user.city)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_username(self, db: Session, username: str):
        return db.query(UserDB).filter(UserDB.username == username).first()
    
    def get_user_by_id(self, db: Session, user_id: int):
        return db.query(UserDB).filter(UserDB.id == user_id).first()
    
    def update_user(self, db: Session, user_id: int, phone: Optional[str] = None, name: Optional[str] = None, city: Optional[str] = None):
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user is None:
            return None

        validated_data = UserUpdate(phone=phone, name=name, city=city)
        if validated_data.phone is not None:
            db_user.phone = validated_data.phone
        if validated_data.name is not None:
            db_user.name = validated_data.name
        if validated_data.city is not None:
            db_user.city = validated_data.city
        db.commit()
        db.refresh(db_user)
        return db_user


        
        
