from fastapi import HTTPException,File,UploadFile,Form
from sqlalchemy.orm import Session
from app.models.User import User
from dotenv import load_dotenv
import os
from app.RAG.rag_pipeline import extract_text_from_pdf,clean_text,split_sections,chunk_section,store_embeddings,get_top_chunks,analyze_resume,generate_llm_analysis

load_dotenv()

UPLOAD_FOLDER="resume_uploads"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

async def analyze_resume_service(db:Session,
                                 current_user:User,
                                 job_description:str=Form(...),
                                 file:UploadFile=File(...),
                                 ):
    if not job_description or job_description.strip()=="":
        raise HTTPException(status_code=400,
                            detail="Job description is required for analysis")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400,
                            detail="Please upload PDF format of Resume")
    filepath=os.path.join(UPLOAD_FOLDER,file.filename)
    with open(filepath,"wb") as f:
        f.write(await file.read())
    pdf_content=extract_text_from_pdf(filepath)
    cleaned_text=clean_text(pdf_content)
    sections=split_sections(cleaned_text)
    chunked=chunk_section(sections)
    store_embeddings(chunked)
    result=analyze_resume(job_description,cleaned_text)
    retrieved_chunks=get_top_chunks(job_description)
    llm_output=generate_llm_analysis(
        job_description,
        retrieved_chunks,
        result
    )

    return llm_output