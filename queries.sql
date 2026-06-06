-- ============================================================
-- Bluestock Mutual Fund Analysis - 10 Analytical SQL Queries
-- ============================================================

-- Query 1: Top 5 Funds by AUM (Assets Under Management)
-- Returns the 5 mutual fund schemes with the highest AUM
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    aum_crore,
    expense_ratio_pct,
    morningstar_rating
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;


-- Query 2: Average NAV per Month for Each Fund
-- Calculates monthly average NAV to track fund performance over time
SELECT 
    fn.amfi_code,
    df.scheme_name,
    dd.year,
    dd.month,
    dd.month_name,
    ROUND(AVG(fn.nav), 4) AS avg_nav,
    ROUND(MIN(fn.nav), 4) AS min_nav,
    ROUND(MAX(fn.nav), 4) AS max_nav,
    COUNT(*) AS trading_days
FROM fact_nav fn
JOIN dim_fund df ON fn.amfi_code = df.amfi_code
JOIN dim_date dd ON fn.date = dd.full_date
GROUP BY fn.amfi_code, dd.year, dd.month
ORDER BY fn.amfi_code, dd.year, dd.month;


-- Query 3: SIP Year-over-Year Growth Analysis
-- Analyzes the growth of SIP inflows year over year
SELECT 
    year,
    month,
    month_name,
    sip_inflow_crore,
    active_sip_accounts_crore,
    yoy_growth_pct,
    sip_aum_lakh_crore,
    LAG(sip_inflow_crore) OVER (ORDER BY month) AS prev_month_inflow,
    ROUND(
        (sip_inflow_crore - LAG(sip_inflow_crore) OVER (ORDER BY month)) / 
        LAG(sip_inflow_crore) OVER (ORDER BY month) * 100, 2
    ) AS mom_growth_pct
FROM fact_sip_inflows
ORDER BY month;


-- Query 4: Transactions by State - Distribution and Volume
-- Shows transaction patterns across different states
SELECT 
    state,
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT investor_id) AS unique_investors,
    SUM(CASE WHEN transaction_type = 'SIP' THEN 1 ELSE 0 END) AS sip_count,
    SUM(CASE WHEN transaction_type = 'Lumpsum' THEN 1 ELSE 0 END) AS lumpsum_count,
    SUM(CASE WHEN transaction_type = 'Redemption' THEN 1 ELSE 0 END) AS redemption_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_amount_inr
FROM fact_transactions
WHERE state IS NOT NULL
GROUP BY state
ORDER BY total_transactions DESC;


-- Query 5: Funds with Expense Ratio Less Than 1%
-- Identifies cost-effective funds for investors
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    plan,
    expense_ratio_pct,
    return_1yr_pct,
    return_3yr_pct,
    return_5yr_pct,
    aum_crore,
    morningstar_rating,
    risk_grade
FROM fact_performance
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;


-- Query 6: Top Performing Funds by Category (3-Year Returns)
-- Ranks funds within each category based on 3-year returns
SELECT 
    category,
    scheme_name,
    fund_house,
    return_3yr_pct,
    return_5yr_pct,
    sharpe_ratio,
    RANK() OVER (PARTITION BY category ORDER BY return_3yr_pct DESC) AS rank_in_category
FROM fact_performance
WHERE return_3yr_pct IS NOT NULL
ORDER BY category, rank_in_category;


-- Query 7: Investor Demographics Analysis
-- Analyzes investor patterns by age group, gender, and city tier
SELECT 
    age_group,
    gender,
    city_tier,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT investor_id) AS unique_investors,
    ROUND(SUM(amount_inr), 2) AS total_invested,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_amount,
    ROUND(AVG(annual_income_lakh), 2) AS avg_annual_income
FROM fact_transactions
WHERE age_group IS NOT NULL
GROUP BY age_group, gender, city_tier
ORDER BY age_group, gender, city_tier;


-- Query 8: Fund House Market Share by AUM
-- Calculates each fund house's market share in the industry
WITH total_aum AS (
    SELECT SUM(aum_crore) AS industry_aum FROM fact_performance
)
SELECT 
    fund_house,
    COUNT(*) AS num_schemes,
    SUM(aum_crore) AS total_aum_crore,
    ROUND(AVG(expense_ratio_pct), 2) AS avg_expense_ratio,
    ROUND(AVG(return_3yr_pct), 2) AS avg_3yr_return,
    ROUND(SUM(aum_crore) / (SELECT industry_aum FROM total_aum) * 100, 2) AS market_share_pct
FROM fact_performance
GROUP BY fund_house
ORDER BY total_aum_crore DESC;


