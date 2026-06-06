"""
Day 2: Data Cleaning and SQLite Database Loading
- Clean nav_history.csv, investor_transactions.csv, scheme_performance.csv
- Design and create SQLite star schema
- Load all cleaned datasets into SQLite
- Verify row counts
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_cleaning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
RAW_DIR = 'data_1/Bluestock_MF_Datasets'
PROCESSED_DIR = 'data/processed'
DB_PATH = 'bluestock_mf.db'

# Ensure processed directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ============================================================
# CLEANING FUNCTIONS
# ============================================================

def clean_nav_history():
    """Clean nav_history.csv: parse dates, sort, forward-fill, dedupe, validate NAV > 0"""
    logger.info("=" * 60)
    logger.info("Cleaning nav_history.csv")
    logger.info("=" * 60)
    
    # Read raw data
    df = pd.read_csv(f'{RAW_DIR}/02_nav_history.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Parse dates to datetime
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    invalid_dates = df['date'].isna().sum()
    if invalid_dates > 0:
        logger.warning(f"Dropping {invalid_dates} rows with invalid dates")
        df = df.dropna(subset=['date'])
    
    # Ensure amfi_code is integer
    df['amfi_code'] = pd.to_numeric(df['amfi_code'], errors='coerce')
    df = df.dropna(subset=['amfi_code'])
    df['amfi_code'] = df['amfi_code'].astype(int)
    
    # Ensure nav is numeric
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    
    # Validate NAV > 0
    invalid_nav = (df['nav'] <= 0).sum()
    if invalid_nav > 0:
        logger.warning(f"Dropping {invalid_nav} rows with NAV <= 0")
        df = df[df['nav'] > 0]
    
    # Remove duplicates (keep first occurrence)
    duplicates = df.duplicated(subset=['amfi_code', 'date'], keep='first').sum()
    if duplicates > 0:
        logger.info(f"Removing {duplicates} duplicate rows")
        df = df.drop_duplicates(subset=['amfi_code', 'date'], keep='first')
    
    # Sort by amfi_code + date
    df = df.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    
    # Forward-fill missing NAV for holidays/weekends
    # Create complete date range for each amfi_code
    logger.info("Forward-filling missing NAV for holidays/weekends...")
    
    filled_dfs = []
    for code in df['amfi_code'].unique():
        code_df = df[df['amfi_code'] == code].copy()
        min_date = code_df['date'].min()
        max_date = code_df['date'].max()
        
        # Create complete business day date range
        full_dates = pd.bdate_range(start=min_date, end=max_date)
        full_df = pd.DataFrame({'date': full_dates})
        full_df['amfi_code'] = code
        
        # Merge with original data
        merged = full_df.merge(code_df, on=['amfi_code', 'date'], how='left')
        
        # Forward fill NAV
        merged['nav'] = merged['nav'].ffill()
        
        filled_dfs.append(merged)
    
    df_filled = pd.concat(filled_dfs, ignore_index=True)
    
    # Drop any rows where NAV is still NaN (beginning of series)
    df_filled = df_filled.dropna(subset=['nav'])
    
    final_rows = len(df_filled)
    logger.info(f"Final rows after forward-fill: {final_rows}")
    logger.info(f"Rows added by forward-fill: {final_rows - initial_rows + duplicates + invalid_dates + invalid_nav}")
    
    # Save cleaned data
    df_filled.to_csv(f'{PROCESSED_DIR}/nav_history_cleaned.csv', index=False)
    logger.info(f"Saved cleaned nav_history.csv to {PROCESSED_DIR}/nav_history_cleaned.csv")
    
    return df_filled


def clean_investor_transactions():
    """Clean investor_transactions.csv: standardize types, validate amounts, fix dates, check KYC"""
    logger.info("=" * 60)
    logger.info("Cleaning investor_transactions.csv")
    logger.info("=" * 60)
    
    # Read raw data
    df = pd.read_csv(f'{RAW_DIR}/08_investor_transactions.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%Y-%m-%d', errors='coerce')
    invalid_dates = df['transaction_date'].isna().sum()
    if invalid_dates > 0:
        logger.warning(f"Dropping {invalid_dates} rows with invalid dates")
        df = df.dropna(subset=['transaction_date'])
    
    # Standardize transaction_type values
    valid_types = ['SIP', 'Lumpsum', 'Redemption']
    df['transaction_type'] = df['transaction_type'].str.strip().str.title()
    
    # Map variations to standard values
    type_mapping = {
        'Sip': 'SIP',
        'Lump Sum': 'Lumpsum',
        'Lump': 'Lumpsum',
        'Redeem': 'Redemption',
        'Red': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].replace(type_mapping)
    
    # Check for invalid transaction types
    invalid_types = ~df['transaction_type'].isin(valid_types)
    if invalid_types.sum() > 0:
        logger.warning(f"Found {invalid_types.sum()} rows with invalid transaction types:")
        logger.warning(f"{df[invalid_types]['transaction_type'].value_counts().to_dict()}")
        # Keep only valid types
        df = df[df['transaction_type'].isin(valid_types)]
    
    # Validate amount > 0
    df['amount_inr'] = pd.to_numeric(df['amount_inr'], errors='coerce')
    invalid_amounts = (df['amount_inr'] <= 0).sum()
    if invalid_amounts > 0:
        logger.warning(f"Dropping {invalid_amounts} rows with amount <= 0")
        df = df[df['amount_inr'] > 0]
    
    # Check KYC status enum values
    valid_kyc = ['Verified', 'Pending', 'Rejected']
    df['kyc_status'] = df['kyc_status'].str.strip().str.title()
    
    invalid_kyc = ~df['kyc_status'].isin(valid_kyc)
    if invalid_kyc.sum() > 0:
        logger.warning(f"Found {invalid_kyc.sum()} rows with invalid KYC status:")
        logger.warning(f"{df[invalid_kyc]['kyc_status'].value_counts().to_dict()}")
        # Keep only valid KYC statuses
        df = df[df['kyc_status'].isin(valid_kyc)]
    
    # Ensure amfi_code is integer
    df['amfi_code'] = pd.to_numeric(df['amfi_code'], errors='coerce')
    df = df.dropna(subset=['amfi_code'])
    df['amfi_code'] = df['amfi_code'].astype(int)
    
    # Standardize city_tier values
    valid_tiers = ['T30', 'B30']
    df['city_tier'] = df['city_tier'].str.strip()
    invalid_tiers = ~df['city_tier'].isin(valid_tiers)
    if invalid_tiers.sum() > 0:
        logger.warning(f"Found {invalid_tiers.sum()} rows with invalid city_tier")
    
    # Standardize age_group values
    valid_age_groups = ['18-25', '26-35', '36-45', '46-55', '56+']
    df['age_group'] = df['age_group'].str.strip()
    
    # Standardize gender values
    df['gender'] = df['gender'].str.strip().str.title()
    valid_genders = ['Male', 'Female']
    df = df[df['gender'].isin(valid_genders)]
    
    # Standardize payment_mode values
    df['payment_mode'] = df['payment_mode'].str.strip().str.title()
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    logger.info(f"Transaction type distribution:\n{df['transaction_type'].value_counts().to_string()}")
    logger.info(f"KYC status distribution:\n{df['kyc_status'].value_counts().to_string()}")
    
    # Save cleaned data
    df.to_csv(f'{PROCESSED_DIR}/investor_transactions_cleaned.csv', index=False)
    logger.info(f"Saved cleaned investor_transactions.csv to {PROCESSED_DIR}/investor_transactions_cleaned.csv")
    
    return df


def clean_scheme_performance():
    """Clean scheme_performance.csv: validate returns, flag anomalies, check expense_ratio"""
    logger.info("=" * 60)
    logger.info("Cleaning scheme_performance.csv")
    logger.info("=" * 60)
    
    # Read raw data
    df = pd.read_csv(f'{RAW_DIR}/07_scheme_performance.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Ensure amfi_code is integer
    df['amfi_code'] = pd.to_numeric(df['amfi_code'], errors='coerce')
    df = df.dropna(subset=['amfi_code'])
    df['amfi_code'] = df['amfi_code'].astype(int)
    
    # Validate all return values are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        non_numeric = df[col].isna().sum()
        if non_numeric > 0:
            logger.warning(f"Column {col}: {non_numeric} non-numeric values converted to NaN")
    
    # Validate risk metrics are numeric
    metric_cols = ['alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 
                   'std_dev_ann_pct', 'max_drawdown_pct']
    for col in metric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Validate aum_crore is numeric
    df['aum_crore'] = pd.to_numeric(df['aum_crore'], errors='coerce')
    
    # Check expense_ratio range (0.1% - 2.5%)
    df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
    
    low_expense = (df['expense_ratio_pct'] < 0.1).sum()
    high_expense = (df['expense_ratio_pct'] > 2.5).sum()
    
    if low_expense > 0:
        logger.warning(f"Found {low_expense} funds with expense_ratio < 0.1%")
        logger.warning(f"AMFI codes: {df[df['expense_ratio_pct'] < 0.1]['amfi_code'].tolist()}")
    
    if high_expense > 0:
        logger.warning(f"Found {high_expense} funds with expense_ratio > 2.5%")
        logger.warning(f"AMFI codes: {df[df['expense_ratio_pct'] > 2.5]['amfi_code'].tolist()}")
    
    # Flag anomalies
    df['anomaly_flag'] = False
    df['anomaly_reason'] = ''
    
    # Anomaly: Negative returns for 5 years (unusual for equity)
    neg_5yr = df['return_5yr_pct'] < 0
    df.loc[neg_5yr, 'anomaly_flag'] = True
    df.loc[neg_5yr, 'anomaly_reason'] += 'Negative 5yr return; '
    
    # Anomaly: Very high returns (>50% for 1 year)
    high_1yr = df['return_1yr_pct'] > 50
    df.loc[high_1yr, 'anomaly_flag'] = True
    df.loc[high_1yr, 'anomaly_reason'] += 'Very high 1yr return (>50%); '
    
    # Anomaly: Beta > 2 (very high volatility)
    high_beta = df['beta'] > 2
    df.loc[high_beta, 'anomaly_flag'] = True
    df.loc[high_beta, 'anomaly_reason'] += 'High beta (>2); '
    
    # Anomaly: Max drawdown > 50%
    high_dd = df['max_drawdown_pct'] < -50
    df.loc[high_dd, 'anomaly_flag'] = True
    df.loc[high_dd, 'anomaly_reason'] += 'Severe max drawdown (<-50%); '
    
    # Anomaly: Negative Sharpe ratio
    neg_sharpe = df['sharpe_ratio'] < 0
    df.loc[neg_sharpe, 'anomaly_flag'] = True
    df.loc[neg_sharpe, 'anomaly_reason'] += 'Negative Sharpe ratio; '
    
    anomalies = df['anomaly_flag'].sum()
    logger.info(f"Total anomalies flagged: {anomalies}")
    
    # Validate morningstar_rating (1-5)
    df['morningstar_rating'] = pd.to_numeric(df['morningstar_rating'], errors='coerce')
    invalid_rating = ~df['morningstar_rating'].between(1, 5)
    if invalid_rating.sum() > 0:
        logger.warning(f"Found {invalid_rating.sum()} funds with invalid morningstar_rating")
    
    # Validate risk_grade values
    valid_risk_grades = ['Low', 'Moderate', 'Moderately High', 'High', 'Very High']
    df['risk_grade'] = df['risk_grade'].str.strip()
    invalid_risk = ~df['risk_grade'].isin(valid_risk_grades)
    if invalid_risk.sum() > 0:
        logger.warning(f"Found {invalid_risk.sum()} funds with invalid risk_grade")
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    # Save cleaned data
    df.to_csv(f'{PROCESSED_DIR}/scheme_performance_cleaned.csv', index=False)
    logger.info(f"Saved cleaned scheme_performance.csv to {PROCESSED_DIR}/scheme_performance_cleaned.csv")
    
    return df


def clean_fund_master():
    """Clean and prepare fund_master.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning fund_master.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/01_fund_master.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Ensure amfi_code is integer
    df['amfi_code'] = pd.to_numeric(df['amfi_code'], errors='coerce')
    df = df.dropna(subset=['amfi_code'])
    df['amfi_code'] = df['amfi_code'].astype(int)
    
    # Parse launch_date
    df['launch_date'] = pd.to_datetime(df['launch_date'], format='%Y-%m-%d', errors='coerce')
    
    # Ensure numeric columns
    df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
    df['exit_load_pct'] = pd.to_numeric(df['exit_load_pct'], errors='coerce')
    df['min_sip_amount'] = pd.to_numeric(df['min_sip_amount'], errors='coerce')
    df['min_lumpsum_amount'] = pd.to_numeric(df['min_lumpsum_amount'], errors='coerce')
    
    # Standardize categorical columns
    df['category'] = df['category'].str.strip().str.title()
    df['sub_category'] = df['sub_category'].str.strip().str.title()
    df['plan'] = df['plan'].str.strip().str.title()
    df['risk_category'] = df['risk_category'].str.strip().str.title()
    
    # Remove duplicates
    duplicates = df.duplicated(subset=['amfi_code'], keep='first').sum()
    if duplicates > 0:
        logger.info(f"Removing {duplicates} duplicate amfi_codes")
        df = df.drop_duplicates(subset=['amfi_code'], keep='first')
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/fund_master_cleaned.csv', index=False)
    logger.info(f"Saved cleaned fund_master.csv")
    
    return df


