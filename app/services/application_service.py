from sqlalchemy.orm import Session
from app.models.User import User
from app.models.Application import Application
from app.schema.application_schema import AddApplication

def add_application_service(application_data:AddApplication,db:Session,current_user:User):
    try:
        new_application=Application(
            company_name=application_data.company_name,
            role=application_data.role,
            location=application_data.location,
            applied_date=application_data.applied_date,
            link=application_data.link,
            status=application_data.status,
            source=application_data.source,
            notes=application_data.notes,
            user_id=current_user.id
        )
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        return new_application
    except:
        db.rollback()
        raise

def view_all_applications_service(db:Session,current_user:User):
    applications=db.query(Application).filter(Application.user_id==current_user.id).all()
    return applications
