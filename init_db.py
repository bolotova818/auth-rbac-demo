from sqlalchemy.orm import Session
from db import engine, SessionLocal
from models import Base, User, Roles, UserRoles, BusinessElements, AccessRolesRules, BusinessObject
import bcrypt


def create_all():
    Base.metadata.create_all(bind=engine)


def seed():
    db: Session = SessionLocal()
    try:

        admin_role = Roles(name="admin")
        user_role = Roles(name="user")
        db.add_all([admin_role, user_role])
        db.commit()

        admin_user = User(
            name="Admin",
            email="admin@example.com",
            password_hash=bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
            is_active=True,
        )
        simple_user = User(
            name="User",
            email="user@example.com",
            password_hash=bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode(),
            is_active=True,
        )
        db.add_all([admin_user, simple_user])
        db.commit()

        db.add_all([
            UserRoles(user_id=admin_user.id, role_id=admin_role.id),
            UserRoles(user_id=simple_user.id, role_id=user_role.id),
        ])
        db.commit()


        rules_elem = BusinessElements(code="rules")
        objects_elem = BusinessElements(code="objects")
        db.add_all([rules_elem, objects_elem])
        db.commit()


        db.add(AccessRolesRules(
            role_id=admin_role.id,
            element_id=rules_elem.id,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True
        ))
        db.add(AccessRolesRules(
            role_id=admin_role.id,
            element_id=objects_elem.id,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True
        ))


        db.add(AccessRolesRules(
            role_id=user_role.id,
            element_id=objects_elem.id,
            read_permission=True,
            read_all_permission=False
        ))

        db.add(BusinessObject(
            title="Admin note",
            description="belongs to admin",
            owner_id=admin_user.id
        ))
        db.add(BusinessObject(
            title="User note",
            description="belongs to user",
            owner_id=simple_user.id
        ))

        db.commit()
        print("Seed OK")
    finally:
        db.close()


if __name__ == "__main__":
    create_all()
    seed()