def clean_aum_by_fund_house():
    """Clean aum_by_fund_house.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning aum_by_fund_house.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/03_aum_by_fund_house.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    
    # Ensure numeric columns
    df['aum_lakh_crore'] = pd.to_numeric(df['aum_lakh_crore'], errors='coerce')
    df['aum_crore'] = pd.to_numeric(df['aum_crore'], errors='coerce')
    df['num_schemes'] = pd.to_numeric(df['num_schemes'], errors='coerce')
    
    # Standardize fund_house names
    df['fund_house'] = df['fund_house'].str.strip()
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/aum_by_fund_house_cleaned.csv', index=False)
    logger.info(f"Saved cleaned aum_by_fund_house.csv")
    
    return df


def clean_monthly_sip_inflows():
    """Clean monthly_sip_inflows.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning monthly_sip_inflows.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/04_monthly_sip_inflows.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Parse month
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    
    # Ensure numeric columns
    numeric_cols = ['sip_inflow_crore', 'active_sip_accounts_crore', 
                    'new_sip_accounts_lakh', 'sip_aum_lakh_crore', 'yoy_growth_pct']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/monthly_sip_inflows_cleaned.csv', index=False)
    logger.info(f"Saved cleaned monthly_sip_inflows.csv")
    
    return df


