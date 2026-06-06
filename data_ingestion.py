"""
Data Ingestion Script for Mutual Fund Analysis
Loads and explores 10 CSV datasets, prints shape, dtypes, and head.
"""

import pandas as pd
import os
from pathlib import Path

# Define the data directory
DATA_DIR = Path(__file__).parent / "data" / "raw"

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
    Load a CSV dataset and print exploration details.
    
    Args:
        file_path: Path to the CSV file
        dataset_name: Name of the dataset for display
        
    Returns:
        Loaded DataFrame
    """
    print("=" * 80)
    print(f"DATASET: {dataset_name}")
    print("=" * 80)
    
    try:
        # Load the dataset
        df = pd.read_csv(file_path)
        
        # Print shape
        print(f"\n📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Print data types
        print(f"\n📋 Data Types:")
        print(df.dtypes)
        
        # Print first few rows
        print(f"\n👀 First 5 rows:")
        print(df.head().to_string())
        
        # Check for anomalies
        print(f"\n⚠️  Anomaly Check:")
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            print(f"  - Missing values detected:")
            for col, count in missing[missing > 0].items():
                print(f"    • {col}: {count} missing ({count/len(df)*100:.1f}%)")
        else:
            print(f"  - No missing values")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            print(f"  - Duplicate rows: {duplicates}")
        else:
            print(f"  - No duplicate rows")
        
        # Check for potential data type issues
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if numeric columns are stored as strings
                try:
                    pd.to_numeric(df[col].dropna().head(100))
                    print(f"  - ⚠️  Column '{col}' might be numeric but stored as object")
                except (ValueError, TypeError):
                    pass
        
        print("\n")
        return df
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        print(f"   Please ensure the file exists in {DATA_DIR}\n")
        return None
    except Exception as e:
        print(f"❌ Error loading {dataset_name}: {str(e)}\n")
        return None


def main():
    """Main function to load and explore all datasets."""
    print("\n" + "=" * 80)
    print("MUTUAL FUND DATA INGESTION")
    print("=" * 80 + "\n")
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        print("   Creating directory structure...")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"   Please place CSV files in {DATA_DIR}")
        return
    
    # Load each dataset
    datasets = {}
    for csv_file in CSV_FILES:
        file_path = DATA_DIR / csv_file
        dataset_name = csv_file.replace('.csv', '').replace('_', ' ').title()
        df = load_and_explore_dataset(file_path, dataset_name)
        if df is not None:
            datasets[csv_file] = df
    
    # Summary
    print("=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"Total datasets expected: {len(CSV_FILES)}")
    print(f"Successfully loaded: {len(datasets)}")
    print(f"Missing files: {len(CSV_FILES) - len(datasets)}")
    
    if len(datasets) < len(CSV_FILES):
        print("\nMissing files:")
        for csv_file in CSV_FILES:
            if csv_file not in datasets:
                print(f"  - {csv_file}")
    
    print("\n✅ Data ingestion complete!")
    return datasets


if __name__ == "__main__":
    datasets = main()
