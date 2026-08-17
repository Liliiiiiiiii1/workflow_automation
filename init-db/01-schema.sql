CREATE SCHEMA IF NOT EXISTS news_monitor;

CREATE TABLE IF NOT EXISTS news_monitor.sources (
    id           SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    source_type  TEXT NOT NULL DEFAULT 'rss',
    listing_url  TEXT NOT NULL,
    enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS news_monitor.articles (
    id             SERIAL PRIMARY KEY,
    source_id      INTEGER NOT NULL REFERENCES news_monitor.sources(id),
    title          TEXT NOT NULL,
    url            TEXT NOT NULL,
    published_at   TIMESTAMPTZ,
    summary        TEXT,
    discovered_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    emailed_at     TIMESTAMPTZ,
    UNIQUE (source_id, url)
);

INSERT INTO news_monitor.sources (name, source_type, listing_url, enabled)
VALUES ('Example News', 'rss', 'https://example.com/rss.xml', TRUE)
ON CONFLICT DO NOTHING;