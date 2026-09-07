-- Topic 12: Dimension Tables (including conformed dimension)
-- Database: retail_warehouse.db

-- dim_date is a CONFORMED DIMENSION — shared standard calendar usable
-- across any fact table (sales, returns, inventory, etc.)

SELECT date_key, full_date, year, quarter, month_name, day_name, is_weekend
FROM dim_date
WHERE year = 2024 AND month = 6
LIMIT 10;

-- dim_customer: descriptive attributes about who bought
SELECT customer_key, customer_id, full_name, email, city, state, is_current
FROM dim_customer
WHERE is_current = 1
LIMIT 10;

-- dim_store: where the sale happened
SELECT store_key, store_id, store_name, city, state
FROM dim_store
LIMIT 10;

-- Join dimensions to fact for a readable report
SELECT
    dd.full_date,
    dc.full_name AS customer,
    ds.store_name,
    dp.product_name,
    fs.quantity,
    fs.revenue
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
JOIN dim_customer dc ON fs.customer_key = dc.customer_key
JOIN dim_store ds ON fs.store_key = ds.store_key
JOIN dim_product dp ON fs.product_key = dp.product_key
LIMIT 10;
