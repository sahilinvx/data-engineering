#!/usr/bin/env python3
"""Create OLTP schema and seed with realistic fake retail data."""

from __future__ import annotations

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "retail_oltp.db"
SCHEMA_PATH = ROOT / "sql" / "oltp_schema.sql"

fake = Faker()
Faker.seed(42)
random.seed(42)

CATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Accessories", "Audio"],
    "Clothing": ["Shirts", "Pants", "Shoes", "Outerwear"],
    "Home": ["Kitchen", "Furniture", "Decor", "Bedding"],
    "Sports": ["Fitness", "Outdoor", "Team Sports", "Cycling"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance"],
}

NUM_STORES = 50
NUM_EMPLOYEES = 200
NUM_CUSTOMERS = 2000
NUM_PRODUCTS = 500
NUM_ORDERS = 3000


def run_sql_file(conn: sqlite3.Connection, path: Path) -> None:
    conn.executescript(path.read_text())


def seed_stores(conn: sqlite3.Connection) -> list[int]:
    store_ids = []
    for i in range(1, NUM_STORES + 1):
        store_ids.append(i)
        conn.execute(
            "INSERT INTO stores VALUES (?, ?, ?, ?, ?)",
            (
                i,
                f"{fake.city()} Store",
                fake.city(),
                fake.state_abbr(),
                fake.date_between(start_date="-10y", end_date="-1y").isoformat(),
            ),
        )
    return store_ids


def seed_employees(conn: sqlite3.Connection, store_ids: list[int]) -> list[int]:
    employee_ids = []
    # CEO / regional managers first (no manager)
    titles = ["Store Manager", "Assistant Manager", "Sales Associate", "Cashier", "Stock Clerk"]
    for i in range(1, NUM_EMPLOYEES + 1):
        employee_ids.append(i)
        manager_id = random.choice(employee_ids[:-1]) if i > 5 and random.random() < 0.85 else None
        conn.execute(
            "INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                i,
                random.choice(store_ids),
                manager_id,
                fake.first_name(),
                fake.last_name(),
                fake.email() if random.random() > 0.05 else None,
                fake.date_between(start_date="-8y", end_date="today").isoformat(),
                random.choice(titles),
            ),
        )
    return employee_ids


def seed_customers(conn: sqlite3.Connection) -> list[int]:
    customer_ids = []
    seen_emails: dict[str, int] = {}
    for i in range(1, NUM_CUSTOMERS + 1):
        customer_ids.append(i)
        # ~8% null emails, ~3% duplicate-ish emails (same local part, different suffix)
        if random.random() < 0.08:
            email = None
        elif random.random() < 0.03 and seen_emails:
            base = random.choice(list(seen_emails.keys()))
            email = base.replace("@", "+dup@")
        else:
            email = fake.email()
            seen_emails[email] = i
        conn.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                i,
                fake.first_name(),
                fake.last_name(),
                email,
                fake.phone_number() if random.random() > 0.1 else None,
                fake.city() if random.random() > 0.05 else None,
                fake.state_abbr() if random.random() > 0.05 else None,
                fake.date_time_between(start_date="-5y", end_date="now").isoformat(sep=" "),
            ),
        )
    return customer_ids


def seed_products(conn: sqlite3.Connection) -> list[int]:
    product_ids = []
    for i in range(1, NUM_PRODUCTS + 1):
        product_ids.append(i)
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        unit_price = round(random.uniform(5, 500), 2)
        cost = round(unit_price * random.uniform(0.35, 0.75), 2)
        conn.execute(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
            (i, category, subcategory, fake.catch_phrase(), unit_price, cost),
        )
    return product_ids


def seed_orders(
    conn: sqlite3.Connection,
    customer_ids: list[int],
    store_ids: list[int],
    employee_ids: list[int],
    product_ids: list[int],
) -> None:
    order_id = 0
    item_id = 0
    statuses = ["pending", "shipped", "delivered", "cancelled", "returned"]
    status_weights = [0.05, 0.15, 0.70, 0.07, 0.03]

    for _ in range(NUM_ORDERS):
        order_id += 1
        order_date = fake.date_time_between(start_date="-2y", end_date="now")
        status = random.choices(statuses, weights=status_weights)[0]
        employee_id = random.choice(employee_ids) if random.random() > 0.03 else None
        conn.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
            (
                order_id,
                random.choice(customer_ids),
                random.choice(store_ids),
                employee_id,
                order_date.isoformat(sep=" "),
                status,
            ),
        )
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            item_id += 1
            product_id = random.choice(product_ids)
            row = conn.execute(
                "SELECT unit_price FROM products WHERE product_id = ?", (product_id,)
            ).fetchone()
            unit_price = row[0]
            discount = round(random.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2]), 2)
            conn.execute(
                "INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item_id,
                    order_id,
                    product_id,
                    random.randint(1, 4),
                    unit_price,
                    discount,
                ),
            )


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        run_sql_file(conn, SCHEMA_PATH)
        store_ids = seed_stores(conn)
        employee_ids = seed_employees(conn, store_ids)
        customer_ids = seed_customers(conn)
        product_ids = seed_products(conn)
        seed_orders(conn, customer_ids, store_ids, employee_ids, product_ids)
        conn.commit()

        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ["stores", "employees", "customers", "products", "orders", "order_items"]
        }
        print(f"Created OLTP database at {DB_PATH}")
        for table, count in counts.items():
            print(f"  {table}: {count:,} rows")
        print(f"  TOTAL: {sum(counts.values()):,} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
