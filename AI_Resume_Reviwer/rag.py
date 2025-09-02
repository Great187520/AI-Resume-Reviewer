# app/rag.py
from openai import OpenAI
import psycopg2
import numpy as np
from pydantic import BaseModel

client = OpenAI()

class FitScore(BaseModel):
    score: float
    rationale: str
    suggested_questions: list[str]

def retrieve_and_score(job_desc: str):
    # embed job desc
    jd_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=job_desc
    ).data[0].embedding
    
    # retrieve candidates from pgvector
    conn = psycopg2.connect("dbname=resume_ai user=postgres password=secret")
    cur = conn.cursor()
    cur.execute("""
        SELECT content, embedding
        FROM resumes
        ORDER BY embedding <-> %s
        LIMIT 5;
    """, (jd_embedding,))
    
    candidates = cur.fetchall()
    conn.close()
    
    # build prompt
    prompt = f"""
    You are an AI HR assistant. Compare the job description to the candidate resumes.
    Return a fit score (0-1), rationale, and 3 behavioral interview questions.
    Job Description: {job_desc}
    Candidates: {candidates}
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        response_format=FitScore.model_json_schema()
    )
    
    return FitScore(**response.choices[0].message["content"])
