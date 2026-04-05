from fastapi import APIRouter,Depends,File,UploadFile,Form
from sqlalchemy.orm import Session
from app.models.User import User
from app.services.resume_service import analyze_resume_service
from app.schema.job_schema import JobRequest
from app.database import get_db
from app.dependencies import get_current_user

router=APIRouter(prefix="/resume",tags=["AI"])


@router.post('/analyze_resume')
async def analyze(db:Session=Depends(get_db),
                  current_user=Depends(get_current_user),
                  job_description:str=Form(...),
            file:UploadFile=File(...)):
    return await analyze_resume_service(db,current_user,job_description,file)
