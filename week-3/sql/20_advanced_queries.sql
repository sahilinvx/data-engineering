-- 20 Advanced SQL Queries against the sales warehouse
-- Database: retail_warehouse.db

-- Q1: Top 5 customers by revenue per quarter (window functions)
WITH quarterly AS (
    SELECT dd.year, dd.quarter, dc.customer_key, dc.full_name,
           SUM(fs.revenue) AS revenue,
           ROW_NUMBER() OVER (
               PARTITION BY dd.year, dd.quarter ORDER BY SUM(fs.revenue) DESC
           ) AS rn
    FROM fact_sales fs
    JOIN dim_date dd ON fs.date_key = dd.date_key
    JOIN dim_customer dc ON fs.customer_key = dc.customer_key
    WHERE dc.is_current = 1
    GROUP BY dd.year, dd.quarter, dc.customer_key, dc.full_name
)
SELECT year, quarter, full_name, revenue
FROM quarterly WHERE rn <= 5
ORDER BY year, quarter, rn;

-- Q2: Month-over-month revenue growth percentage
WITH monthly AS (
    SELECT dd.year, dd.month, SUM(fs.revenue) AS revenue
    FROM fact_sales fs JOIN dim_date dd ON fs.date_key = dd.date_key
    GROUP BY dd.year, dd.month
)
SELECT year, month, revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY year, month))
             / LAG(revenue) OVER (ORDER BY year, month) * 100, 2) AS mom_growth_pct
FROM monthly ORDER BY year, month;

-- Q3: Products never sold (anti-join)
SELECT dp.product_key, dp.product_name
FROM dim_product dp
LEFT JOIN fact_sales fs ON dp.product_key = fs.product_key
WHERE fs.sales_key IS NULL
LIMIT 20;

-- Q4: Store revenue rank within each state
SELECT ds.state, ds.store_name, SUM(fs.revenue) AS revenue,
       RANK() OVER (PARTITION BY ds.state ORDER BY SUM(fs.revenue) DESC) AS state_rank
FROM fact_sales fs
JOIN dim_store ds ON fs.store_key = ds.store_key
GROUP BY ds.state, ds.store_name
ORDER BY ds.state, state_rank
LIMIT 20;

-- Q5: Average order value by customer segment (high/medium/low spenders)
WITH customer_totals AS (
    SELECT customer_key, SUM(revenue) AS total
    FROM fact_sales GROUP BY customer_key
),
segments AS (
    SELECT customer_key,
           CASE
               WHEN total >= 5000 THEN 'High'
               WHEN total >= 1000 THEN 'Medium'
               ELSE 'Low'
           END AS segment
    FROM customer_totals
)
SELECT s.segment, COUNT(DISTINCT fs.order_id) AS orders,
       ROUND(AVG(fs.revenue), 2) AS avg_line_revenue
FROM fact_sales fs
JOIN segments s ON fs.customer_key = s.customer_key
GROUP BY s.segment;

-- Q6: Category revenue share by year
WITH yearly_cat AS (
    SELECT dd.year, dpc.category, SUM(fs.revenue) AS revenue
    FROM fact_sales fs
    JOIN dim_date dd ON fs.date_key = dd.date_key
    JOIN dim_product dp ON fs.product_key = dp.product_key
    JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
    GROUP BY dd.year, dpc.category
),
yearly_total AS (
    SELECT year, SUM(revenue) AS total FROM yearly_cat GROUP BY year
)
SELECT yc.year, yc.category, yc.revenue,
       ROUND(yc.revenue * 100.0 / yt.total, 2) AS pct_share
FROM yearly_cat yc JOIN yearly_total yt ON yc.year = yt.year
ORDER BY yc.year, yc.revenue DESC;

-- Q7: Weekend vs weekday revenue comparison
SELECT dd.is_weekend,
       CASE dd.is_weekend WHEN 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       COUNT(*) AS transactions,
       ROUND(SUM(fs.revenue), 2) AS total_revenue
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.is_weekend;

