<<<<<<< HEAD
# workflow_automation
=======
# Ameria Bank Monitoring System

An automation project built with **n8n** to monitor Ameria Bank's website and automatically notify users about new articles and webpage changes.

## Overview

This project contains two automated monitoring workflows:

1. **Ameria Bank News Monitor** — checks an RSS feed for new articles and sends an email notification when a new article is published.
2. **Ameria Bank Page Change Monitor** — checks selected Ameria Bank webpages, compares their current content with previously saved snapshots, and sends an email when a change is detected.

The workflows use **PostgreSQL** to store monitoring data and **SMTP** to send email notifications.

## Workflows

### 1. Ameria Bank News Monitor

This workflow monitors an RSS feed and identifies newly published articles.

#### Workflow

```text
Schedule Trigger
       ↓
Get RSS Source
       ↓
Fetch Feed
       ↓
Parse & Keep Latest
       ↓
Insert If New
       ↓
Build Email
       ↓
Send Email
       ↓
Has New Article?
      ↙ ↘
    Yes  No
     ↓    ↓
Mark As   Skip
Emailed
```

#### How it works

1. **Schedule Trigger** starts the workflow at a scheduled time.
2. **Get RSS Source** retrieves the RSS source information from PostgreSQL.
3. **Fetch Feed** requests the latest RSS feed content.
4. **Parse & Keep Latest** extracts the relevant article information and keeps the latest article.
5. **Insert If New** checks whether the article has already been stored and inserts it if it is new.
6. **Build Email** prepares the email subject and HTML content.
7. **Send Email** sends the notification through the configured SMTP account.
8. **Has New Article?** checks whether a new article was found.
9. If a new article exists, **Mark As Emailed** updates the database to indicate that the notification was sent.
10. If no new article exists, the workflow follows the **No New Article (Skip)** path.

### 2. Ameria Bank Page Change Monitor

This workflow monitors selected Ameria Bank webpages and detects changes in their content.

#### Workflow

```text
Schedule Trigger
       ↓
Get Monitored Pages
       ↓
Fetch Page
       ↓
Extract & Hash
       ↓
Crypto
       ↓
Get Latest Snapshot
       ↓
Compare
       ↓
Save Snapshot
       ↓
If Changed?
      ↙ ↘
    Yes  No
     ↓    ↓
Build    Build
Combined No-Change
Diff     Email
     ↓      ↓
Send     Send
Change   No-Change
Report   Email

Error → Build Error Email → Send Error Email
```

#### How it works

1. **Schedule Trigger** starts the workflow according to the configured schedule.
2. **Get Monitored Pages** retrieves the list of webpages being monitored from PostgreSQL.
3. **Fetch Page** requests the current HTML content of each webpage.
4. **Extract & Hash** extracts the relevant page content and prepares it for comparison.
5. **Crypto** generates a hash of the extracted content.
6. **Get Latest Snapshot** retrieves the most recently saved snapshot of the corresponding webpage.
7. **Compare** compares the current hash with the previous hash.
8. **Save Snapshot** stores the current snapshot in PostgreSQL.
9. **If Changed?** determines whether the webpage has changed.

#### If a change is detected

The workflow:

* Builds a combined change report.
* Sends an email notification.
* Appends a new row to the Google Sheet.

#### If no change is detected

The workflow:

* Builds a no-change email.
* Sends the no-change notification.

#### If an error occurs

The workflow follows the error path:

```text
Fetch Page Error
       ↓
Build Error Email
       ↓
Send Error Email
```

This allows errors during webpage fetching to be reported by email.

## Technologies Used

* **n8n** — workflow automation
* **PostgreSQL** — stores monitored pages, articles, and snapshots
* **SMTP** — sends email notifications
* **Google Sheets** — stores detected webpage changes
* **JavaScript** — processes and compares extracted content
* **Ameria Bank website / RSS feed** — monitoring sources

## Database

The PostgreSQL database stores information required by the workflows, including:

* Monitored webpages
* RSS sources
* News articles
* Page snapshots
* Content hashes
* Monitoring timestamps

The database is used to determine whether an article or webpage change is new.

## Email Notifications

The workflows use an SMTP account to send notifications.

Email notifications include:

* New article alerts
* Webpage change reports
* No-change notifications
* Error notifications

> **Note:** SMTP credentials and other sensitive configuration values should not be included in the GitHub repository.

## Google Sheets Integration

When the Page Change Monitor detects a change, it appends a new row to a Google Sheet.

The sheet can be used as a historical record of webpage changes, including information such as:

* Page name
* Page URL
* Detected changes
* Timestamp
* Other relevant monitoring details

## How to Import the Workflows

1. Install or open **n8n**.
2. Import the workflow JSON files from the `workflows/` folder.
3. Configure the required credentials:

   * PostgreSQL
   * SMTP
   * Google Sheets
4. Verify the monitored page URLs and RSS source configuration.
5. Activate the workflows or execute them manually for testing.

## Testing

The workflows can be tested manually by:

1. Executing the workflow in n8n.
2. Checking the execution results of each node.
3. Confirming that new articles or webpage changes are detected.
4. Verifying that the email notification is received.
5. Checking that detected changes are appended to the Google Sheet.

For the Page Change Monitor, a test can also be performed by changing a stored snapshot or modifying a monitored webpage's content, then executing the workflow again.

## Project Structure

```text
ameria-bank-monitoring/
├── README.md
├── workflows/
│   ├── ameria-bank-news-monitor.json
│   └── ameria-bank-page-change-monitor.json
└── screenshots/
```

## Future Improvements

* Add Jira integration for creating issues when webpage changes are detected.
* Improve change reports by showing only the exact modified text.
* Add more monitoring sources and webpages.
* Add more detailed logging and error handling.
* Deploy the workflows to a hosted n8n environment.

## Author

Created as an automation and website monitoring project using n8n.
>>>>>>> 2a3fd85 (Add Ameria Bank monitoring workflows and documentation)
