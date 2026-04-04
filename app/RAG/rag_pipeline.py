from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import certifi
import os
from dotenv import load_dotenv
import chromadb
import uuid
import re
import numpy as np
import json

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()

model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma_client=chromadb.Client()
collection=chroma_client.get_or_create_collection(name="resume_data")

def extract_text_from_pdf(filepath):
    reader=PdfReader(filepath)
    text=""
    for page in reader.pages:
        extracted=page.extract_text()
        if extracted:
            text+=extracted+"\n"
    return text

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

SECTION_KEYWORDS={
    "summary":["summary","professional summary","profile","about me","profile summary"],
    "skills":["skills","technical skills","core skills","competencies"],
    "experience":["experience","work experience","professional experience","internships","internship"],
    "projects":["projects","personal projects","personal work","academic projects"],
    "education":["education","academic background","qualification"],
    "certifications":["certifications","achievements","certificate"],
    "contact":["contact details","contact"]
    }

def split_sections(text):
    sections = {}

    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            match = re.search(rf'\b{keyword}\b', text, re.IGNORECASE)
            if match:
                sections[section] = match.start()
                break
    if not sections:
        return {"raw": text}

    sorted_sections = sorted(sections.items(), key=lambda x: x[1])
    result = {}

    for i in range(len(sorted_sections)):
        name, start = sorted_sections[i]
        end = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(text)

        content = text[start:end]

        for other_keywords in SECTION_KEYWORDS.values():
            for keyword in other_keywords:
                content = re.sub(rf'\b{keyword}\b', '', content, flags=re.IGNORECASE)

        result[name] = content.strip()

    return result

def chunk_section(section_dict):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n","\n",".",""," "]
    )
    all_chunks=[]
    for section_name,content in section_dict.items():
        if not content.strip():
            continue
        chunks=splitter.split_text(content)
        for chunk in chunks:
            all_chunks.append({
                "section":section_name,
                "text":chunk
            })
    return all_chunks

def store_embeddings(chunks):
    texts=[chunk["text"] for chunk in chunks]
    embeddings=model.encode(texts)
    for i,embedding in enumerate(embeddings):
        collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding.tolist()],
            documents=[texts[i]],
            metadatas=[{"section":chunks[i]["section"]}]
        )

SKILL_SET=[
    "python","sql","machine learning","deep learning",
    "nlp","data analysis","pandas","numpy","docker","aws","flask","fastapi",
    "C","C++","Java","MongoDB","PostgreSQL","MYSQL","power BI","Excel","tableau","statistics",
    "ReactJS","NodeJS","springboot","TypeScript","javascript","NextJS","ExpressJS","Kafka","LangChain","AutoGen","HuggingFace","LIamaIndex",
    "Docker","Kubernetes","GitHub Actions","CI-CD","Grafana","Prometheus","Psotman","Curl","Git","GitHub","Jenkins",
    "PineCone","InfluxDB","Redis","ORMs:SQLAlchemy","Prisma","Drizzle","OS","DBMS","OOPs","Compler Design","Machine Learning","AI","NLP","LLM","DSA",
    "Problem Solving","AWS"
]

def extract_skills(text:str):
    text=text.lower()
    found_skills=[]
    for skill in SKILL_SET:
        if skill in text:
            found_skills.append(skill)
    return list(set(found_skills))

def get_top_chunks(job_description:str,top_k:int=3):
    query_embedding=model.encode(job_description).tolist()
    results=collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    documents=results.get("documents",[])
    if not documents:
        return []
    top_chunks=documents[0]
    return top_chunks

def get_semantic_score(job_description:str,top_k:int=5):
    query_embedding=model.encode(job_description).tolist()
    results=collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    distances=results["distances"][0]

    similarities=[1-d for d in distances]
    if len(similarities)==0:
        return 0
    return float(np.mean(similarities))

def get_skill_match_score(job_desc:str,resume_text:str):
    job_skills=extract_skills(job_desc)
    resume_skills=extract_skills(resume_text)
    if len(job_skills)==0:
        return 0,[],[]
    matched=list(set(job_skills) & set(resume_skills))
    missing=list(set(job_skills)-set(resume_skills))
    score=len(matched)/len(job_skills)
    return score,matched,missing

def analyze_resume(job_description:str,resume_text:str):
    semantic_score=get_semantic_score(job_description)
    skill_score,strengths,missing_skills=get_skill_match_score(job_description,resume_text)
    final_score=(0.6*semantic_score+0.4*skill_score)*100

    return{
        "semantic_score":round(semantic_score*100,2),
        "skill_match_score":round(skill_score*100,2),
        "final_score":round(final_score,2),
        "strengths":strengths,
        "missing_skills":missing_skills,
        "explanation":f"Matched {len(strengths)} out of {len(strengths)+len(missing_skills)} required skills."
    }

from openai import OpenAI

llm_client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def generate_llm_analysis(job_description,resume_chunks,analysis):
    prompt=f"""
    You are an AI resume evaluator.

    Compare the candidate's resume with the job description.
     
    IMPORTANT:
    - Return ONLY valid JSON
    - Do NOT add explanation outside JSON
    - Do NOT add text like "Here is the result"

    Format strictly:

    {{
    "summary":"...",
    "strengths_explanation":"...",
    "missing_skills_explanation":"...",
    "suggestions":["...","..."]
    }}

    Job Description:
    {job_description}

    Resume Content:
    {resume_chunks}

    Precomputed Analysis:
    {analysis}

    Tasks:
    1. Explain match quality
    2.Highlight strengths
    3.Explain missing skills
    4.Suggest improvements

    """

    response=llm_client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {"role":"user","content":prompt}
        ],
        temperature=0.3
    )

    content= response.choices[0].message.content
    try:
        return json.loads(content)
    except:
        return {
            "summary":content,
            "strengths_explanation":"",
            "missing_skills_explanation":"",
            "suggestions":[]
        }