from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool = True

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class RuleFlagsIn(BaseModel):
    read: Optional[bool] = None
    read_all: Optional[bool] = None
    create: Optional[bool] = None
    update: Optional[bool] = None
    update_all: Optional[bool] = None
    delete: Optional[bool] = None
    delete_all: Optional[bool] = None


class UpsertRuleIn(BaseModel):
    role: str
    element: str
    flags: RuleFlagsIn
