from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.schema.application_schema import AddApplication,ApplicationResponse,AllApplicationResponse,UpdateApplicationStatus
from app.services.application_service import add_application_service,view_all_applications_service,view_single_application_service,update_application_status_service,delete_application_service
from app.database import get_db
from app.dependencies import get_current_user
from typing import List

router=APIRouter(prefix='/application',tags=["Application"])

@router.post("/new_application",response_model=ApplicationResponse)
def add_application(application_data:AddApplication,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return add_application_service(application_data,db,current_user)

@router.get('/all_applications',response_model=List[AllApplicationResponse])
def view_all_applications(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return view_all_applications_service(db,current_user)

@router.get('/{application_id}',response_model=ApplicationResponse)
def view_single_application(application_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return view_single_application_service(application_id,db,current_user)

@router.patch("/update/{application_id}",response_model=ApplicationResponse)
def update_application_status(application_id:int,
                              application_status:UpdateApplicationStatus,
                              db:Session=Depends(get_db),
                              current_user=Depends(get_current_user)):
    return update_application_status_service(application_id,application_status,db,current_user)

@router.delete("/delete/{application_id}")
def delete_application(application_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return delete_application_service(application_id,db,current_user)