def clean_category_inflows():
    """Clean category_inflows.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning category_inflows.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/05_category_inflows.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Parse month
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    
    # Ensure numeric columns
    df['net_inflow_crore'] = pd.to_numeric(df['net_inflow_crore'], errors='coerce')
    
    # Standardize category names
    df['category'] = df['category'].str.strip().str.title()
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/category_inflows_cleaned.csv', index=False)
    logger.info(f"Saved cleaned category_inflows.csv")
    
    return df


def clean_industry_folio_count():
    """Clean industry_folio_count.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning industry_folio_count.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/06_industry_folio_count.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Parse month
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    
    # Ensure numeric columns
    numeric_cols = ['total_folios_crore', 'equity_folios_crore', 'debt_folios_crore',
                    'hybrid_folios_crore', 'others_folios_crore']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/industry_folio_count_cleaned.csv', index=False)
    logger.info(f"Saved cleaned industry_folio_count.csv")
    
    return df


def clean_portfolio_holdings():
    """Clean portfolio_holdings.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning portfolio_holdings.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/09_portfolio_holdings.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Ensure amfi_code is integer
    df['amfi_code'] = pd.to_numeric(df['amfi_code'], errors='coerce')
    df = df.dropna(subset=['amfi_code'])
    df['amfi_code'] = df['amfi_code'].astype(int)
    
    # Parse portfolio_date
    df['portfolio_date'] = pd.to_datetime(df['portfolio_date'], format='%Y-%m-%d', errors='coerce')
    
    # Ensure numeric columns
    df['weight_pct'] = pd.to_numeric(df['weight_pct'], errors='coerce')
    df['market_value_cr'] = pd.to_numeric(df['market_value_cr'], errors='coerce')
    df['current_price_inr'] = pd.to_numeric(df['current_price_inr'], errors='coerce')
    
    # Standardize text columns
    df['stock_symbol'] = df['stock_symbol'].str.strip().str.upper()
    df['stock_name'] = df['stock_name'].str.strip()
    df['sector'] = df['sector'].str.strip().str.title()
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/portfolio_holdings_cleaned.csv', index=False)
    logger.info(f"Saved cleaned portfolio_holdings.csv")
    
    return df


def clean_benchmark_indices():
    """Clean benchmark_indices.csv"""
    logger.info("=" * 60)
    logger.info("Cleaning benchmark_indices.csv")
    logger.info("=" * 60)
    
    df = pd.read_csv(f'{RAW_DIR}/10_benchmark_indices.csv')
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    
    # Ensure numeric columns
    df['close_value'] = pd.to_numeric(df['close_value'], errors='coerce')
    
    # Standardize index names
    df['index_name'] = df['index_name'].str.strip().str.upper()
    
    final_rows = len(df)
    logger.info(f"Final rows: {final_rows}")
    
    df.to_csv(f'{PROCESSED_DIR}/benchmark_indices_cleaned.csv', index=False)
    logger.info(f"Saved cleaned benchmark_indices.csv")
    
    return df


# ============================================================
# SQLITE SCHEMA CREATION
# ============================================================

def create_schema_sql():
    """Generate schema.sql file with CREATE TABLE statements"""
    
    schema_sql = """
