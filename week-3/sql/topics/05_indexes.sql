-- Topic 05: Indexes — before/after comparison
-- Database: retail_oltp.db

-- BEFORE index: filter orders by status (full table scan likely)
EXPLAIN QUERY PLAN
SELECT order_id, customer_id, order_date
FROM orders
WHERE status = 'delivered'
LIMIT 10;

-- Create index on frequently filtered column
DROP INDEX IF EXISTS idx_orders_status;
CREATE INDEX idx_orders_status ON orders(status);

-- AFTER index: same query should use the index
EXPLAIN QUERY PLAN
SELECT order_id, customer_id, order_date
FROM orders
WHERE status = 'delivered'
LIMIT 10;

-- Verify query still returns data
SELECT COUNT(*) AS delivered_orders FROM orders WHERE status = 'delivered';
