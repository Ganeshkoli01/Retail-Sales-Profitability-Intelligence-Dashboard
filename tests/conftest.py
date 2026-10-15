"""Pytest fixtures and known synthetic mini-datasets for unit tests."""

import pytest
import pandas as pd


@pytest.fixture
def sample_raw_dataframe():
    """Deterministic synthetic fixture with known mathematical sums:
    Sales: 100 + 200 + 50 + 400 = 750.0
    Profit: 20 + (-40) + 15 + 80 = 75.0
    Quantity: 2 + 4 + 1 + 5 = 12
    Orders: 3 unique orders ('ORD-001', 'ORD-002', 'ORD-003')
    Margin: 75.0 / 750.0 = 0.10 (10.0%)
    AOV: 750.0 / 3 = 250.0
    """
    data = {
        "Row ID": [1, 2, 3, 4],
        "Order ID": ["ORD-001", "ORD-001", "ORD-002", "ORD-003"],
        "Order Date": ["2016-01-10", "2016-01-10", "2016-02-15", "2016-03-20"],
        "Ship Date": ["2016-01-14", "2016-01-14", "2016-02-18", "2016-03-22"],
        "Ship Mode": ["Standard Class", "Standard Class", "Second Class", "First Class"],
        "Customer ID": ["CUST-101", "CUST-101", "CUST-102", "CUST-103"],
        "Customer Name": ["Alice Smith", "Alice Smith", "Bob Jones", "Charlie Brown"],
        "Segment": ["Consumer", "Consumer", "Corporate", "Home Office"],
        "Country": ["United States", "United States", "United States", "United States"],
        "City": ["New York", "New York", "Los Angeles", "Chicago"],
        "State": ["New York", "New York", "California", "Illinois"],
        "Postal Code": [10001, 10001, 90001, 60601],
        "Region": ["East", "East", "West", "Central"],
        "Product ID": ["PROD-A", "PROD-B", "PROD-C", "PROD-D"],
        "Category": ["Technology", "Furniture", "Office Supplies", "Technology"],
        "Sub-Category": ["Phones", "Tables", "Paper", "Accessories"],
        "Product Name": ["Smartphone X", "Dining Table Large", "A4 Printing Paper", "Wireless Mouse"],
        "Sales": [100.0, 200.0, 50.0, 400.0],
        "Quantity": [2, 4, 1, 5],
        "Discount": [0.0, 0.40, 0.0, 0.10],
        "Profit": [20.0, -40.0, 15.0, 80.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def empty_dataframe():
    """Empty dataframe fixture with expected columns."""
    from src.config import COLUMN_MAPPING
    cols = list(COLUMN_MAPPING.values())
    return pd.DataFrame(columns=cols)
