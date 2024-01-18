from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import psycopg2
from dotenv import load_dotenv
from typing import List
import searches
from pdfminer.high_level import extract_text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, options='-c client_encoding=latin-1')
    conn.set_client_encoding('latin-1')
    return conn


@app.get("/works")
async def get_works(limit: int = 10, offset: int = 0):
    try:
        from nlp_backend.works import works
        return works
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/works/{id}")
async def get_works(id: int):
    try:
        from nlp_backend.works import works

        work = next((work for work in works if work["id"] == id), None)
        return work

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/works/{id}/summary")
async def search(id: int):
    try:
        from nlp_backend.summarization import summarize_text_with_sumy
        from nlp_backend.works import works
        from nlp_backend.cleanText import clean_pdf_text

        work = next((work for work in works if work["id"] == id), None)
        text = extract_text("works/" + work["pdf"])
        text = clean_pdf_text(text)
        summary = summarize_text_with_sumy(text)
        response = {"summary": summary}
        return response

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/search")
async def search(query: str):
    try:
        return searches.search(query)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
