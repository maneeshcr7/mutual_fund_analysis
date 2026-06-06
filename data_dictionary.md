# Bluestock Mutual Fund Analysis - Data Dictionary

## Overview
This document provides a comprehensive data dictionary for the Bluestock Mutual Fund database, including column descriptions, data types, business definitions, and source references.

---

## Dimension Tables

### dim_fund
**Description:** Master dimension table containing information about mutual fund schemes.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| amfi_code | INTEGER | Unique identifier assigned by AMFI (Association of Mutual Funds in India) | 01_fund_master.csv | PRIMARY KEY |
| fund_house | TEXT | Name of the mutual fund company/asset management company | 01_fund_master.csv | NOT NULL |
| scheme_name | TEXT | Full name of the mutual fund scheme | 01_fund_master.csv | NOT NULL |
| category | TEXT | Broad classification of the fund (Equity, Debt, Hybrid) | 01_fund_master.csv | NOT NULL |
| sub_category | TEXT | Specific category within the broad classification (Large Cap, Mid Cap, etc.) | 01_fund_master.csv | - |
| plan | TEXT | Type of plan (Regular - through distributor, Direct - direct from AMC) | 01_fund_master.csv | NOT NULL |
| launch_date | DATE | Date when the scheme was launched | 01_fund_master.csv | - |
| benchmark | TEXT | Index against which fund performance is measured | 01_fund_master.csv | - |
| expense_ratio_pct | REAL | Annual expense charged by the fund as a percentage of AUM | 01_fund_master.csv | Range: 0.1% - 2.5% |
| exit_load_pct | REAL | Penalty charged for exiting the fund before specified period | 01_fund_master.csv | - |
| min_sip_amount | REAL | Minimum amount required for Systematic Investment Plan | 01_fund_master.csv | - |
| min_lumpsum_amount | REAL | Minimum amount for one-time investment | 01_fund_master.csv | - |
| fund_manager | TEXT | Name of the fund manager managing the scheme | 01_fund_master.csv | - |
| risk_category | TEXT | Risk classification (Low, Moderate, High, Very High) | 01_fund_master.csv | - |
| sebi_category_code | TEXT | SEBI classification code for the fund category | 01_fund_master.csv | - |

---

### dim_date
**Description:** Date dimension table for time-based analysis.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| date_key | INTEGER | Surrogate key in YYYYMMDD format | Generated | PRIMARY KEY |
| full_date | DATE | Actual date value | Generated | UNIQUE, NOT NULL |
| year | INTEGER | Calendar year | Generated | NOT NULL |
| quarter | INTEGER | Calendar quarter (1-4) | Generated | NOT NULL |
| month | INTEGER | Month number (1-12) | Generated | NOT NULL |
| month_name | TEXT | Full name of the month | Generated | NOT NULL |
| day | INTEGER | Day of the month (1-31) | Generated | NOT NULL |
| day_of_week | INTEGER | Day of week (0=Monday, 6=Sunday) | Generated | NOT NULL |
| day_name | TEXT | Full name of the day | Generated | NOT NULL |
| is_weekend | BOOLEAN | Flag indicating if the day is a weekend | Generated | NOT NULL |
| is_month_end | BOOLEAN | Flag indicating if the day is month-end | Generated | NOT NULL |
| fiscal_year | INTEGER | Indian fiscal year (April-March) | Generated | NOT NULL |

---

## Fact Tables

### fact_nav
**Description:** Daily NAV (Net Asset Value) history for all mutual fund schemes.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| nav_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| amfi_code | INTEGER | Reference to the mutual fund scheme | 02_nav_history.csv | FOREIGN KEY (dim_fund) |
| date | DATE | Date of the NAV record | 02_nav_history.csv | FOREIGN KEY (dim_date) |
| nav | REAL | Net Asset Value per unit in INR | 02_nav_history.csv | NOT NULL, > 0 |

