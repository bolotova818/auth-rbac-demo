from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from authen import get_current_user
from models import BusinessObject, User
from business import check_read_allowed

router = APIRouter(prefix="/objects", tags=["objects"])


@router.get("")
def list_objects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    # проверяем доступ
    try:
        check_read_allowed(db, user_id=user_id, element_code="objects")
        return db.query(BusinessObject).all()
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            return db.query(BusinessObject).filter(BusinessObject.owner_id == user_id).all()
        raise


@router.get("/{object_id}")
def get_object(
    object_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id

    obj = db.query(BusinessObject).filter(BusinessObject.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объект не найден")
    
    check_read_allowed(db, user_id=user_id, element_code="objects", resource_owner_id=obj.owner_id)
    return obj
