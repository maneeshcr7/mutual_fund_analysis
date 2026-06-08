"""
Fund Master Exploration and AMFI Code Validation Script
Explores fund master data and validates AMFI codes against NAV history.
"""

import pandas as pd
from pathlib import Path

# Define the data directory
DATA_DIR = Path(__file__).parent / "data" / "raw"


def load_fund_master() -> pd.DataFrame:
    """Load fund master dataset."""
    filepath = DATA_DIR / "01_fund_master.csv"
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Loaded 01_fund_master.csv: {df.shape[0]} rows × {df.shape[1]} columns\n")
        return df
    except FileNotFoundError:
        print(f"❌ 01_fund_master.csv not found in {DATA_DIR}")
        return None


def load_nav_history() -> pd.DataFrame:
    """Load NAV history dataset."""
    filepath = DATA_DIR / "02_nav_history.csv"
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Loaded 02_nav_history.csv: {df.shape[0]} rows × {df.shape[1]} columns\n")
        return df
    except FileNotFoundError:
        print(f"❌ 02_nav_history.csv not found in {DATA_DIR}")
        return None


def explore_fund_master(df: pd.DataFrame):
    """
    Explore fund master data and print unique values.
    
    Args:
        df: Fund master DataFrame
    """
    if df is None:
        return
    
    print("=" * 80)
    print("FUND MASTER EXPLORATION")
    print("=" * 80)
    
    # Print column names
    print("\n📋 Columns in fund_master:")
    for col in df.columns:
        print(f"  • {col}")
    
    # Identify key columns (adjust based on actual column names)
    # Common column names in mutual fund data
    column_mapping = {
        'fund_house': ['fund_house', 'amc', 'asset_management_company', 'fund_company', 'amc_name'],
        'category': ['category', 'fund_category', 'scheme_category', 'fund_type'],
        'sub_category': ['sub_category', 'subcategory', 'scheme_sub_category', 'category_name'],
        'risk_grade': ['risk_grade', 'risk', 'risk_level', 'riskometer', 'risk_rating'],
        'scheme_code': ['scheme_code', 'amfi_code', 'code', 'scheme_id', 'amfi_scheme_code']
    }
    
    # Find actual column names in the dataset
    actual_columns = {}
    for key, possible_names in column_mapping.items():
        for name in possible_names:
            if name in df.columns:
                actual_columns[key] = name
                break
    
    print("\n" + "=" * 80)
    print("UNIQUE VALUES ANALYSIS")
    print("=" * 80)
    
    # Fund Houses
    if 'fund_house' in actual_columns:
        col = actual_columns['fund_house']
        unique_fund_houses = df[col].dropna().unique()
        print(f"\n🏢 Unique Fund Houses ({len(unique_fund_houses)}):")
        for fh in sorted(unique_fund_houses):
            count = df[df[col] == fh].shape[0]
            print(f"  • {fh} ({count} schemes)")
    
    # Categories
    if 'category' in actual_columns:
        col = actual_columns['category']
        unique_categories = df[col].dropna().unique()
        print(f"\n📁 Unique Categories ({len(unique_categories)}):")
        for cat in sorted(unique_categories):
            count = df[df[col] == cat].shape[0]
            print(f"  • {cat} ({count} schemes)")
    
    # Sub-Categories
    if 'sub_category' in actual_columns:
        col = actual_columns['sub_category']
        unique_sub_categories = df[col].dropna().unique()
        print(f"\n📂 Unique Sub-Categories ({len(unique_sub_categories)}):")
        for sub_cat in sorted(unique_sub_categories):
            count = df[df[col] == sub_cat].shape[0]
            print(f"  • {sub_cat} ({count} schemes)")
    
    # Risk Grades
    if 'risk_grade' in actual_columns:
        col = actual_columns['risk_grade']
        unique_risk_grades = df[col].dropna().unique()
        print(f"\n⚠️  Unique Risk Grades ({len(unique_risk_grades)}):")
        for risk in sorted(unique_risk_grades):
            count = df[df[col] == risk].shape[0]
            print(f"  • {risk} ({count} schemes)")
    
    # AMFI Scheme Code Structure
    if 'scheme_code' in actual_columns:
        col = actual_columns['scheme_code']
        print(f"\n🔢 AMFI Scheme Code Structure:")
        print(f"  • Total codes: {df[col].nunique()}")
        print(f"  • Sample codes: {df[col].head(10).tolist()}")
        print(f"  • Data type: {df[col].dtype}")
        
        # Check if codes are numeric
        if df[col].dtype == 'object':
            numeric_codes = pd.to_numeric(df[col], errors='coerce').notna().sum()
            print(f"  • Numeric codes: {numeric_codes}/{len(df)}")
    
    return actual_columns