**Cleaning Applied:**
- Parsed dates to datetime format
- Sorted by amfi_code and date
- Forward-filled missing NAV for holidays/weekends
- Removed duplicates
- Validated NAV > 0

---

### fact_transactions
**Description:** Individual investor transaction records.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| transaction_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| investor_id | TEXT | Unique identifier for the investor | 08_investor_transactions.csv | NOT NULL |
| transaction_date | DATE | Date of the transaction | 08_investor_transactions.csv | FOREIGN KEY (dim_date) |
| amfi_code | INTEGER | Reference to the mutual fund scheme | 08_investor_transactions.csv | FOREIGN KEY (dim_fund) |
| transaction_type | TEXT | Type of transaction (SIP/Lumpsum/Redemption) | 08_investor_transactions.csv | CHECK: SIP, Lumpsum, Redemption |
| amount_inr | REAL | Transaction amount in Indian Rupees | 08_investor_transactions.csv | NOT NULL, > 0 |
| state | TEXT | State where investor resides | 08_investor_transactions.csv | - |
| city | TEXT | City where investor resides | 08_investor_transactions.csv | - |
| city_tier | TEXT | City classification (T30/B30) | 08_investor_transactions.csv | CHECK: T30, B30 |
| age_group | TEXT | Age bracket of investor | 08_investor_transactions.csv | CHECK: 18-25, 26-35, 36-45, 46-55, 56+ |
| gender | TEXT | Gender of investor | 08_investor_transactions.csv | CHECK: Male, Female |
| annual_income_lakh | TEXT | Annual income in lakhs | 08_investor_transactions.csv | - |
| payment_mode | TEXT | Mode of payment used | 08_investor_transactions.csv | - |
| kyc_status | TEXT | KYC verification status | 08_investor_transactions.csv | CHECK: Verified, Pending, Rejected |

**Cleaning Applied:**
- Standardized transaction_type values (SIP/Lumpsum/Redemption)
- Validated amount > 0
- Fixed date formats
- Validated KYC status enum values
- Standardized city_tier, age_group, gender values

---

### fact_performance
**Description:** Performance metrics and details for mutual fund schemes.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| performance_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| amfi_code | INTEGER | Reference to the mutual fund scheme | 07_scheme_performance.csv | FOREIGN KEY (dim_fund) |
| scheme_name | TEXT | Name of the scheme | 07_scheme_performance.csv | NOT NULL |
| fund_house | TEXT | Name of the fund house | 07_scheme_performance.csv | NOT NULL |
| category | TEXT | Fund category | 07_scheme_performance.csv | NOT NULL |
| plan | TEXT | Plan type (Regular/Direct) | 07_scheme_performance.csv | NOT NULL |
| return_1yr_pct | REAL | 1-year return percentage | 07_scheme_performance.csv | Numeric |
| return_3yr_pct | REAL | 3-year annualized return percentage | 07_scheme_performance.csv | Numeric |
| return_5yr_pct | REAL | 5-year annualized return percentage | 07_scheme_performance.csv | Numeric |
| benchmark_3yr_pct | REAL | 3-year benchmark return percentage | 07_scheme_performance.csv | Numeric |
| alpha | REAL | Alpha value (excess return vs benchmark) | 07_scheme_performance.csv | Numeric |
| beta | REAL | Beta value (volatility vs market) | 07_scheme_performance.csv | Numeric |
| sharpe_ratio | REAL | Sharpe ratio (risk-adjusted return) | 07_scheme_performance.csv | Numeric |
| sortino_ratio | REAL | Sortino ratio (downside risk-adjusted return) | 07_scheme_performance.csv | Numeric |
| std_dev_ann_pct | REAL | Annualized standard deviation | 07_scheme_performance.csv | Numeric |
| max_drawdown_pct | REAL | Maximum drawdown percentage | 07_scheme_performance.csv | Numeric |
| aum_crore | REAL | Assets Under Management in crores | 07_scheme_performance.csv | Numeric |
| expense_ratio_pct | REAL | Expense ratio percentage | 07_scheme_performance.csv | CHECK: 0.1 - 2.5 |
| morningstar_rating | INTEGER | Morningstar rating (1-5 stars) | 07_scheme_performance.csv | CHECK: 1 - 5 |
| risk_grade | TEXT | Risk classification | 07_scheme_performance.csv | CHECK: Low, Moderate, Moderately High, High, Very High |
| anomaly_flag | BOOLEAN | Flag indicating data anomalies | Generated | DEFAULT: FALSE |
| anomaly_reason | TEXT | Description of anomalies found | Generated | - |

