"""Feature Engineering module for Retail Sales Analytics."""

import logging
import numpy as np
import pandas as pd

from src.config import DISCOUNT_BINS, DISCOUNT_LABELS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive temporal, operational, and financial features using vectorized operations.

    Args:
        df: Cleaned sales transactions DataFrame.

    Returns:
        pd.DataFrame enriched with analytical features.
    """
    logger.info("Enriching dataset with analytical and financial features...")
    df_feat = df.copy()

    # Ensure datetime format
    if not np.issubdtype(df_feat["order_date"].dtype, np.datetime64):
        df_feat["order_date"] = pd.to_datetime(df_feat["order_date"])
    if not np.issubdtype(df_feat["ship_date"].dtype, np.datetime64):
        df_feat["ship_date"] = pd.to_datetime(df_feat["ship_date"])

    # 1. Temporal dimensions
    df_feat["order_year"] = df_feat["order_date"].dt.year
    df_feat["order_month"] = df_feat["order_date"].dt.month
    df_feat["order_quarter"] = "Q" + df_feat["order_date"].dt.quarter.astype(str)
    df_feat["order_year_month"] = df_feat["order_date"].dt.strftime("%Y-%m")

    # 2. Fulfillment latency
    df_feat["shipping_duration_days"] = (
        df_feat["ship_date"] - df_feat["order_date"]
    ).dt.days

    # 3. Financial efficiency ratios
    # Vectorized safe division for profit margin: profit / sales
    df_feat["profit_margin"] = np.where(
        df_feat["sales"] != 0,
        np.round(df_feat["profit"] / df_feat["sales"], 4),
        0.0,
    )

    # 4. Unit economics
    # Realized unit price and implied unit cost of goods sold (COGS)
    df_feat["unit_price"] = np.round(df_feat["sales"] / df_feat["quantity"], 2)
    df_feat["unit_cost"] = np.round(
        (df_feat["sales"] - df_feat["profit"]) / df_feat["quantity"], 2
    )

    # 5. Profitability indicator
    df_feat["is_profitable"] = np.where(df_feat["profit"] > 0, 1, 0)

    # 6. Discount tier segmentation
    df_feat["discount_tier"] = pd.cut(
        df_feat["discount"],
        bins=DISCOUNT_BINS,
        labels=DISCOUNT_LABELS,
        right=True,
        include_lowest=True,
    ).astype(str)

    logger.info(f"Feature engineering complete. Total enriched columns: {len(df_feat.columns)}")
    return df_feat
