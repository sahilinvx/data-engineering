# Week 2 Pipeline — How Everything Connects

A map of the whole `week-2/` setup: what lives where, and the order things
actually run in. Read this top to bottom once, then use the "topic lookup"
table at the end as a reference.

## Directory map

```
week-2/
├── .env                    secrets / per-environment overrides — NOT committed (gitignored)
├── .env.example            template showing what .env can contain — IS committed
├── config/
│   └── config.ini          default settings — IS committed
├── data/
│   └── csv_batch/          10 raw input CSVs for the merge task (deliberately messy)
├── pipeline_utils/         the reusable package — shared building blocks
│   ├── paths.py            Pathlib helpers
│   ├── context.py          the timed_step() context manager
│   ├── io_csv.py           CSV read (generator) / write / delimiter sniffing
│   ├── io_json.py          JSON read / write
│   ├── config.py           loads config.ini + .env into one Settings object
│   ├── http_client.py      requests wrapper + the iter_users_with_posts() generator
│   └── logging_setup.py    one shared logging.basicConfig()
├── merge_csvs.py           hands-on #1 — reads data/csv_batch/, writes output/merged_*
├── fetch_api_to_json.py    hands-on #2 — calls a REST API, writes output/api_*
├── output/                 everything the scripts produce lands here
└── requirements.txt        exact installed package versions (pip freeze)
```

Everything in `pipeline_utils/` is *used by* both scripts — it's not a third
script you run, it's the toolbox the other two import from.

## Flow 1: config + `.env` (read this part first — it trips people up)

Both scripts start with the same line: `settings = load_settings()`. Here's
exactly what that does, in order:

```
 .env file  ──(load_dotenv)──▶  os.environ
                                     │
 config.ini ──(configparser)──▶  defaults
                                     │
                                     ▼
                For each setting: os.getenv(NAME, fallback=value from config.ini)
                                     │
                                     ▼
                          one Settings object
                (api_base_url, request_timeout, log_level, output_dir)
```

1. `load_dotenv()` opens `.env` (if it exists) and injects each `KEY=VALUE`
   line into `os.environ` — exactly as if you'd typed `export KEY=VALUE` in
   your terminal before running the script.
2. `configparser` separately reads `config/config.ini` — plain defaults, safe
   to commit to git since nothing in it is secret.
3. For every setting, `load_settings()` checks the environment **first**; if
   nothing's set there, it falls back to the value from `config.ini`.
4. The result is packaged into one typed `Settings` object, passed around
   instead of scattering `os.getenv()` calls through the rest of the code.

**Why two files instead of one:** `config.ini` is the same for everyone and
lives in git. `.env` is local to your machine, gitignored, and is where a real
API key or password would go — right now it only holds `LOG_LEVEL=INFO`
because JSONPlaceholder needs no auth, but the mechanism is the same one
you'd use for a real secret.

## Flow 2: `merge_csvs.py` (hands-on #1)

```
data/csv_batch/*.csv
        │  find_csv_files()          [Pathlib]
        ▼
   list of 10 file paths
        │
        │  for each file, wrapped in timed_step()   [Context manager: logs start/end/duration]
        ▼
   sniff_delimiter()  →  iter_csv_rows()   [csv.Sniffer, then a generator that yields rows lazily]
        │
        │  try/except around the read:
        │    - bad encoding / unreadable file → log error, skip THIS FILE, keep going
        │    - row missing an email → log warning, skip THIS ROW, keep going
        ▼
   merged_rows() generator yields validated {source_file, name, email, city} dicts
        │
        │  list(...) — materialized once, since it's needed twice below
        ▼
   write_csv_rows()  →  output/merged_customers.csv
   write_json()       →  output/merged_customers.json   (stamped with merged_at, via datetime)
```

Of the 10 input files: 9 merge cleanly (23 rows total), 1 row is skipped for
a missing email, and 1 whole file is skipped for bad encoding — all logged,
none of it crashes the script.

## Flow 3: `fetch_api_to_json.py` (hands-on #2)

```
load_settings()  →  api_base_url, timeout
        │
        ▼
iter_users_with_posts(api_base_url)          [Requests + generator]
        │
        │  fetch_json(base_url/users)  →  list of 10 users
        │  for each user:
        │      fetch_json(base_url/users/{id}/posts)
        │      yield {**user, "posts": posts}     ← one full record at a time
        │
        │  wrapped in try/except requests.exceptions.RequestException
        │  (a network failure logs an error and the script exits cleanly)
        ▼
list(...) of 10 user+posts records
        │
        ▼
write_json()  →  output/api_users_with_posts.json   (stamped with fetched_at, via datetime)
```

## Topic → file quick reference

| Topic | Where to look |
|---|---|
| File Handling (CSV/JSON/XML) | `csv_basics.py`; `pipeline_utils/io_csv.py`, `io_json.py` |
| Logging | `pipeline_utils/logging_setup.py`, used everywhere via `logger = logging.getLogger(__name__)` |
| Error Handling | `merge_csvs.py`'s `try/except` around each file; `fetch_api_to_json.py`'s `try/except` around the API call |
| Virtual Env & Requirements | `.venv/` (gitignored), `requirements.txt` |
| Typing | every function signature, e.g. `load_settings(...) -> Settings` |
| Datetime | `merged_at` / `fetched_at` timestamps in both scripts' JSON output |
| Generators | `pipeline_utils/io_csv.py: iter_csv_rows()`, `http_client.py: iter_users_with_posts()`, `merge_csvs.py: merged_rows()` |
| Context Managers | `pipeline_utils/context.py: timed_step()` |
| Requests Library | `pipeline_utils/http_client.py` |
| Pathlib | `pipeline_utils/paths.py` |
| Config Files | `config/config.ini`, loaded in `pipeline_utils/config.py` |
| Environment Variables | `.env`, `.env.example`, `load_dotenv()` in `pipeline_utils/config.py` |
