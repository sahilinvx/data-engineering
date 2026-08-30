-- Topic 07: Partitioning (simulated — SQLite has no native table partitioning)
-- Database: retail_warehouse.db
--
-- In PostgreSQL/BigQuery/Snowflake, you'd partition fact_sales by year or month.
-- SQLite workaround: create separate tables per partition and UNION ALL in queries.

DROP TABLE IF EXISTS fact_sales_2024;
DROP TABLE IF EXISTS fact_sales_2025;

-- Simulate range partitions by year
CREATE TABLE fact_sales_2024 AS
SELECT fs.* FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE dd.year = 2024;

CREATE TABLE fact_sales_2025 AS
SELECT fs.* FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE dd.year = 2025;

-- Query across partitions (what a view would do in production)
SELECT '2024' AS partition_year, COUNT(*) AS rows, SUM(revenue) AS revenue
FROM fact_sales_2024
UNION ALL
SELECT '2025', COUNT(*), SUM(revenue)
FROM fact_sales_2025;

-- Cleanup simulation tables
DROP TABLE IF EXISTS fact_sales_2024;
DROP TABLE IF EXISTS fact_sales_2025;
