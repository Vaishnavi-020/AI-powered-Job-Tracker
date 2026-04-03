from pypdf import PdfReader
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

def extract_text_from_pdf(filepath):
    reader=PdfReader(filepath)
    text=""
    for page in reader.pages:
        text+=page.extract_text() or ""
    return text
