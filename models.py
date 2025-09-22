from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Text
)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, server_default="false")


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)


class BusinessElements(Base):
    __tablename__ = "business_elements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)


class BusinessObject(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)


class UserRoles(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)


class AccessRolesRules(Base):
    __tablename__ = "access_roles_rules"
    __table_args__ = (
        UniqueConstraint("role_id", "element_id", name="uq_role_element"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    element_id = Column(Integer, ForeignKey("business_elements.id", ondelete="CASCADE"), nullable=False, index=True)

    read_permission = Column(Boolean, nullable=False, server_default="false")
    read_all_permission = Column(Boolean, nullable=False, server_default="false")
    create_permission = Column(Boolean, nullable=False, server_default="false")
    update_permission = Column(Boolean, nullable=False, server_default="false")
    update_all_permission = Column(Boolean, nullable=False, server_default="false")
    delete_permission = Column(Boolean, nullable=False, server_default="false")
    delete_all_permission = Column(Boolean, nullable=False, server_default="false")
