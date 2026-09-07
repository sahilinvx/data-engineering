# Week 4 — How Data Enters a Platform

Goal: understand ingestion — pulling data from external systems (APIs,
files, databases) into a platform, and the strategies for keeping it
up to date afterward.

## Setup

```bash
cd week-4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # fill in GITHUB_TOKEN if you have one (optional)
docker-compose up -d          # starts Postgres 16 on localhost:5433
```

Postgres runs in Docker instead of the host's system Postgres so this week
is self-contained and disposable (`docker-compose down -v` wipes it clean).
Port 5433, not 5432, so it doesn't clash with anything else running locally.

## Concepts

**REST APIs** — Data sources expose data over HTTP as JSON, addressed by
URL, using standard verbs (`GET` to read). Task 1 talks to
`api.github.com`, a real public REST API.

**Pagination** — APIs never hand back an unbounded list in one response;
they cap each response (e.g. 30 items) and give you a way to ask for the
next chunk. GitHub does this with a `Link` response header (`rel="next"`)
instead of you guessing page numbers — see `common/http_client.py`.

**Authentication** — Most APIs rate-limit or block unauthenticated
requests. GitHub allows 60 requests/hour per IP with no token, 5000/hour
with a bearer token in the `Authorization` header. `common/http_client.py`
builds that header when `GITHUB_TOKEN` is set, and works without one too
(just slower).

**JSON Parsing** — Raw API responses carry far more fields than you need.
`01_github_api/ingest_github_repos.py`'s `parse_repo()` explicitly picks
the fields worth keeping, rather than dumping the whole payload downstream.

**CSV Ingestion** — Reading a flat file, inferring types (a CSV is just
text — "50000" and "50000.0" and "hello" are all strings until you decide
otherwise), and mapping those types to a destination schema. See
`02_csv_to_postgres/load_csv_to_postgres.py`'s `infer_columns()`.

**Database Ingestion** — Getting parsed data into a database efficiently.
Row-by-row `INSERT` is fine for dozens of rows and far too slow for tens
of thousands — task 2 uses Postgres's `COPY` bulk-load protocol instead.

**Full Load** — Reload the entire dataset every run (truncate + reload, or
drop + recreate). Simple, always correct, but cost scales with total data
size regardless of how much actually changed. Used in task 2.

**Incremental Loading** — Load only what changed since the last run, using
some marker (a timestamp, an auto-incrementing ID) to define "since." Cost
scales with the size of the *change*, not the whole dataset. Used in task 3.

**CDC Concepts (Change Data Capture)** — The general problem of noticing
and propagating changes at the source. Task 3's `updated_at`-column
polling is the simplest form of CDC: ask "what changed since X?" on a
schedule. Production systems increasingly use *log-based* CDC (e.g.
Debezium reading Postgres's write-ahead log) instead, because polling has
real gaps:
- it can't see `DELETE`s (a deleted row just isn't in the `SELECT` anymore)
- it depends on every writer reliably updating the timestamp column
- rows written at the exact same timestamp as the watermark are ambiguous
- it only sees the *latest* state per row, not the sequence of changes in between

**Schema Evolution** — Source schemas change over time (a new column gets
added upstream). A pipeline should detect that and adapt the destination
schema (`ALTER TABLE ADD COLUMN`) instead of erroring out or silently
dropping the new field. Demonstrated in task 2.

## Hands-on tasks

| # | Task | Folder | Concepts covered |
|---|------|--------|-------------------|
| 1 | Ingest GitHub API | [`01_github_api/`](01_github_api/NOTES.md) | REST APIs, pagination, auth, JSON parsing |
| 2 | Load CSV into PostgreSQL | [`02_csv_to_postgres/`](02_csv_to_postgres/NOTES.md) | CSV ingestion, DB ingestion, full load, schema evolution |
| 3 | Incremental pipeline (timestamp column) | [`03_incremental_pipeline/`](03_incremental_pipeline/NOTES.md) | Incremental loading, full load contrast, CDC concepts |

Each task folder has its own `NOTES.md` with what the code does, why, and
sample output — read those for the details. This file is the map.

## Repo layout

```
week-4/
├── common/                    # shared client code (HTTP + Postgres helpers, logging)
├── data/                      # source CSVs used by tasks 2 & 3
├── docker-compose.yml         # Postgres 16, localhost:5433
├── 01_github_api/
├── 02_csv_to_postgres/
└── 03_incremental_pipeline/
```
