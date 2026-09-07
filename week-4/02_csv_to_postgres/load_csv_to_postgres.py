from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
from psycopg2 import sql

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.db import get_connection
from common.logging_setup import get_logger

logger = get_logger(__name__)

DEFAULT_CSV = Path(__file__).resolve().parents[1] / "data" / "spotify_artist_streaming_2020_2025.csv"
DEFAULT_TABLE = "streaming_tracks"

PANDAS_TO_PG = {
    "int64": "BIGINT",
    "float64": "DOUBLE PRECISION",
    "bool": "BOOLEAN",
    "object": "TEXT",
    "datetime64[ns]": "TIMESTAMP",
}


def infer_columns(df: pd.DataFrame) -> list[tuple[str, str]]:
    """('CSV ingestion' + schema inference: map pandas dtypes -> Postgres
    column types instead of hardcoding a schema by hand.)"""
    return [(col, PANDAS_TO_PG.get(str(dtype), "TEXT")) for col, dtype in df.dtypes.items()]


def ensure_table(conn, table: str, columns: list[tuple[str, str]], primary_key: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
            (table,),
        )
        exists = cur.fetchone()[0]

        if not exists:
            col_defs = [
                sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(pg_type))
                for name, pg_type in columns
            ]
            create_stmt = sql.SQL("CREATE TABLE {} ({}, PRIMARY KEY ({}))").format(
                sql.Identifier(table),
                sql.SQL(", ").join(col_defs),
                sql.Identifier(primary_key),
            )
            cur.execute(create_stmt)
            logger.info("Created table '%s' with %d columns.", table, len(columns))
            conn.commit()
            return

        # Table already exists -- this is the schema evolution path: find
        # any CSV columns the table doesn't have yet and ALTER them in,
        # rather than failing or silently dropping the new data.
        cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            (table,),
        )
        existing_cols = {row[0] for row in cur.fetchall()}
        new_cols = [(name, pg_type) for name, pg_type in columns if name not in existing_cols]

        for name, pg_type in new_cols:
            alter_stmt = sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
                sql.Identifier(table), sql.Identifier(name), sql.SQL(pg_type)
            )
            cur.execute(alter_stmt)
            logger.info("Schema evolution: added new column '%s %s' to '%s'.", name, pg_type, table)

        if new_cols:
            conn.commit()
        else:
            logger.info("Table '%s' already has all %d columns -- no schema change.", table, len(columns))


def full_load(conn, table: str, df: pd.DataFrame) -> None:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    with conn.cursor() as cur:
        cur.execute(sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(table)))
        columns_sql = sql.SQL(", ").join(sql.Identifier(c) for c in df.columns)
        copy_stmt = sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT csv)").format(
            sql.Identifier(table), columns_sql
        )
        cur.copy_expert(copy_stmt.as_string(conn), buffer)
    conn.commit()
    logger.info("Full load complete: %d rows written to '%s'.", len(df), table)


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    table = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TABLE

    logger.info("Reading %s...", csv_path)
    df = pd.read_csv(csv_path)
    logger.info("Read %d rows, %d columns.", len(df), len(df.columns))

    columns = infer_columns(df)
    print("Inferred columns:", columns)

    conn = get_connection()
    try:
        ensure_table(conn, table, columns, primary_key="track_id")
        full_load(conn, table, df)

        with conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
            logger.info("Row count in '%s' after load: %d", table, cur.fetchone()[0])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
