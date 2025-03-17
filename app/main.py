from fastapi import FastAPI, Form, Request, HTTPException, Response, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from .UserRepository import UserDB, UserRequest, UserResponse, UsersRepository, UserUpdate
from .ShanyraqRepository import AdsDB, AdRequest, AdResponse, AdRepository, GetAd, AdUpdateRequest
from .CommentRepository import CommentRepository, CommentRequest
from .tools import create_jwt, decode_jwt
from typing import Optional

app = FastAPI()
user_repo = UsersRepository()
ads_repo = AdRepository()
com_repo = CommentRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["User"])
def read_root():
    return Response("Sanyraq Project", status_code=200)

# Регистрация ------------------------------
@app.post("/auth/users", responses={400: {"description": "Username already exists"}}, tags=["User"])
def create_user(input: UserRequest, db: Session = Depends(get_db)):
    if user_repo.get_user_by_username(db, input.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = user_repo.create_user(db, UserRequest(username=input.username, phone=input.phone, password=input.password, name=input.name, city=input.city))
    return Response("OK", status_code=200)

# Авторизация ------------------------------
@app.post("/auth/users/login", responses={400: {"description": "Invalid username or password"}}, tags=["User"])
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_username(db, username)

    if user is None or user.password != password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_jwt(user.id)
    return JSONResponse(content={"access_token": token}, status_code=200)

# Изменение данных пользователя -------------
@app.patch("/auth/users/me", responses={404: {"description": "User not found"}}, tags=["User"])
def update_user(update_user: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = user_repo.update_user(db, user_id, phone=update_user.phone, name=update_user.name, city=update_user.city)
    return Response("OK", status_code=200)

# Получение данных пользователя -------------
@app.get("/auth/users/me", response_model=UserResponse, responses={404: {"description": "User not found"}}, tags=["User"])
def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Создание объявления -----------------------
@app.post("/shanyraks/", response_model=AdResponse, tags=["Ad"])
def create_shanyrak(input: AdRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    ad = ads_repo.create_ad(db, input, user_id)
    return ad

# Получение объявления + Получение объявления - количество комментариев 
@app.get("/shanyraks/{id}/", response_model=GetAd, responses={404: {"description": "Ad not found"}}, tags=["Ad"])
def get_shanyrak(id: int, db: Session = Depends(get_db)):
    ad = ads_repo.get_ad_by_id(db, id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    total_comments = com_repo.get_total_comments(db, id)

    return GetAd(
        id=ad.id,
        type=ad.type,
        price=ad.price,
        address=ad.address,
        area=ad.area,
        rooms_count=ad.rooms_count,
        description=ad.description,
        user_id=ad.user_id,
        total_comments=total_comments
    )

# Изменение объявления ----------------------
@app.patch("/shanyraks/{id}", responses={404: {"description": "Ad not found"}},tags=["Ad"])
def update_shanyrak(id: int, ad: AdUpdateRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    updated_shanyrak = ads_repo.update_ad(db, id, user_id, **ad.model_dump(exclude_unset=True))
    if not updated_shanyrak:
        raise HTTPException(status_code=404, detail="Ad not found")
    return Response("OK", status_code=200)

# Удаление объявления -----------------------
@app.delete("/shanyraks/{id}", responses={404: {"description": "Ad not found"}}, tags=["Ad"])
def delete_shanyrak(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    deleted_shanyrak = ads_repo.delete_ad(db, id, user_id)
    if not deleted_shanyrak:
        raise HTTPException(status_code=404, detail="Ad not found")
    return Response("OK", status_code=200)

# Добавление комментария к объявлению -------
@app.post("/shanyraks/{shanyrak_id}/comments", responses={404: {"description": "Ad not found"}}, tags=["Comments"])
def add_comment(shanyrak_id: int, comment: CommentRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    if not ads_repo.get_ad_by_id(db, shanyrak_id):
        raise HTTPException(status_code=404, detail="Ad not found")
    com_repo.add_comment(db, user_id, shanyrak_id, comment.content)
    return Response("OK", status_code=200)

# Получение списка комментариев объявления ---
@app.get("/shanyraks/{shanyrak_id}/comments", tags=["Comments"])
def get_comments(shanyrak_id: int, db: Session = Depends(get_db)):
    return com_repo.get_all_comments(db, shanyrak_id)

# Изменение текста комментария ---------------
@app.patch("/shanyraks/{shanyrak_id}/comments/{comment_id}", responses={404: {"description": "Ad not found"}}, tags=["Comments"])
def update_comment(shanyrak_id: int, comment: CommentRequest, comment_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    shanyrak = ads_repo.get_ad_by_id(db, shanyrak_id)
    if not shanyrak:
        raise HTTPException(status_code=404, detail="Ad not found")
    updated_comment = com_repo.update_comment(db, comment_id, user_id, **comment.model_dump(exclude_unset=True))
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return Response("OK", status_code=200)

# Удаление комментария -----------------------
@app.delete("/shanyraks/{shanyrak_id}/comments/{comment_id}", responses={404: {"description": "Ad not found"}}, tags=["Comments"])
def delete_comment(shanyrak_id: int, comment_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)

    shanyrak = ads_repo.get_ad_by_id(db, shanyrak_id)
    if not shanyrak:
        raise HTTPException(status_code=404, detail="Ad not found")
    deleted_comment = com_repo.delete_comment(db, comment_id, user_id)
    if not deleted_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return Response("OK", status_code=200)

# Добавление объявления в избранное ---------
@app.post("/auth/users/favorites/{shanyrak_id}", responses={404: {"description": "Ad not found"}}, tags=["Favorites"])
def add_favorite(shanyrak_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    if not ads_repo.get_ad_by_id(db, shanyrak_id):
        raise HTTPException(status_code=404, detail="Ad not found")
    user_repo.add_favorite(db, user_id, shanyrak_id)
    return Response("OK", status_code=200)

# Получение списка избранных ----------------
@app.get("/auth/users/favorites", tags=["Favorites"])
def get_favorites(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    return user_repo.get_favorites(db, user_id)

# Удаление из избранного --------------------
@app.delete("/auth/users/favorites/{shanyrak_id}", responses={404: {"description": "Ad not found"}}, tags=["Favorites"])
def delete_favorites(shanyrak_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    if not ads_repo.get_ad_by_id(db, shanyrak_id):
        raise HTTPException(status_code=404, detail="Ad not found")
    user_repo.delete_favorite(db, user_id, shanyrak_id)
    return Response("OK", status_code=200)

# Получение объявлений с поиском и пагинацией - 
@app.get("/shanyraks/", tags=["Ad"])
def search_shanyraks(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    ad_type: Optional[str] = None,
    rooms_count: Optional[int] = None,
    price_from: Optional[int] = None,
    price_until: Optional[int] = None
):
    print("DEBUG:", db, limit, offset, ad_type, rooms_count, price_from, price_until)
    return ads_repo.search_shanyrak(
        db,
        limit,
        offset,
        ad_type,
        rooms_count,
        price_from,
        price_until)




