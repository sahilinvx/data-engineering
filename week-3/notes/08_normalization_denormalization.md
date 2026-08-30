# 08 — Normalization vs Denormalization

## What it is

**Normalization** splits data into many small tables to eliminate redundancy (our OLTP schema). **Denormalization** intentionally combines tables back together for faster reads, accepting some data duplication.

## Why it matters

Every data engineering role requires knowing when to normalize (transactional systems) vs denormalize (analytics/reporting). The OLTP → warehouse transformation is essentially a controlled denormalization.

## The code

Our OLTP query needs 4 joins for one order line:
```sql
FROM orders o
JOIN customers c ON ...
JOIN stores s ON ...
JOIN order_items oi ON ...
JOIN products p ON ...
```

We create a flat reporting table:
```sql
CREATE TABLE denormalized_order_lines AS
SELECT o.order_id, customer_name, store_name, product_name, line_revenue
FROM orders o JOIN customers c JOIN stores s JOIN order_items oi JOIN products p ...;
```

Now reporting is a simple `SELECT` with no joins.

## Trade-offs

| Normalized (OLTP) | Denormalized (reporting) |
|-------------------|--------------------------|
| No duplicate data | Faster reads |
| Easy to update | Harder to update (must sync many copies) |
| Many joins for reports | Storage cost increases |
| Good for writes | Good for reads |

## Common interview questions

1. **What is 3NF?** Third Normal Form — every non-key column depends only on the primary key, not on other non-key columns.
2. **When do you denormalize?** Analytics warehouses, read-heavy dashboards, materialized views for BI tools.
3. **What's an update anomaly?** In denormalized data, changing a customer's name requires updating every row that contains it.
