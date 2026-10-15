"""Main orchestration pipeline for Retail Sales & Profitability Analytics."""

import logging
import sys
from pathlib import Path
import json
import pandas as pd

from src.config import (
    RAW_DATA_FILE,
    CLEANED_DATA_FILE,
    REJECTED_DATA_FILE,
    DATABASE_FILE,
    EXCEL_OUTPUT_FILE,
    REPORTS_DIR,
    SCREENSHOTS_DIR,
)
from src.data_ingestion import load_raw_data
from src.data_cleaning import clean_retail_data, save_cleaned_data
from src.feature_engineering import engineer_features
from src.database import initialize_database, load_data_to_database, execute_query
from src.metrics import (
    calculate_kpi_summary,
    calculate_monthly_summary,
    calculate_category_summary,
    calculate_discount_sensitivity,
    calculate_sales_traps,
    calculate_regional_summary,
    calculate_rfm_metrics,
)
from src.analysis import reconcile_python_and_sql, generate_full_analysis
from src.visualizations import generate_all_visualizations
from src.export_excel import export_full_excel_workbook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("RetailAnalyticsPipeline")


def run_pipeline() -> dict:
    """Execute the full end-to-end data analytics pipeline."""
    logger.info("=================================================================")
    logger.info("STARTING RETAIL SALES & PROFITABILITY ANALYTICS PIPELINE")
    logger.info("=================================================================")

    # Step 1: Ingestion
    logger.info("Step 1: Ingesting raw retail sales dataset...")
    raw_df = load_raw_data(RAW_DATA_FILE)

    # Step 2: Cleaning & Validation
    logger.info("Step 2: Cleaning and validating records...")
    cleaned_df, rejected_df, quality_metrics = clean_retail_data(raw_df)

    # Step 3: Feature Engineering
    logger.info("Step 3: Deriving temporal, financial, and operational features...")
    enriched_df = engineer_features(cleaned_df)

    # Step 4: Persist Processed Data
    logger.info("Step 4: Persisting cleaned and quarantined datasets...")
    save_cleaned_data(enriched_df, rejected_df, CLEANED_DATA_FILE, REJECTED_DATA_FILE)

    # Step 5: Database Loading
    logger.info("Step 5: Initializing SQLite database and loading tables/views...")
    initialize_database()
    loaded_records = load_data_to_database(enriched_df, table_name="retail_orders")

    # Step 6: Quantitative Analysis & SQL Reconciliation
    logger.info("Step 6: Executing analytical calculations and SQL reconciliation...")
    reconciliation = reconcile_python_and_sql(enriched_df)
    analysis_mats = generate_full_analysis(enriched_df)
    kpis = calculate_kpi_summary(enriched_df)

    # Step 7: Visualization Generation
    logger.info("Step 7: Generating presentation-ready visualization charts...")
    generate_all_visualizations(
        analysis_mats["monthly_summary"],
        analysis_mats["category_summary"],
        analysis_mats["discount_sensitivity"],
        analysis_mats["regional_summary"],
        SCREENSHOTS_DIR,
    )

    # Step 8: Polished Excel Workbook Export
    logger.info("Step 8: Exporting polished 10-sheet corporate Excel workbook...")
    excel_path = export_full_excel_workbook(enriched_df, EXCEL_OUTPUT_FILE)

    logger.info("=================================================================")
    logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    logger.info(f"Verified Records in Database: {loaded_records:,}")
    logger.info(f"Total Sales Revenue: ${kpis['total_revenue']:,.2f}")
    logger.info(f"Total Net Profit: ${kpis['total_profit']:,.2f} (Margin: {kpis['profit_margin_pct']:.2f}%)")
    logger.info(f"Total Orders: {kpis['total_orders']:,} | AOV: ${kpis['average_order_value']:,.2f}")
    logger.info(f"Python-SQL Reconciliation: {'PASS' if reconciliation['is_reconciled'] else 'FAIL'}")
    logger.info(f"Excel Workbook: {excel_path}")
    logger.info("=================================================================")

    return {
        "status": "SUCCESS",
        "records_processed": loaded_records,
        "kpis": kpis,
        "reconciliation": reconciliation,
        "quality_metrics": quality_metrics,
    }


if __name__ == "__main__":
    run_pipeline()
