# Mutual Fund Analysis Project

A comprehensive data analysis project for Indian mutual funds, featuring data ingestion, live NAV fetching, and exploratory analysis.

## Project Structure

```
mutual_fund_analysis/
├── data/
│   ├── raw/              # Raw CSV datasets (10 files)
│   └── processed/        # Processed data files
├── notebooks/            # Jupyter notebooks for analysis
├── sql/                  # SQL queries
├── dashboard/            # Dashboard files
├── reports/              # Generated reports
│   └── data_quality_summary.txt
├── data_ingestion.py     # Load and explore CSV datasets
├── live_nav_fetch.py     # Fetch live NAV from mfapi.in
├── explore_fund_master.py # Explore fund master & validate AMFI codes
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Datasets

The project uses 10 CSV datasets:
1. **Fund Master** - Scheme details (40 schemes, 15 columns)
2. **NAV History** - Historical NAV data (46,000 records)
3. **AUM by Fund House** - Assets under management (90 records)
4. **Monthly SIP Inflows** - SIP flow data (48 records)
5. **Category Inflows** - Category-wise inflows (30 records)
6. **Industry Folio Count** - Investor folio data (12 records)
7. **Scheme Performance** - Performance metrics (40 records)
8. **Investor Transactions** - Transaction data (32,778 records)
9. **Portfolio Holdings** - Stock holdings (322 records)
10. **Benchmark Indices** - Index data (8,050 records)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run data ingestion:**
   ```bash
   python data_ingestion.py
   ```

3. **Fetch live NAV data:**
   ```bash
   python live_nav_fetch.py
   ```

4. **Explore fund master & validate codes:**
   ```bash
   python explore_fund_master.py
   ```

## Key Features

### Data Ingestion
- Loads all 10 CSV datasets using Pandas
- Prints shape, dtypes, and head for each dataset
- Detects anomalies (missing values, duplicates, type issues)

### Live NAV Fetching
- Fetches live NAV from mfapi.in API
- Covers 6 key schemes:
  - HDFC Top 100 Direct (125497)
  - SBI Bluechip (119551)
  - ICICI Bluechip (120503)
  - Nippon Large Cap (118632)
  - Axis Bluechip (119092)
  - Kotak Bluechip (120841)
- Saves individual and combined CSV files

### Fund Master Exploration
- **10 Unique Fund Houses:** SBI, ICICI, HDFC, Nippon, Kotak, Axis, DSP, Mirae, Aditya Birla, UTI
- **2 Categories:** Equity (34 schemes), Debt (6 schemes)
- **12 Sub-Categories:** Large Cap, Mid Cap, Small Cap, Flexi Cap, ELSS, Gilt, Liquid, etc.
- **AMFI Code Validation:** 100% match between fund_master and nav_history

### Data Quality Summary
- Fund Master: 40 records, 0 missing values, 0 duplicates
- NAV History: 46,000 records, 0 missing values, 0 duplicates
- AMFI Code Match: 100% (40/40 codes)

## API Reference

**mfapi.in Endpoint:**
```
GET https://api.mfapi.in/mf/{scheme_code}
```

Returns JSON with scheme metadata and NAV history.

## Dependencies

- pandas >= 1.5.0
- numpy >= 1.23.0
- matplotlib >= 3.6.0
- seaborn >= 0.12.0
- plotly >= 5.10.0
- sqlalchemy >= 1.4.0
- requests >= 2.28.0
- scipy >= 1.9.0
- jupyter >= 1.0.0

## Git History

- **Day 1:** Data ingestion complete - Initial setup with all datasets and scripts

## Author

Created as part of an internship project for mutual fund data analysis.

## License

This project is developed for internship purposes.
