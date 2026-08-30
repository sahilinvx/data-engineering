# 11 — Fact Tables

## What it is

A **fact table** stores the measurable business events — the "what happened" of your data. Each row is one event at a specific grain (level of detail). Facts contain numbers you sum/average (revenue, quantity) and foreign keys pointing to dimensions.

## Why it matters

Designing the fact table correctly (choosing the right grain, measures, and keys) is the most important warehouse design decision. Get the grain wrong and every downstream report is wrong.

## Our fact table: `fact_sales`

- **Grain:** one row per order line item
- **Measures:** quantity, unit_price, discount, revenue, cost, profit
- **Foreign keys:** date_key, customer_key, product_key, store_key, employee_key
- **Degenerate dimensions:** order_id, order_item_id (IDs with no separate dim table)

## The code

```sql
SELECT COUNT(*) AS rows,
       SUM(revenue) AS total_revenue,
       SUM(profit) AS total_profit,
       AVG(revenue) AS avg_line_revenue
FROM fact_sales;
```

Output: ~7,620 rows, millions in revenue.

## Common interview questions

1. **What is fact table grain?** The level of detail — "one row per line item" vs "one row per order" vs "one row per day per store." Choose the finest grain you'll ever need.
2. **Additive vs semi-additive vs non-additive facts?** Revenue is additive (sum across any dimension). Inventory is semi-additive (sum across stores, but not across time). Ratios are non-additive (must recalculate, not sum).
3. **What are degenerate dimensions?** Attributes like order_id that stay in the fact table because creating a separate dimension table for them adds no value.
