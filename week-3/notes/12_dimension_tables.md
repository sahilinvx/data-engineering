# 12 — Dimension Tables

## What it is

**Dimension tables** provide descriptive context for facts — the "who, what, where, when, why" surrounding each event. They contain human-readable attributes (names, categories, dates) that you filter and group by in reports.

## Why it matters

Dimensions are what make a warehouse usable for business users. A fact table full of integer keys is useless without dimensions to translate them into meaningful labels.

## Our dimensions

| Table | Conformed? | Key attributes |
|-------|-----------|----------------|
| `dim_date` | Yes — reusable across any fact | year, quarter, month, day_name, is_weekend |
| `dim_customer` | Yes | full_name, email, city, state, SCD columns |
| `dim_product` | No | product_name, category_key |
| `dim_store` | No | store_name, city, state |
| `dim_employee` | No | full_name, title, store_name |

**Conformed dimension** = shared standard definition used across multiple fact tables. `dim_date` is the classic example — every subject area (sales, returns, inventory) uses the same calendar.

## The code

```sql
SELECT dd.full_date, dc.full_name, ds.store_name, dp.product_name, fs.revenue
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
JOIN dim_customer dc ON fs.customer_key = dc.customer_key
JOIN dim_store ds ON fs.store_key = ds.store_key
JOIN dim_product dp ON fs.product_key = dp.product_key
LIMIT 10;
```

## Common interview questions

1. **What is a conformed dimension?** A dimension with consistent meaning across the organization, shared by multiple fact tables (e.g. one `dim_date` for sales and returns).
2. **Surrogate key vs natural key?** Surrogate (`customer_key` = auto integer) is preferred because source system IDs can change, merge, or collide across systems.
3. **How wide should dimensions be?** Include every attribute business users might filter or group by. It's OK for dimensions to have 30+ columns.
