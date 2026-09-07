-- Topic 01: Advanced Joins
-- Database: retail_oltp.db

-- 1) SELF JOIN: find employee pairs who share the same manager
SELECT
    e1.employee_id   AS emp1_id,
    e1.first_name || ' ' || e1.last_name AS emp1_name,
    e2.employee_id   AS emp2_id,
    e2.first_name || ' ' || e2.last_name AS emp2_name,
    m.first_name || ' ' || m.last_name AS shared_manager
FROM employees e1
JOIN employees e2
    ON e1.manager_id = e2.manager_id
   AND e1.employee_id < e2.employee_id
JOIN employees m ON e1.manager_id = m.employee_id
LIMIT 10;

-- 2) MULTIPLE JOINS: order details with customer, store, product
SELECT
    o.order_id,
    c.first_name || ' ' || c.last_name AS customer,
    s.store_name,
    p.product_name,
    oi.quantity,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS line_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN stores s ON o.store_id = s.store_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'delivered'
LIMIT 10;

-- 3) NON-EQUI JOIN: match products to price tiers without a lookup table
SELECT
    p.product_id,
    p.product_name,
    p.unit_price,
    tier.tier_name
FROM products p
JOIN (
    SELECT 'Budget' AS tier_name, 0 AS min_price, 50 AS max_price
    UNION ALL SELECT 'Mid-range', 50, 150
    UNION ALL SELECT 'Premium', 150, 99999
) tier ON p.unit_price >= tier.min_price AND p.unit_price < tier.max_price
LIMIT 10;

-- 4) ANTI-JOIN: customers who have NEVER placed an order
SELECT c.customer_id, c.first_name, c.last_name, c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
LIMIT 10;

-- 5) SEMI-JOIN (EXISTS): stores that have at least one delivered order
SELECT s.store_id, s.store_name, s.city
FROM stores s
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.store_id = s.store_id AND o.status = 'delivered'
)
LIMIT 10;
