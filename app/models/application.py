from sqlalchemy import Column,String,Integer,Date,func,Enum,DateTime
from app.models.base import Base
from sqlalchemy.orm import relationship

class Application(Base):
    __tablename__="application"
    id=Column(Integer,primary_key=True)
    company_name=Column(String,nullable=False)
    role=Column(String,nullable=False)
    location=Column(String,nullable=False)
    applied_date=Column(Date,server_default=func.now())
    link=Column(String(2048))
    status=Column(Enum(
        'Applied',
        'Interview',
        'Rejected',
        'Offer',
        name="application_status"
    ),nullable=False,default="Applied")
    source=Column(String(100))
    notes=Column(String(500))
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    owner=relationship("User",back_populates="applications")