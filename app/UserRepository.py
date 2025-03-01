from pydantic import BaseModel, field_validator, EmailStr
import re
from .database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    city = Column(String)




class UserResponse(BaseModel):
    username: EmailStr
    phone: str
    name: str
    city: str


class UserRequest(BaseModel):
    email: EmailStr
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
        db_user = UserDB(email=user.email, phone=user.phone, password=user.password, name=user.name, city=user.city)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_email(self, db: Session, email: str):
        return db.query(UserDB).filter(UserDB.email == email).first()

    def get_user_by_username(self, db: Session, username: str):
        return db.query(UserDB).filter(UserDB.username == username).first()
    
    
