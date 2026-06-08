"""
Fund Recommender System
Content-based filtering using fund characteristics and cosine similarity.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import os

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data_1" / "Bluestock_MF_Datasets"


def load_features():
    """Load and prepare fund feature matrix."""
    perf_df = pd.read_csv(DATA_DIR / "07_scheme_performance.csv")

    features = perf_df[["amfi_code", "scheme_name", "category", "return_1yr_pct",
                         "return_3yr_pct", "sharpe_ratio", "sortino_ratio", "beta",
                         "expense_ratio_pct", "aum_crore", "morningstar_rating",
                         "max_drawdown_pct", "risk_grade"]].copy()

    risk_map = {"Low": 1, "Moderate": 2, "Moderately High": 3, "High": 4, "Very High": 5}
    features["risk_score"] = features["risk_grade"].map(risk_map)

    numeric_cols = ["return_1yr_pct", "return_3yr_pct", "sharpe_ratio", "sortino_ratio",
                    "beta", "expense_ratio_pct", "aum_crore", "morningstar_rating",
                    "max_drawdown_pct", "risk_score"]

    features[numeric_cols] = features[numeric_cols].fillna(features[numeric_cols].median())

    scaler = MinMaxScaler()
    features_scaled = pd.DataFrame(
        scaler.fit_transform(features[numeric_cols]),
        columns=numeric_cols,
        index=features.index
    )

    return features, features_scaled


def recommend_similar(fund_name, n=5):
    """Recommend similar funds based on cosine similarity."""
    features, features_scaled = load_features()

    mask = features["scheme_name"].str.contains(fund_name, case=False, na=False)
    if not mask.any():
        print("Fund not found. Available funds:")
        for name in features["scheme_name"].tolist():
            print("  -", name)
        return None

    idx = mask.idxmax()
    fund_name_full = features.loc[idx, "scheme_name"]

    sim_matrix = cosine_similarity(features_scaled)
    sim_scores = sorted(enumerate(sim_matrix[idx]), key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in sim_scores[1:n+1]]

    result = features.iloc[top_indices][["scheme_name", "category", "return_3yr_pct",
                                          "sharpe_ratio", "expense_ratio_pct", "risk_grade"]].copy()
    result["similarity_score"] = [round(sim_scores[i][1], 4) for i in range(1, n+1)]

    print("\nRecommendations for:", fund_name_full)
    print(result.to_string(index=False))
    return result


def recommend_by_profile(risk_tolerance, investment_horizon, top_n=5):
    """Recommend funds based on investor risk profile.

    risk_tolerance: 'conservative', 'moderate', 'aggressive'
    investment_horizon: 'short' (<2yr), 'medium' (2-5yr), 'long' (>5yr)
    """
    features, _ = load_features()

    risk_filters = {
        "conservative": ["Low", "Moderate"],
        "moderate": ["Moderate", "Moderately High"],
        "aggressive": ["High", "Very High"]
    }

    filtered = features[features["risk_grade"].isin(risk_filters[risk_tolerance])].copy()

    if investment_horizon == "short":
        filtered["score"] = (
            0.3 * filtered["sharpe_ratio"].rank(pct=True) +
            0.3 * (1 - filtered["expense_ratio_pct"].rank(pct=True)) +
            0.2 * filtered["morningstar_rating"].rank(pct=True) +
            0.2 * filtered["max_drawdown_pct"].rank(pct=True)
        )
    elif investment_horizon == "medium":
        filtered["score"] = (
            0.3 * filtered["return_3yr_pct"].rank(pct=True) +
            0.25 * filtered["sharpe_ratio"].rank(pct=True) +
            0.2 * (1 - filtered["expense_ratio_pct"].rank(pct=True)) +
            0.15 * filtered["morningstar_rating"].rank(pct=True) +
            0.1 * filtered["max_drawdown_pct"].rank(pct=True)
        )
    else:
        filtered["score"] = (
            0.35 * filtered["return_3yr_pct"].rank(pct=True) +
            0.25 * filtered["sharpe_ratio"].rank(pct=True) +
            0.15 * (1 - filtered["expense_ratio_pct"].rank(pct=True)) +
            0.15 * filtered["morningstar_rating"].rank(pct=True) +
            0.1 * filtered["max_drawdown_pct"].rank(pct=True)
        )

    result = filtered.nlargest(top_n, "score")[["scheme_name", "category", "risk_grade",
                                                   "return_3yr_pct", "sharpe_ratio",
                                                   "expense_ratio_pct", "score"]]
    print("\nProfile:", risk_tolerance, "|", investment_horizon, "term")
    print(result.to_string(index=False))
    return result


def main():
    print("=" * 60)
    print("FUND RECOMMENDER SYSTEM")
    print("=" * 60)

    # Demo: Similar fund recommendations
    print("\n--- Similar Fund Recommendations ---")
    for fund in ["SBI Bluechip", "HDFC Mid-Cap", "Axis Small Cap"]:
        recommend_similar(fund, n=3)

    # Demo: Profile-based recommendations
    print("\n\n--- Profile-Based Recommendations ---")
    for risk in ["conservative", "moderate", "aggressive"]:
        for horizon in ["short", "medium", "long"]:
            recommend_by_profile(risk, horizon, top_n=3)


if __name__ == "__main__":
    main()
