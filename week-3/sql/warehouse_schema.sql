-- Sales data warehouse (star schema with one snowflaked dimension)
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_employee;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product_category;

CREATE TABLE dim_date (
    date_key      INTEGER PRIMARY KEY,  -- YYYYMMDD
    full_date     DATE NOT NULL UNIQUE,
    year          INTEGER NOT NULL,
    quarter       INTEGER NOT NULL,
    month         INTEGER NOT NULL,
    month_name    TEXT NOT NULL,
    day           INTEGER NOT NULL,
    day_of_week   INTEGER NOT NULL,     -- 0=Sunday
    day_name      TEXT NOT NULL,
    is_weekend    INTEGER NOT NULL
);

-- Conformed dimension: shared date dimension usable across subject areas
CREATE TABLE dim_customer (
    customer_key  INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL,
    full_name     TEXT NOT NULL,
    email         TEXT,
    city          TEXT,
    state         TEXT,
    effective_from DATE NOT NULL,
    effective_to   DATE,
    is_current    INTEGER NOT NULL DEFAULT 1
);

-- Snowflake: category normalized out of product
CREATE TABLE dim_product_category (
    category_key    INTEGER PRIMARY KEY,
    category        TEXT NOT NULL,
    subcategory     TEXT NOT NULL,
    UNIQUE(category, subcategory)
);

CREATE TABLE dim_product (
    product_key     INTEGER PRIMARY KEY,
    product_id      INTEGER NOT NULL,
    product_name    TEXT NOT NULL,
    category_key    INTEGER NOT NULL REFERENCES dim_product_category(category_key),
    unit_price      REAL NOT NULL
);

CREATE TABLE dim_store (
    store_key     INTEGER PRIMARY KEY,
    store_id      INTEGER NOT NULL,
    store_name    TEXT NOT NULL,
    city          TEXT NOT NULL,
    state         TEXT NOT NULL
);

CREATE TABLE dim_employee (
    employee_key  INTEGER PRIMARY KEY,
    employee_id   INTEGER NOT NULL,
    full_name     TEXT NOT NULL,
    title         TEXT NOT NULL,
    store_name    TEXT NOT NULL
);

CREATE TABLE fact_sales (
    sales_key      INTEGER PRIMARY KEY,
    date_key       INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key   INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key    INTEGER NOT NULL REFERENCES dim_product(product_key),
    store_key      INTEGER NOT NULL REFERENCES dim_store(store_key),
    employee_key   INTEGER REFERENCES dim_employee(employee_key),
    order_id       INTEGER NOT NULL,
    order_item_id  INTEGER NOT NULL,
    quantity       INTEGER NOT NULL,
    unit_price     REAL NOT NULL,
    discount       REAL NOT NULL,
    revenue        REAL NOT NULL,
    cost           REAL NOT NULL,
    profit         REAL NOT NULL
);

CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
