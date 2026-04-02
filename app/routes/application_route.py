from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.schema.application_schema import AddApplication
from app.services.application_service import add_application_service
from app.database import get_db
from app.dependencies import get_current_user

router=APIRouter(prefix='/application',tags=["Application"])

@router.post("/new_application")
def add_application(application_data:AddApplication,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return add_application_service(application_data,db,current_user)
