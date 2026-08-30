-- Topic 13: Slowly Changing Dimensions (SCD Type 1 and Type 2)
-- Database: retail_warehouse.db

-- === SCD TYPE 1: Overwrite old value (no history kept) ===
-- BEFORE: customer 42 has old email
SELECT customer_key, customer_id, full_name, email, city, is_current
FROM dim_customer WHERE customer_id = 42;

-- Type 1 update: fix a typo / update email in place
UPDATE dim_customer
SET email = 'corrected.email@example.com', city = 'Seattle'
WHERE customer_id = 42 AND is_current = 1;

-- AFTER Type 1: same row, new values (history lost)
SELECT customer_key, customer_id, full_name, email, city, is_current
FROM dim_customer WHERE customer_id = 42;

-- === SCD TYPE 2: Keep history with effective dates ===
-- BEFORE: customer 100 current record
SELECT customer_key, customer_id, full_name, email, city, state,
       effective_from, effective_to, is_current
FROM dim_customer WHERE customer_id = 100;

-- Type 2: customer moved from CA to NY — expire old row, insert new
UPDATE dim_customer
SET effective_to = '2025-06-01', is_current = 0
WHERE customer_id = 100 AND is_current = 1;

INSERT INTO dim_customer (customer_key, customer_id, full_name, email, city, state,
                          effective_from, effective_to, is_current)
SELECT
    (SELECT MAX(customer_key) + 1 FROM dim_customer),
    customer_id,
    full_name,
    email,
    'New York',
    'NY',
    '2025-06-02',
    NULL,
    1
FROM dim_customer
WHERE customer_id = 100 AND is_current = 0
ORDER BY effective_to DESC
LIMIT 1;

-- AFTER Type 2: two rows — historical CA record + current NY record
SELECT customer_key, customer_id, full_name, city, state,
       effective_from, effective_to, is_current
FROM dim_customer WHERE customer_id = 100
ORDER BY effective_from;
