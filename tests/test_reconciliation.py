"""Integration tests validating reconciliation between Python vectorized metrics and SQLite database."""

import pytest
import pandas as pd

from src.config import CLEANED_DATA_FILE
from src.analysis import reconcile_python_and_sql


def test_python_and_sql_reconciliation():
    """Verify that Python and SQL enterprise KPIs reconcile with 100% precision."""
    assert CLEANED_DATA_FILE.exists()
    df = pd.read_csv(CLEANED_DATA_FILE)

    recon = reconcile_python_and_sql(df)

    assert recon["is_reconciled"] is True, f"Reconciliation discrepancies: {recon}"
    assert recon["sales"]["status"] == "PASS"
    assert recon["profit"]["status"] == "PASS"
    assert recon["quantity"]["status"] == "PASS"
    assert recon["orders"]["status"] == "PASS"
    assert recon["customers"]["status"] == "PASS"

    # Verify tolerance bounds
    assert recon["sales"]["difference"] <= 0.05
    assert recon["profit"]["difference"] <= 0.05
    assert recon["quantity"]["difference"] == 0
    assert recon["orders"]["difference"] == 0
    assert recon["customers"]["difference"] == 0
