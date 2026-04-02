from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.User import User
from app.schema.auth_schema import UserCreate
from sqlalchemy.orm import Session
from app.core.security import hash_password,verify_passwrod
from app.core.security import create_access_token
from datetime import timedelta
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

def signup_user_service(user_data:UserCreate,db:Session):
    try:
        email=user_data.email.lower()
        existing_user=db.query(User).filter(User.email==email).first()
        if existing_user:
            raise HTTPException(status_code=400,
                                detail="User already exists")
        hashed_password=hash_password(user_data.password)
        new_user=User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password
        )
        db.add(new_user)
        db.flush()
        access_token=create_access_token(
            data={
                "sub":str(new_user.id)
            },expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        db.commit()
        db.refresh(new_user)

        return {
            "access_token":access_token,
            "token_type":"bearer",
            "user":new_user
        }

    except:
        db.rollback()
        raise 
    

def login_user_service(form_data:OAuth2PasswordRequestForm,db:Session):
    user=db.query(User).filter(User.email==form_data.username).first()
    if not user or not verify_passwrod(form_data.password,user.password_hash):
        raise HTTPException(status_code=401,
                            detail="Invalid credentials")
    
    access_token=create_access_token(
        data={
            "sub":str(user.id)
        },expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token":access_token,
        "token_type":"bearer",
        "user":{
            "id":user.id,
            "name":user.name,
            "email":user.email
        }
    }
    