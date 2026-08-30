-- Topic 11: Fact Table
-- Database: retail_warehouse.db

-- A fact table stores measurable business events (sales) at the lowest grain.
-- Grain here: one row per order line item.

SELECT
    COUNT(*) AS total_fact_rows,
    COUNT(DISTINCT order_id) AS distinct_orders,
    SUM(quantity) AS total_units,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(revenue), 2) AS avg_line_revenue
FROM fact_sales;

-- Fact tables contain:
--   - Foreign keys to dimensions (date_key, customer_key, ...)
--   - Degenerate dimensions (order_id, order_item_id — no separate dim table)
--   - Measures (quantity, revenue, cost, profit)

SELECT sales_key, date_key, customer_key, product_key, order_id, quantity, revenue, profit
FROM fact_sales
LIMIT 10;
