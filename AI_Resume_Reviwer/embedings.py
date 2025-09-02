# app/embeddings.py
from sentence_transformers import SentenceTransformer
import psycopg2
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_and_store(text: str, job_id: str):
    embedding = model.encode([text])[0].tolist()
    
    conn = psycopg2.connect("dbname=resume_ai user=postgres password=secret")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resumes (job_id, content, embedding) VALUES (%s, %s, %s)",
        (job_id, text, embedding)
    )
    conn.commit()
    conn.close()
