from sqlalchemy.orm import Session
from typing import Optional
import bcrypt
from models import User, UserRoles, Roles
from shemas import UserCreate, UserOut, UserLogin, UserUpdate


def create_user(db: Session, user: UserCreate) -> Optional[UserOut]:
    email_norm = user.email.lower()
    existing_user = db.query(User).filter(User.email == email_norm).first()
    if existing_user:
        return None

    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    new_user = User(name=user.name, password_hash=password_hash, email=email_norm)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    default_role = db.query(Roles).filter(Roles.name == "user").first()
    if default_role:
        exists = db.query(UserRoles).filter(
            UserRoles.user_id == new_user.id,
            UserRoles.role_id == default_role.id
        ).first()
        if not exists:
            db.add(UserRoles(user_id=new_user.id, role_id=default_role.id))
            db.commit()
    return UserOut(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        is_active=new_user.is_active,
    )


def authenticate_user(db: Session, user: UserLogin) -> Optional[UserOut]:
    email_norm = user.email.lower()
    existing_user = db.query(User).filter(User.email == email_norm).first()

    if existing_user is None:
        return None

    if not existing_user.is_active:
        return None

    if not bcrypt.checkpw(
        user.password.encode(), existing_user.password_hash.encode("utf-8")
    ):
        return None

    return UserOut(
        id=existing_user.id,
        name=existing_user.name,
        email=existing_user.email,
        is_active=existing_user.is_active,
    )


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[UserOut]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    if data.name is not None:
        user.name = data.name

    if data.email is not None:
        new_email = data.email.lower()
        exists = db.query(User.id).filter(
            User.email == new_email, User.id != user_id
        ).first()
        if exists:

            raise ValueError("email_already_exists")
        user.email = new_email

    if data.password is not None:
        user.password_hash = bcrypt.hashpw(
            data.password.encode(), bcrypt.gensalt()
        ).decode()

    db.commit()
    db.refresh(user)

    return UserOut(id=user.id, name=user.name, email=user.email, is_active=user.is_active)



def delete_user(db: Session, user_id: int) -> Optional[UserOut]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    user.is_active = False
    db.commit()

    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
    )
