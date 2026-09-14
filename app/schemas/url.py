CREATE TABLE urls (
    id           BIGSERIAL PRIMARY KEY,
    short_code   VARCHAR(10) NOT NULL,
    long_url     TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at   TIMESTAMPTZ,
    is_active    BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT uq_short_code UNIQUE (short_code)
);

CREATE TABLE clicks (
    id           BIGSERIAL PRIMARY KEY,
    url_id       BIGINT NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    clicked_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    referrer     TEXT,
    ip_address   INET,
    user_agent   TEXT
);

-- Indexes
CREATE UNIQUE INDEX idx_urls_short_code ON urls (short_code);
CREATE INDEX idx_clicks_url_id_clicked_at ON clicks (url_id, clicked_at);
CREATE INDEX idx_urls_created_at ON urls (created_at); -- optional, for cleanup jobs