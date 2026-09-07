from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.db import get_connection
from common.logging_setup import get_logger

logger = get_logger(__name__)


def main() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (customer, amount, status)
                SELECT 'customer_' || (100 + i), (random() * 500)::numeric(10,2), 'pending'
                FROM generate_series(1, 3) AS i
                """
            )
            inserted = cur.rowcount

            cur.execute(
                """
                UPDATE orders
                SET status = 'shipped', updated_at = now()
                WHERE order_id IN (
                    SELECT order_id FROM orders ORDER BY random() LIMIT 3
                )
                """
            )
            updated = cur.rowcount
        conn.commit()
        logger.info("Simulated %d new orders and %d status updates in the source table.", inserted, updated)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
