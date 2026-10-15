"""Data Cleaning and Quality Assurance module for Retail Sales Analytics."""

import logging
from pathlib import Path
from typing import Dict, Tuple, Any
import numpy as np
import pandas as pd

from src.config import (
    CLEANED_DATA_FILE,
    REJECTED_DATA_FILE,
    COLUMN_MAPPING,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_retail_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Clean, standardize, and validate the raw retail dataset.

    Separates records violating data-quality constraints into a rejected DataFrame
    with explicit error reasons instead of silently dropping data.

    Args:
        df: Raw pandas DataFrame.

    Returns:
        Tuple of (cleaned_df, rejected_df, quality_metrics_dict).
    """
    total_raw_rows = len(df)
    logger.info(f"Initiating data cleaning pipeline for {total_raw_rows:,} records.")

    # 1. Rename columns to snake_case standard
    renamed_df = df.rename(columns=COLUMN_MAPPING).copy()

    # Track rejection reasons per record
    rejection_reasons = pd.Series("", index=renamed_df.index)

    # 2. Check for exact duplicate rows
    duplicate_mask = renamed_df.duplicated()
    if duplicate_mask.any():
        rejection_reasons[duplicate_mask] += "Exact duplicate row; "

    # 3. Parse and validate dates
    renamed_df["order_date"] = pd.to_datetime(renamed_df["order_date"], errors="coerce")
    renamed_df["ship_date"] = pd.to_datetime(renamed_df["ship_date"], errors="coerce")

    invalid_order_date = renamed_df["order_date"].isna()
    if invalid_order_date.any():
        rejection_reasons[invalid_order_date] += "Invalid or unparseable order_date; "

    invalid_ship_date = renamed_df["ship_date"].isna()
    if invalid_ship_date.any():
        rejection_reasons[invalid_ship_date] += "Invalid or unparseable ship_date; "

    # Chronological logic: ship_date must not precede order_date
    invalid_shipping_seq = (
        (~invalid_order_date)
        & (~invalid_ship_date)
        & (renamed_df["ship_date"] < renamed_df["order_date"])
    )
    if invalid_shipping_seq.any():
        rejection_reasons[invalid_shipping_seq] += "Ship date precedes order date; "

    # 4. Numerical validation
    renamed_df["sales"] = pd.to_numeric(renamed_df["sales"], errors="coerce")
    renamed_df["quantity"] = pd.to_numeric(renamed_df["quantity"], errors="coerce")
    renamed_df["discount"] = pd.to_numeric(renamed_df["discount"], errors="coerce")
    renamed_df["profit"] = pd.to_numeric(renamed_df["profit"], errors="coerce")

    # Sales must be positive (> 0)
    invalid_sales = renamed_df["sales"].isna() | (renamed_df["sales"] <= 0)
    if invalid_sales.any():
        rejection_reasons[invalid_sales] += "Sales must be positive numerical value; "

    # Quantity must be integer >= 1
    invalid_quantity = renamed_df["quantity"].isna() | (renamed_df["quantity"] < 1)
    if invalid_quantity.any():
        rejection_reasons[invalid_quantity] += "Quantity must be integer >= 1; "

    # Discount must be between 0.0 and 1.0 (0% to 100%)
    invalid_discount = (
        renamed_df["discount"].isna()
        | (renamed_df["discount"] < 0.0)
        | (renamed_df["discount"] > 1.0)
    )
    if invalid_discount.any():
        rejection_reasons[invalid_discount] += "Discount must be between 0.00 and 1.00; "

    # Profit must be a valid finite number
    invalid_profit = renamed_df["profit"].isna() | ~np.isfinite(renamed_df["profit"])
    if invalid_profit.any():
        rejection_reasons[invalid_profit] += "Profit must be a valid finite numerical value; "

    # 5. Mandatory identifier strings
    mandatory_text_cols = ["order_id", "customer_id", "product_id"]
    for col in mandatory_text_cols:
        missing_id = renamed_df[col].isna() | (renamed_df[col].astype(str).str.strip() == "")
        if missing_id.any():
            rejection_reasons[missing_id] += f"Missing mandatory field '{col}'; "

    # Separate into Cleaned and Rejected
    rejected_mask = rejection_reasons != ""
    rejected_df = renamed_df[rejected_mask].copy()
    rejected_df["rejection_reason"] = rejection_reasons[rejected_mask].str.rstrip("; ")

    cleaned_df = renamed_df[~rejected_mask].copy()

    # 6. Standardization of text fields in cleaned dataset
    text_columns = [
        "order_id",
        "customer_id",
        "customer_name",
        "segment",
        "country",
        "city",
        "state",
        "region",
        "product_id",
        "category",
        "sub_category",
        "product_name",
        "ship_mode",
    ]
    for col in text_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

    # Format postal_code as clean 5-digit zero-padded string
    cleaned_df["postal_code"] = (
        cleaned_df["postal_code"]
        .fillna(0)
        .astype(np.int64)
        .astype(str)
        .str.zfill(5)
    )

    # Cast integer fields explicitly
    cleaned_df["row_id"] = cleaned_df["row_id"].astype(np.int64)
    cleaned_df["quantity"] = cleaned_df["quantity"].astype(np.int64)

    # Ensure precision rounding on financials
    cleaned_df["sales"] = cleaned_df["sales"].round(4)
    cleaned_df["discount"] = cleaned_df["discount"].round(4)
    cleaned_df["profit"] = cleaned_df["profit"].round(4)

    # Calculate Data Quality Metrics
    quality_metrics = {
        "total_records_ingested": total_raw_rows,
        "clean_records_count": len(cleaned_df),
        "rejected_records_count": len(rejected_df),
        "clean_record_rate_pct": round(len(cleaned_df) / total_raw_rows * 100, 2),
        "duplicate_rows_detected": int(duplicate_mask.sum()),
        "invalid_order_dates": int(invalid_order_date.sum()),
        "invalid_ship_dates": int(invalid_ship_date.sum()),
        "invalid_shipping_duration": int(invalid_shipping_seq.sum()),
        "invalid_sales_count": int(invalid_sales.sum()),
        "invalid_quantity_count": int(invalid_quantity.sum()),
        "invalid_discount_count": int(invalid_discount.sum()),
        "invalid_profit_count": int(invalid_profit.sum()),
        "rejection_reasons_breakdown": rejected_df["rejection_reason"].value_counts().to_dict()
        if len(rejected_df) > 0
        else {},
    }

    logger.info(
        f"Cleaning complete: {len(cleaned_df):,} records validated ({quality_metrics['clean_record_rate_pct']}%), "
        f"{len(rejected_df):,} records quarantined."
    )

    return cleaned_df, rejected_df, quality_metrics


def save_cleaned_data(
    cleaned_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
    clean_path: Path = CLEANED_DATA_FILE,
    reject_path: Path = REJECTED_DATA_FILE,
) -> None:
    """Save cleaned and quarantined data to destination CSV files."""
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    reject_path.parent.mkdir(parents=True, exist_ok=True)

    cleaned_df.to_csv(clean_path, index=False, encoding="utf-8")
    rejected_df.to_csv(reject_path, index=False, encoding="utf-8")
    logger.info(f"Saved cleaned data to: {clean_path}")
    logger.info(f"Saved quarantined data to: {reject_path}")
