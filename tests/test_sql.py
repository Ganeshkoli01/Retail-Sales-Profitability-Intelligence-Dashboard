"""Integration tests for SQLite database schema, views, and analytical SQL library."""

import pytest
import sqlite3
from pathlib import Path
import pandas as pd

from src.config import DATABASE_FILE, BUSINESS_ANALYSIS_SQL_FILE
from src.database import get_db_connection, execute_query


def test_database_exists_and_table_populated():
    """Verify retail_analytics.db exists and contains populated retail_orders table."""
    assert DATABASE_FILE.exists(), f"Database file missing at: {DATABASE_FILE}"
    with get_db_connection(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM retail_orders;")
        row_count = cursor.fetchone()[0]
        assert row_count > 0, "retail_orders table has zero records"


def test_database_views_exist():
    """Verify required analytical views are present and queryable."""
    views_to_test = ["v_monthly_summary", "v_category_performance", "v_customer_rfm"]
    with get_db_connection(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        for v in views_to_test:
            cursor.execute(f"SELECT COUNT(*) FROM {v};")
            res = cursor.fetchone()[0]
            assert res > 0, f"View {v} returned 0 rows"


def test_all_21_business_analysis_queries():
    """Parse and execute all 21 queries from business_analysis.sql to verify syntax and execution."""
    assert BUSINESS_ANALYSIS_SQL_FILE.exists()
    with open(BUSINESS_ANALYSIS_SQL_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split into discrete queries by semicolon
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    select_queries = []
    for s in statements:
        # Strip comments
        lines = [line for line in s.splitlines() if not line.strip().startswith("--")]
        cleaned = "\n".join(lines).strip()
        if cleaned.upper().startswith("SELECT") or cleaned.upper().startswith("WITH"):
            select_queries.append(cleaned)

    assert len(select_queries) >= 20, f"Expected at least 20 queries, found {len(select_queries)}"

    with get_db_connection(DATABASE_FILE) as conn:
        for idx, query in enumerate(select_queries, start=1):
            try:
                res_df = pd.read_sql_query(query, conn)
                assert len(res_df) > 0, f"Query {idx} executed but returned empty DataFrame"
            except Exception as e:
                pytest.fail(f"Query {idx} failed execution: {e}\nSQL:\n{query}")
