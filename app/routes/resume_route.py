from fastapi import APIRouter,Depends,File,UploadFile
from sqlalchemy.orm import Session
from app.services.resume_service import upload_file_service
from app.database import get_db
from app.dependencies import get_current_user

router=APIRouter(prefix="/resume",tags=["AI"])

@router.post("/upload")
async def upload_file(file:UploadFile=File(...)):
    return await upload_file_service(file)

