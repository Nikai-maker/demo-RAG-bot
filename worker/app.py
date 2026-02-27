# app.py
from fastapi import FastAPI
import threading
from redis_consumer import consume

app = FastAPI()

@app.on_event("startup")
def start_consumer():
    thread = threading.Thread(target=consume, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok"}


from db import init_schema
@app.on_event("startup")
def startup():
    init_schema()