-- Q8: Top 3 products per category by units sold
WITH ranked AS (
    SELECT dpc.category, dp.product_name, SUM(fs.quantity) AS units,
           ROW_NUMBER() OVER (PARTITION BY dpc.category ORDER BY SUM(fs.quantity) DESC) AS rn
    FROM fact_sales fs
    JOIN dim_product dp ON fs.product_key = dp.product_key
    JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
    GROUP BY dpc.category, dp.product_name
)
SELECT category, product_name, units FROM ranked WHERE rn <= 3
ORDER BY category, rn;

-- Q9: Employee sales performance vs store average
WITH emp_sales AS (
    SELECT de.employee_key, de.full_name, de.store_name, SUM(fs.revenue) AS revenue
    FROM fact_sales fs
    JOIN dim_employee de ON fs.employee_key = de.employee_key
    GROUP BY de.employee_key, de.full_name, de.store_name
),
store_avg AS (
    SELECT store_name, AVG(revenue) AS avg_revenue FROM emp_sales GROUP BY store_name
)
SELECT e.full_name, e.store_name, e.revenue,
       ROUND(s.avg_revenue, 2) AS store_avg,
       ROUND(e.revenue - s.avg_revenue, 2) AS vs_avg
FROM emp_sales e JOIN store_avg s ON e.store_name = s.store_name
ORDER BY vs_avg DESC LIMIT 15;

-- Q10: Cumulative revenue by month within each year
SELECT dd.year, dd.month, SUM(fs.revenue) AS monthly_revenue,
       SUM(SUM(fs.revenue)) OVER (
           PARTITION BY dd.year ORDER BY dd.month
       ) AS ytd_revenue
FROM fact_sales fs JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year, dd.month ORDER BY dd.year, dd.month;

-- Q11: Customers with orders in 3+ different stores (cross-store shoppers)
SELECT dc.full_name, COUNT(DISTINCT fs.store_key) AS stores_shopped
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_key = dc.customer_key
WHERE dc.is_current = 1
GROUP BY dc.customer_key, dc.full_name
HAVING COUNT(DISTINCT fs.store_key) >= 3
ORDER BY stores_shopped DESC LIMIT 15;

-- Q12: Discount impact analysis
SELECT
    CASE WHEN discount = 0 THEN 'No discount'
         WHEN discount <= 0.1 THEN '1-10%'
         WHEN discount <= 0.2 THEN '11-20%'
         ELSE '20%+' END AS discount_band,
    COUNT(*) AS lines,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(AVG(quantity), 2) AS avg_qty
FROM fact_sales GROUP BY 1 ORDER BY revenue DESC;

-- Q13: Profit margin by category
SELECT dpc.category,
       ROUND(SUM(fs.revenue), 2) AS revenue,
       ROUND(SUM(fs.cost), 2) AS cost,
       ROUND(SUM(fs.profit), 2) AS profit,
       ROUND(SUM(fs.profit) / SUM(fs.revenue) * 100, 2) AS margin_pct
FROM fact_sales fs
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_product_category dpc ON dp.category_key = dpc.category_key
GROUP BY dpc.category ORDER BY margin_pct DESC;

-- Q14: New vs returning customers per month (first order month)
WITH first_order AS (
    SELECT customer_key, MIN(date_key) AS first_date_key
    FROM fact_sales GROUP BY customer_key
),
monthly_orders AS (
    SELECT fs.customer_key, dd.year, dd.month, fs.date_key
    FROM fact_sales fs JOIN dim_date dd ON fs.date_key = dd.date_key
)
SELECT mo.year, mo.month,
       SUM(CASE WHEN mo.date_key = fo.first_date_key THEN 1 ELSE 0 END) AS new_customer_orders,
       SUM(CASE WHEN mo.date_key > fo.first_date_key THEN 1 ELSE 0 END) AS returning_orders
FROM monthly_orders mo
JOIN first_order fo ON mo.customer_key = fo.customer_key
GROUP BY mo.year, mo.month ORDER BY mo.year, mo.month;

