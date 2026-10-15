"""Unit tests for data ingestion, cleaning, and quality quarantine rules."""

import pytest
import pandas as pd
import numpy as np

from src.data_cleaning import clean_retail_data
from src.feature_engineering import engineer_features


def test_clean_retail_data_valid(sample_raw_dataframe):
    """Test standard cleaning on valid fixture."""
    clean_df, rejected_df, metrics = clean_retail_data(sample_raw_dataframe)
    assert len(clean_df) == 4
    assert len(rejected_df) == 0
    assert metrics["clean_record_rate_pct"] == 100.0
    assert "postal_code" in clean_df.columns
    assert clean_df["postal_code"].iloc[0] == "10001"


def test_quarantine_negative_sales(sample_raw_dataframe):
    """Ensure sales <= 0 are quarantined into rejected_df."""
    bad_df = sample_raw_dataframe.copy()
    bad_df.loc[0, "Sales"] = -50.0  # Invalid negative sale

    clean_df, rejected_df, metrics = clean_retail_data(bad_df)
    assert len(clean_df) == 3
    assert len(rejected_df) == 1
    assert "Sales must be positive" in rejected_df.iloc[0]["rejection_reason"]


def test_quarantine_invalid_discount(sample_raw_dataframe):
    """Ensure discounts outside 0.0-1.0 are quarantined."""
    bad_df = sample_raw_dataframe.copy()
    bad_df.loc[1, "Discount"] = 1.50  # 150% discount invalid

    clean_df, rejected_df, metrics = clean_retail_data(bad_df)
    assert len(clean_df) == 3
    assert len(rejected_df) == 1
    assert "Discount must be between" in rejected_df.iloc[0]["rejection_reason"]


def test_quarantine_ship_date_preceding_order_date(sample_raw_dataframe):
    """Ensure chronological paradox (ship before order) is caught."""
    bad_df = sample_raw_dataframe.copy()
    bad_df.loc[2, "Ship Date"] = "2015-01-01"  # Order date is 2016-02-15

    clean_df, rejected_df, metrics = clean_retail_data(bad_df)
    assert len(clean_df) == 3
    assert len(rejected_df) == 1
    assert "Ship date precedes order date" in rejected_df.iloc[0]["rejection_reason"]


def test_feature_engineering_derivatives(sample_raw_dataframe):
    """Verify feature engineering derives expected dimensions."""
    clean_df, _, _ = clean_retail_data(sample_raw_dataframe)
    enriched = engineer_features(clean_df)

    expected_cols = [
        "order_year", "order_month", "order_quarter", "order_year_month",
        "shipping_duration_days", "profit_margin", "unit_price", "unit_cost",
        "is_profitable", "discount_tier"
    ]
    for col in expected_cols:
        assert col in enriched.columns

    # Test unit price = 100 / 2 = 50.0 for row 0
    assert enriched.iloc[0]["unit_price"] == 50.0
    # Test margin = 20 / 100 = 0.20 for row 0
    assert enriched.iloc[0]["profit_margin"] == 0.20
    # Test is_profitable flag
    assert enriched.iloc[0]["is_profitable"] == 1
    assert enriched.iloc[1]["is_profitable"] == 0  # profit is -40
