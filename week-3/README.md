# Week 3: SQL for Data Engineering

A hands-on SQL curriculum covering OLTP design, data warehousing, star/snowflake schemas, and advanced query patterns — all runnable against local SQLite databases.

## Quick Start

```bash
# 1. Create virtual environment
#    If `python3 -m venv venv` fails (e.g. Cursor AppImage wrapper), use:
pip install virtualenv --break-system-packages   # one-time, if needed
virtualenv venv

# 2. Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# 3. Build databases
python scripts/setup_oltp.py          # creates db/retail_oltp.db
python scripts/etl_to_warehouse.py    # creates db/retail_warehouse.db

# 4. Run a topic SQL file
python scripts/run_sql.py sql/topics/02_window_functions.sql

# 5. Verify everything
python scripts/verify_all.py
```

**Alternative:** use the helper script (sets PYTHONPATH automatically):

```bash
./run.sh python scripts/setup_oltp.py
./run.sh python scripts/etl_to_warehouse.py
./run.sh python scripts/verify_all.py
```

## Project Structure

```
db/                          SQLite database files
scripts/
  setup_oltp.py              Create + seed OLTP database
  etl_to_warehouse.py        ETL from OLTP → warehouse
  run_sql.py                 Run any .sql file
  verify_all.py              Test all queries
sql/
  oltp_schema.sql            OLTP DDL
  warehouse_schema.sql       Warehouse DDL
  topics/                    13 topic SQL files (01–13)
  20_advanced_queries.sql    20 business questions
  star_schema_design.md      OLTP → warehouse decisions
notes/                       Teaching notes per topic
```

## Databases

| Database | Purpose | Tables |
|----------|---------|--------|
| `db/retail_oltp.db` | Normalized source (3NF) | stores, employees, customers, products, orders, order_items |
| `db/retail_warehouse.db` | Star schema warehouse | fact_sales + 6 dimension tables |

## Topics Covered

1. Advanced Joins (self, multi, non-equi, anti, semi)
2. Window Functions (ROW_NUMBER, RANK, LAG/LEAD, running totals)
3. CTEs (basic and chained)
4. Recursive Queries (org chart)
5. Indexes (before/after)
6. Execution Plans (EXPLAIN QUERY PLAN)
7. Partitioning (simulated — SQLite limitation noted)
8. Normalization / Denormalization
9. Star Schema
10. Snowflake Schema
11. Fact Tables
12. Dimension Tables (conformed dimension)
13. Slowly Changing Dimensions (Type 1 & 2)

## Running SQL Manually

```bash
sqlite3 db/retail_warehouse.db < sql/topics/02_window_functions.sql
```

Or with the Python runner (shows formatted output):

```bash
python scripts/run_sql.py sql/20_advanced_queries.sql --limit 5
```

## Seed Data

- ~50 stores, ~200 employees, ~2,000 customers, ~500 products
- ~3,000 orders, ~8,000+ order items
- Includes realistic messiness: null emails, duplicate-ish records, varied order statuses
