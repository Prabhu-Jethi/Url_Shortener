from pydantic import BaseModel, HttpUrl
from datetime import datetime


class ShortenRequest(BaseModel):
    long_url: HttpUrl   # validates real url
    ## Optional: custom name and expiry time
    custom_alias: str | None=None
    expires_at: datetime | None=None


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str  # full url 
    long_url: str
    created_at: datetime
    expires_at: datetime | None=None


class UrlInfo(BaseModel):
    ## full url details 
    id: int
    short_code: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None=None
    is_active: bool
    total_clicks: int = 0

