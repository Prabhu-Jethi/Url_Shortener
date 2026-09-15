from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Url


def create_url(db: Session, short_code: str, long_url: str, expires_at: datetime | None=None,) -> Url:
    ## Inserts a new shortened url and return it
    url = Url(
        short_code=short_code,
        long_url=long_url,
        expires_at=expires_at
    )
    db.add(url)
    db.commit()
    db.refresh(url) ## reloads from db
    return url


def get_by_short_code(db: Session, short_code: str) -> Url | None:
    ## Looks up a url by it's short code. Returns None if found nothing
    stmt = select(Url).where(Url.short_code == short_code)
    return db.execute(stmt).scalar_one_or_none()


def short_code_exists(db: Session, short_code: str) -> bool:
    ## Checks if a short_code is already taken or used
    return get_by_short_code(db, short_code) is not None


def deactivate_url(db: Session, short_code: str) -> Url | None:
    url = get_by_short_code(db, short_code)
    if url:
        url.is_active = False
        db.commit()
        db.refresh(url)
    return url
