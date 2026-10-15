"""Data Ingestion module for Retail Sales Analytics."""

import logging
from pathlib import Path
from typing import Optional
import pandas as pd

from src.config import RAW_DATA_FILE, REQUIRED_COLUMNS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_raw_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load raw retail sales data and validate schema completeness.

    Args:
        file_path: Path to the raw CSV file. Defaults to config.RAW_DATA_FILE.

    Returns:
        pd.DataFrame containing raw sales transactions.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If mandatory columns are missing from the dataset.
    """
    target_path = file_path or RAW_DATA_FILE
    if not Path(target_path).exists():
        raise FileNotFoundError(f"Raw dataset file not found at: {target_path}")

    logger.info(f"Loading raw dataset from: {target_path}")

    # Attempt windows-1252 first as standard for Superstore, fallback to utf-8 / latin1
    encodings_to_try = ["windows-1252", "utf-8", "latin1"]
    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(target_path, encoding=enc)
            logger.info(f"Successfully read raw file with encoding: {enc}")
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(f"Failed to decode {target_path} with standard encodings.")

    # Validate mandatory columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    logger.info(f"Raw data loaded successfully: {len(df):,} rows, {len(df.columns)} columns.")
    return df


if __name__ == "__main__":
    raw_df = load_raw_data()
    print(raw_df.head(2))