**Cleaning Applied:**
- Validated all return values are numeric
- Flagged anomalies (negative returns, high beta, severe drawdowns)
- Checked expense_ratio range (0.1% - 2.5%)
- Validated morningstar_rating (1-5)
- Validated risk_grade enum values

---

### fact_aum
**Description:** Assets Under Management data by fund house over time.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| aum_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| date | DATE | Date of AUM record | 03_aum_by_fund_house.csv | FOREIGN KEY (dim_date) |
| fund_house | TEXT | Name of the fund house | 03_aum_by_fund_house.csv | NOT NULL |
| aum_lakh_crore | REAL | AUM in lakh crores | 03_aum_by_fund_house.csv | Numeric |
| aum_crore | REAL | AUM in crores | 03_aum_by_fund_house.csv | Numeric |
| num_schemes | INTEGER | Number of schemes managed | 03_aum_by_fund_house.csv | Numeric |

---

### fact_sip_inflows
**Description:** Monthly SIP (Systematic Investment Plan) inflow data.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| sip_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| month | DATE | Month of the record | 04_monthly_sip_inflows.csv | NOT NULL |
| sip_inflow_crore | REAL | Total SIP inflow in crores | 04_monthly_sip_inflows.csv | Numeric |
| active_sip_accounts_crore | REAL | Number of active SIP accounts in crores | 04_monthly_sip_inflows.csv | Numeric |
| new_sip_accounts_lakh | REAL | New SIP accounts added in lakhs | 04_monthly_sip_inflows.csv | Numeric |
| sip_aum_lakh_crore | REAL | SIP AUM in lakh crores | 04_monthly_sip_inflows.csv | Numeric |
| yoy_growth_pct | REAL | Year-over-year growth percentage | 04_monthly_sip_inflows.csv | Numeric |

---

### fact_category_inflows
**Description:** Category-wise net inflow data.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| category_inflow_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| month | DATE | Month of the record | 05_category_inflows.csv | NOT NULL |
| category | TEXT | Fund category | 05_category_inflows.csv | NOT NULL |
| net_inflow_crore | REAL | Net inflow in crores | 05_category_inflows.csv | Numeric |

---

### fact_folio_count
**Description:** Industry folio (account) count data.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| folio_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| month | DATE | Month of the record | 06_industry_folio_count.csv | NOT NULL |
| total_folios_crore | REAL | Total folios in crores | 06_industry_folio_count.csv | Numeric |
| equity_folios_crore | REAL | Equity fund folios in crores | 06_industry_folio_count.csv | Numeric |
| debt_folios_crore | REAL | Debt fund folios in crores | 06_industry_folio_count.csv | Numeric |
| hybrid_folios_crore | REAL | Hybrid fund folios in crores | 06_industry_folio_count.csv | Numeric |
| others_folios_crore | REAL | Other fund folios in crores | 06_industry_folio_count.csv | Numeric |

---

