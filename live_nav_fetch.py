"""
Live NAV Fetch Script for Mutual Fund Analysis
Fetches live NAV data from mfapi.in for specified mutual fund schemes.
"""

import requests
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import time

# Define the data directory
DATA_DIR = Path(__file__).parent / "data" / "raw"

# API Base URL
BASE_URL = "https://api.mfapi.in/mf"

# Key schemes to fetch
KEY_SCHEMES = {
    "HDFC Top 100 Direct": "125497",
    "SBI Bluechip": "119551",
    "ICICI Bluechip": "120503",
    "Nippon Large Cap": "118632",
    "Axis Bluechip": "119092",
    "Kotak Bluechip": "120841"
}


def fetch_nav_data(scheme_code: str, scheme_name: str) -> dict:
    """
    Fetch NAV data for a specific mutual fund scheme.
    
    Args:
        scheme_code: AMFI scheme code
        scheme_name: Name of the scheme
        
    Returns:
        Dictionary containing the API response
    """
    url = f"{BASE_URL}/{scheme_code}"
    
    print(f"Fetching NAV for {scheme_name} (Code: {scheme_code})...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Successfully fetched data for {scheme_name}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {scheme_name}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON for {scheme_name}: {str(e)}")
        return None


def save_nav_to_csv(data: dict, scheme_name: str, scheme_code: str) -> pd.DataFrame:
    """
    Parse and save NAV data to CSV.
    
    Args:
        data: API response data
        scheme_name: Name of the scheme
        scheme_code: AMFI scheme code
        
    Returns:
        DataFrame containing NAV history
    """
    if not data or 'data' not in data:
        print(f"⚠️  No data available for {scheme_name}")
        return None
    
    # Extract NAV history
    nav_data = data['data']
    
    # Convert to DataFrame
    df = pd.DataFrame(nav_data)
    
    # The API returns data with columns: date, nav (alphabetical order)
    # Ensure correct column mapping regardless of order
    if 'date' not in df.columns or 'nav' not in df.columns:
        print(f"⚠️  Unexpected column structure: {df.columns.tolist()}")
        return None
    
    # Add metadata columns
    df['scheme_code'] = scheme_code
    df['scheme_name'] = scheme_name
    df['fetch_timestamp'] = datetime.now().isoformat()
    
    # Convert data types
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    
    # Sort by date
    df = df.sort_values('date', ascending=False).reset_index(drop=True)
    
    # Save to CSV
    filename = f"nav_{scheme_code}_{scheme_name.replace(' ', '_').lower()}.csv"
    filepath = DATA_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"💾 Saved NAV data to {filename}")
    
    return df


def display_nav_summary(df: pd.DataFrame, scheme_name: str):
    """
    Display summary of NAV data.
    
    Args:
        df: DataFrame containing NAV data
        scheme_name: Name of the scheme
    """
    if df is None or df.empty:
        return
    
    print(f"\n📊 NAV Summary for {scheme_name}:")
    print(f"   Latest NAV: ₹{df.iloc[0]['nav']:.2f} (as of {df.iloc[0]['date'].strftime('%Y-%m-%d')})")
    print(f"   NAV History: {len(df)} records")
    print(f"   Date Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"   NAV Range: ₹{df['nav'].min():.2f} - ₹{df['nav'].max():.2f}")
    print()


def main():
    """Main function to fetch and save NAV data for all key schemes."""
    print("\n" + "=" * 80)
    print("LIVE NAV FETCH FROM mfapi.in")
    print("=" * 80)
    print(f"Fetch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch NAV for each scheme
    all_nav_data = {}
    
    for scheme_name, scheme_code in KEY_SCHEMES.items():
        # Fetch data
        data = fetch_nav_data(scheme_code, scheme_name)
        
        if data:
            # Save to CSV and get DataFrame
            df = save_nav_to_csv(data, scheme_name, scheme_code)
            
            if df is not None:
                # Display summary
                display_nav_summary(df, scheme_name)
                all_nav_data[scheme_name] = df
        
        # Add delay to avoid overwhelming the API
        time.sleep(0.5)
    
    # Create combined NAV file
    if all_nav_data:
        combined_df = pd.concat(all_nav_data.values(), ignore_index=True)
        combined_filepath = DATA_DIR / "nav_all_schemes.csv"
        combined_df.to_csv(combined_filepath, index=False)
        print(f"\n💾 Combined NAV data saved to nav_all_schemes.csv")
    
    # Summary
    print("\n" + "=" * 80)
    print("FETCH SUMMARY")
    print("=" * 80)
    print(f"Total schemes: {len(KEY_SCHEMES)}")
    print(f"Successfully fetched: {len(all_nav_data)}")
    print(f"Failed: {len(KEY_SCHEMES) - len(all_nav_data)}")
    
    if len(all_nav_data) < len(KEY_SCHEMES):
        print("\nFailed schemes:")
        for scheme_name in KEY_SCHEMES.keys():
            if scheme_name not in all_nav_data:
                print(f"  - {scheme_name}")
    
    print("\n✅ Live NAV fetch complete!")
    return all_nav_data


if __name__ == "__main__":
    nav_data = main()