-- Q15: 7-day moving average of daily transactions
SELECT dd.full_date,
       COUNT(*) AS daily_transactions,
       ROUND(AVG(COUNT(*)) OVER (
           ORDER BY dd.full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 2) AS moving_avg_7d
FROM fact_sales fs JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.full_date ORDER BY dd.full_date LIMIT 20;

-- Q16: Pareto analysis — products contributing 80% of revenue
WITH product_rev AS (
    SELECT dp.product_name, SUM(fs.revenue) AS revenue
    FROM fact_sales fs JOIN dim_product dp ON fs.product_key = dp.product_key
    GROUP BY dp.product_name
),
ranked AS (
    SELECT product_name, revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative,
           SUM(revenue) OVER () AS total
    FROM product_rev
)
SELECT product_name, revenue,
       ROUND(cumulative * 100.0 / total, 2) AS cumulative_pct
FROM ranked WHERE cumulative <= total * 0.8
ORDER BY revenue DESC LIMIT 20;

-- Q17: Quarterly same-store revenue (stores open all 4 quarters of a year)
WITH store_qtr AS (
    SELECT ds.store_key, ds.store_name, dd.year, dd.quarter, SUM(fs.revenue) AS revenue
    FROM fact_sales fs
    JOIN dim_store ds ON fs.store_key = ds.store_key
    JOIN dim_date dd ON fs.date_key = dd.date_key
    GROUP BY ds.store_key, ds.store_name, dd.year, dd.quarter
),
full_year_stores AS (
    SELECT store_key, year FROM store_qtr
    GROUP BY store_key, year HAVING COUNT(DISTINCT quarter) = 4
)
SELECT sq.store_name, sq.year, sq.quarter, sq.revenue
FROM store_qtr sq
JOIN full_year_stores fys ON sq.store_key = fys.store_key AND sq.year = fys.year
ORDER BY sq.store_name, sq.year, sq.quarter LIMIT 20;

-- Q18: Basket size distribution (items per order)
WITH basket AS (
    SELECT order_id, SUM(quantity) AS items, SUM(revenue) AS order_total
    FROM fact_sales GROUP BY order_id
)
SELECT
    CASE WHEN items = 1 THEN '1 item'
         WHEN items <= 3 THEN '2-3 items'
         WHEN items <= 5 THEN '4-5 items'
         ELSE '6+ items' END AS basket_size,
    COUNT(*) AS num_orders,
    ROUND(AVG(order_total), 2) AS avg_order_value
FROM basket GROUP BY 1 ORDER BY num_orders DESC;

-- Q19: Year-over-year revenue by quarter
SELECT dd.year, dd.quarter, SUM(fs.revenue) AS revenue,
       LAG(SUM(fs.revenue)) OVER (PARTITION BY dd.quarter ORDER BY dd.year) AS prev_year_revenue,
       ROUND((SUM(fs.revenue) - LAG(SUM(fs.revenue)) OVER (PARTITION BY dd.quarter ORDER BY dd.year))
             / LAG(SUM(fs.revenue)) OVER (PARTITION BY dd.quarter ORDER BY dd.year) * 100, 2) AS yoy_pct
FROM fact_sales fs JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year, dd.quarter ORDER BY dd.quarter, dd.year;

-- Q20: Recursive employee hierarchy depth distribution (OLTP cross-reference via employee dim)
-- Uses warehouse employee dimension; for hierarchy depth, query OLTP separately.
-- Here: revenue by employee title as a proxy for org level
SELECT de.title,
       COUNT(DISTINCT de.employee_key) AS num_employees,
       ROUND(SUM(fs.revenue), 2) AS total_revenue,
       ROUND(AVG(fs.revenue), 2) AS avg_line_revenue
FROM fact_sales fs
JOIN dim_employee de ON fs.employee_key = de.employee_key
GROUP BY de.title ORDER BY total_revenue DESC;
