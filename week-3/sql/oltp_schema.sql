-- OLTP schema for fictional retail company "Northwind Retail" (3NF)
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS stores;

CREATE TABLE stores (
    store_id     INTEGER PRIMARY KEY,
    store_name   TEXT NOT NULL,
    city         TEXT NOT NULL,
    state        TEXT NOT NULL,
    opened_date  DATE NOT NULL
);

CREATE TABLE employees (
    employee_id  INTEGER PRIMARY KEY,
    store_id     INTEGER NOT NULL REFERENCES stores(store_id),
    manager_id   INTEGER REFERENCES employees(employee_id),
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    email        TEXT,
    hire_date    DATE NOT NULL,
    title        TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    email        TEXT,
    phone        TEXT,
    city         TEXT,
    state        TEXT,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    category      TEXT NOT NULL,
    subcategory   TEXT NOT NULL,
    product_name  TEXT NOT NULL,
    unit_price    REAL NOT NULL CHECK (unit_price > 0),
    cost          REAL NOT NULL CHECK (cost >= 0)
);

CREATE TABLE orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
    store_id     INTEGER NOT NULL REFERENCES stores(store_id),
    employee_id  INTEGER REFERENCES employees(employee_id),
    order_date   TIMESTAMP NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled', 'returned'))
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    REAL NOT NULL,
    discount      REAL NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 1)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