-- ============================================================
-- Bluestock Mutual Fund Database Schema
-- Star Schema Design
-- ============================================================

-- Dimension Table: Fund
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT NOT NULL,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- Dimension Table: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    fiscal_year INTEGER NOT NULL
);

-- Fact Table: NAV History
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(full_date),
    UNIQUE(amfi_code, date)
);

-- Fact Table: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr REAL NOT NULL CHECK(amount_inr > 0),
    state TEXT,
    city TEXT,
    city_tier TEXT CHECK(city_tier IN ('T30', 'B30')),
    age_group TEXT CHECK(age_group IN ('18-25', '26-35', '36-45', '46-55', '56+')),
    gender TEXT CHECK(gender IN ('Male', 'Female')),
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT CHECK(kyc_status IN ('Verified', 'Pending', 'Rejected')),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(full_date)
);

-- Fact Table: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL CHECK(expense_ratio_pct BETWEEN 0.1 AND 2.5),
    morningstar_rating INTEGER CHECK(morningstar_rating BETWEEN 1 AND 5),
    risk_grade TEXT CHECK(risk_grade IN ('Low', 'Moderate', 'Moderately High', 'High', 'Very High')),
    anomaly_flag BOOLEAN DEFAULT FALSE,
    anomaly_reason TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Fact Table: AUM by Fund House
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    FOREIGN KEY (date) REFERENCES dim_date(full_date)
);

