from fastapi import FastAPI #FastAPI → framework
from sqlalchemy import text

from app.core.db import SessionLocal #SessionLocal → połączenie z bazą
from app.api.routes import router

app = FastAPI(title="Room Booking API") #Tu tworzysz aplikację.startuje serwer
app.include_router(router) #dolaczam post , delete,get z router


@app.get("/")
def root():
    return {"message": "Room Booking API is running 🚀"}


@app.get("/db-check") #łaczy sie z bazą/ENDPOINT API na mojej stronie FAST-API
def db_check():
    with SessionLocal() as db:
        db.execute(text("SELECT 1")) #wykonuje select 1
    return {"db": "ok"}
from app.core.db import engine
from app.domain.models import Base

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

