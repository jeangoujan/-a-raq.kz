from fastapi import FastAPI, Form, Request, HTTPException, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from .UserRepository import UserDB, UserRequest, UserResponse, UsersRepository, UserUpdate
from .tools import create_jwt, decode_jwt

app = FastAPI()
user_repo = UsersRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")
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

# Регистрация ------------------------------
@app.post("/auth/users")
def create_user(input: UserRequest, db: Session = Depends(get_db)):
    if user_repo.get_user_by_username(db, input.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = user_repo.create_user(db, UserRequest(username=input.username, phone=input.phone, password=input.password, name=input.name, city=input.city))
    return Response("OK", status_code=200)

# Авторизация ------------------------------
@app.post("/auth/users/login")
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_username(db, username)

    if user is None or user.password != password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_jwt(user.id)
    return JSONResponse(content={"access_token": token}, status_code=200)

# Изменение данных пользователя -------------
@app.patch("/auth/users/me")
def update_user(update_user: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    user = user_repo.update_user(db, user_id, phone=update_user.phone, name=update_user.name, city=update_user.city)
    return Response("OK", status_code=200)
