-- Topic 06: Execution Plans (EXPLAIN QUERY PLAN)
-- Database: retail_warehouse.db

-- Simple scan on fact table
EXPLAIN QUERY PLAN
SELECT SUM(revenue) FROM fact_sales;

-- Join plan: fact + date + product
EXPLAIN QUERY PLAN
SELECT dd.year, dp.product_name, SUM(fs.revenue)
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
JOIN dim_product dp ON fs.product_key = dp.product_key
GROUP BY dd.year, dp.product_name;

-- After index exists (created in warehouse_schema.sql), filter should use index
EXPLAIN QUERY PLAN
SELECT SUM(revenue)
FROM fact_sales
WHERE date_key BETWEEN 20240101 AND 20241231;

-- Interpretation guide (SQLite output):
-- SEARCH = index used (good for large tables)
-- SCAN  = full table scan (OK for small tables, slow at scale)
-- USE TEMP B-TREE = sorting/aggregation spill to temp storage
