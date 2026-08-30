# 02 — Window Functions

## What it is

**Window functions** perform calculations across a set of rows that are related to the current row — without collapsing them into a single result like `GROUP BY` does. Think of them as adding a new column computed "over a window" of data.

## Why it matters

Window functions are the #1 SQL skill tested in data engineering interviews. They're essential for rankings, running totals, period-over-period comparisons, and deduplication — tasks that are awkward or impossible with plain `GROUP BY`.

## The code

```sql
-- ROW_NUMBER: unique sequential rank (no ties)
ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS spend_rank

-- RANK: skips numbers after ties (1, 2, 2, 4)
-- DENSE_RANK: no gaps after ties (1, 2, 2, 3)

-- LAG/LEAD: access previous/next row
revenue - LAG(revenue) OVER (ORDER BY year, month) AS mom_change

-- Running total
SUM(revenue) OVER (ORDER BY full_date) AS running_total

-- Moving average (last 7 rows including current)
AVG(revenue) OVER (ORDER BY full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

## Sample output

Top customers by spend:
```
David Yang      | 15538.06 | 1
Wendy Johnson   | 14025.59 | 2
Kevin Mills     | 12774.25 | 3
```

## Common interview questions

1. **ROW_NUMBER vs RANK vs DENSE_RANK?** ROW_NUMBER always unique; RANK and DENSE_RANK handle ties differently (gaps vs no gaps).
2. **Write a query for month-over-month revenue growth.** Use `LAG()` in a CTE of monthly aggregates.
3. **How do you deduplicate rows keeping the latest?** `ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC)` then filter `WHERE rn = 1`.
