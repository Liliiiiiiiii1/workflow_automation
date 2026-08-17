import datetime
import html
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
import psycopg2
from psycopg2.extras import RealDictCursor

# --- CONFIGURATION ---
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}

SMTP_CONFIG = {
    "host": "smtp.yourcompany.am",
    "port": 587,
    "user": "news-monitor@yourcompany.am",
    "password": "your_smtp_password",
    "from": "news-monitor@yourcompany.am",
    "to": "your.email@yourcompany.am",
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def run_news_monitor():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 2: Get RSS Source from Postgres
        cursor.execute(
            """
            SELECT id, name, source_type, listing_url 
            FROM news_monitor.sources 
            WHERE enabled = TRUE AND source_type = 'rss' 
            ORDER BY id LIMIT 1;
        """
        )
        source = cursor.fetchone()
        if not source:
            print("No active RSS source found.")
            return

        # Step 3: Read RSS Feed
        feed = feedparser.parse(source["listing_url"])
        if not feed.entries:
            print("No entries found in RSS feed.")
            return

        # Step 4: Keep Latest Article
        def get_entry_date(entry):
            for key in ("published_parsed", "updated_parsed", "created_parsed"):
                if getattr(entry, key, None):
                    return datetime.datetime(*getattr(entry, key)[:6])
            return datetime.datetime.min

        sorted_entries = sorted(feed.entries, key=get_entry_date, reverse=True)
        latest = sorted_entries[0]

        pub_date = (
            get_entry_date(latest)
            if get_entry_date(latest) != datetime.datetime.min
            else None
        )
        url = latest.get("link") or latest.get("id") or ""
        title = latest.get("title", "Untitled article")
        summary = (
            latest.get("summary")
            or latest.get("description")
            or latest.get("content", [{}])[0].get("value", "")
        )

        # Step 5: Insert If New (Postgres Deduplication)
        cursor.execute(
            """
            INSERT INTO news_monitor.articles (source_id, title, url, published_at, summary)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_id, url) DO NOTHING
            RETURNING id, source_id, title, url, published_at, summary, discovered_at;
        """,
            (source["id"], title, url, pub_date, summary),
        )

        inserted_article = cursor.fetchone()
        conn.commit()

        # If article already exists (ON CONFLICT DO NOTHING), inserted_article will be None
        if not inserted_article:
            print("Latest article already processed. Skipping email.")
            return

        # Step 6: Build Email Content
        article_id = inserted_article["id"]
        source_name = html.escape(source["name"])
        safe_title = html.escape(title)
        safe_summary = html.escape(summary) if summary else ""
        safe_url = html.escape(url)

        pub_date_str = (
            pub_date.strftime("%d/%m/%Y, %H:%M:%S")
            if pub_date
            else "Date unavailable"
        )

        email_html = f"""
        <h2>Daily News Update</h2>
        <h3>{source_name}</h3>
        <p><strong>{safe_title}</strong></p>
        <p>{pub_date_str}</p>
        {"<p>" + safe_summary + "</p>" if safe_summary else ""}
        <p><a href="{safe_url}">Read full article</a></p>
        <hr><p style="font-size:12px;color:#666">Generated automatically by Python News Monitor.</p>
        """

        # Step 7: Send Email via SMTP
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"News Update - {source['name']}"
        msg["From"] = SMTP_CONFIG["from"]
        msg["To"] = SMTP_CONFIG["to"]
        msg.attach(MIMEText(email_html, "html"))

        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.sendmail(
                SMTP_CONFIG["from"], [SMTP_CONFIG["to"]], msg.as_string()
            )

        print(f"Email sent successfully for article ID: {article_id}")

        # Step 8: Mark As Emailed
        cursor.execute(
            """
            UPDATE news_monitor.articles
            SET emailed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, title, emailed_at;
        """,
            (article_id,),
        )
        conn.commit()
        print("Database record updated successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Error executing workflow: {e}")
    finally:
        cursor.close()
        conn.close()


# --- Step 1: Schedule Trigger (Daily at 08:00 Asia/Yerevan) ---
if __name__ == "__main__":
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler(timezone="Asia/Yerevan")
    scheduler.add_job(run_news_monitor, "cron", hour=8, minute=0)

    print("News Monitor scheduler started. Running daily at 08:00 Asia/Yerevan...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass