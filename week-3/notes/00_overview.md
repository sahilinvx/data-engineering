# Week 3 Overview: SQL for Data Engineering

## What This Week Covers

This project builds a complete **retail analytics pipeline** from scratch:

1. **OLTP database** — a normalized operational database (how a store's app records transactions)
2. **Data warehouse** — a star-schema analytics database optimized for reporting
3. **ETL pipeline** — Python script that transforms source data into the warehouse
4. **13 SQL topics** — each with runnable examples
5. **20 advanced queries** — real business questions against the warehouse

## Key Concepts

| Term | Plain English |
|------|---------------|
| **OLTP** | Online Transaction Processing — handles day-to-day operations (placing orders, updating inventory) |
| **OLAP / Warehouse** | Online Analytical Processing — handles reporting and analysis across millions of rows |
| **3NF** | Third Normal Form — data split into many small tables with no duplication |
| **Star Schema** | A warehouse design with one big fact table in the center and flat dimension tables around it |
| **ETL** | Extract, Transform, Load — the process of moving data from source to warehouse |
| **SCD** | Slowly Changing Dimension — how to handle when a customer's address or email changes over time |

## How to Work Through This

1. Read `README.md` and run the setup scripts
2. Explore the OLTP schema: `sql/oltp_schema.sql`
3. Work through topic files in `sql/topics/` in order (01–13)
4. Read the matching note in `notes/` after running each topic
5. Study `sql/star_schema_design.md` to understand the warehouse design
6. Run and study `sql/20_advanced_queries.sql`
7. Run `scripts/verify_all.py` to confirm everything works

## Databases Created

- `db/retail_oltp.db` — 14,646 rows across 6 tables
- `db/retail_warehouse.db` — 7,620 fact rows + 4,596 dimension rows

## What You'll Be Able to Do After This Week

- Design normalized schemas for transactional systems
- Derive star schemas from OLTP sources
- Write window functions, CTEs, and recursive queries confidently
- Explain SCD Type 1 vs Type 2 in an interview
- Read execution plans and know when to add indexes
- Discuss partitioning trade-offs (even when your DB doesn't support it natively)
