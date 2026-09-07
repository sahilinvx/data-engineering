# Star Schema Design: OLTP → Warehouse Transformation

## Source (OLTP — 3NF)

| Table | Role | Grain |
|-------|------|-------|
| `stores` | Physical retail locations | One row per store |
| `employees` | Staff, with manager hierarchy | One row per employee |
| `customers` | Buyers | One row per customer |
| `products` | Catalog items with category | One row per product |
| `orders` | Purchase events | One row per order |
| `order_items` | Line items within orders | One row per product line |

## Target (Star Schema Warehouse)

```
                    dim_date (conformed)
                         |
dim_customer ----> fact_sales <---- dim_product ----> dim_product_category
                         |              (snowflake)
                    dim_store
                         |
                   dim_employee
```

## Transformation Decisions

### `fact_sales` (central fact table)
- **Grain:** One row per order line item (from `order_items`)
- **Source joins:** `order_items` → `orders` → `products`
- **Filter:** Only `shipped` and `delivered` orders (excludes cancelled/returned)
- **Measures calculated at ETL time:**
  - `revenue` = quantity × unit_price × (1 − discount)
  - `cost` = quantity × product.cost
  - `profit` = revenue − cost
- **Degenerate dimensions:** `order_id`, `order_item_id` kept in fact (no separate dim table needed)

### `dim_date` (conformed dimension)
- **Generated** during ETL (not sourced from OLTP — no date table in source)
- Date range: 2022-01-01 to 2026-12-31
- `date_key` = YYYYMMDD integer for fast joins
- **Why conformed:** Same calendar usable for future fact tables (returns, inventory)

### `dim_customer` (SCD Type 2 ready)
- **Source:** `customers` table
- **Denormalized:** `first_name + last_name` → `full_name`
- **SCD Type 2 columns:** `effective_from`, `effective_to`, `is_current`
- Initial load: all rows `is_current = 1`

### `dim_product` + `dim_product_category` (snowflake)
- **Star would:** store `category` and `subcategory` directly in `dim_product`
- **Snowflake choice:** normalize category into `dim_product_category` to avoid repeating category strings across hundreds of products
- **Trade-off:** one extra join at query time, but consistent category naming

### `dim_store`
- **Direct mapping** from `stores` — already flat, no further normalization needed

### `dim_employee`
- **Denormalized:** joins `employees` + `stores` at ETL to include `store_name`
- Avoids joining `dim_store` when analyzing employee performance

## What Was Denormalized and Why

| OLTP (normalized) | Warehouse (denormalized) | Reason |
|-------------------|--------------------------|--------|
| `customers.first_name + last_name` | `dim_customer.full_name` | Simpler BI queries |
| `employees` + `stores` | `dim_employee.store_name` | Avoid extra join for reports |
| `products.category/subcategory` | `dim_product_category` table | Snowflake for consistency |
| Multiple tables for one sale | Single `fact_sales` row | Fast aggregation |

## What Stayed Normalized

- Categories separated from products (snowflake, not full denormalization)
- Customers, products, stores, employees as separate dimensions (not stuffed into fact)
- Date as its own dimension (not just a timestamp column in fact)

## ETL Pipeline

```
retail_oltp.db  →  scripts/etl_to_warehouse.py  →  retail_warehouse.db
```

Run order:
1. `python scripts/setup_oltp.py` — creates source
2. `python scripts/etl_to_warehouse.py` — builds warehouse
