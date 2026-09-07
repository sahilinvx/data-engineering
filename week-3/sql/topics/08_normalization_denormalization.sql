-- Topic 08: Normalization vs Denormalization
-- Database: retail_oltp.db

-- Normalized OLTP: order details require 4 joins
SELECT o.order_id, c.first_name, s.store_name, p.product_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN stores s ON o.store_id = s.store_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LIMIT 5;

-- Denormalized reporting table (derived from normalized source)
DROP TABLE IF EXISTS denormalized_order_lines;
CREATE TABLE denormalized_order_lines AS
SELECT
    o.order_id,
    o.order_date,
    o.status,
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email AS customer_email,
    s.store_name,
    s.city AS store_city,
    e.first_name || ' ' || e.last_name AS employee_name,
    p.product_id,
    p.category,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    oi.quantity * oi.unit_price * (1 - oi.discount) AS line_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN stores s ON o.store_id = s.store_id
LEFT JOIN employees e ON o.employee_id = e.employee_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Now a simple query — no joins needed (trade-off: storage + update anomalies)
SELECT order_id, customer_name, product_name, line_revenue
FROM denormalized_order_lines
WHERE status = 'delivered'
ORDER BY line_revenue DESC
LIMIT 10;
