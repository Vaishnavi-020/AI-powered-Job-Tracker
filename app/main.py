from fastapi import FastAPI
from app.database import engine
from app.models.base import Base
from app.models.User import User
from app.models.Application import Application
from app.routes.auth_route import router as auth_router
from app.routes.application_route import router as application_router

app=FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(application_router)
