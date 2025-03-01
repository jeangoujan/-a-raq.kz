from fastapi import FastAPI, Form, Request, HTTPException, Response, Depends
from .database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from .UserRepository import UserDB, UserRequest, UserResponse, UsersRepository
from .tools import create_jwt, decode_jwt

app = FastAPI()
user_repo = UsersRepository()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return Response("Sanyraq Project", status_code=200)

#Authorization ------------------------------
@app.post("/auth/users")
def create_user(input: UserRequest, db: Session = Depends(get_db)):
    if user_repo.get_user_by_email(db, input.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    user = user_repo.create_user(db, UserRequest(email=input.email, phone=input.phone, password=input.password, name=input.name, city=input.city))
    return Response("OK", status_code=200)

@app.post("/auth/users/login")
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_email(db, username)

    if user is None or user.password != password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_jwt(user.id)
    return Response({"access_token": token}, status_code=200)

    
