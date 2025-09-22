from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shemas import UpsertRuleIn
from db import get_db
from authen import get_current_user
from admin import list_rules, upsert_rule

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/rules")
def get_rules(
    role: Optional[str] = Query(default=None, description="Имя роли (опционально)"),
    element: Optional[str] = Query(default=None, description="Код элемента (опционально)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    user_id = current_user.id  
    data = list_rules(db, current_user_id=user_id, role_name=role, element_code=element)
    return {"items": data, "count": len(data)}


@router.put("/rules")
def put_rule(
    payload: UpsertRuleIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    user_id = current_user.id
    result = upsert_rule(
        db,
        current_user_id=user_id,
        role_name=payload.role,
        element_code=payload.element,
        flags=payload.flags.model_dump(),
    )
    return result
