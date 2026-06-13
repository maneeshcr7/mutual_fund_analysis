"""
Compute Performance Metrics for Mutual Fund Analysis
=====================================================

Computes key performance metrics from first principles using daily NAV data:
- Sharpe Ratio: Risk-adjusted return measure
- Sortino Ratio: Downside risk-adjusted return
- Alpha & Beta: OLS regression against benchmark
- CAGR: Compound Annual Growth Rate
- Maximum Drawdown: Largest peak-to-trough decline
- Value at Risk (VaR): Potential loss at given confidence level

All metrics are annualized using 252 trading days.

Functions:
    load_data: Load NAV, benchmark, performance, and fund master data
    compute_daily_returns: Calculate daily percentage returns
    compute_cagr: Calculate Compound Annual Growth Rate
    compute_sharpe: Calculate Sharpe Ratio
    compute_sortino: Calculate Sortino Ratio
    compute_alpha_beta: Calculate Alpha and Beta via OLS regression
    compute_max_drawdown: Calculate Maximum Drawdown
    compute_var: Calculate Value at Risk
    main: Orchestrate metric computation for all funds

Author: Bluestock Capstone Project
Version: 1.0
"""

import pandas as pd
import numpy as np
from scipy import stats
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use pathlib for cross-platform paths
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data_1" / "Bluestock_MF_Datasets"

# Constants
RF = 0.065  # Risk-free rate (RBI repo rate proxy)
TRADING_DAYS = 252  # Number of trading days per year


def load_data():
    """
    Load NAV, benchmark, performance, and fund master data.
    
    Returns:
        tuple: (nav_df, bench_df, perf_df, fm_df) - DataFrames for
               NAV history, benchmark indices, scheme performance, and fund master.
    """
    nav_df = pd.read_csv(DATA_DIR / "02_nav_history.csv", parse_dates=["date"])
    bench_df = pd.read_csv(DATA_DIR / "10_benchmark_indices.csv", parse_dates=["date"])
    perf_df = pd.read_csv(DATA_DIR / "07_scheme_performance.csv")
    fm_df = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    return nav_df, bench_df, perf_df, fm_df


def compute_daily_returns(nav_df):
    """
    Compute daily returns from NAV data.
    
    Formula: daily_return = nav_t / nav_{t-1} - 1
    
    Args:
        nav_df (pd.DataFrame): DataFrame with columns ['date', 'amfi_code', 'nav'].
        
    Returns:
        pd.DataFrame: Daily returns indexed by date, columns are AMFI codes.
    """
    nav_pivot = nav_df.pivot(index="date", columns="amfi_code", values="nav").sort_index()
    daily_returns = nav_pivot.pct_change().dropna()
    return daily_returns


def compute_cagr(nav_series):
    """
    Compute Compound Annual Growth Rate (CAGR).
    
    Formula: CAGR = (NAV_end / NAV_start) ^ (1/n) - 1
    
    Args:
        nav_series (pd.Series): Time series of NAV values with datetime index.
        
    Returns:
        float: CAGR as a decimal (e.g., 0.15 for 15%), or np.nan if insufficient data.
    """
    nav_clean = nav_series.dropna()
    if len(nav_clean) < 2:
        return np.nan
    nav_start = nav_clean.iloc[0]
    nav_end = nav_clean.iloc[-1]
    if nav_start <= 0:
        return np.nan
    actual_years = (nav_clean.index[-1] - nav_clean.index[0]).days / 365.25
    if actual_years < 0.5:
        return np.nan
    return (nav_end / nav_start) ** (1 / actual_years) - 1


def compute_sharpe(returns):
    """
    Compute Sharpe Ratio.
    
    Formula: Sharpe = (Rp - Rf) / Std(Rp) * sqrt(252)
    
    Where:
        Rp = mean daily return
        Rf = daily risk-free rate (annual rate / 252)
        Std(Rp) = standard deviation of daily returns
    
    Args:
        returns (pd.Series): Daily return series.
        
    Returns:
        float: Annualized Sharpe Ratio.
    """
    excess = returns.mean() - RF / TRADING_DAYS
    return (excess / returns.std()) * np.sqrt(TRADING_DAYS)


def compute_sortino(returns):
    """
    Compute Sortino Ratio.
    
    Formula: Sortino = (Rp - Rf) / Std(downside) * sqrt(252)
    
    Where:
        Std(downside) = standard deviation of negative returns only
    
    Args:
        returns (pd.Series): Daily return series.
        
    Returns:
        float: Annualized Sortino Ratio, or np.inf if no downside returns.
    """
    excess = returns.mean() - RF / TRADING_DAYS
    downside = returns[returns < 0]
    if len(downside) == 0:
        return np.inf
    return (excess / downside.std()) * np.sqrt(TRADING_DAYS)


