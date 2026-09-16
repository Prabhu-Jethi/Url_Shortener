from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import url_repository, click_repository
from app.schemas.stats import ClickDetails, ClickStats


def get_url_stats(db: Session, short_code: str) -> ClickStats:
    ## Fetch url info + click stats package into a response
    url = url_repository.get_by_short_code(db, short_code)
    if not url:
        raise HTTPException(status_code=404, detail="Short link is not found")
    
    ## Get click data
    total = click_repository.count_clicks(db, url.id)
    recent = click_repository.get_recent_clicks(db, url.id, limit=10)


    ## Build response
    return ClickStats(
        short_code=url.short_code,
        long_url=url.long_url,
        total_clicks=total,
        created_at=url.created_at,
        is_active=url.is_active,
        recent_clicks=[ClickDetails(
            clicked_at=click.clicked_at,
            referrer=click.referrer,
        ip_address=str(click.ip_address) if click.ip_address else None,
        user_agent=click.user_agent) for click in recent
        ],
    )

