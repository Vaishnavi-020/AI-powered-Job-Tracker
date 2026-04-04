from fastapi import HTTPException,File,UploadFile
from dotenv import load_dotenv
import os
from app.RAG.rag_pipeline import extract_text_from_pdf,clean_text,split_sections,chunk_section

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
    # print(pdf_content)
    cleaned_text=clean_text(pdf_content)
    # print(cleaned_text)
    sections=split_sections(cleaned_text)
    # print(sections)
    chunked=chunk_section(sections)
    print(chunked)
    return {"message":"Successful"}