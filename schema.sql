
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
