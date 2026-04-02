from pydantic import BaseModel
from datetime import date,datetime
from typing import Optional
from app.enums.application_status import ApplicationStatus

class AddApplication(BaseModel):
    company_name:str
    role:str
    location:str
    applied_date:Optional[date]=None
    link:Optional[str]=None
    status:ApplicationStatus
    source:Optional[str]=None
    notes:Optional[str]=None

    
class ApplicationResponse(BaseModel):
    id:int
    company_name:str
    role:str
    location:str
    applied_date:Optional[date]=None
    link:Optional[str]=None
    status:ApplicationStatus
    source:Optional[str]=None
    notes:Optional[str]=None
    created_at:datetime

    class Config:
        from_attributes=True

class AllApplicationResponse(BaseModel):
    company_name:str
    role:str
    status:ApplicationStatus
    created_at:datetime

    class Config:
        from_attributes=True

