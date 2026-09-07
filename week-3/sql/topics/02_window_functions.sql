-- Topic 02: Window Functions
-- Database: retail_warehouse.db

-- ROW_NUMBER: unique rank per customer by total spend
SELECT customer_key, full_name, total_revenue,
       ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS spend_rank
FROM (
    SELECT dc.customer_key, dc.full_name, SUM(fs.revenue) AS total_revenue
    FROM fact_sales fs
    JOIN dim_customer dc ON fs.customer_key = dc.customer_key
    WHERE dc.is_current = 1
    GROUP BY dc.customer_key, dc.full_name
)
LIMIT 10;

-- RANK vs DENSE_RANK: product revenue ranking (note ties)
SELECT product_key, product_name, revenue,
       RANK() OVER (ORDER BY revenue DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rnk
FROM (
    SELECT dp.product_key, dp.product_name, SUM(fs.revenue) AS revenue
    FROM fact_sales fs
    JOIN dim_product dp ON fs.product_key = dp.product_key
    GROUP BY dp.product_key, dp.product_name
)
LIMIT 15;

-- LAG / LEAD: month-over-month revenue change
WITH monthly AS (
    SELECT dd.year, dd.month, SUM(fs.revenue) AS revenue
    FROM fact_sales fs
    JOIN dim_date dd ON fs.date_key = dd.date_key
    GROUP BY dd.year, dd.month
)
SELECT year, month, revenue,
       LAG(revenue) OVER (ORDER BY year, month) AS prev_month_revenue,
       revenue - LAG(revenue) OVER (ORDER BY year, month) AS mom_change,
       LEAD(revenue) OVER (ORDER BY year, month) AS next_month_revenue
FROM monthly
ORDER BY year, month
LIMIT 12;

-- Running total: cumulative revenue by date
SELECT dd.full_date, daily.revenue,
       SUM(daily.revenue) OVER (ORDER BY dd.full_date) AS running_total
FROM (
    SELECT date_key, SUM(revenue) AS revenue
    FROM fact_sales
    GROUP BY date_key
) daily
JOIN dim_date dd ON daily.date_key = dd.date_key
ORDER BY dd.full_date
LIMIT 15;

-- Moving average: 7-day rolling average revenue
SELECT dd.full_date, daily.revenue,
       AVG(daily.revenue) OVER (
           ORDER BY dd.full_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS moving_avg_7day
FROM (
    SELECT date_key, SUM(revenue) AS revenue
    FROM fact_sales
    GROUP BY date_key
) daily
JOIN dim_date dd ON daily.date_key = dd.date_key
ORDER BY dd.full_date
LIMIT 15;
