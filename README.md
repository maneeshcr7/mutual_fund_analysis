# Bluestock Mutual Fund Capstone Project

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)](https://github.com/maneeshreddy/bluestock-mf-capstone)

A comprehensive data analysis and analytics project for Indian mutual funds, featuring ETL pipelines, SQLite database, exploratory analysis, performance metrics, advanced analytics (VaR, cohort analysis, recommender system), and interactive dashboards.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Datasets](#datasets)
- [Setup Instructions](#setup-instructions)
- [How to Run](#how-to-run)
- [ETL Pipeline](#etl-pipeline)
- [Database Schema](#database-schema)
- [Performance Metrics](#performance-metrics)
- [Advanced Analytics](#advanced-analytics)
- [Dashboard](#dashboard)
- [Key Findings](#key-findings)
- [Deliverables](#deliverables)
- [Technologies Used](#technologies-used)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [License](#license)
- [Contact](#contact)

## Project Overview

This project provides a complete end-to-end solution for analyzing Indian mutual fund performance. It processes 10 datasets containing 87,493+ records covering 40 mutual fund schemes across 10 fund houses, spanning equity, debt, and hybrid categories.

**Analysis Period:** January 2022 – May 2026

**Key Objectives:**
- Design and implement a complete ETL pipeline for mutual fund data
- Build a SQLite star schema database with 11 tables (2 dimension + 9 fact)
- Conduct exploratory data analysis with 24+ visualizations
- Compute performance metrics from first principles (Sharpe, Sortino, Alpha, Beta, VaR)
- Develop an interactive dashboard with slicers and drill-down capabilities
- Implement advanced analytics including cohort analysis and fund recommender system
- Generate actionable insights for investors and fund managers

## Features

### D1 — ETL Pipeline (`scripts/etl_pipeline.py`)
- Loads all 10 CSV datasets using `pathlib.Path` (no hard-coded paths)
- Error handling with try/except, missing file detection
- Prints shape, dtypes, head, anomaly checks (missing, duplicates, type issues)
- Clean, modular code with functions

### D2 — SQLite Database (`data/db/bluestock_mf.db`)
- Star schema: 2 dimension tables + 9 fact tables
- `dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `fact_sip_inflows`, `fact_category_inflows`, `fact_folio_count`, `fact_portfolio_holdings`, `fact_benchmark_indices`
- Indexes on all foreign keys and frequently queried columns
- CHECK constraints on enums (transaction_type, kyc_status, risk_grade, etc.)
- 15 analytical SQL queries in `queries.sql`
- Row count verification: all tables PASS

### D3 — EDA Notebook (`notebooks/03_eda_analysis.ipynb`)
- NAV trend analysis (all schemes + faceted)
- AUM growth by fund house
- SIP inflow time series
- Category inflow heatmaps
- Investor demographics (age, gender, city tier, geographic)
- Industry folio count growth
- NAV correlation matrix
- Sector allocation donut chart

### D4 — Performance Analytics (`notebooks/04_performance_analytics.ipynb`)
- **Daily returns**: `nav_t / nav_{t-1} - 1` with distribution validation (histograms, box plots, Shapiro-Wilk)
- **CAGR**: `(NAV_end / NAV_start) ^ (1/n) - 1` for 1yr, 3yr, 5yr with comparison charts
- **Sharpe Ratio**: `(Rp - Rf) / Std(Rp) × √252`, Rf = 6.5%, ranked all 40 funds
- **Sortino Ratio**: downside deviation only, compared with Sharpe
- **Alpha & Beta**: OLS regression via `scipy.stats.linregress` vs Nifty 100, Alpha = intercept × 252
- **Max Drawdown**: `min(NAV / running_max - 1)` with peak/trough/recovery dates
- **Fund Scorecard (0-100)**: 30% 3yr CAGR + 25% Sharpe + 20% Alpha + 15% Expense (inverse) + 10% Max DD (inverse)
- **Benchmark comparison**: Top 5 funds vs Nifty 50 & Nifty 100 (3-year cumulative)
- **Tracking Error**: `std(fund_return - benchmark_return) × √252`
- Deliverables: `fund_scorecard.csv`, `alpha_beta.csv`, `benchmark_comparison_3yr.png`

### D5 — Interactive Dashboard
- Power BI / Tableau file in `dashboard/`
- 4 pages: Overview, Fund Performance, Investor Analytics, Benchmark Comparison
- Slicers: Category, Fund House, Risk Grade, Date Range

### D6 — Advanced Analytics (`notebooks/05_advanced_analytics.ipynb`)
- **Value at Risk (VaR)**: Parametric, Historical, and CVaR at 95% and 99% confidence
- **Cohort Analysis**: Age group, city tier, gender cross-tabulations with heatmaps; SIP retention analysis
- **Fund Recommender**: Content-based filtering using cosine similarity on normalized fund features; profile-based recommendations (conservative/moderate/aggressive × short/medium/long)

### D7 — Final Report & Presentation
- `reports/Final_Report.pdf`: Professional report with executive summary, methodology, findings, recommendations
- `reports/Bluestock_MF_Presentation.pptx`: 12-slide deck for stakeholder presentation

## Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/              ← original downloaded files (gitignored)
│   ├── processed/        ← cleaned, merged CSVs
│   └── db/               ← bluestock_mf.db (gitignored, see schema.sql)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py       ← data ingestion & exploration
│   ├── data_cleaning.py      ← cleaning + SQLite loading
│   ├── live_nav_fetch.py     ← auto-fetch NAV from mfapi.in
│   ├── compute_metrics.py    ← Sharpe, Sortino, Alpha, Beta, VaR
│   ├── recommender.py        ← fund recommender system
│   ├── explore_fund_master.py
│   ├── generate_final_report.py  ← PDF report generator
│   └── generate_presentation.py  ← PPTX presentation generator
├── sql/
│   ├── schema.sql            ← star schema DDL
│   └── queries.sql           ← 15 analytical SQL queries
├── dashboard/
│   └── (Power BI / Tableau files)
├── reports/
│   ├── figures/              ← 24 analysis charts (PNG)
│   ├── data_quality_summary.txt
│   ├── Final_Report.pdf
│   └── Bluestock_MF_Presentation.pptx
├── data_dictionary.md        ← column-level documentation
├── run_pipeline.py           ← master execution script
├── requirements.txt          ← Python dependencies
├── .gitignore                ← excludes *.db, data files
└── README.md                 ← this file
```

## Datasets

| # | File | Description | Records | Columns |
|---|------|-------------|---------|---------|
| 1 | 01_fund_master.csv | Scheme details (AMFI code, fund house, category) | 40 | 15 |
| 2 | 02_nav_history.csv | Daily NAV history for all schemes | 46,000 | 3 |
| 3 | 03_aum_by_fund_house.csv | AUM by fund house over time | 90 | 5 |
| 4 | 04_monthly_sip_inflows.csv | Monthly SIP inflow data | 48 | 6 |
| 5 | 05_category_inflows.csv | Category-wise net inflows | 144 | 3 |
| 6 | 06_industry_folio_count.csv | Industry folio count data | 21 | 6 |
| 7 | 07_scheme_performance.csv | Scheme performance metrics | 40 | 18 |
| 8 | 08_investor_transactions.csv | Investor transaction records | 32,778 | 12 |
| 9 | 09_portfolio_holdings.csv | Portfolio holdings details | 322 | 8 |
| 10 | 10_benchmark_indices.csv | Benchmark index data (7 indices) | 8,050 | 3 |

**Total Records:** 87,493+

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/maneeshreddy/bluestock-mf-capstone.git
   cd bluestock-mf-capstone
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python -c "import pandas; import numpy; import sklearn; print('All packages installed successfully!')"
   ```

### Requirements

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
plotly>=5.10.0
sqlalchemy>=1.4.0
requests>=2.28.0
scipy>=1.9.0
scikit-learn>=1.1.0
jupyter>=1.0.0
reportlab>=3.6.0
python-pptx>=0.6.21
```

## How to Run

### Option 1: Master Pipeline Script (Recommended)

Run the complete pipeline with a single command:

```bash
python run_pipeline.py
```

This will execute all steps in sequence:
1. ETL Pipeline (data ingestion)
2. Data Cleaning & Database Loading
3. Performance Metrics Computation
4. Fund Recommender System
5. Live NAV Fetch
6. Report Generation (PDF + PPTX)

### Option 2: Run Specific Steps

```bash
# Run only ETL steps
python run_pipeline.py --etl

# Run only analytics
python run_pipeline.py --analytics

# Generate reports only
python run_pipeline.py --reports

# Clean and rebuild database
python run_pipeline.py --clean

# Fetch live NAV data only
python run_pipeline.py --nav
```

### Option 3: Run Individual Scripts

```bash
# Step 1: Data Ingestion
python scripts/etl_pipeline.py

# Step 2: Data Cleaning + SQLite Loading
python scripts/data_cleaning.py

# Step 3: Fetch Live NAV Data
python scripts/live_nav_fetch.py

# Step 4: Compute Performance Metrics
python scripts/compute_metrics.py

# Step 5: Run Recommender
python scripts/recommender.py

# Step 6: Generate Reports
python scripts/generate_final_report.py
python scripts/generate_presentation.py
```

### Option 4: Jupyter Notebooks

```bash
jupyter notebook notebooks/01_data_ingestion.ipynb
jupyter notebook notebooks/02_data_cleaning.ipynb
jupyter notebook notebooks/03_eda_analysis.ipynb
jupyter notebook notebooks/04_performance_analytics.ipynb
jupyter notebook notebooks/05_advanced_analytics.ipynb
```

## ETL Pipeline

The ETL (Extract, Transform, Load) pipeline processes raw CSV data through three stages:

### Extract
- Load 10 CSV datasets using `pathlib.Path` for cross-platform compatibility
- Error handling with try/except blocks ensures graceful failure for missing files
- Initial data quality checks (shape, dtypes, missing values, duplicates)

### Transform
- **Date parsing** with format validation and error handling
- **Numeric conversion** with coercion for invalid values
- **Forward-filling** NAV for holidays/weekends using `pd.bdate_range`
- **Deduplication** based on composite keys (amfi_code + date)
- **Standardization** of categorical values (transaction_type, kyc_status, risk_grade)
- **Anomaly flagging** for unusual values (negative returns, high beta, severe drawdown)

### Load
- Insert cleaned data into SQLite star schema with 11 tables
- Create indexes on foreign keys and frequently queried columns
- Add CHECK constraints for data integrity
- Verify row counts match between source CSVs and database tables

## Database Schema

The database follows a star schema design with 2 dimension tables and 9 fact tables:

### Dimension Tables

**dim_fund** (40 records)
- amfi_code (PK), fund_house, scheme_name, category, sub_category
- plan, launch_date, benchmark, expense_ratio_pct, exit_load_pct
- min_sip_amount, min_lumpsum_amount, fund_manager, risk_category

**dim_date** (~1,600 records)
- date_key (PK), full_date, year, quarter, month, month_name
- day, day_of_week, day_name, is_weekend, is_month_end, fiscal_year

### Fact Tables

| Table | Records | Description |
|-------|---------|-------------|
| fact_nav | ~46,000 | Daily NAV history |
| fact_transactions | 32,778 | Investor transactions |
| fact_performance | 40 | Scheme performance metrics |
| fact_aum | 90 | AUM by fund house |
| fact_sip_inflows | 48 | Monthly SIP inflows |
| fact_category_inflows | 144 | Category-wise net inflows |
| fact_folio_count | 21 | Industry folio count |
| fact_portfolio_holdings | 322 | Portfolio holdings |
| fact_benchmark_indices | 8,050 | Benchmark index data |

### Indexes

All foreign keys and frequently queried columns are indexed for optimal query performance:
- `idx_nav_amfi_date` on fact_nav(amfi_code, date)
- `idx_trans_date` on fact_transactions(transaction_date)
- `idx_trans_amfi` on fact_transactions(amfi_code)
- `idx_perf_category` on fact_performance(category)
- And more...

## Performance Metrics

All metrics are computed from first principles using daily NAV data and annualized using 252 trading days.

### Sharpe Ratio
```
Sharpe = (Rp - Rf) / Std(Rp) × √252
```
Where:
- Rp = mean daily return
- Rf = 6.5% (RBI repo rate proxy)
- Std(Rp) = standard deviation of daily returns

### Sortino Ratio
```
Sortino = (Rp - Rf) / Std(downside) × √252
```
Uses downside deviation only (negative returns).

### Alpha & Beta
Computed via OLS regression against Nifty 100:
- Alpha = intercept × 252 (annualized)
- Beta = slope of regression line

### CAGR (Compound Annual Growth Rate)
```
CAGR = (NAV_end / NAV_start)^(1/n) - 1
```
Where n = number of years.

### Maximum Drawdown
```
Max Drawdown = min(NAV / running_max - 1)
```

### Value at Risk (VaR)
Historical VaR at 95% and 99% confidence levels.

## Advanced Analytics

### Value at Risk (VaR)
Three methods implemented:
1. **Parametric VaR**: Assumes normal distribution of returns
2. **Historical VaR**: Uses actual historical return distribution
3. **Conditional VaR (CVaR)**: Expected loss given VaR is exceeded

### Cohort Analysis
- Age group analysis (18-25, 26-35, 36-45, 46-55, 56+)
- City tier analysis (T30 vs B30)
- Gender-based investment patterns
- SIP retention analysis

### Fund Recommender System
Two approaches:
1. **Content-based filtering**: Cosine similarity on normalized fund features
2. **Profile-based recommendations**: Risk tolerance × investment horizon matrix

## Dashboard

The interactive dashboard includes 4 pages:

### 1. Overview Page
- Total AUM, number of schemes, average returns
- Top-performing funds summary
- Key metrics cards with real-time aggregation

### 2. Fund Performance Page
- Sharpe ratio comparison
- Drawdown visualization
- Rolling performance charts
- Fund comparison tools

### 3. Investor Analytics Page
- Demographic distribution
- Transaction patterns
- Geographic distribution
- SIP retention analysis

### 4. Benchmark Comparison Page
- Fund vs benchmark performance
- Tracking error analysis
- Information ratio calculation

### Dashboard Slicers
- Category (Equity, Debt, Hybrid, etc.)
- Fund House (HDFC, SBI, ICICI, etc.)
- Risk Grade (Low, Moderate, High, etc.)
- Date Range (custom date picker)

## Key Findings

### 1. Top Performing Funds (by composite score)
1. Mirae Asset Large Cap (86.25)
2. ICICI Pru Midcap (82.25)
3. Kotak Flexicap (82.00)
4. HDFC Mid-Cap Opportunities (81.13)
5. ICICI Pru Bluechip Direct (79.63)

### 2. Risk-Adjusted Returns
- Sharpe ratios range from -0.5 to 1.45
- Liquid/gilt funds show highest Sharpe due to low volatility
- Mid-cap funds offer best risk-adjusted returns among equity categories

### 3. Investor Demographics
- 26-35 age group dominates SIP investments (38% of transactions, 42% of volume)
- T30 cities contribute ~65% of total inflows
- Male investors represent 72% of transactions
- Female investors have 15% higher average transaction size

### 4. VaR Analysis
- Small cap funds show highest daily VaR (~3.5%)
- Liquid funds show lowest VaR (~0.1%)
- Mid-cap funds: ~2.8% daily VaR at 95% confidence

### 5. Cohort Insights
- SIP investors average 8+ transactions with 200+ day tenure
- Strong retention in equity funds (75% continue after 1 year)
- Average SIP tenure: 2.5 years

### 6. Cost Analysis
- Direct plans outperform regular plans by 0.5-1.0%
- Expense ratio impact compounds significantly over long periods
- Index funds offer lowest cost exposure

## Deliverables

### 1. Final Report (PDF)
**File:** `reports/Final_Report.pdf` (15-20 pages)

Sections:
- Executive Summary
- Data Sources
- ETL Design
- EDA Findings
- Performance Analysis
- Dashboard Screenshots
- Limitations
- Recommendations

### 2. Presentation (PPTX)
**File:** `reports/Bluestock_MF_Presentation.pptx` (12 slides)

Slides:
1. Title
2. Problem & Objective
3. Data Sources
4. Architecture
5. EDA Highlights (Part 1)
6. EDA Highlights (Part 2)
7. Performance Metrics (Part 1)
8. Performance Metrics (Part 2)
9. Dashboard Screenshots (Part 1)
10. Dashboard Screenshots (Part 2)
11. Key Findings
12. Thank You

### 3. GitHub Repository
**URL:** https://github.com/maneeshreddy/bluestock-mf-capstone

Contents:
- Clean, documented Python code
- Jupyter notebooks for analysis
- SQL schema and queries
- Dashboard files
- Generated reports
- README documentation

### 4. Interactive Dashboard
**Location:** `dashboard/`

Power BI/Tableau file with 4 pages and interactive slicers.

## Technologies Used

### Programming Languages
- **Python 3.8+**: Primary language for data processing and analysis
- **SQL**: Database queries and analytics

### Libraries & Frameworks
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib/seaborn**: Data visualization
- **plotly**: Interactive visualizations
- **scipy**: Statistical analysis
- **scikit-learn**: Machine learning (recommender system)
- **sqlalchemy**: Database ORM
- **requests**: API calls (live NAV fetch)
- **reportlab**: PDF generation
- **python-pptx**: PowerPoint generation

### Database
- **SQLite**: Lightweight, file-based database

### Tools
- **Jupyter Notebook**: Interactive analysis
- **Power BI/Tableau**: Dashboard creation
- **Git**: Version control
- **VS Code**: Development environment

## Limitations

### Data Limitations
- Dataset covers limited time period (2022-2026), may not capture full market cycles
- Historical NAV data may not reflect future performance
- Investor transaction data is anonymized, limiting demographic depth
- Benchmark indices may not perfectly match fund mandates

### Methodological Limitations
- Sharpe Ratio assumes normal distribution of returns
- VaR calculations based on historical data may not predict future tail risks
- CAGR is sensitive to start and end dates
- Composite scorecard weights are subjective

### Technical Limitations
- SQLite has size limitations compared to enterprise databases
- Dashboard refresh rates depend on data source connectivity
- Real-time NAV data requires API access with rate limits

## Future Work

### Short-term Enhancements
- [ ] Add more benchmark indices (sectoral, international)
- [ ] Implement Monte Carlo simulation for portfolio optimization
- [ ] Add sentiment analysis from news/articles
- [ ] Create web-based dashboard using Streamlit/Dash

### Long-term Enhancements
- [ ] Real-time data pipeline with Apache Kafka
- [ ] Machine learning models for return prediction
- [ ] Portfolio optimization using mean-variance analysis
- [ ] Integration with broker APIs for live trading data
- [ ] Mobile app for dashboard access

### Research Extensions
- [ ] Factor-based analysis (Fama-French, Carhart)
- [ ] Style analysis (Sharpe's returns-based style)
- [ ] Performance attribution analysis
- [ ] Peer group analysis and ranking

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Author:** Maneesh Reddy  
**Email:** maneesh.reddy@example.com  
**GitHub:** [@maneeshreddy](https://github.com/maneeshreddy)  
**LinkedIn:** [Maneesh Reddy](https://linkedin.com/in/maneeshreddy)

---

## Acknowledgments

- Bluestock for providing the capstone project opportunity
- AMFI (Association of Mutual Funds in India) for data standards
- mfapi.in for providing free NAV data API
- Open-source community for excellent Python libraries

---

**Last Updated:** June 2026  
**Version:** 1.0
