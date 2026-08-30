-- Topic 09: Star Schema Design
-- Database: retail_warehouse.db
--
-- Star schema = one central FACT table surrounded by DIMENSION tables.
-- Dimensions are denormalized (flat); joins are simple and fast for BI tools.

-- Visual structure (implemented in warehouse_schema.sql):
--   fact_sales  -->  dim_date
--                -->  dim_customer
--                -->  dim_product --> dim_product_category (snowflake exception)
--                -->  dim_store
--                -->  dim_employee

-- Star-schema query: revenue by category and quarter (simple joins)
SELECT
    dd.year,
    dd.quarter,
    dpc.category,
    SUM(fs.revenue) AS total_revenue,
    SUM(fs.quantity) AS units_sold
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
GROUP BY dd.year, dd.quarter, dpc.category
ORDER BY dd.year, dd.quarter, total_revenue DESC
LIMIT 15;
