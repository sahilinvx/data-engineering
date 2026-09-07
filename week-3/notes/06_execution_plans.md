# 06 — Execution Plans

## What it is

An **execution plan** shows how the database engine will (or did) execute your query — which tables it scans, which indexes it uses, and in what order it joins tables. `EXPLAIN QUERY PLAN` in SQLite reveals this.

## Why it matters

Reading execution plans is how you diagnose slow queries in production. Interviewers give you a slow query and ask "how would you optimize this?" — the answer starts with `EXPLAIN`.

## The code

```sql
EXPLAIN QUERY PLAN
SELECT dd.year, SUM(fs.revenue)
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE dd.year = 2024
GROUP BY dd.year;
```

## How to read SQLite output

| Keyword | Meaning |
|---------|---------|
| `SCAN table` | Full table scan — reads every row |
| `SEARCH table USING INDEX` | Index lookup — much faster |
| `USE TEMP B-TREE` | Sorting/grouping spilled to temp storage |
| `COMPOUND SUBQUERY` | Subquery or CTE being evaluated |

## Sample output

```
SEARCH fact_sales USING INDEX idx_fact_sales_date (date_key=?)
SEARCH dim_date USING INDEX sqlite_autoindex_dim_date_1 (date_key=?)
USE TEMP B-TREE FOR GROUP BY
```

The index on `date_key` is being used — good. The temp B-tree for GROUP BY is normal for aggregations.

## Common interview questions

1. **SCAN vs SEARCH — which is better?** SEARCH (index) is faster for large tables; SCAN is fine when the table is small or you're reading most rows anyway.
2. **How do you fix a full table scan on a large table?** Add an index on the filtered/joined column, or rewrite the query.
3. **EXPLAIN vs EXPLAIN ANALYZE?** EXPLAIN shows the plan; EXPLAIN ANALYZE (PostgreSQL) actually runs the query and shows real timings.
