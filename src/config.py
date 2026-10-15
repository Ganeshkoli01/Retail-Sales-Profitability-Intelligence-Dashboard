"""Configuration module for Retail Sales & Profitability Analytics."""

import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories and file paths
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

RAW_DATA_FILE = DATA_RAW_DIR / "sample_superstore.csv"
CLEANED_DATA_FILE = DATA_PROCESSED_DIR / "retail_sales_cleaned.csv"
REJECTED_DATA_FILE = DATA_PROCESSED_DIR / "retail_sales_rejected.csv"
PROVENANCE_FILE = DATA_RAW_DIR / "provenance.json"

# Database paths
DATABASE_DIR = BASE_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "retail_analytics.db"
SQL_DIR = BASE_DIR / "sql"
SCHEMA_SQL_FILE = SQL_DIR / "schema.sql"
BUSINESS_ANALYSIS_SQL_FILE = SQL_DIR / "business_analysis.sql"

# Excel output
EXCEL_DIR = BASE_DIR / "excel"
EXCEL_OUTPUT_FILE = EXCEL_DIR / "retail_sales_analytics.xlsx"

# Reports and Docs
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Required raw schema columns
REQUIRED_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Postal Code",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]

# Standardized column mapping (snake_case)
COLUMN_MAPPING = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}

# Discount segmentation bins and labels
DISCOUNT_BINS = [-0.001, 0.0, 0.10, 0.20, 0.40, 1.0]
DISCOUNT_LABELS = [
    "0% (No Discount)",
    "1% - 10% (Low)",
    "11% - 20% (Moderate)",
    "21% - 40% (High)",
    "> 40% (Deep Discount)",
]
