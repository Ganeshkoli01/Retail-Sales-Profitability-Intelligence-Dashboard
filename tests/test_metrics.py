"""Unit tests for metric and KPI calculation formulas."""

import pytest
import pandas as pd
import numpy as np

from src.data_cleaning import clean_retail_data
from src.feature_engineering import engineer_features
from src.metrics import (
    calculate_total_revenue,
    calculate_total_profit,
    calculate_overall_profit_margin,
    calculate_total_orders,
    calculate_total_units_sold,
    calculate_average_order_value,
    calculate_loss_order_rate,
    calculate_kpi_summary,
    calculate_sales_traps,
    calculate_rfm_metrics,
)


def test_kpi_metrics_exact_values(sample_raw_dataframe):
    """Verify calculated metrics match manually computed ground truth."""
    clean_df, _, _ = clean_retail_data(sample_raw_dataframe)
    enriched = engineer_features(clean_df)

    # Ground truth values:
    # Sales: 100 + 200 + 50 + 400 = 750.0
    # Profit: 20 - 40 + 15 + 80 = 75.0
    # Units: 2 + 4 + 1 + 5 = 12
    # Orders: 3
    # Margin: 75.0 / 750.0 = 0.10 (10.0%)
    # AOV: 750.0 / 3 = 250.0
    # Loss lines: 1 out of 4 = 25.0%

    assert calculate_total_revenue(enriched) == 750.0
    assert calculate_total_profit(enriched) == 75.0
    assert calculate_total_units_sold(enriched) == 12
    assert calculate_total_orders(enriched) == 3
    assert calculate_overall_profit_margin(enriched) == 0.10
    assert calculate_average_order_value(enriched) == 250.0
    assert calculate_loss_order_rate(enriched) == 25.0


def test_empty_dataframe_edge_cases(empty_dataframe):
    """Ensure all metric functions handle empty DataFrames safely without crashing or zero-division errors."""
    assert calculate_total_revenue(empty_dataframe) == 0.0
    assert calculate_total_profit(empty_dataframe) == 0.0
    assert calculate_overall_profit_margin(empty_dataframe) == 0.0
    assert calculate_total_orders(empty_dataframe) == 0
    assert calculate_total_units_sold(empty_dataframe) == 0
    assert calculate_average_order_value(empty_dataframe) == 0.0
    assert calculate_loss_order_rate(empty_dataframe) == 0.0

    kpi_dict = calculate_kpi_summary(empty_dataframe)
    assert kpi_dict["total_revenue"] == 0.0
    assert kpi_dict["total_profit"] == 0.0


def test_zero_sales_margin_safe_division():
    """Verify margin calculation when sales are zero."""
    zero_df = pd.DataFrame({"sales": [0.0, 0.0], "profit": [0.0, 0.0], "order_id": ["O1", "O2"]})
    assert calculate_overall_profit_margin(zero_df) == 0.0


def test_rfm_metrics_structure(sample_raw_dataframe):
    """Verify RFM metric computation."""
    clean_df, _, _ = clean_retail_data(sample_raw_dataframe)
    enriched = engineer_features(clean_df)
    rfm = calculate_rfm_metrics(enriched)

    assert len(rfm) == 3  # 3 distinct customers: CUST-101, CUST-102, CUST-103
    assert "recency_days" in rfm.columns
    assert "order_frequency" in rfm.columns
    assert "total_spend" in rfm.columns
    # CUST-101 has 2 lines under order ORD-001 -> frequency is 1 order
    cust_101 = rfm[rfm["customer_id"] == "CUST-101"].iloc[0]
    assert cust_101["order_frequency"] == 1
    assert cust_101["total_spend"] == 300.0  # 100 + 200
