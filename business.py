from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import UserRoles, BusinessElements, AccessRolesRules


def get_role_ids_for_user(db: Session, user_id: int) -> List[int]:
    rows = db.query(UserRoles.role_id).filter(UserRoles.user_id == user_id).all()
    return [r[0] for r in rows]


def get_element_id(db: Session, code: str) -> int:
    elem = db.query(BusinessElements.id).filter(BusinessElements.code == code).first()
    if not elem:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Неизвестный элемент '{code}'"
        )
    return elem[0]


def get_rules(db: Session, role_ids: List[int], element_id: int) -> List[AccessRolesRules]:
    if not role_ids:
        return []
    return (
        db.query(AccessRolesRules)
        .filter(
            AccessRolesRules.role_id.in_(role_ids),
            AccessRolesRules.element_id == element_id
        )
        .all()
    )


def check_read_allowed(
    db: Session,
    user_id: int,
    element_code: str,
    resource_owner_id: Optional[int] = None,
) -> None:
    role_ids = get_role_ids_for_user(db, user_id)
    element_id = get_element_id(db, element_code)
    rules = get_rules(db, role_ids, element_id)

    if not rules:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет правил доступа")

    for r in rules:
        if r.read_all_permission:
            return
        if resource_owner_id is not None and r.read_permission and resource_owner_id == user_id:
            return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
