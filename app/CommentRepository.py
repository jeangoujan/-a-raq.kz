from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from fastapi import HTTPException
from sqlalchemy.sql import func
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Session
from .database import Base
from pydantic import BaseModel
import pytz


local_timezone = pytz.timezone("Asia/Almaty")

class CommentDB(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(local_timezone))
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shanyrak_id = Column(Integer, ForeignKey("ads.id"), nullable=False)

    author = relationship("UserDB", back_populates="comments")
    shanyrak = relationship("AdsDB", back_populates="comments")

class CommentRequest(BaseModel):
    content: str

class CommentRepository:
    def __init__(self):
        pass

    def add_comment(self, db: Session, user_id: int, shanyrak_id: int, content: str):
        comment = CommentDB(author_id=user_id, shanyrak_id=shanyrak_id, content=content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def get_comment_by_id(self, db: Session, comment_id: int):
        return db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    
    def get_all_comments(self, db: Session, shanyrak_id: int):
        comments = db.query(CommentDB).filter(CommentDB.shanyrak_id==shanyrak_id).all()
        return {
            "comments": [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at,
                    "author_id": comment.author_id
                }
                for comment in comments
            ]
        }
    
    def get_total_comments(self, db: Session, shanyrak_id):
        comments = db.query(CommentDB).filter(CommentDB.shanyrak_id==shanyrak_id).all()
        total = 0
        for comment in comments:
            total += 1
        return total

    def update_comment(self, db: Session, comment_id: int, user_id: int, **kwargs):
        db_comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
        if not db_comment:
            return None
        if db_comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        for key, value in kwargs.items():
            setattr(db_comment, key, value)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    def delete_comment(self, db: Session, comment_id: int, user_id: int):
        db_comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
        if db_comment is None:
            return None
        if db_comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        db.delete(db_comment)
        db.commit()
        return db_comment