### fact_portfolio_holdings
**Description:** Portfolio holdings details for mutual fund schemes.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| holding_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| amfi_code | INTEGER | Reference to the mutual fund scheme | 09_portfolio_holdings.csv | FOREIGN KEY (dim_fund) |
| stock_symbol | TEXT | Stock ticker symbol | 09_portfolio_holdings.csv | NOT NULL |
| stock_name | TEXT | Name of the company | 09_portfolio_holdings.csv | NOT NULL |
| sector | TEXT | Industry sector of the stock | 09_portfolio_holdings.csv | - |
| weight_pct | REAL | Weight in portfolio percentage | 09_portfolio_holdings.csv | Numeric |
| market_value_cr | REAL | Market value in crores | 09_portfolio_holdings.csv | Numeric |
| current_price_inr | REAL | Current stock price in INR | 09_portfolio_holdings.csv | Numeric |
| portfolio_date | DATE | Date of portfolio disclosure | 09_portfolio_holdings.csv | NOT NULL |

---

### fact_benchmark_indices
**Description:** Benchmark index historical data.

| Column Name | Data Type | Business Definition | Source | Constraints |
|-------------|-----------|---------------------|--------|-------------|
| benchmark_id | INTEGER | Surrogate primary key | Generated | PRIMARY KEY, AUTOINCREMENT |
| date | DATE | Date of the record | 10_benchmark_indices.csv | FOREIGN KEY (dim_date) |
| index_name | TEXT | Name of the benchmark index | 10_benchmark_indices.csv | NOT NULL |
| close_value | REAL | Closing value of the index | 10_benchmark_indices.csv | NOT NULL, Numeric |

---

## Data Quality Summary

### Cleaning Operations Performed

1. **nav_history.csv**
   - Parsed dates to datetime format
   - Sorted by amfi_code + date
   - Forward-filled missing NAV for holidays/weekends
   - Removed duplicates
   - Validated NAV > 0

2. **investor_transactions.csv**
   - Standardized transaction_type values (SIP/Lumpsum/Redemption)
   - Validated amount > 0
   - Fixed date formats
   - Checked KYC status enum values (Verified/Pending/Rejected)

3. **scheme_performance.csv**
   - Validated all return values are numeric
   - Flagged anomalies (negative returns, high beta, severe drawdowns)
   - Checked expense_ratio range (0.1% - 2.5%)

### Row Count Verification

| Table | Raw Count | Cleaned Count | DB Count | Status |
|-------|-----------|---------------|----------|--------|
| dim_fund | 40 | 40 | 40 | PASS |
| fact_nav | 46,000 | 46,000 | 46,000 | PASS |
| fact_transactions | 32,778 | 32,778 | 32,778 | PASS |
| fact_performance | 40 | 40 | 40 | PASS |
| fact_aum | 90 | 90 | 90 | PASS |
| fact_sip_inflows | 48 | 48 | 48 | PASS |
| fact_category_inflows | 144 | 144 | 144 | PASS |
| fact_folio_count | 21 | 21 | 21 | PASS |
| fact_portfolio_holdings | 322 | 322 | 322 | PASS |
| fact_benchmark_indices | 8,050 | 8,050 | 8,050 | PASS |

---

## Source Files Reference

| File Name | Description | Records |
|-----------|-------------|---------|
| 01_fund_master.csv | Master data for mutual fund schemes | 40 |
| 02_nav_history.csv | Daily NAV history | 46,000 |
| 03_aum_by_fund_house.csv | AUM by fund house over time | 90 |
| 04_monthly_sip_inflows.csv | Monthly SIP inflow data | 48 |
| 05_category_inflows.csv | Category-wise net inflows | 144 |
| 06_industry_folio_count.csv | Industry folio count data | 21 |
| 07_scheme_performance.csv | Scheme performance metrics | 40 |
| 08_investor_transactions.csv | Investor transaction records | 32,778 |
| 09_portfolio_holdings.csv | Portfolio holdings details | 322 |
| 10_benchmark_indices.csv | Benchmark index data | 8,050 |

---

## Database Information

- **Database Name:** bluestock_mf.db
- **Database Type:** SQLite
- **Schema:** Star Schema
- **Total Tables:** 11 (2 dimension + 9 fact tables)
- **Total Records:** ~87,493

---

*Last Updated: 2026-06-06*
