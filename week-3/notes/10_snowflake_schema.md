# 10 — Snowflake Schema

## What it is

A **snowflake schema** is a star schema where dimension tables are further normalized into sub-dimensions. Instead of storing `category` directly in `dim_product`, we have a separate `dim_product_category` table.

## Why it matters

Understanding the star vs snowflake trade-off is a common interview topic. Snowflake schemas appear in enterprise warehouses where data consistency across categories matters.

## Our example

**Star would look like:**
```sql
dim_product (product_key, product_name, category, subcategory, unit_price)
-- category repeated on every product row
```

**Snowflake (what we built):**
```sql
dim_product_category (category_key, category, subcategory)
dim_product (product_key, product_name, category_key, unit_price)
-- category stored once, referenced by key
```

## The code

```sql
SELECT dpc.category, dpc.subcategory, SUM(fs.revenue)
FROM fact_sales fs
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
GROUP BY dpc.category, dpc.subcategory;
```

Note the extra join compared to a pure star schema.

## Common interview questions

1. **When to choose snowflake over star?** When dimension attributes are large/repeated (many products share few categories) or when you need to enforce referential integrity on dimension attributes.
2. **Performance impact?** More joins = slower queries, but modern columnar engines (BigQuery, Snowflake) handle this well.
3. **Can you mix star and snowflake?** Yes — most real warehouses do. Keep frequently-queried dimensions flat (star) and normalize rarely-used ones (snowflake).
