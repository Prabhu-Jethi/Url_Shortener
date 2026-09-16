from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services import url_service

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=201)
def shorten(request: ShortenRequest, db: Session = Depends(get_db)):
    """Shorten a long URL."""
    return url_service.shorten_url(db, request)