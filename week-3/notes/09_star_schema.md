# 09 — Star Schema

## What it is

A **star schema** is a warehouse design with one central **fact table** (measurable events like sales) surrounded by **dimension tables** (descriptive context like who, what, where, when). The diagram looks like a star — fact in the center, dimensions as points.

## Why it matters

Star schemas are the default warehouse design. BI tools (Tableau, Looker, Power BI) are optimized for star-schema joins. Interviewers expect you to design one from an OLTP source.

## Our design

```
fact_sales → dim_date
           → dim_customer
           → dim_product
           → dim_store
           → dim_employee
```

## The code

```sql
SELECT dd.year, dd.quarter, dpc.category, SUM(fs.revenue)
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
GROUP BY dd.year, dd.quarter, dpc.category;
```

Every dimension join is a simple equality on a surrogate key (`date_key`, `customer_key`, etc.).

## Common interview questions

1. **How do you choose the grain of the fact table?** The lowest level of detail needed for analysis — here, one row per order line item.
2. **What is a surrogate key?** An auto-generated integer key in the dimension (e.g. `customer_key`) separate from the source system's ID (`customer_id`).
3. **Star vs snowflake?** Star = flat dimensions (fewer joins, faster). Snowflake = normalized dimensions (less storage, more joins).
