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
    print("Detected sections:", sections)
    if not sections:
        return {"raw": text}

    sorted_sections = sorted(sections.items(), key=lambda x: x[1])
    result = {}

    for i in range(len(sorted_sections)):
        name, start = sorted_sections[i]
        end = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(text)

        content = text[start:end]

        # REMOVE other section headers inside this chunk
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