-- Query 9: Monthly Category-wise Net Inflows
-- Tracks investment flows across different fund categories
SELECT 
    month,
    category,
    net_inflow_crore,
    SUM(net_inflow_crore) OVER (PARTITION BY category ORDER BY month) AS cumulative_inflow,
    LAG(net_inflow_crore) OVER (PARTITION BY category ORDER BY month) AS prev_month_inflow,
    ROUND(
        (net_inflow_crore - LAG(net_inflow_crore) OVER (PARTITION BY category ORDER BY month)) / 
        NULLIF(LAG(net_inflow_crore) OVER (PARTITION BY category ORDER BY month), 0) * 100, 2
    ) AS mom_change_pct
FROM fact_category_inflows
ORDER BY category, month;


-- Query 10: Risk-Adjusted Performance Analysis
-- Identifies funds with best risk-adjusted returns (Sharpe Ratio)
SELECT 
    fp.amfi_code,
    fp.scheme_name,
    fp.fund_house,
    fp.category,
    fp.return_1yr_pct,
    fp.return_3yr_pct,
    fp.return_5yr_pct,
    fp.sharpe_ratio,
    fp.sortino_ratio,
    fp.beta,
    fp.std_dev_ann_pct,
    fp.max_drawdown_pct,
    fp.risk_grade,
    fp.aum_crore,
    CASE 
        WHEN fp.sharpe_ratio > 1.5 THEN 'Excellent'
        WHEN fp.sharpe_ratio > 1.0 THEN 'Good'
        WHEN fp.sharpe_ratio > 0.5 THEN 'Average'
        ELSE 'Below Average'
    END AS risk_adjusted_rating
FROM fact_performance fp
WHERE fp.sharpe_ratio IS NOT NULL
ORDER BY fp.sharpe_ratio DESC;


-- ============================================================
-- BONUS QUERIES (Additional Analysis)
-- ============================================================

-- Bonus Query 11: NAV Volatility Analysis
-- Identifies most and least volatile funds based on NAV standard deviation
SELECT 
    fn.amfi_code,
    df.scheme_name,
    df.category,
    ROUND(AVG(fn.nav), 4) AS avg_nav,
    ROUND(((MAX(fn.nav) - MIN(fn.nav)) / MIN(fn.nav)) * 100, 2) AS nav_range_pct,
    COUNT(*) AS data_points
FROM fact_nav fn
JOIN dim_fund df ON fn.amfi_code = df.amfi_code
GROUP BY fn.amfi_code
ORDER BY nav_range_pct DESC;


-- Bonus Query 12: Investor Retention Analysis (SIP vs Lumpsum)
-- Compares SIP and Lumpsum patterns to understand investor behavior
SELECT 
    transaction_type,
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT investor_id) AS unique_investors,
    ROUND(SUM(amount_inr), 2) AS total_amount,
    ROUND(AVG(amount_inr), 2) AS avg_amount,
    ROUND(MIN(amount_inr), 2) AS min_amount,
    ROUND(MAX(amount_inr), 2) AS max_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;


-- Bonus Query 13: Benchmark Index Performance
-- Tracks benchmark index performance over time
SELECT 
    index_name,
    YEAR(date) AS year,
    MONTH(date) AS month,
    ROUND(AVG(close_value), 2) AS avg_close,
    ROUND(MIN(close_value), 2) AS min_close,
    ROUND(MAX(close_value), 2) AS max_close,
    COUNT(*) AS trading_days
FROM fact_benchmark_indices
GROUP BY index_name, YEAR(date), MONTH(date)
ORDER BY index_name, year, month;


-- Bonus Query 14: Portfolio Concentration by Sector
-- Analyzes which sectors have the highest allocation across funds
SELECT 
    sector,
    COUNT(DISTINCT amfi_code) AS num_funds_holding,
    COUNT(*) AS total_holdings,
    ROUND(AVG(weight_pct), 2) AS avg_weight,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM fact_portfolio_holdings
WHERE sector IS NOT NULL
GROUP BY sector
ORDER BY total_market_value_cr DESC;


-- Bonus Query 15: AUM Growth by Fund House Over Time
-- Tracks how AUM has changed for each fund house
SELECT 
    date,
    fund_house,
    aum_crore,
    num_schemes,
    LAG(aum_crore) OVER (PARTITION BY fund_house ORDER BY date) AS prev_aum,
    ROUND(
        (aum_crore - LAG(aum_crore) OVER (PARTITION BY fund_house ORDER BY date)) / 
        LAG(aum_crore) OVER (PARTITION BY fund_house ORDER BY date) * 100, 2
    ) AS aum_growth_pct
FROM fact_aum
ORDER BY fund_house, date;
