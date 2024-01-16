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
    return psycopg2.connect(DATABASE_URL,  options='-c client_encoding=latin-1', encoding='latin-1')

@app.get("/works", response_model=List[dict])
async def get_works():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM works")
        results = cur.fetchall()
        cur.close()
        conn.close()

        works_list = []
        for row in results:
            print("Raw id value:", row[0])
            work_dict = {
                "id": str(row[0]),
                "genre": row[1],
                "title": row[2],
                "description": row[3].decode('utf-8', 'ignore'),
                "meter": row[4],
                "subject": row[5],
                "original_language": row[6],
                "elaboration_start_date": str(row[7]),
                "elaboration_end_date": str(row[8]),
                "elaboration_places": row[9],
            }
            works_list.append(work_dict)

        return works_list

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
