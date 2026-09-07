"""
Sets up a fake OLTP-style 'orders' source table and a separate warehouse
'orders_dw' target table, both in the same Postgres instance for
simplicity (in real life these are two different databases/systems).

Run once at the start, then use simulate_source_changes.py + incremental_load.py
to see incremental loading in action.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.db import get_connection
from common.logging_setup import get_logger

logger = get_logger(__name__)

SEED_ROWS = 20


def main() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS orders")
            cur.execute(
                """
                CREATE TABLE orders (
                    order_id     SERIAL PRIMARY KEY,
                    customer     TEXT NOT NULL,
                    amount       NUMERIC(10, 2) NOT NULL,
                    status       TEXT NOT NULL,
                    updated_at   TIMESTAMP NOT NULL DEFAULT now()
                )
                """
            )
            # The updated_at column is the whole trick: every insert AND
            # every update touches it, so "give me everything with
            # updated_at > last_watermark" captures both new and changed
            # rows without needing to know which happened.
            cur.execute(
                """
                INSERT INTO orders (customer, amount, status)
                SELECT 'customer_' || i, (random() * 500)::numeric(10,2), 'pending'
                FROM generate_series(1, %s) AS i
                """,
                (SEED_ROWS,),
            )

            cur.execute("DROP TABLE IF EXISTS orders_dw")
            cur.execute(
                """
                CREATE TABLE orders_dw (
                    order_id     INTEGER PRIMARY KEY,
                    customer     TEXT NOT NULL,
                    amount       NUMERIC(10, 2) NOT NULL,
                    status       TEXT NOT NULL,
                    updated_at   TIMESTAMP NOT NULL
                )
                """
            )
        conn.commit()
        logger.info("Seeded 'orders' (source) with %d rows and created empty 'orders_dw' (warehouse target).", SEED_ROWS)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
