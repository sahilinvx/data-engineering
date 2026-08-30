# 07 — Partitioning

## What it is

**Partitioning** splits one large table into smaller physical pieces (partitions) based on a key — usually date. Queries that filter on the partition key only scan relevant partitions, not the entire table.

## Why it matters

Partitioning is standard in production warehouses (BigQuery, Snowflake, PostgreSQL). Even though SQLite doesn't support it natively, you need to understand the concept for interviews and for when you work with real warehouse platforms.

## SQLite limitation

SQLite has **no native table partitioning**. We simulate it by creating separate tables per year and UNION-ing them:

```sql
CREATE TABLE fact_sales_2024 AS
SELECT fs.* FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key WHERE dd.year = 2024;

CREATE TABLE fact_sales_2025 AS ...;

-- Query across partitions
SELECT '2024', COUNT(*), SUM(revenue) FROM fact_sales_2024
UNION ALL
SELECT '2025', COUNT(*), SUM(revenue) FROM fact_sales_2025;
```

## Real-world equivalents

| Platform | Partitioning |
|----------|-------------|
| PostgreSQL | `PARTITION BY RANGE (date)` — declarative |
| BigQuery | Partitioned tables by `DATE` or `TIMESTAMP` column |
| Snowflake | Automatic micro-partitioning by ingestion order |
| SQLite | Manual separate tables + UNION (our simulation) |

## Common interview questions

1. **Partitioning vs indexing?** Complementary: partitioning reduces data scanned; indexes speed lookups within a partition.
2. **What makes a good partition key?** High-cardinality column used in most queries (usually date). Avoid partitioning on low-cardinality columns.
3. **What is partition pruning?** The optimizer skips partitions that don't match the WHERE clause — the main performance benefit.
