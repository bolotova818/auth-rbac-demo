from typing import List, Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Roles, BusinessElements, AccessRolesRules
from business import get_role_ids_for_user, get_element_id, get_rules


def ensure_can_read_rules(db: Session, user_id: int) -> None:
    role_ids = get_role_ids_for_user(db, user_id)
    element_id = get_element_id(db, "rules")
    rules = get_rules(db, role_ids, element_id)
    if not rules or not any(r.read_all_permission for r in rules):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на просмотр правил")


def ensure_can_update_rules(db: Session, user_id: int) -> None:
    role_ids = get_role_ids_for_user(db, user_id)
    element_id = get_element_id(db, "rules")
    rules = get_rules(db, role_ids, element_id)
    if not rules or not any(r.update_all_permission for r in rules):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на изменение правил")


def list_rules(
    db: Session,
    current_user_id: int,
    role_name: Optional[str] = None,
    element_code: Optional[str] = None,
) -> List[Dict]:
    ensure_can_read_rules(db, current_user_id)

    q = (
        db.query(
            AccessRolesRules.id,
            Roles.name,
            BusinessElements.code,
            AccessRolesRules.read_permission,
            AccessRolesRules.read_all_permission,
            AccessRolesRules.create_permission,
            AccessRolesRules.update_permission,
            AccessRolesRules.update_all_permission,
            AccessRolesRules.delete_permission,
            AccessRolesRules.delete_all_permission,
        )
        .join(Roles, Roles.id == AccessRolesRules.role_id)
        .join(BusinessElements, BusinessElements.id == AccessRolesRules.element_id)
    )

    if role_name:
        q = q.filter(Roles.name == role_name)
    if element_code:
        q = q.filter(BusinessElements.code == element_code)

    rows = q.all()
    result = []
    for r in rows:
        result.append({
            "id": r.id,
            "role": r.name,
            "element": r.code,
            "read": r.read_permission,
            "read_all": r.read_all_permission,
            "create": r.create_permission,
            "update": r.update_permission,
            "update_all": r.update_all_permission,
            "delete": r.delete_permission,
            "delete_all": r.delete_all_permission,
        })
    return result


def upsert_rule(
    db: Session,
    current_user_id: int,
    role_name: str,
    element_code: str,
    flags: Dict[str, Optional[bool]],
) -> Dict:
    ensure_can_update_rules(db, current_user_id)

    role = db.query(Roles).filter(Roles.name == role_name).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_name}' not found")

    element = db.query(BusinessElements).filter(BusinessElements.code == element_code).first()
    if not element:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Element '{element_code}' not found")

    rule = db.query(AccessRolesRules).filter(
        AccessRolesRules.role_id == role.id,
        AccessRolesRules.element_id == element.id
    ).first()

    if rule is None:
        rule = AccessRolesRules(
            role_id=role.id,
            element_id=element.id,
            **flags
        )
        db.add(rule)
    else:
        for k, v in flags.items():
            if hasattr(rule, f"{k}_permission") and v is not None:
                setattr(rule, f"{k}_permission", v)

    db.commit()
    db.refresh(rule)

    return {
        "id": rule.id,
        "role": role.name,
        "element": element.code,
        "read": rule.read_permission,
        "read_all": rule.read_all_permission,
        "create": rule.create_permission,
        "update": rule.update_permission,
        "update_all": rule.update_all_permission,
        "delete": rule.delete_permission,
        "delete_all": rule.delete_all_permission,
    }
