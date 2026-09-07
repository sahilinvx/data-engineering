from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.db import get_connection
from common.logging_setup import get_logger

logger = get_logger(__name__)

STATE_FILE = Path(__file__).parent / "state" / "watermark.json"
EPOCH = "1970-01-01T00:00:00"


def load_watermark() -> str:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())["last_loaded_updated_at"]
    return EPOCH


def save_watermark(value: datetime) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps({"last_loaded_updated_at": value.isoformat()}, indent=2))


def main() -> None:
    watermark = load_watermark()
    logger.info("Loading rows with updated_at > %s", watermark)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT order_id, customer, amount, status, updated_at
                FROM orders
                WHERE updated_at > %s
                ORDER BY updated_at
                """,
                (watermark,),
            )
            rows = cur.fetchall()

            if not rows:
                logger.info("No new or changed rows since last run. Nothing to load.")
                return

            for order_id, customer, amount, status, updated_at in rows:
                cur.execute(
                    """
                    INSERT INTO orders_dw (order_id, customer, amount, status, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (order_id) DO UPDATE SET
                        customer = EXCLUDED.customer,
                        amount = EXCLUDED.amount,
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (order_id, customer, amount, status, updated_at),
                )

            conn.commit()
            max_updated_at = max(row[4] for row in rows)
            save_watermark(max_updated_at)

            logger.info("Upserted %d row(s) (new inserts + changed updates combined).", len(rows))
            logger.info("Watermark advanced to %s", max_updated_at.isoformat())

            cur.execute("SELECT COUNT(*) FROM orders_dw")
            logger.info("Total rows in orders_dw now: %d", cur.fetchone()[0])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
