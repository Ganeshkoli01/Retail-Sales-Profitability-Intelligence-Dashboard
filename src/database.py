"""Database manager module for SQLite operations."""

import logging
import sqlite3
from pathlib import Path
from typing import Optional, Union
import pandas as pd

from src.config import DATABASE_FILE, SCHEMA_SQL_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a SQLite database connection with row factory enabled."""
    target_path = db_path or DATABASE_FILE
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(
    db_path: Optional[Path] = None, schema_file: Optional[Path] = None
) -> None:
    """Execute DDL script to create tables, indexes, and views."""
    target_db = db_path or DATABASE_FILE
    target_schema = schema_file or SCHEMA_SQL_FILE

    logger.info(f"Initializing database at: {target_db} using schema: {target_schema}")
    with open(target_schema, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_connection(target_db) as conn:
        conn.executescript(schema_sql)
        conn.commit()

    logger.info("Database initialized successfully with tables and views.")


def load_data_to_database(
    df: pd.DataFrame,
    table_name: str = "retail_orders",
    db_path: Optional[Path] = None,
) -> int:
    """Load cleaned DataFrame into SQLite table.

    Formats dates to ISO strings before writing to ensure portable SQL querying.
    """
    target_db = db_path or DATABASE_FILE
    df_to_load = df.copy()

    # Format datetime columns to ISO string YYYY-MM-DD
    for date_col in ["order_date", "ship_date"]:
        if date_col in df_to_load.columns:
            df_to_load[date_col] = pd.to_datetime(df_to_load[date_col]).dt.strftime("%Y-%m-%d")

    logger.info(f"Loading {len(df_to_load):,} rows into table '{table_name}'...")
    with get_db_connection(target_db) as conn:
        # Ensure table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            initialize_database(db_path=target_db)

        # Clear existing data for idempotency and append
        conn.execute(f"DELETE FROM {table_name}")
        df_to_load.to_sql(table_name, conn, if_exists="append", index=False)
        conn.commit()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        inserted_count = cursor.fetchone()[0]

    logger.info(f"Table '{table_name}' verified with {inserted_count:,} records.")
    return inserted_count


def execute_query(
    query_sql: str,
    db_path: Optional[Path] = None,
    params: Optional[Union[tuple, dict]] = None,
) -> pd.DataFrame:
    """Execute SQL query and return results as pandas DataFrame."""
    target_db = db_path or DATABASE_FILE
    with get_db_connection(target_db) as conn:
        if params:
            df = pd.read_sql_query(query_sql, conn, params=params)
        else:
            df = pd.read_sql_query(query_sql, conn)
    return df
