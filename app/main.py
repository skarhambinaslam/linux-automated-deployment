import os

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Linux Automated Deployment")


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


class NoteIn(BaseModel):
    text: str


@app.get("/")
def root():
    return {"message": "FastAPI is running in Docker"}


@app.get("/health")
def health():
    try:
        conn = get_conn()
        with conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"database error: {exc}")


@app.post("/notes")
def create_note(note: NoteIn):
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text, created_at",
            (note.text,),
        )
        row = cur.fetchone()
    conn.close()
    return {"id": row[0], "text": row[1], "created_at": row[2].isoformat()}


@app.get("/notes")
def list_notes():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "text": r[1], "created_at": r[2].isoformat()} for r in rows]