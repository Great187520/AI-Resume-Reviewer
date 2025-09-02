# app/main.py
from fastapi import FastAPI, UploadFile
from celery import Celery
import shutil
import uuid
import os

app = FastAPI()
celery_app = Celery(
    "resume_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_resume/")
async def upload_resume(file: UploadFile):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    celery_app.send_task("tasks.process_resume", args=[file_path])
    return {"status": "queued", "file_id": file_id}
