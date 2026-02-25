from fastapi import FastAPI
from sqlalchemy import text

from app.core.db import SessionLocal
from app.api.routes import router

app = FastAPI(title="Room Booking API")
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Room Booking API is running 🚀"}


@app.get("/db-check")
def db_check():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"db": "ok"}