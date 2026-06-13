"""
Data Ingestion Script for Mutual Fund Analysis
===============================================

Loads and explores 10 CSV datasets, performs initial data quality checks,
and prints shape, dtypes, and head for each dataset.

This script is part of the Bluestock Mutual Fund Capstone Project.

Functions:
    load_and_explore_dataset: Load a single CSV and perform exploration
    main: Orchestrate loading of all 10 datasets

Author: Bluestock Capstone Project
Version: 1.0
"""

import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the data directory using pathlib for cross-platform compatibility
DATA_DIR = Path(__file__).parent.parent / "data_1" / "Bluestock_MF_Datasets"

# List of expected CSV files (10 datasets)
CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]


def load_and_explore_dataset(file_path: Path, dataset_name: str) -> pd.DataFrame:
    """
    Load a CSV dataset and perform exploration analysis.
    
    This function loads a CSV file, displays its shape, data types,
    first few rows, and checks for anomalies including missing values,
    duplicates, and potential data type issues.
    
    Args:
        file_path (Path): Path to the CSV file.
        dataset_name (str): Name of the dataset for display purposes.
        
    Returns:
        pd.DataFrame: Loaded DataFrame, or None if loading fails.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: For any other loading errors.
    """
    logger.info("=" * 60)
    logger.info(f"DATASET: {dataset_name}")
    logger.info("=" * 60)
    
    try:
        # Load the dataset
        df = pd.read_csv(file_path)
        
        # Log shape
        logger.info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Log data types
        logger.info(f"Data Types:\n{df.dtypes}")
        
        # Log first few rows
        logger.info(f"First 5 rows:\n{df.head().to_string()}")
        
        # Check for anomalies
        logger.info("Anomaly Check:")
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            logger.warning("Missing values detected:")
            for col, count in missing[missing > 0].items():
                logger.warning(f"  {col}: {count} missing ({count/len(df)*100:.1f}%)")
        else:
            logger.info("No missing values")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            logger.warning(f"Duplicate rows: {duplicates}")
        else:
            logger.info("No duplicate rows")
        
        # Check for potential data type issues
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if numeric columns are stored as strings
                try:
                    pd.to_numeric(df[col].dropna().head(100))
                    logger.warning(f"Column '{col}' might be numeric but stored as object")
                except (ValueError, TypeError):
                    pass
        
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        logger.error(f"Please ensure the file exists in {DATA_DIR}")
        return None
    except Exception as e:
        logger.error(f"Error loading {dataset_name}: {str(e)}")
        return None


def main():
    """
    Main function to load and explore all datasets.
    
    Orchestrates the loading of all 10 CSV datasets, performs initial
    exploration, and provides a summary of the ingestion process.
    
    Returns:
        dict: Dictionary mapping filenames to loaded DataFrames.
    """
    logger.info("=" * 60)
    logger.info("MUTUAL FUND DATA INGESTION")
    logger.info("=" * 60)
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        logger.error(f"Data directory not found: {DATA_DIR}")
        logger.info("Creating directory structure...")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Please place CSV files in {DATA_DIR}")
        return {}
    
    # Load each dataset
    datasets = {}
    for csv_file in CSV_FILES:
        file_path = DATA_DIR / csv_file
        dataset_name = csv_file.replace('.csv', '').replace('_', ' ').title()
        df = load_and_explore_dataset(file_path, dataset_name)
        if df is not None:
            datasets[csv_file] = df
    
    # Summary
    logger.info("=" * 60)
    logger.info("INGESTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total datasets expected: {len(CSV_FILES)}")
    logger.info(f"Successfully loaded: {len(datasets)}")
    logger.info(f"Missing files: {len(CSV_FILES) - len(datasets)}")
    
    if len(datasets) < len(CSV_FILES):
        logger.warning("Missing files:")
        for csv_file in CSV_FILES:
            if csv_file not in datasets:
                logger.warning(f"  {csv_file}")
    
    logger.info("Data ingestion complete!")
    return datasets


if __name__ == "__main__":
    datasets = main()
