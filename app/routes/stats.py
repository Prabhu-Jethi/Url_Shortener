from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stats import ClickStats
from app.services import stats_service

router = APIRouter()


@router.get("/{short_code}/stats", response_model=ClickStats)
def stats(short_code: str, db: Session = Depends(get_db)):
    """Get click statistics for a shortened URL."""
    return stats_service.get_url_stats(db, short_code)