# 01 — Advanced Joins

## What it is

A **join** combines rows from two or more tables based on a related column. "Advanced" joins go beyond a simple `INNER JOIN` — they include self-joins (a table joined to itself), non-equi joins (joining on ranges instead of equality), anti-joins (finding rows with *no* match), and semi-joins (checking existence without returning duplicate columns).

## Why it matters

In data engineering interviews, join questions test whether you can navigate real schemas with 5+ tables. Anti-joins and semi-joins appear constantly in data quality checks ("find customers who never ordered") and incremental ETL ("load only records not yet in the warehouse").

## The code

See `sql/topics/01_advanced_joins.sql`. Key patterns:

```sql
-- Self join: table aliased twice
FROM employees e1 JOIN employees e2 ON e1.manager_id = e2.manager_id

-- Anti-join: LEFT JOIN + WHERE right side IS NULL
FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL

-- Semi-join: EXISTS subquery (returns rows from left table only)
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.store_id = s.store_id)
```

## Sample output

Self-join found coworkers sharing manager "Cindy":
```
Matthew | Cindy
```

Anti-join found customers with zero orders (about 10 in our sample).

## Common interview questions

1. **What's the difference between LEFT JOIN and NOT EXISTS for finding unmatched rows?** Both work; `NOT EXISTS` often performs better on large tables and is clearer in intent.
2. **When would you use a non-equi join?** Matching records to tiers/buckets (price ranges, date ranges, salary bands) without a lookup table.
3. **Self join vs recursive CTE?** Self join works for one level (coworkers with same manager); recursive CTE walks the full tree (entire org chart).
