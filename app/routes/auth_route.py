from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import signup_user_service,login_user_service
from app.schema.auth_schema import UserCreate,Token
from app.database import get_db

router=APIRouter(prefix="/auth",tags=["Authorization"])

@router.post("/signup",response_model=Token)
def signup_user(user_data:UserCreate,db:Session=Depends(get_db)):
    return signup_user_service(user_data,db)

@router.post("/login",response_model=Token)
def login_user(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    return login_user_service(form_data,db)