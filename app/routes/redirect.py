from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import url_service

router = APIRouter()


@router.get("/{short_code}")
def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    """Redirect to the original URL and record the click."""
    long_url = url_service.resolve_redirect(
        db=db,
        short_code=short_code,
        referrer=request.headers.get("referer"),      # note: HTTP header is "referer" (misspelling is standard)
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse(url=long_url, status_code=307)