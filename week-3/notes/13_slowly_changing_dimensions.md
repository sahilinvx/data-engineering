# 13 — Slowly Changing Dimensions (SCD)

## What it is

**Slowly Changing Dimensions** handle the reality that dimension data changes over time — a customer moves cities, a product gets renamed, an employee gets promoted. SCD strategies define whether you keep history or overwrite.

## Why it matters

SCD Type 1 vs Type 2 is one of the most asked data warehousing interview questions. Getting it wrong means your historical reports show incorrect data ("this customer was always in NY" when they were in CA for 3 years).

## Type 1: Overwrite (no history)

```sql
-- Customer 42's email was wrong — just fix it
UPDATE dim_customer
SET email = 'corrected@example.com'
WHERE customer_id = 42 AND is_current = 1;
```

**Before:** `email = 'old@wrong.com'`
**After:** `email = 'corrected@example.com'` — same row, old value gone.

**Use when:** typos, unimportant changes, or you don't need history.

## Type 2: Keep history (new row)

```sql
-- Expire old record
UPDATE dim_customer
SET effective_to = '2025-06-01', is_current = 0
WHERE customer_id = 100 AND is_current = 1;

-- Insert new record with updated city
INSERT INTO dim_customer (..., city, state, effective_from, is_current)
VALUES (..., 'New York', 'NY', '2025-06-02', 1);
```

**Before:** 1 row (city = CA, is_current = 1)
**After:** 2 rows:
```
| city | effective_from | effective_to | is_current |
| CA   | 2020-01-01     | 2025-06-01   | 0          |
| NY   | 2025-06-02     | NULL         | 1          |
```

**Use when:** you need to answer "what did reports show at the time?" — regulatory, financial, or trend analysis.

## Common interview questions

1. **Type 1 vs Type 2 — when to use each?** Type 1 for corrections/typos; Type 2 when historical accuracy matters.
2. **What is Type 3?** Keeps limited history in the same row (previous value in a separate column). Rarely used.
3. **How do you join fact to Type 2 dimension?** Match on the key that was current at the time of the transaction: `fact.date_key BETWEEN dim.effective_from AND COALESCE(dim.effective_to, '9999-12-31')`.
