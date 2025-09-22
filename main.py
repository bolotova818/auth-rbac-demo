from fastapi import FastAPI
from db import engine
from models import Base
from app_user import router as user_router
from app_admin import router as admin_router
from app_business import router as objects_router

app = FastAPI(title="Auth/RBAC Demo")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(objects_router)
