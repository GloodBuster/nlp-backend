from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import psycopg2
from dotenv import load_dotenv
from typing import List

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, options='-c client_encoding=latin-1')
    conn.set_client_encoding('latin-1')
    return conn


@app.get("/works/{id}")
async def get_works(id: int, limit: int = 10, offset: int = 0):
    try:
        return {"author": 'Peter Johnson', "id": id, "limit": limit, "offset": offset}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
