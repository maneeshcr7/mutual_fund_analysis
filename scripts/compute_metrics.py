"""
Compute Performance Metrics for Mutual Fund Analysis
Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR
"""

import pandas as pd
import numpy as np
from scipy import stats
import os
import sys
from pathlib import Path

# Use pathlib for cross-platform paths
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data_1" / "Bluestock_MF_Datasets"
RF = 0.065  # Risk-free rate (RBI repo rate proxy)
TRADING_DAYS = 252


def load_data():
    """Load NAV and benchmark data."""
    nav_df = pd.read_csv(DATA_DIR / "02_nav_history.csv", parse_dates=["date"])
    bench_df = pd.read_csv(DATA_DIR / "10_benchmark_indices.csv", parse_dates=["date"])
    perf_df = pd.read_csv(DATA_DIR / "07_scheme_performance.csv")
    fm_df = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    return nav_df, bench_df, perf_df, fm_df


def compute_daily_returns(nav_df):
    """Compute daily returns: nav_t / nav_{t-1} - 1"""
    nav_pivot = nav_df.pivot(index="date", columns="amfi_code", values="nav").sort_index()
    daily_returns = nav_pivot.pct_change().dropna()
    return daily_returns


def compute_cagr(nav_series):
    """Compute CAGR: (NAV_end / NAV_start) ^ (1/n) - 1"""
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
    """Sharpe Ratio: (Rp - Rf) / Std(Rp) * sqrt(252)"""
    excess = returns.mean() - RF / TRADING_DAYS
    return (excess / returns.std()) * np.sqrt(TRADING_DAYS)


def compute_sortino(returns):
    """Sortino Ratio: (Rp - Rf) / Std(downside) * sqrt(252)"""
    excess = returns.mean() - RF / TRADING_DAYS
    downside = returns[returns < 0]
    if len(downside) == 0:
        return np.inf
    return (excess / downside.std()) * np.sqrt(TRADING_DAYS)


def compute_alpha_beta(fund_returns, bench_returns):
    """OLS regression: Alpha = intercept * 252, Beta = slope"""
    common = fund_returns.index.intersection(bench_returns.index)
    if len(common) < 60:
        return np.nan, np.nan, np.nan
    y = fund_returns.loc[common].values
    x = bench_returns.loc[common].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return intercept * TRADING_DAYS, slope, r_value ** 2


def compute_max_drawdown(nav_series):
    """Max Drawdown: min(NAV / running_max - 1)"""
    running_max = nav_series.cummax()
    drawdown = nav_series / running_max - 1
    return drawdown.min(), drawdown.idxmin()


def compute_var(returns, confidence=0.95):
    """Historical VaR at given confidence level."""
    return -np.percentile(returns.dropna(), (1 - confidence) * 100)


def main():
    print("=" * 60)
    print("COMPUTING PERFORMANCE METRICS")
    print("=" * 60)

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

    print("\nTop 10 by Sharpe Ratio:")
    print(results_df[["scheme_name", "cagr", "sharpe_ratio", "alpha_annualized", "beta", "max_drawdown"]].head(10).to_string(index=False))
    print("\nMetrics saved to computed_metrics.csv")
    return results_df


if __name__ == "__main__":
    main()
