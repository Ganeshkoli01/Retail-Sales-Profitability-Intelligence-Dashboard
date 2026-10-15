"""Reusable metric calculation functions for Retail Analytics.

Provides vectorized NumPy and pandas operations to compute executive KPIs,
growth rates, profitability measures, and customer RFM profiles.
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd


def calculate_total_revenue(df: pd.DataFrame) -> float:
    """Calculate total sales revenue, rounded to 2 decimal places."""
    if df.empty or "sales" not in df.columns:
        return 0.0
    return float(np.round(df["sales"].sum(), 2))


def calculate_total_profit(df: pd.DataFrame) -> float:
    """Calculate net contribution profit, rounded to 2 decimal places."""
    if df.empty or "profit" not in df.columns:
        return 0.0
    return float(np.round(df["profit"].sum(), 2))


def calculate_overall_profit_margin(df: pd.DataFrame) -> float:
    """Calculate overall profit margin ratio (Profit / Revenue).

    Returns 0.0 if revenue is zero or DataFrame is empty.
    """
    if df.empty or "sales" not in df.columns or "profit" not in df.columns:
        return 0.0
    total_sales = df["sales"].sum()
    if total_sales == 0:
        return 0.0
    return float(np.round(df["profit"].sum() / total_sales, 4))


def calculate_total_orders(df: pd.DataFrame) -> int:
    """Count unique purchase order IDs."""
    if df.empty or "order_id" not in df.columns:
        return 0
    return int(df["order_id"].nunique())


def calculate_total_units_sold(df: pd.DataFrame) -> int:
    """Calculate total merchandise units sold."""
    if df.empty or "quantity" not in df.columns:
        return 0
    return int(df["quantity"].sum())


def calculate_average_order_value(df: pd.DataFrame) -> float:
    """Calculate Average Order Value (AOV = Total Sales / Unique Orders).

    Returns 0.0 if order count is zero.
    """
    orders = calculate_total_orders(df)
    if orders == 0:
        return 0.0
    return float(np.round(calculate_total_revenue(df) / orders, 2))


def calculate_loss_order_rate(df: pd.DataFrame) -> float:
    """Calculate the percentage of transaction line items with negative profit."""
    if df.empty or "profit" not in df.columns:
        return 0.0
    total_lines = len(df)
    if total_lines == 0:
        return 0.0
    loss_lines = (df["profit"] < 0).sum()
    return float(np.round((loss_lines / total_lines) * 100.0, 2))


def calculate_kpi_summary(df: pd.DataFrame) -> Dict[str, Union[float, int]]:
    """Compute executive-level KPI scorecard dictionary."""
    return {
        "total_revenue": calculate_total_revenue(df),
        "total_profit": calculate_total_profit(df),
        "profit_margin_pct": round(calculate_overall_profit_margin(df) * 100.0, 2),
        "total_orders": calculate_total_orders(df),
        "total_units_sold": calculate_total_units_sold(df),
        "average_order_value": calculate_average_order_value(df),
        "unique_customers": int(df["customer_id"].nunique()) if "customer_id" in df.columns else 0,
        "loss_transaction_rate_pct": calculate_loss_order_rate(df),
    }


def calculate_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly time series performance table with MoM growth."""
    if df.empty:
        return pd.DataFrame()

    monthly = (
        df.groupby(["order_year_month", "order_year", "order_month"], as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_lines=("row_id", "count"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            total_quantity=("quantity", "sum"),
            avg_discount=("discount", "mean"),
        )
        .sort_values("order_year_month")
        .reset_index(drop=True)
    )

    monthly["total_sales"] = monthly["total_sales"].round(2)
    monthly["total_profit"] = monthly["total_profit"].round(2)
    monthly["profit_margin_pct"] = np.where(
        monthly["total_sales"] != 0,
        np.round((monthly["total_profit"] / monthly["total_sales"]) * 100.0, 2),
        0.0,
    )
    monthly["average_order_value"] = np.where(
        monthly["total_orders"] != 0,
        np.round(monthly["total_sales"] / monthly["total_orders"], 2),
        0.0,
    )

    # MoM calculations via vectorized shift
    monthly["prior_sales"] = monthly["total_sales"].shift(1)
    monthly["mom_sales_growth_pct"] = np.where(
        monthly["prior_sales"].notna() & (monthly["prior_sales"] != 0),
        np.round(((monthly["total_sales"] - monthly["prior_sales"]) / monthly["prior_sales"]) * 100.0, 2),
        np.nan,
    )

    monthly["prior_profit"] = monthly["total_profit"].shift(1)
    monthly["mom_profit_growth_pct"] = np.where(
        monthly["prior_profit"].notna() & (monthly["prior_profit"] != 0),
        np.round(((monthly["total_profit"] - monthly["prior_profit"]) / monthly["prior_profit"].abs()) * 100.0, 2),
        np.nan,
    )

    return monthly


def calculate_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute category and subcategory profitability breakdown."""
    if df.empty:
        return pd.DataFrame()

    cat_df = (
        df.groupby(["category", "sub_category"], as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
            loss_orders=("profit", lambda p: (p < 0).sum()),
            total_lines=("row_id", "count"),
        )
        .reset_index(drop=True)
    )

    cat_df["total_sales"] = cat_df["total_sales"].round(2)
    cat_df["total_profit"] = cat_df["total_profit"].round(2)
    cat_df["profit_margin_pct"] = np.where(
        cat_df["total_sales"] != 0,
        np.round((cat_df["total_profit"] / cat_df["total_sales"]) * 100.0, 2),
        0.0,
    )
    cat_df["avg_discount_pct"] = np.round(cat_df["avg_discount"] * 100.0, 1)
    cat_df["loss_rate_pct"] = np.where(
        cat_df["total_lines"] != 0,
        np.round((cat_df["loss_orders"] / cat_df["total_lines"]) * 100.0, 2),
        0.0,
    )

    # Subcategory rank within category
    cat_df["profit_rank_in_category"] = (
        cat_df.groupby("category")["total_profit"]
        .rank(ascending=False, method="dense")
        .astype(int)
    )

    return cat_df.sort_values(["category", "total_profit"], ascending=[True, False]).reset_index(drop=True)


def calculate_discount_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze discount tiers vs realized profit margins and loss rates."""
    if df.empty:
        return pd.DataFrame()

    disc = (
        df.groupby("discount_tier", as_index=False, observed=False)
        .agg(
            transaction_count=("row_id", "count"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
            loss_transactions=("profit", lambda p: (p < 0).sum()),
        )
        .reset_index(drop=True)
    )

    disc["total_sales"] = disc["total_sales"].round(2)
    disc["total_profit"] = disc["total_profit"].round(2)
    disc["profit_margin_pct"] = np.where(
        disc["total_sales"] != 0,
        np.round((disc["total_profit"] / disc["total_sales"]) * 100.0, 2),
        0.0,
    )
    disc["loss_rate_pct"] = np.where(
        disc["transaction_count"] != 0,
        np.round((disc["loss_transactions"] / disc["transaction_count"]) * 100.0, 2),
        0.0,
    )
    disc["avg_discount_pct"] = np.round(disc["avg_discount"] * 100.0, 1)

    return disc.sort_values("avg_discount_pct").reset_index(drop=True)


def calculate_sales_traps(df: pd.DataFrame, min_sales: float = 2500.0) -> pd.DataFrame:
    """Isolate high-sales products that yield net losses ('Sales Traps')."""
    if df.empty:
        return pd.DataFrame()

    prod = (
        df.groupby(["product_id", "product_name", "category", "sub_category"], as_index=False)
        .agg(
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
            units_sold=("quantity", "sum"),
            order_count=("order_id", "nunique"),
        )
    )

    traps = prod[(prod["total_sales"] >= min_sales) & (prod["total_profit"] < 0)].copy()
    traps["total_sales"] = traps["total_sales"].round(2)
    traps["total_profit"] = traps["total_profit"].round(2)
    traps["profit_margin_pct"] = np.round((traps["total_profit"] / traps["total_sales"]) * 100.0, 2)
    traps["avg_discount_pct"] = np.round(traps["avg_discount"] * 100.0, 1)

    return traps.sort_values("total_profit", ascending=True).reset_index(drop=True)


def calculate_rfm_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Recency, Frequency, Monetary (RFM) and Customer Profit."""
    if df.empty:
        return pd.DataFrame()

    max_date = pd.to_datetime(df["order_date"]).max()
    rfm = (
        df.groupby(["customer_id", "customer_name", "segment"], as_index=False)
        .agg(
            last_order_date=("order_date", "max"),
            order_frequency=("order_id", "nunique"),
            total_spend=("sales", "sum"),
            total_profit=("profit", "sum"),
            units_bought=("quantity", "sum"),
        )
        .reset_index(drop=True)
    )

    rfm["recency_days"] = (max_date - pd.to_datetime(rfm["last_order_date"])).dt.days
    rfm["total_spend"] = rfm["total_spend"].round(2)
    rfm["total_profit"] = rfm["total_profit"].round(2)
    rfm["profit_margin_pct"] = np.where(
        rfm["total_spend"] != 0,
        np.round((rfm["total_profit"] / rfm["total_spend"]) * 100.0, 2),
        0.0,
    )
    rfm["average_order_value"] = np.where(
        rfm["order_frequency"] != 0,
        np.round(rfm["total_spend"] / rfm["order_frequency"], 2),
        0.0,
    )

    return rfm.sort_values("total_spend", ascending=False).reset_index(drop=True)


def calculate_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics across geographic regions."""
    if df.empty:
        return pd.DataFrame()

    grand_profit = df["profit"].sum()
    reg = (
        df.groupby("region", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
        )
        .reset_index(drop=True)
    )

    reg["total_sales"] = reg["total_sales"].round(2)
    reg["total_profit"] = reg["total_profit"].round(2)
    reg["profit_margin_pct"] = np.where(
        reg["total_sales"] != 0,
        np.round((reg["total_profit"] / reg["total_sales"]) * 100.0, 2),
        0.0,
    )
    reg["profit_share_pct"] = np.where(
        grand_profit != 0,
        np.round((reg["total_profit"] / grand_profit) * 100.0, 2),
        0.0,
    )
    reg["avg_discount_pct"] = np.round(reg["avg_discount"] * 100.0, 1)

    return reg.sort_values("total_profit", ascending=False).reset_index(drop=True)
