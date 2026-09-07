# 03 — CTEs (Common Table Expressions)

## What it is

A **CTE** (Common Table Expression) is a temporary named result set defined with `WITH ... AS (...)` that you can reference in the main query. Think of it as a "named subquery" that makes complex SQL readable.

## Why it matters

CTEs are the standard way to break complex analytics queries into readable steps. In interviews, chaining 3–4 CTEs shows you can structure logic clearly. They're also the foundation for recursive queries.

## The code

```sql
-- Basic CTE
WITH store_revenue AS (
    SELECT store_name, SUM(revenue) AS total
    FROM fact_sales fs JOIN dim_store ds ON ...
    GROUP BY store_name
)
SELECT * FROM store_revenue ORDER BY total DESC;

-- Chained CTEs: step 1 → step 2 → final query
WITH category_sales AS (...),
     total AS (SELECT SUM(revenue) AS grand_total FROM category_sales)
SELECT category, revenue, revenue * 100.0 / grand_total AS pct
FROM category_sales CROSS JOIN total;
```

## Sample output

Category revenue share:
```
Electronics | 245000 | 28.5%
Clothing    | 198000 | 23.1%
Home        | 175000 | 20.4%
```

## Common interview questions

1. **CTE vs subquery — when to use which?** CTEs are more readable and can be referenced multiple times; subqueries are fine for one-off filters.
2. **Are CTEs materialized?** In PostgreSQL 12+, `WITH ... AS MATERIALIZED` forces it; otherwise it depends on the optimizer. SQLite re-evaluates CTEs each reference.
3. **Can you use multiple CTEs?** Yes — comma-separate them in the `WITH` clause.