def compute_alpha_beta(fund_returns, bench_returns):
    """
    Compute Alpha and Beta via OLS regression against benchmark.
    
    Formula:
        Alpha = intercept * 252 (annualized)
        Beta = slope of regression line
    
    Args:
        fund_returns (pd.Series): Daily returns of the fund.
        bench_returns (pd.Series): Daily returns of the benchmark.
        
    Returns:
        tuple: (alpha, beta, r_squared) - Annualized alpha, beta, and R-squared.
               Returns (np.nan, np.nan, np.nan) if insufficient data.
    """
    common = fund_returns.index.intersection(bench_returns.index)
    if len(common) < 60:
        return np.nan, np.nan, np.nan
    y = fund_returns.loc[common].values
    x = bench_returns.loc[common].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return intercept * TRADING_DAYS, slope, r_value ** 2


def compute_max_drawdown(nav_series):
    """
    Compute Maximum Drawdown.
    
    Formula: Max Drawdown = min(NAV / running_max - 1)
    
    Args:
        nav_series (pd.Series): Time series of NAV values.
        
    Returns:
        tuple: (max_drawdown, drawdown_date) - Maximum drawdown value and
               the date it occurred.
    """
    running_max = nav_series.cummax()
    drawdown = nav_series / running_max - 1
    return drawdown.min(), drawdown.idxmin()


def compute_var(returns, confidence=0.95):
    """
    Compute Historical Value at Risk (VaR).
    
    Args:
        returns (pd.Series): Daily return series.
        confidence (float): Confidence level (e.g., 0.95 for 95%).
        
    Returns:
        float: VaR as a positive number representing potential loss.
    """
    return -np.percentile(returns.dropna(), (1 - confidence) * 100)


def main():
    """
    Main function to compute performance metrics for all funds.
    
    Orchestrates the computation of all performance metrics for each fund
    and saves results to a CSV file.
    
    Returns:
        pd.DataFrame: DataFrame containing all computed metrics for each fund.
    """
    logger.info("=" * 60)
    logger.info("COMPUTING PERFORMANCE METRICS")
    logger.info("=" * 60)

    nav_df, bench_df, perf_df, fm_df = load_data()
    daily_returns = compute_daily_returns(nav_df)

    # Benchmark returns
    nifty100 = bench_df[bench_df["index_name"] == "NIFTY100"].set_index("date")["close_value"].pct_change().dropna()

    # NAV pivot for CAGR and drawdown
    nav_pivot = nav_df.pivot(index="date", columns="amfi_code", values="nav").sort_index()

    code_to_name = dict(zip(fm_df["amfi_code"], fm_df["scheme_name"]))

    results = []
    for code in nav_pivot.columns:
        nav_series = nav_pivot[code].dropna()
        returns = daily_returns[code].dropna()

        if len(returns) < 60:
            continue

        cagr = compute_cagr(nav_series)
        sharpe = compute_sharpe(returns)
        sortino = compute_sortino(returns)
        alpha, beta, r_sq = compute_alpha_beta(returns, nifty100)
        max_dd, dd_date = compute_max_drawdown(nav_series)
        var95 = compute_var(returns, 0.95)

        results.append({
            "amfi_code": code,
            "scheme_name": code_to_name.get(code, str(code)),
            "cagr": round(cagr, 4),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "alpha_annualized": round(alpha, 4) if not np.isnan(alpha) else np.nan,
            "beta": round(beta, 4) if not np.isnan(beta) else np.nan,
            "r_squared": round(r_sq, 4) if not np.isnan(r_sq) else np.nan,
            "max_drawdown": round(max_dd, 4),
            "max_dd_date": dd_date,
            "var_95_daily": round(var95, 4),
            "n_obs": len(returns)
        })

    results_df = pd.DataFrame(results).sort_values("sharpe_ratio", ascending=False)
    results_df.to_csv(WORKSPACE / "computed_metrics.csv", index=False)

    logger.info("Top 10 by Sharpe Ratio:")
    logger.info(f"\n{results_df[['scheme_name', 'cagr', 'sharpe_ratio', 'alpha_annualized', 'beta', 'max_drawdown']].head(10).to_string(index=False)}")
    logger.info("Metrics saved to computed_metrics.csv")
    return results_df


if __name__ == "__main__":
    main()
