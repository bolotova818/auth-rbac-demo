from fastapi import APIRouter, HTTPException, status, Body, Depends
from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session

from shemas import UserCreate, UserOut, UserLogin, UserUpdate
from users import create_user, authenticate_user, update_user, delete_user
from authen import create_access_token, get_current_user
from db import get_db
from models import RefreshToken, User

router = APIRouter(prefix="/users", tags=["users"])

REFRESH_TTL_DAYS = 14


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email уже есть в системе",
        )
    return user


@router.post("/login")
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    access_token = create_access_token(user.id)

    refresh_str = secrets.token_urlsafe(32)
    rt = RefreshToken(
        user_id=user.id,
        token=refresh_str,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TTL_DAYS),
        revoked=False,
    )
    db.add(rt)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_str,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    rec = db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.revoked == False).first()
    if not rec or rec.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный refresh token")

    user = db.query(User).filter(User.id == rec.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    rec = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    if rec:
        rec.revoked = True
        db.commit()
    return {"ok": True}


@router.post("/logout_all")
def logout_all(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    db.commit()
    return {"ok": True}


@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    updated_user = update_user(db, current_user.id, data)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return updated_user


@router.delete("/me", response_model=UserOut)
def delete_me(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    deleted_user = delete_user(db, current_user.id)
    if deleted_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return deleted_user
