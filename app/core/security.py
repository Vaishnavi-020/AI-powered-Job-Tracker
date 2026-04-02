from fastapi import HTTPException,Depends
from jose import jwt,JWTError
from datetime import timedelta,datetime,timezone
import bcrypt

from app.models.User import User
from app.core.config import SECRET_KEY,JWT_ALGORITHM

#Hash password
def hash_password(password:str)->str:
    salt=bcrypt.gensalt()
    hashed=bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashed.decode('utf-8')

#Verify Password
def verify_passwrod(plain_pwd:str,hashed_pwd:str)->bool:
    return bcrypt.checkpw(plain_pwd.encode('utf-8'),
                          hashed_pwd.encode('utf-8'))

#Create Access Token
def create_access_token(data:dict,expires_delta:timedelta|None=None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc)+expires_delta
    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=15)
    to_encode.update({
        "exp":expire,
        "type":"access"
    })
    return jwt.encode(to_encode,SECRET_KEY,algorithm=JWT_ALGORITHM)

#Decode Access Token
def decode_access_token(token:str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithm=JWT_ALGORITHM)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )