from fastapi import FastAPI
from app.routes import shorten, redirect, stats

app = FastAPI(title="URL Shortener")

app.include_router(shorten.router)
app.include_router(stats.router)
app.include_router(redirect.router)


@app.get("/")
def root():
    return{
        "status": "healthy"
    }
