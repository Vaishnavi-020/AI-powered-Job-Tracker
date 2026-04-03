from fastapi import HTTPException,File,UploadFile
from dotenv import load_dotenv
import os
from app.RAG.rag_pipeline import extract_text_from_pdf

load_dotenv()

UPLOAD_FOLDER="resume_uploads"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

async def upload_file_service(file:UploadFile=File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException (status_code=400,
                             detail="Please upload pdf format of resume")
    filepath=os.path.join(UPLOAD_FOLDER,file.filename)
    with open (filepath,"wb") as f:
        f.write(await file.read())
    pdf_content=extract_text_from_pdf(filepath)
    print(pdf_content)
    return {"message":"Successful"}