from datetime import datetime
from pydantic import BaseModel


class ClickDetails(BaseModel):
    ## Details about a single url-clicked event
    clicked_at: datetime
    referrer: str | None=None
    ip_address: str | None=None
    user_agent: str | None=None


class ClickStats(BaseModel):
    ## Stats response for GET /{short_code}/stats
    short_code: str
    long_url: str
    total_clicks: int
    created_at: datetime
    is_active: bool
    recent_clicks: list[ClickDetails] = []