from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import Click


def record_click(db: Session, url_id: int, referrer: str | None=None, 
                 ip_address: str | None=None, user_agent: str | None=None) -> Click:
    ## Records a new click event
    click = Click(
        url_id=url_id,
        referrer=referrer,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(click)
    db.commit()
    db.refresh(click)
    return click


def get_recent_clicks(db: Session, url_id: int, limit: int = 10) -> list[Click]:
    ## Returns most recent clicks
    stmt = (
        select(Click).where(Click.url_id == url_id)
        .order_by(Click.clicked_at.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def count_clicks(db: Session, url_id: int) -> int:
    ## Return total click count for a url
    stmt = select(func.count()).where(Click.url_id == url_id)
    return db.execute(stmt).scalar() or 0

