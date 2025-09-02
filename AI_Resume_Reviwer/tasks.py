# app/tasks.py
from celery import Celery
from PyPDF2 import PdfReader
import json

celery = Celery(
    "resume_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery.task(name="tasks.process_resume")
def process_resume(file_path: str):
    reader = PdfReader(file_path)
    text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    metadata = {
        "length": len(text.split()),
        "has_email": "@" in text,
        "skills_detected": [w for w in ["Python", "AWS", "Django", "LLM"] if w in text]
    }
    
    # store text + metadata in DB/S3
    return {"text": text[:500], "metadata": metadata}
