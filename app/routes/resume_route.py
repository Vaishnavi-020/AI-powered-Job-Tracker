from fastapi import APIRouter,Depends,File,UploadFile,Form
from sqlalchemy.orm import Session
from app.services.resume_service import analyze_resume_service
from app.schema.job_schema import JobRequest
from app.database import get_db
from app.dependencies import get_current_user

router=APIRouter(prefix="/resume",tags=["AI"])


@router.post('/analyze_resume')
async def analyze(job_description:str=Form(...),
            file:UploadFile=File(...)):
    return await analyze_resume_service(job_description,file)
