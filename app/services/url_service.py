import secrets
import string
from datetime import timezone, datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import url_repository, click_repository
from app.schemas.url import ShortenRequest, ShortenResponse

BASE_URL = "http://localhost:8000"


def generate_short_code(length: int = 7) -> str:
    ## Generate a random url-safe short code
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def shorten_url(db: Session, request: ShortenRequest) -> ShortenResponse:
    ## Creates shortened url
    ## 1. decide short code by checking it's availability
    if request.custom_alias:
        if url_repository.short_code_exists(db, request.custom_alias):
            raise HTTPException(status_code=409, detail="Alias already taken")
        short_code = request.custom_alias
    else:
        short_code = generate_short_code()
        while url_repository.short_code_exists(db, short_code):
            short_code = generate_short_code()

    
    ## 2. Save to db
    url = url_repository.create_url(db=db, short_code=short_code, long_url=str(request.long_url), expires_at=request.expires_at)

    ## 3. Build response
    return ShortenResponse(
        short_code=url.short_code,
        short_url=f"{BASE_URL}/{url.short_code}",
        long_url=url.long_url,
        created_at=url.created_at,
        expires_at=url.expires_at
    )


def resolve_redirect(db: Session, short_code: str, referrer: str | None=None, 
                     ip_address: str | None=None, user_agent: str | None=None) -> str:
    ## Look up the short code, record the click and return long_url
    url = url_repository.get_by_short_code(db, short_code)

    if not url:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    ## Checks if it's active 
    if not url.is_active:
        raise HTTPException(status_code=410, detail="Short link has been deactivated")
    
    ## Checks if it's expired
    if url.expires_at:
        now = datetime.now(timezone.utc)
        # If DB returned naive datetime, assume it's UTC
        expires = url.expires_at if url.expires_at.tzinfo else url.expires_at.replace(tzinfo=timezone.utc)
        if expires < now:
            raise HTTPException(status_code=410, detail="This link has expired")
    
    ## Record clicks
    click_repository.record_click(db=db, url_id=url.id, referrer=referrer, ip_address=ip_address, user_agent=user_agent)

    ## Now route will redirect it
    return url.long_url