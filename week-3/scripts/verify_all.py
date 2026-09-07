#!/usr/bin/env python3
"""Verify all SQL topic files and advanced queries run without errors."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLTP_DB = ROOT / "db" / "retail_oltp.db"
WAREHOUSE_DB = ROOT / "db" / "retail_warehouse.db"

OLTP_TOPICS = {"01_advanced_joins", "04_recursive_queries", "05_indexes", "08_normalization_denormalization"}
WAREHOUSE_TOPICS = {
    "02_window_functions", "03_ctes", "06_execution_plans", "07_partitioning",
    "09_star_schema", "10_snowflake_schema", "11_fact_table", "12_dimension_tables",
    "13_slowly_changing_dimensions",
}


def run_sql_file(conn: sqlite3.Connection, path: Path) -> tuple[bool, str]:
    sql = path.read_text()
    try:
        conn.executescript(sql)
        conn.commit()
        return True, "OK"
    except Exception as e:
        return False, str(e)


def main() -> int:
    errors = []
    topics_dir = ROOT / "sql" / "topics"

    for sql_file in sorted(topics_dir.glob("*.sql")):
        name = sql_file.stem
        db = OLTP_DB if name in OLTP_TOPICS else WAREHOUSE_DB
        conn = sqlite3.connect(db)
        ok, msg = run_sql_file(conn, sql_file)
        conn.close()
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {sql_file.name} ({db.name})")
        if not ok:
            errors.append(f"{sql_file.name}: {msg}")

    # Advanced queries — run entire file as script
    adv_path = ROOT / "sql" / "20_advanced_queries.sql"
    conn = sqlite3.connect(WAREHOUSE_DB)
    ok, msg = run_sql_file(conn, adv_path)
    conn.close()
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] 20_advanced_queries.sql (20 queries)")
    if not ok:
        errors.append(f"20_advanced_queries.sql: {msg}")

    print(f"\n{'All checks passed!' if not errors else f'{len(errors)} error(s) found.'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