-- Fact Table: Monthly SIP Inflows
CREATE TABLE IF NOT EXISTS fact_sip_inflows (
    sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- Fact Table: Category Inflows
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    category_inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL
);

-- Fact Table: Industry Folio Count
CREATE TABLE IF NOT EXISTS fact_folio_count (
    folio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- Fact Table: Portfolio Holdings
CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Fact Table: Benchmark Indices
CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date(full_date)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_trans_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_trans_amfi ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_trans_type ON fact_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_perf_category ON fact_performance(category);
CREATE INDEX IF NOT EXISTS idx_perf_fund_house ON fact_performance(fund_house);
CREATE INDEX IF NOT EXISTS idx_aum_date ON fact_aum(date);
CREATE INDEX IF NOT EXISTS idx_benchmark_date ON fact_benchmark_indices(date);
CREATE INDEX IF NOT EXISTS idx_benchmark_name ON fact_benchmark_indices(index_name);
"""
    
    with open('schema.sql', 'w') as f:
        f.write(schema_sql)
    
    logger.info("Created schema.sql")
    return schema_sql


def populate_dim_date(engine):
    """Populate dim_date with all dates from the datasets"""
    logger.info("Populating dim_date table...")
    
    # Get min and max dates from all date columns
    dates = set()
    
    # From nav_history
    nav_df = pd.read_csv(f'{PROCESSED_DIR}/nav_history_cleaned.csv', usecols=['date'])
    dates.update(pd.to_datetime(nav_df['date']).tolist())
    
    # From transactions
    trans_df = pd.read_csv(f'{PROCESSED_DIR}/investor_transactions_cleaned.csv', usecols=['transaction_date'])
    dates.update(pd.to_datetime(trans_df['transaction_date']).tolist())
    
    # From aum
    aum_df = pd.read_csv(f'{PROCESSED_DIR}/aum_by_fund_house_cleaned.csv', usecols=['date'])
    dates.update(pd.to_datetime(aum_df['date']).tolist())
    
    # From benchmark
    bench_df = pd.read_csv(f'{PROCESSED_DIR}/benchmark_indices_cleaned.csv', usecols=['date'])
    dates.update(pd.to_datetime(bench_df['date']).tolist())
    
    # Create date range
    min_date = min(dates)
    max_date = max(dates)
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Create dim_date dataframe
    dim_date = pd.DataFrame({
        'full_date': all_dates
    })
    
    dim_date['date_key'] = dim_date['full_date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['year'] = dim_date['full_date'].dt.year
    dim_date['quarter'] = dim_date['full_date'].dt.quarter
    dim_date['month'] = dim_date['full_date'].dt.month
    dim_date['month_name'] = dim_date['full_date'].dt.month_name()
    dim_date['day'] = dim_date['full_date'].dt.day
    dim_date['day_of_week'] = dim_date['full_date'].dt.dayofweek
    dim_date['day_name'] = dim_date['full_date'].dt.day_name()
    dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
    dim_date['is_month_end'] = dim_date['full_date'].dt.is_month_end
    dim_date['fiscal_year'] = dim_date['full_date'].apply(
        lambda x: x.year if x.month >= 4 else x.year - 1
    )
    
    # Rename for SQLite
    dim_date = dim_date.rename(columns={'full_date': 'full_date'})
    
    # Write to SQLite
    dim_date.to_sql('dim_date', engine, if_exists='replace', index=False)
    
    logger.info(f"Populated dim_date with {len(dim_date)} rows")
    return dim_date


def load_data_to_sqlite(engine, dataframes):
    """Load all cleaned dataframes into SQLite"""
    logger.info("=" * 60)
    logger.info("Loading data to SQLite")
    logger.info("=" * 60)
    
    row_counts = {}
    
    # Load dimension tables first
    logger.info("Loading dim_fund...")
    dataframes['fund_master'].to_sql('dim_fund', engine, if_exists='replace', index=False)
    row_counts['dim_fund'] = len(dataframes['fund_master'])
    
    # Populate dim_date
    populate_dim_date(engine)
    
    # Load fact tables
    logger.info("Loading fact_nav...")
    nav_df = dataframes['nav_history'][['amfi_code', 'date', 'nav']].copy()
    nav_df.to_sql('fact_nav', engine, if_exists='replace', index=False)
    row_counts['fact_nav'] = len(nav_df)
    
    logger.info("Loading fact_transactions...")
    trans_df = dataframes['investor_transactions'].copy()
    trans_df = trans_df.rename(columns={'transaction_date': 'transaction_date'})
    trans_df.to_sql('fact_transactions', engine, if_exists='replace', index=False)
    row_counts['fact_transactions'] = len(trans_df)
    
    logger.info("Loading fact_performance...")
    dataframes['scheme_performance'].to_sql('fact_performance', engine, if_exists='replace', index=False)
    row_counts['fact_performance'] = len(dataframes['scheme_performance'])
    
    logger.info("Loading fact_aum...")
    dataframes['aum_by_fund_house'].to_sql('fact_aum', engine, if_exists='replace', index=False)
    row_counts['fact_aum'] = len(dataframes['aum_by_fund_house'])
    
    logger.info("Loading fact_sip_inflows...")
    dataframes['monthly_sip_inflows'].to_sql('fact_sip_inflows', engine, if_exists='replace', index=False)
    row_counts['fact_sip_inflows'] = len(dataframes['monthly_sip_inflows'])
    
    logger.info("Loading fact_category_inflows...")
    dataframes['category_inflows'].to_sql('fact_category_inflows', engine, if_exists='replace', index=False)
    row_counts['fact_category_inflows'] = len(dataframes['category_inflows'])
    
    logger.info("Loading fact_folio_count...")
    dataframes['industry_folio_count'].to_sql('fact_folio_count', engine, if_exists='replace', index=False)
    row_counts['fact_folio_count'] = len(dataframes['industry_folio_count'])
    
    logger.info("Loading fact_portfolio_holdings...")
    dataframes['portfolio_holdings'].to_sql('fact_portfolio_holdings', engine, if_exists='replace', index=False)
    row_counts['fact_portfolio_holdings'] = len(dataframes['portfolio_holdings'])
    
    logger.info("Loading fact_benchmark_indices...")
    dataframes['benchmark_indices'].to_sql('fact_benchmark_indices', engine, if_exists='replace', index=False)
    row_counts['fact_benchmark_indices'] = len(dataframes['benchmark_indices'])
    
    return row_counts


def verify_row_counts(engine, raw_counts, cleaned_counts):
    """Verify row counts match between source CSVs and SQLite tables"""
    logger.info("=" * 60)
    logger.info("Verifying row counts")
    logger.info("=" * 60)
    
    verification_results = []
    
    for table_name, raw_count in raw_counts.items():
        query = f"SELECT COUNT(*) as cnt FROM {table_name}"
        result = pd.read_sql(query, engine)
        db_count = result['cnt'].iloc[0]
        
        cleaned_count = cleaned_counts.get(table_name, 'N/A')
        
        status = "PASS" if db_count == cleaned_count else "FAIL"
        
        verification_results.append({
            'table': table_name,
            'raw_count': raw_count,
            'cleaned_count': cleaned_count,
            'db_count': db_count,
            'status': status
        })
        
        logger.info(f"{table_name}: Raw={raw_count}, Cleaned={cleaned_count}, DB={db_count} [{status}]")
    
    return pd.DataFrame(verification_results)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("STARTING DATA CLEANING AND DATABASE LOADING")
    logger.info("=" * 60)
    
    # Step 1: Clean all datasets
    logger.info("\n--- STEP 1: Cleaning datasets ---\n")
    
    dataframes = {}
    
    # Clean the three main datasets as specified
    dataframes['nav_history'] = clean_nav_history()
    dataframes['investor_transactions'] = clean_investor_transactions()
    dataframes['scheme_performance'] = clean_scheme_performance()
    
    # Clean remaining datasets
    dataframes['fund_master'] = clean_fund_master()
    dataframes['aum_by_fund_house'] = clean_aum_by_fund_house()
    dataframes['monthly_sip_inflows'] = clean_monthly_sip_inflows()
    dataframes['category_inflows'] = clean_category_inflows()
    dataframes['industry_folio_count'] = clean_industry_folio_count()
    dataframes['portfolio_holdings'] = clean_portfolio_holdings()
    dataframes['benchmark_indices'] = clean_benchmark_indices()
    
    # Step 2: Create schema
    logger.info("\n--- STEP 2: Creating schema ---\n")
    create_schema_sql()
    
    # Step 3: Load to SQLite
    logger.info("\n--- STEP 3: Loading to SQLite ---\n")
    
    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logger.info(f"Removed existing {DB_PATH}")
    
    engine = create_engine(f'sqlite:///{DB_PATH}')
    
    cleaned_counts = {
        'dim_fund': len(dataframes['fund_master']),
        'fact_nav': len(dataframes['nav_history']),
        'fact_transactions': len(dataframes['investor_transactions']),
        'fact_performance': len(dataframes['scheme_performance']),
        'fact_aum': len(dataframes['aum_by_fund_house']),
        'fact_sip_inflows': len(dataframes['monthly_sip_inflows']),
        'fact_category_inflows': len(dataframes['category_inflows']),
        'fact_folio_count': len(dataframes['industry_folio_count']),
        'fact_portfolio_holdings': len(dataframes['portfolio_holdings']),
        'fact_benchmark_indices': len(dataframes['benchmark_indices'])
    }
    
    row_counts = load_data_to_sqlite(engine, dataframes)
    
    # Step 4: Verify row counts
    logger.info("\n--- STEP 4: Verifying row counts ---\n")
    
    # Get raw counts
    raw_counts = {
        'dim_fund': len(pd.read_csv(f'{RAW_DIR}/01_fund_master.csv')),
        'fact_nav': len(pd.read_csv(f'{RAW_DIR}/02_nav_history.csv')),
        'fact_transactions': len(pd.read_csv(f'{RAW_DIR}/08_investor_transactions.csv')),
        'fact_performance': len(pd.read_csv(f'{RAW_DIR}/07_scheme_performance.csv')),
        'fact_aum': len(pd.read_csv(f'{RAW_DIR}/03_aum_by_fund_house.csv')),
        'fact_sip_inflows': len(pd.read_csv(f'{RAW_DIR}/04_monthly_sip_inflows.csv')),
        'fact_category_inflows': len(pd.read_csv(f'{RAW_DIR}/05_category_inflows.csv')),
        'fact_folio_count': len(pd.read_csv(f'{RAW_DIR}/06_industry_folio_count.csv')),
        'fact_portfolio_holdings': len(pd.read_csv(f'{RAW_DIR}/09_portfolio_holdings.csv')),
        'fact_benchmark_indices': len(pd.read_csv(f'{RAW_DIR}/10_benchmark_indices.csv'))
    }
    
    verification_df = verify_row_counts(engine, raw_counts, cleaned_counts)
    verification_df.to_csv(f'{PROCESSED_DIR}/row_count_verification.csv', index=False)
    
    engine.dispose()
    
    logger.info("\n" + "=" * 60)
    logger.info("DATA CLEANING AND DATABASE LOADING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Cleaned CSVs: {PROCESSED_DIR}/")
    logger.info(f"Schema: schema.sql")
    
    return dataframes


if __name__ == '__main__':
    main()
