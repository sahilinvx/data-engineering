-- Topic 10: Snowflake Schema (contrast with star)
-- Database: retail_warehouse.db
--
-- Snowflake = dimensions are further normalized into sub-dimensions.
-- Our dim_product links to dim_product_category instead of storing category inline.

-- STAR style (hypothetical — category denormalized into dim_product):
--   SELECT dp.category, SUM(revenue) ... GROUP BY dp.category

-- SNOWFLAKE style (actual schema — extra join to category table):
SELECT
    dpc.category,
    dpc.subcategory,
    COUNT(DISTINCT dp.product_key) AS num_products,
    SUM(fs.revenue) AS revenue
FROM fact_sales fs
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
GROUP BY dpc.category, dpc.subcategory
ORDER BY revenue DESC
LIMIT 15;

-- Trade-off: snowflake saves storage and enforces consistency;
-- star schema is faster to query (fewer joins).
