# Bluestock Mutual Fund Capstone Project

A comprehensive data analysis and analytics project for Indian mutual funds, featuring ETL pipelines, SQLite database, exploratory analysis, performance metrics, advanced analytics (VaR, cohort analysis, recommender system), and interactive dashboards.

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
│   └── explore_fund_master.py
├── sql/
│   ├── schema.sql            ← star schema DDL
│   └── queries.sql           ← 15 analytical SQL queries
├── dashboard/
│   └── (Power BI / Tableau files)
├── reports/
│   ├── figures/              ← 23 analysis charts (PNG)
│   ├── data_quality_summary.txt
│   ├── Final_Report.pdf
│   └── Presentation.pptx
├── data_dictionary.md        ← column-level documentation
├── requirements.txt          ├── Python dependencies
├── .gitignore                ← excludes *.db, data files
└── README.md                 ← this file
```

## Datasets

| # | File | Description | Records |
|---|------|-------------|---------|
| 1 | 01_fund_master.csv | Scheme details (40 schemes, 15 columns) | 40 |
| 2 | 02_nav_history.csv | Daily NAV history | 46,000 |
| 3 | 03_aum_by_fund_house.csv | AUM by fund house over time | 90 |
| 4 | 04_monthly_sip_inflows.csv | Monthly SIP inflow data | 48 |
| 5 | 05_category_inflows.csv | Category-wise net inflows | 144 |
| 6 | 06_industry_folio_count.csv | Industry folio count data | 21 |
| 7 | 07_scheme_performance.csv | Scheme performance metrics | 40 |
| 8 | 08_investor_transactions.csv | Investor transaction records | 32,778 |
| 9 | 09_portfolio_holdings.csv | Portfolio holdings details | 322 |
| 10 | 10_benchmark_indices.csv | Benchmark index data (7 indices) | 8,050 |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run ETL pipeline
python scripts/etl_pipeline.py

# Run data cleaning + SQLite loading
python scripts/data_cleaning.py

# Fetch live NAV data
python scripts/live_nav_fetch.py

# Compute performance metrics
python scripts/compute_metrics.py

# Run recommender
python scripts/recommender.py
```

## Key Features

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
- `reports/Presentation.pptx`: Slide deck for stakeholder presentation

## Key Findings

1. **Top Performing Funds** (by composite score): Mirae Asset Large Cap (86.25), ICICI Pru Midcap (82.25), Kotak Flexicap (82.00)
2. **Risk-Adjusted Returns**: Sharpe ratios range from -0.5 to 1.45; liquid/gilt funds show highest Sharpe due to low volatility
3. **Investor Demographics**: 26-35 age group dominates SIP investments; T30 cities contribute ~65% of total inflows
4. **VaR Analysis**: Small cap funds show highest daily VaR (~3.5%), liquid funds lowest (~0.1%)
5. **Cohort Insights**: SIP investors average 8+ transactions with 200+ day tenure; strong retention in equity funds

## SQL Queries (15 analytical queries in `queries.sql`)

1. Top 5 Funds by AUM
2. Average NAV per Month for Each Fund
3. SIP Year-over-Year Growth Analysis
4. Transactions by State — Distribution and Volume
5. Funds with Expense Ratio Less Than 1%
6. Top Performing Funds by Category (3-Year Returns)
7. Investor Demographics Analysis
8. Fund House Market Share by AUM
9. Monthly Category-wise Net Inflows
10. Risk-Adjusted Performance Analysis
11. NAV Volatility Analysis (Bonus)
12. Investor Retention Analysis (Bonus)
13. Benchmark Index Performance (Bonus)
14. Portfolio Concentration by Sector (Bonus)
15. AUM Growth by Fund House Over Time (Bonus)

## Common Mistakes Avoided

- No hard-coded file paths — all use `pathlib.Path`
- Weekends/holidays handled via `pd.bdate_range` + `ffill()`
- CAGR annualized with `252 / n_trading_days` (not calendar days)
- Dashboard includes slicers on every page
- Column names include units (e.g., `aum_crore`, `aum_lakh_crore`)
- `*.db` files in `.gitignore` — `schema.sql` shared instead

## Dependencies

```
pandas>=1.5.0, numpy>=1.23.0, matplotlib>=3.6.0, seaborn>=0.12.0,
plotly>=5.10.0, sqlalchemy>=1.4.0, requests>=2.28.0, scipy>=1.9.0,
scikit-learn>=1.1.0, jupyter>=1.0.0
```

## Author

Created as part of the Bluestock Mutual Fund Capstone Project.
