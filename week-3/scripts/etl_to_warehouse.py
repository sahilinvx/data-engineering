#!/usr/bin/env python3
"""ETL: populate sales warehouse from OLTP source database."""

from __future__ import annotations

import sqlite3
from calendar import month_name, day_name
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLTP_DB = ROOT / "db" / "retail_oltp.db"
WAREHOUSE_DB = ROOT / "db" / "retail_warehouse.db"
SCHEMA_PATH = ROOT / "sql" / "warehouse_schema.sql"


def run_sql_file(conn: sqlite3.Connection, path: Path) -> None:
    conn.executescript(path.read_text())


def populate_dim_date(conn: sqlite3.Connection, start: date, end: date) -> None:
    current = start
    rows = []
    while current <= end:
        date_key = int(current.strftime("%Y%m%d"))
        rows.append(
            (
                date_key,
                current.isoformat(),
                current.year,
                (current.month - 1) // 3 + 1,
                current.month,
                month_name[current.month],
                current.day,
                (current.weekday() + 1) % 7,
                day_name[(current.weekday() + 1) % 7],
                1 if current.weekday() >= 5 else 0,
            )
        )
        current = date.fromordinal(current.toordinal() + 1)
    conn.executemany(
        """INSERT INTO dim_date
           (date_key, full_date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )


def populate_dimensions(conn: sqlite3.Connection, oltp: sqlite3.Connection) -> None:
    # dim_customer — SCD Type 2 ready: initial load, all current
    customers = oltp.execute(
        "SELECT customer_id, first_name, last_name, email, city, state, created_at FROM customers"
    ).fetchall()
    conn.executemany(
        """INSERT INTO dim_customer
           (customer_key, customer_id, full_name, email, city, state, effective_from, effective_to, is_current)
           VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 1)""",
        [
            (
                cid,
                cid,
                f"{first} {last}",
                email,
                city,
                state,
                created_at[:10] if created_at else "2020-01-01",
            )
            for cid, first, last, email, city, state, created_at in customers
        ],
    )

    # dim_product_category (snowflake)
    categories = oltp.execute(
        "SELECT DISTINCT category, subcategory FROM products ORDER BY 1, 2"
    ).fetchall()
    category_map: dict[tuple[str, str], int] = {}
    for key, (cat, sub) in enumerate(categories, start=1):
        category_map[(cat, sub)] = key
        conn.execute(
            "INSERT INTO dim_product_category VALUES (?, ?, ?)", (key, cat, sub)
        )

    products = oltp.execute(
        "SELECT product_id, product_name, category, subcategory, unit_price FROM products"
    ).fetchall()
    conn.executemany(
        """INSERT INTO dim_product (product_key, product_id, product_name, category_key, unit_price)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (pid, pid, name, category_map[(cat, sub)], price)
            for pid, name, cat, sub, price in products
        ],
    )

    stores = oltp.execute(
        "SELECT store_id, store_name, city, state FROM stores"
    ).fetchall()
    conn.executemany(
        "INSERT INTO dim_store VALUES (?, ?, ?, ?, ?)",
        [(sid, sid, name, city, state) for sid, name, city, state in stores],
    )

    employees = oltp.execute(
        """SELECT e.employee_id, e.first_name, e.last_name, e.title, s.store_name
           FROM employees e JOIN stores s ON e.store_id = s.store_id"""
    ).fetchall()
    conn.executemany(
        "INSERT INTO dim_employee VALUES (?, ?, ?, ?, ?)",
        [
            (eid, eid, f"{first} {last}", title, store)
            for eid, first, last, title, store in employees
        ],
    )


def populate_fact_sales(conn: sqlite3.Connection, oltp: sqlite3.Connection) -> None:
    rows = oltp.execute(
        """SELECT
               o.order_id,
               oi.order_item_id,
               CAST(strftime('%Y%m%d', o.order_date) AS INTEGER) AS date_key,
               o.customer_id,
               oi.product_id,
               o.store_id,
               o.employee_id,
               oi.quantity,
               oi.unit_price,
               oi.discount,
               oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue,
               oi.quantity * p.cost AS cost
           FROM order_items oi
           JOIN orders o ON oi.order_id = o.order_id
           JOIN products p ON oi.product_id = p.product_id
           WHERE o.status IN ('shipped', 'delivered')"""
    ).fetchall()

    conn.executemany(
        """INSERT INTO fact_sales
           (sales_key, date_key, customer_key, product_key, store_key, employee_key,
            order_id, order_item_id, quantity, unit_price, discount, revenue, cost, profit)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                i + 1,
                date_key,
                customer_id,
                product_id,
                store_id,
                employee_id,
                order_id,
                order_item_id,
                qty,
                price,
                disc,
                revenue,
                cost,
                revenue - cost,
            )
            for i, (
                order_id,
                order_item_id,
                date_key,
                customer_id,
                product_id,
                store_id,
                employee_id,
                qty,
                price,
                disc,
                revenue,
                cost,
            ) in enumerate(rows)
        ],
    )


def main() -> None:
    if not OLTP_DB.exists():
        raise SystemExit(f"OLTP database not found. Run scripts/setup_oltp.py first.")

    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)
    if WAREHOUSE_DB.exists():
        WAREHOUSE_DB.unlink()

    oltp = sqlite3.connect(OLTP_DB)
    wh = sqlite3.connect(WAREHOUSE_DB)
    try:
        run_sql_file(wh, SCHEMA_PATH)
        populate_dim_date(wh, date(2022, 1, 1), date(2026, 12, 31))
        populate_dimensions(wh, oltp)
        populate_fact_sales(wh, oltp)
        wh.commit()

        counts = {
            t: wh.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in [
                "dim_date",
                "dim_customer",
                "dim_product_category",
                "dim_product",
                "dim_store",
                "dim_employee",
                "fact_sales",
            ]
        }
        print(f"Created warehouse at {WAREHOUSE_DB}")
        for table, count in counts.items():
            print(f"  {table}: {count:,} rows")
    finally:
        oltp.close()
        wh.close()


if __name__ == "__main__":
    main()