def validate_amfi_codes(fund_master_df: pd.DataFrame, nav_history_df: pd.DataFrame, 
                        actual_columns: dict):
    """
    Validate AMFI codes - confirm every code in fund_master exists in nav_history.
    
    Args:
        fund_master_df: Fund master DataFrame
        nav_history_df: NAV history DataFrame
        actual_columns: Dictionary mapping logical column names to actual column names
    """
    if fund_master_df is None or nav_history_df is None:
        return
    
    print("\n" + "=" * 80)
    print("AMFI CODE VALIDATION")
    print("=" * 80)
    
    # Find scheme code column in both datasets
    fm_code_col = actual_columns.get('scheme_code')
    
    # Find scheme code column in nav_history
    nav_code_col = None
    possible_nav_code_cols = ['scheme_code', 'amfi_code', 'code', 'scheme_id', 'amfi_scheme_code']
    for col in possible_nav_code_cols:
        if col in nav_history_df.columns:
            nav_code_col = col
            break
    
    if not fm_code_col or not nav_code_col:
        print("❌ Could not find scheme code columns in one or both datasets")
        print(f"   Fund Master columns: {fund_master_df.columns.tolist()}")
        print(f"   NAV History columns: {nav_history_df.columns.tolist()}")
        return
    
    # Get unique codes from both datasets
    fm_codes = set(fund_master_df[fm_code_col].dropna().astype(str).unique())
    nav_codes = set(nav_history_df[nav_code_col].dropna().astype(str).unique())
    
    print(f"\n📊 Code Statistics:")
    print(f"  • Codes in fund_master: {len(fm_codes)}")
    print(f"  • Codes in nav_history: {len(nav_codes)}")
    
    # Find codes in fund_master but not in nav_history
    missing_in_nav = fm_codes - nav_codes
    print(f"\n❌ Codes in fund_master but NOT in nav_history: {len(missing_in_nav)}")
    if missing_in_nav:
        print(f"   Sample missing codes: {list(missing_in_nav)[:10]}")
    
    # Find codes in nav_history but not in fund_master
    missing_in_fm = nav_codes - fm_codes
    print(f"\n⚠️  Codes in nav_history but NOT in fund_master: {len(missing_in_fm)}")
    if missing_in_fm:
        print(f"   Sample extra codes: {list(missing_in_fm)[:10]}")
    
    # Find common codes
    common_codes = fm_codes & nav_codes
    print(f"\n✅ Common codes (present in both): {len(common_codes)}")
    
    # Calculate match percentage
    if len(fm_codes) > 0:
        match_percentage = (len(common_codes) / len(fm_codes)) * 100
        print(f"\n📈 Match Percentage: {match_percentage:.2f}%")
    
    return {
        'fund_master_codes': len(fm_codes),
        'nav_history_codes': len(nav_codes),
        'common_codes': len(common_codes),
        'missing_in_nav': len(missing_in_nav),
        'missing_in_fm': len(missing_in_fm),
        'match_percentage': match_percentage if len(fm_codes) > 0 else 0
    }


