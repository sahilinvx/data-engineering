#!/usr/bin/env python3
"""Run a .sql file against a SQLite database and print results."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def run_sql_file(db_path: Path, sql_path: Path, limit: int = 10) -> None:
    sql = sql_path.read_text()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        # Split on semicolons but keep it simple — execute as script
        statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
        for i, stmt in enumerate(statements):
            if not stmt:
                continue
            upper = stmt.upper()
            if upper.startswith("SELECT") or upper.startswith("WITH") or upper.startswith("EXPLAIN"):
                print(f"\n--- Statement {i + 1} ---")
                cur = conn.execute(stmt)
                rows = cur.fetchall()
                if not rows:
                    print("(no rows)")
                    continue
                cols = rows[0].keys()
                print(" | ".join(cols))
                print("-" * min(80, sum(len(c) for c in cols) + 3 * len(cols)))
                for row in rows[:limit]:
                    print(" | ".join(str(row[c]) for c in cols))
                if len(rows) > limit:
                    print(f"... ({len(rows) - limit} more rows)")
            else:
                conn.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SQL file against SQLite DB")
    parser.add_argument("sql_file", type=Path)
    parser.add_argument("--db", type=Path, default=Path("db/retail_warehouse.db"))
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Database not found: {args.db}", file=sys.stderr)
        sys.exit(1)
    run_sql_file(args.db, args.sql_file, args.limit)


if __name__ == "__main__":
    main()
