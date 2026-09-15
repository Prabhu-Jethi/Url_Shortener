from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    String,
    Index,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    long_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    ## Relationship: One url -> many clicks
    clicks: Mapped[list["Click"]] = relationship(back_populates="url", cascade="all, delete-orphan")


    ## Extra indexes: (the unique index on short_code is automatic from unique=True)
    __table_args__ = (
        Index("idx_urls_created_at", "created_at"),
    )



class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)


    ## rel: back to url
    url: Mapped["Url"] = relationship(back_populates="clicks")

    __table_args__ = (
        Index("idx_clicks_url_id_clicked_at", "url_id", "clicked_at"),
    )