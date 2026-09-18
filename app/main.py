from fastapi import FastAPI
from app.routes import shorten, redirect, stats
from fastapi.responses import RedirectResponse

app = FastAPI(title="URL Shortener")

app.include_router(shorten.router)
app.include_router(stats.router)
app.include_router(redirect.router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/")
def health():
    return{
        "status": "healthy"
    }