def generate_data_quality_summary(fund_master_df: pd.DataFrame, 
                                  nav_history_df: pd.DataFrame,
                                  validation_results: dict):
    """
    Generate a short data quality summary.
    
    Args:
        fund_master_df: Fund master DataFrame
        nav_history_df: NAV history DataFrame
        validation_results: Results from AMFI code validation
    """
    print("\n" + "=" * 80)
    print("DATA QUALITY SUMMARY")
    print("=" * 80)
    
    summary = []
    
    # Fund Master Quality
    summary.append("\n📋 Fund Master Dataset:")
    summary.append(f"  • Total Records: {len(fund_master_df)}")
    summary.append(f"  • Total Columns: {len(fund_master_df.columns)}")
    
    # Missing values
    fm_missing = fund_master_df.isnull().sum().sum()
    fm_total = fund_master_df.shape[0] * fund_master_df.shape[1]
    fm_missing_pct = (fm_missing / fm_total) * 100 if fm_total > 0 else 0
    summary.append(f"  • Missing Values: {fm_missing} ({fm_missing_pct:.2f}%)")
    
    # Duplicate rows
    fm_duplicates = fund_master_df.duplicated().sum()
    summary.append(f"  • Duplicate Rows: {fm_duplicates}")
    
    # NAV History Quality
    summary.append("\n📈 NAV History Dataset:")
    summary.append(f"  • Total Records: {len(nav_history_df)}")
    summary.append(f"  • Total Columns: {len(nav_history_df.columns)}")
    
    # Missing values
    nav_missing = nav_history_df.isnull().sum().sum()
    nav_total = nav_history_df.shape[0] * nav_history_df.shape[1]
    nav_missing_pct = (nav_missing / nav_total) * 100 if nav_total > 0 else 0
    summary.append(f"  • Missing Values: {nav_missing} ({nav_missing_pct:.2f}%)")
    
    # Duplicate rows
    nav_duplicates = nav_history_df.duplicated().sum()
    summary.append(f"  • Duplicate Rows: {nav_duplicates}")
    
    # AMFI Code Validation
    if validation_results:
        summary.append("\n🔗 AMFI Code Validation:")
        summary.append(f"  • Fund Master Codes: {validation_results['fund_master_codes']}")
        summary.append(f"  • NAV History Codes: {validation_results['nav_history_codes']}")
        summary.append(f"  • Common Codes: {validation_results['common_codes']}")
        summary.append(f"  • Missing in NAV: {validation_results['missing_in_nav']}")
        summary.append(f"  • Match Rate: {validation_results['match_percentage']:.2f}%")
    
    # Overall Quality Assessment
    summary.append("\n✅ Overall Quality Assessment:")
    if fm_missing_pct < 5 and nav_missing_pct < 5:
        summary.append("  • Data Completeness: GOOD (< 5% missing values)")
    elif fm_missing_pct < 10 and nav_missing_pct < 10:
        summary.append("  • Data Completeness: MODERATE (5-10% missing values)")
    else:
        summary.append("  • Data Completeness: POOR (> 10% missing values)")
    
    if validation_results and validation_results['match_percentage'] > 95:
        summary.append("  • Code Validation: EXCELLENT (> 95% match)")
    elif validation_results and validation_results['match_percentage'] > 85:
        summary.append("  • Code Validation: GOOD (85-95% match)")
    elif validation_results:
        summary.append("  • Code Validation: NEEDS ATTENTION (< 85% match)")
    
    # Print summary
    for line in summary:
        print(line)
    
    # Save summary to file
    summary_path = Path(__file__).parent / "reports" / "data_quality_summary.txt"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        f.write("DATA QUALITY SUMMARY\n")
        f.write("=" * 80 + "\n")
        for line in summary:
            f.write(line + "\n")
    
    print(f"\n💾 Summary saved to reports/data_quality_summary.txt")


def main():
    """Main function to explore fund master and validate AMFI codes."""
    print("\n" + "=" * 80)
    print("FUND MASTER EXPLORATION & AMFI CODE VALIDATION")
    print("=" * 80 + "\n")
    
    # Load datasets
    fund_master_df = load_fund_master()
    nav_history_df = load_nav_history()
    
    if fund_master_df is not None:
        # Explore fund master
        actual_columns = explore_fund_master(fund_master_df)
        
        # Validate AMFI codes
        if nav_history_df is not None:
            validation_results = validate_amfi_codes(fund_master_df, nav_history_df, 
                                                     actual_columns)
            
            # Generate data quality summary
            generate_data_quality_summary(fund_master_df, nav_history_df, 
                                         validation_results)
        else:
            print("\n⚠️  Cannot validate AMFI codes without nav_history.csv")
    else:
        print("\n❌ Cannot proceed without fund_master.csv")
    
    print("\n✅ Exploration and validation complete!")


if __name__ == "__main__":
    main()
