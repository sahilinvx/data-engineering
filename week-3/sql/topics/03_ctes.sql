-- Topic 03: CTEs (Common Table Expressions)
-- Database: retail_warehouse.db

-- Basic CTE: top 10 stores by revenue
WITH store_revenue AS (
    SELECT ds.store_key, ds.store_name, SUM(fs.revenue) AS total_revenue
    FROM fact_sales fs
    JOIN dim_store ds ON fs.store_key = ds.store_key
    GROUP BY ds.store_key, ds.store_name
)
SELECT store_name, total_revenue
FROM store_revenue
ORDER BY total_revenue DESC
LIMIT 10;

-- Multi-step chained CTEs: category performance with share of total
WITH category_sales AS (
    SELECT dpc.category, SUM(fs.revenue) AS revenue
    FROM fact_sales fs
    JOIN dim_product dp ON fs.product_key = dp.product_key
    JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
    GROUP BY dpc.category
),
total AS (
    SELECT SUM(revenue) AS grand_total FROM category_sales
)
SELECT
    cs.category,
    cs.revenue,
    ROUND(cs.revenue * 100.0 / t.grand_total, 2) AS pct_of_total
FROM category_sales cs
CROSS JOIN total t
ORDER BY cs.revenue DESC;
