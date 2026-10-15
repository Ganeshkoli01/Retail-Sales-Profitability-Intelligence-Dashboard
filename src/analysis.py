"""Analysis and SQL-Python reconciliation engine for Retail Analytics."""

import logging
from typing import Dict, Any, Tuple
import pandas as pd

from src.database import execute_query, get_db_connection
from src.metrics import (
    calculate_kpi_summary,
    calculate_monthly_summary,
    calculate_category_summary,
    calculate_discount_sensitivity,
    calculate_sales_traps,
    calculate_rfm_metrics,
    calculate_regional_summary,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def reconcile_python_and_sql(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute rigorous reconciliation between Python vectorized calculations and SQLite queries.

    Checks:
    - Total Revenue
    - Total Profit
    - Total Quantity
    - Total Distinct Orders
    - Total Distinct Customers

    Returns:
        Dictionary containing values, absolute differences, and boolean PASS/FAIL flags.
    """
    logger.info("Executing Python vs SQL quantitative reconciliation...")

    # Python metrics
    py_kpis = calculate_kpi_summary(df)

    # SQL Query
    sql_kpi_query = """
    SELECT
        ROUND(SUM(sales), 2) AS sql_sales,
        ROUND(SUM(profit), 2) AS sql_profit,
        SUM(quantity) AS sql_quantity,
        COUNT(DISTINCT order_id) AS sql_orders,
        COUNT(DISTINCT customer_id) AS sql_customers
    FROM retail_orders;
    """
    sql_res = execute_query(sql_kpi_query).iloc[0]

    sales_diff = abs(float(py_kpis["total_revenue"]) - float(sql_res["sql_sales"]))
    profit_diff = abs(float(py_kpis["total_profit"]) - float(sql_res["sql_profit"]))
    quantity_diff = abs(int(py_kpis["total_units_sold"]) - int(sql_res["sql_quantity"]))
    orders_diff = abs(int(py_kpis["total_orders"]) - int(sql_res["sql_orders"]))
    customers_diff = abs(int(py_kpis["unique_customers"]) - int(sql_res["sql_customers"]))

    is_reconciled = (
        sales_diff <= 0.05
        and profit_diff <= 0.05
        and quantity_diff == 0
        and orders_diff == 0
        and customers_diff == 0
    )

    reconciliation_report = {
        "is_reconciled": bool(is_reconciled),
        "sales": {
            "python": float(py_kpis["total_revenue"]),
            "sql": float(sql_res["sql_sales"]),
            "difference": round(sales_diff, 4),
            "status": "PASS" if sales_diff <= 0.05 else "FAIL",
        },
        "profit": {
            "python": float(py_kpis["total_profit"]),
            "sql": float(sql_res["sql_profit"]),
            "difference": round(profit_diff, 4),
            "status": "PASS" if profit_diff <= 0.05 else "FAIL",
        },
        "quantity": {
            "python": int(py_kpis["total_units_sold"]),
            "sql": int(sql_res["sql_quantity"]),
            "difference": quantity_diff,
            "status": "PASS" if quantity_diff == 0 else "FAIL",
        },
        "orders": {
            "python": int(py_kpis["total_orders"]),
            "sql": int(sql_res["sql_orders"]),
            "difference": orders_diff,
            "status": "PASS" if orders_diff == 0 else "FAIL",
        },
        "customers": {
            "python": int(py_kpis["unique_customers"]),
            "sql": int(sql_res["sql_customers"]),
            "difference": customers_diff,
            "status": "PASS" if customers_diff == 0 else "FAIL",
        },
    }

    if is_reconciled:
        logger.info("Reconciliation SUCCESSFUL: 100% match between Python and SQL.")
    else:
        logger.error(f"Reconciliation FAILED: Discrepancies detected -> {reconciliation_report}")

    return reconciliation_report


def generate_full_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generate all standard analytical cuts across time, product, discount, and geography."""
    logger.info("Generating full multi-dimensional analytics suite...")
    return {
        "monthly_summary": calculate_monthly_summary(df),
        "category_summary": calculate_category_summary(df),
        "discount_sensitivity": calculate_discount_sensitivity(df),
        "sales_traps": calculate_sales_traps(df),
        "rfm_metrics": calculate_rfm_metrics(df),
        "regional_summary": calculate_regional_summary(df),
    }
